# type: ignore
from collections import UserDict
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, List, Generator, Iterable
from xml.parsers.expat import ExpatError
import logging
import os
import re
import sys
import uuid

from psycopg2 import sql, connect
from psycopg2 import Error as Psycopg2Error
from psycopg2.extras import RealDictCursor
import xmltodict

from pydavinci.exceptions import *
from pydavinci.main import pydavinci_context
from pydavinci.wrappers.renderjob import RenderJob
from pydavinci.utils import is_valid_uuid, auto_cast_str

logger = logging.getLogger(__name__)


class PydavinciDiskPathsMap(UserDict):
    def add(self, name: str, disk_path: str | Path) -> None:
        """
        Store disk paths for local disk databases

        @param name:        Database name
        @param disk_path:   Full disk path
        """
        return self.data.update(
            dict(
                name = name,
                disk_path = disk_path,
            ),
        )
    
    def get(self, name: str) -> str | Path:
        return self.data.get(name)
    
    def remove(self, name: str) -> None:
        return self.data.__delitem__(name)


class DavinciDatabase(object):
    name: str = None
    type: str = None
    _disk_path: Path | None = None
    _disk_path_projects: Path | None = None

    def __init__(
        self,
        name: str = None,
        ip_address: str | None = None,
        **kwargs,
    ):
        self.name = name
        self.ip_address = ip_address
        self.type = type(self).__name__
    
    @classmethod
    def make(
        self,
        DbName: str,
        DbType: str,
        IpAddress: str | None = None,
        **kwargs,
    ):
        if DbType == 'Disk':
            db_instance = DavinciLocalDiskDatabase
        elif DbType == 'PostgreSQL':
            # Blackmagic Cloud databases are still marked as 'PostgreSQL' by the API
            # At the moment, only way I can see to test for Cloud is to examine the IP address string
            # 
            # IP address example:
            #   postgres-jkxc912f.czqkhtruf1hi.ap-southeast-2.rds.amazonaws.com
            # 
            CLOUD_DATABASE_IP_ADDRESS_PATTERN = re.compile(
                r"^postgres-[a-zA-Z0-9]{8}.*(amazonaws)"
            )
            if CLOUD_DATABASE_IP_ADDRESS_PATTERN.match(IpAddress):
                db_instance = DavinciCloudDatabase
            else:
                db_instance = DavinciNetworkDatabase
        return db_instance(
            name = DbName,
            ip_address = IpAddress,
            **kwargs,
        )

    def _make_render_job_instances(self, results: Iterable) -> List[RenderJob] | RenderJob:
        if len(results) == 1:
            return RenderJob(database=self, source=results[0])
        else:
            return list( RenderJob(database=self, source=row) for row in results )
    
    def get_render_job(self, id: str = None, **kwargs) -> RenderJob | None:
        """
        Given render job UUID string, return render job data directly from Database

        @param job_id:  Render job UUID string
        """
        return self._get_render_job(id, **kwargs)
    
    def get_render_jobs(self, **kwargs) -> RenderJob | List[RenderJob]:
        """
        Gets all render jobs from the Database

        @param id:              Return the render job with this ID
        @param job_name:        Return only results with this job name
        @param status:          Return only results with this status - str
        @param timeline_id:     Return only results with this timeline ID - UUID(str)
        @param timeline_name:   Return only results with this timeline name - str
        @param filters:         Other DB col names to filter the returned result - { db_col_name: filter_value }. Col names must be from table `SyRecordInfo`.
        """
        return self._get_render_jobs(**kwargs)
    
    
class DavinciLocalDiskDatabase(DavinciDatabase):
    type_api = 'Disk'

    def __init__(self, **kwargs):
        super(DavinciLocalDiskDatabase, self).__init__(**kwargs)
        if kwargs.get('disk_path'):
            self._set_disk_path( kwargs.pop('disk_path') )
        else:
            # Look for the OS default db disk path
            self._set_disk_path()

    def __repr__(self):
        if self.disk_path:
            return f'{self.name} ({self.type}: {self.disk_path})'
        else:
            return f'{self.name} ({self.type})'

    def _parse_render_job_xml(self, xml_filepath: Path, **kwargs) -> dict:
        def _type_cast(path, key, value):
            # Account for lower case bools
            if value == "true": value = "True"
            if value == "false": value = "False"
            return key, auto_cast_str(value)
        
        if xml_filepath is not None:
            if xml_filepath.is_file():
                try:
                    with open(xml_filepath, 'rb') as f:
                        job_data = xmltodict.parse(
                            f,
                            postprocessor = _type_cast,
                        )
                        if job_data.get('SyRecordInfo'):
                            if job_data.get('SyRecordInfo').get('@DbId'):
                                return job_data.get('SyRecordInfo')
                        else:
                            logger.warning(f"Invalid render job data structure from this XML file: {xml_filepath}")
                except ExpatError as e:
                    logger.error(f"{type(e)} - Exception while parsing XML render job data from disk database, at filepath {xml_filepath}")
                    logger.debug(e, exc_info=1)
            else:
                raise RenderJobDataNotFound(extra=(self._disk_path, xml_filepath))
        else:
            raise RenderJobDataNotFound
    
    def _search_render_jobs(self, id: str = None) -> List[Path]: 
        if not self._disk_path_projects:
            raise RenderJobDataNotFound('No disk path to the database has been specified')
        if id:
            glob = self._disk_path_projects.glob(f'**/Batch Renders/{id}.xml')
            # Get the first result only - render jobs IDs are unique
            try:
                first = next(glob)
            except StopIteration:
                first = None
            return [ first ] if first else None
        else:
            glob = self._disk_path_projects.glob('**/Batch Renders/*.xml')
            return list( item for item in glob if is_valid_uuid(item.stem) )

    def _set_disk_path(self, path: str | Path | None = None) -> bool:
        # Set according to user specified path
        if path:
            p = Path(path)
            if p.is_dir():
                self._disk_path = p
        # Look for saved db disk paths
        if self.name in pydavinci_context.db_disk_paths_map:
            self._disk_path = pydavinci_context.db_disk_paths_map.get(self.name)['disk_path']
        else:
            # Look for a db in the Resolve default location, per platform
            if self.name == 'Local Database':
                if sys.platform.startswith('win32'):
                    # TODO: Need to support windows!
                    pass
                else:
                    # Compose path to the local disk database location
                    p = ( 
                        Path(os.environ['HOME'])
                        .joinpath('Library/Application Support/Blackmagic Design/DaVinci Resolve/Resolve Disk Database')
                    )
                    if p.is_dir():
                        self._disk_path = p
                    else:
                        logger.error(f'{self.name}: No local disk database found at this path: {p}. Calls to interact with the database will fail. You may specify the path manually when calling projectmanager with `disk_path=`.')
                        return False

        if self._disk_path:
            # Create a path to Projects
            self._disk_path_projects = self.disk_path.joinpath(
                'Resolve Projects', 'Users', 'guest', 'Projects',
            )
            # Save it to disk paths for this context
            pydavinci_context.db_disk_paths_map.add(
                name = self.name,
                disk_path = self._disk_path,
            )
            return True
        else:
            logger.error(f'{self.name}: No path to this disk database was identified. Calls to interact with the database will fail. You must specify the path manually by setting `resolve.project_manager.db.disk_path` to a string path or Path().')
            return False
        
    def _get_render_jobs(
        self,
        id: str = None,
        **kwargs,
    ) -> RenderJob | List[RenderJob]:
        if id:
            if not is_valid_uuid(id):
                raise PydavinciException('Render job ID was not a valid UUID')
        filepaths = self._search_render_jobs(id)
        if filepaths:
            results = list(
                self._parse_render_job_xml(filepath) for filepath in filepaths
            )
        else:
            raise RenderJobNotFound(f'{id} not found in database: {self.__repr__()}')
        if kwargs.get('_data_only') is True:
            # Return it plainly, so that it can be used to populate an existing RenderJob()
            if id:
                return results[0]
            else:
                return results
        else:
            # Otherwise return RenderJob() instances
            return self._make_render_job_instances(results)

    def _get_render_job(self, id: str, **kwargs) -> RenderJob:
        return self._get_render_jobs(id=id, **kwargs)
        
    @property
    def disk_path(self):
        return self._disk_path
    
    @disk_path.setter
    def disk_path(self, path: str) -> bool:
        return self._set_disk_path(path)
        
    @property
    def info(self):
        return dict(
            DbName = self.name,
            DbType = self.type_api,
        )


class DavinciPostgreSQLDatabase(DavinciDatabase):
    ip_address: str | None = None
    type_api = 'PostgreSQL'

    # Defaults are derived from DaVinci Resolve Project Server
    user: str = 'postgres'
    password: str = 'DaVinci'

    # Process these easy filter names for use in get_render_jobs(filters=)
    _easy_filter_keynames = [
        # KWARG : DB COL NAME
        ( 'id', 'SyRecordInfo_id' ),
        ( 'job_name', 'RecordInfoName' ),
        ( 'status', 'Status' ),
        ( 'timeline_id', 'Timeline' ),
        ( 'timeline_name', 'SessionName' ),
    ]

    def __repr__(self):
        return f'{self.name} ({self.type} @ {self.ip_address})'

    @classmethod
    def connect(self, conn_params: dict):
        """
        Decorator for postgreSQL connections.

        Operations:
        It will connect to postgreSQL database with the params you specify in `conn_params` (dict):
            - dbname
            - host
            - user
            - password
            - (as specified by psycopg2.connect())
        Then start a DB session as ReadOnly.
        Then create a cursor object for you to define - as first arg 'cur' in your function.
        By default the cursor has a Dict transformer attached, so the results are returned as a dict with type casting.
        Then executes your function.
        Then closes the DB connection.

        Usage:
            ```python
            conn_params = {} # where keys are dbname, host, user, password
            @DavinciPostgreSQLDatabase.connect(conn_params)
            def my_query(cur):
                query = sql.SQL("SELECT * etc")
                cur.execute(query)
                return cur.fetchone()
            result = my_query()
            ```
        """
        def wrap(f):
            @wraps(f)
            def _connect(*args, **kwargs):
                conn = connect(**conn_params)
                # Read only
                conn.set_session(readonly=True, autocommit=True)
                # By default results are instantiated as a dict
                cur = conn.cursor(
                    cursor_factory = RealDictCursor,
                )
                # Run
                statement = f(cur, *args, **kwargs)
                # Disconnect
                conn.close()
                return statement
            return _connect
        return wrap
    
    @property 
    def conn_params(self):
        """Create conn_params on demand, drawing from the current credential values"""
        return dict(
            dbname = self.name,
            host = self.ip_address,
            password = self.password,
            user = self.user,
        )
    
    def _get_render_jobs(self, filters: dict = None, **kwargs) -> RenderJob | List[RenderJob]:
        @self.connect(self.conn_params)
        def query(cur):
            # Turn filters (k:v) into multiple WHERE clauses
            clauses = [
                sql.SQL('{} = {}').format(
                    sql.Identifier(k),
                    sql.Literal(v),
                ) for k, v in filter_table.items()
            ]
            if len(clauses) > 0:
                q = sql.SQL("SELECT * FROM {table} WHERE ({clauses})").format(
                    table = sql.Identifier('SyRecordInfo'),
                    clauses = sql.SQL(' AND ').join(clauses),
                )
            else:
                q = sql.SQL("SELECT * FROM {table}").format(
                    table = sql.Identifier('SyRecordInfo'),
                )
            try:
                cur.execute(q)
                return cur.fetchall()
            except Psycopg2Error as e:
                logger.error(e, exc_info=1)

        filter_table = {}
        # Transform easy filter names -> db col names
        for easy_name, db_col in self._easy_filter_keynames:
            if kwargs.get(easy_name):
                filter_table[db_col] = kwargs.get(easy_name)
        # Process any filters specified in `filters=` kwarg
        # These will override any of the easy kwargs
        if filters:
            filter_table.update(
                **filters,
            )
        # Validate
        if filter_table.get('SyRecordInfo_id'):
            if not is_valid_uuid(
                filter_table.get('SyRecordInfo_id')
            ):
                raise PydavinciException('render job ID must be valid UUID string (36 characters)')
        results = query()
        if len(results) == 0:
            if kwargs.get('id'):
                exception_msg = f'{kwargs.get('id')} not found in database: {self.__repr__()}'
            else:
                exception_msg = f'No results from the query on this database: {self.__repr__()}'
            raise RenderJobNotFound(exception_msg)
        if kwargs.get('_data_only') is True:
            # Return it plainly, so that it can be used to populate an existing RenderJob()
            if id:
                return results[0]
            else:
                return results
        else:
            # Otherwise return RenderJob() instances
            return self._make_render_job_instances(results)
        
    def _get_render_job(self, id: str, **kwargs) -> RenderJob:
        return self._get_render_jobs(id=id, **kwargs)

    @property
    def info(self):
        """
        Return info in the dict format recognised by the Resolve API
        """
        return dict(
            DbName = self.name,
            DbType = self.type_api,
            IpAddress = self.ip_address,
        )
    

class DavinciNetworkDatabase(DavinciPostgreSQLDatabase):
    def __init__(self, *args, **kwargs):
        super(DavinciPostgreSQLDatabase, self).__init__(*args, **kwargs)
        super(DavinciNetworkDatabase, self).__init__(*args, **kwargs)


class DavinciCloudDatabase(DavinciPostgreSQLDatabase):
    def __init__(self, *args, **kwargs):
        super(DavinciPostgreSQLDatabase, self).__init__(*args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

