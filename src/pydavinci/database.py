# type: ignore
from collections import UserDict
from pathlib import Path
from typing import TYPE_CHECKING, Generator
import logging
import os
import re
import sys

import xmltodict

from pydavinci.exceptions import *
from pydavinci.main import resolve_obj, pydavinci_context
from pydavinci.wrappers.project import Project

if TYPE_CHECKING:
    from pydavinci.wrappers._resolve_stubs import PyRemoteProjectManager

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
    disk_path_projects: Path | None = None

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
            return f'{self.name} ({self.type}) @ {self.disk_path}'
        else:
            return f'{self.name} ({self.type})'

    def _parse_batch_render_xml(self, xml_filepath: str) -> dict:
        try:
            with open(xml_filepath, 'rb') as f:
                job_data = xmltodict.parse(f)
                if job_data.get('SyRecordInfo'):
                    if job_data.get('SyRecordInfo').get('@DbId'):
                        return job_data.get('SyRecordInfo')
            logger.warning(f"Invalid render job data structure from this XML file: {xml_filepath}")
        except Exception as e:
            logger.error(f"{type(e)} - Exception while parsing XML render job data from disk database, at filepath {xml_filepath}")
            logger.debug(e, exc_info=1)
        return xml_data
    
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
                if sys.platform.startswith("win32"):
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
            self.disk_path_projects = self.disk_path.joinpath(
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
        
    @property
    def disk_path(self):
        return self._disk_path
    
    @disk_path.setter
    def disk_path(self, path: str) -> bool:
        return self._set_disk_path(path)
    
    def get_all_render_jobs(self, file_paths: bool = False) -> Generator:
        if not self.disk_path_projects:
            raise RenderJobDataNotFound('No disk path to the database has been specified')
        for f in self.disk_path_projects.glob('**/Batch Renders/*.xml'):
            # Render jobs are saved with job ID UUID (36char)
            if len(f.stem) == 36:
                if file_paths:
                    yield f
                else:
                    yield f.stem

    def get_render_job(
        self,
        job_id: str,
        project: Project | None = None,
    ):
        if not self.disk_path_projects:
            raise RenderJobDataNotFound('No disk path to the database has been specified')
        if project:
            batch_render_xml_filepath = (
                Path(self.disk_path_projects)
                .joinpath(
                    project.folder_path,
                    'Batch Renders',
                    job_id + '.xml',
                )
            )
        else:
            # Look it up in our current disk database
            batch_render_xml_filepath = next(
                ( f for f in self.get_all_render_jobs(file_paths=True) if f.stem == job_id ),
                None,
            )
        if batch_render_xml_filepath is not None:
            if batch_render_xml_filepath.is_file():
                return self._parse_batch_render_xml(batch_render_xml_filepath)
            else:
                raise RenderJobDataNotFound(extra=(self.disk_path, batch_render_xml_filepath))
        else:
            raise RenderJobDataNotFound
        
    @property
    def info(self):
        return dict(
            DbName = self.name,
            DbType = self.type_api,
        )
        

class DavinciPostgreSQLDatabase(DavinciDatabase):
    type_api = 'PostgreSQL'
    ip_address: str | None = None

    @property
    def info(self):
        return dict(
            DbName = self.name,
            DbType = self.type_api,
            IpAddress = self.ip_address,
        )
    
    def __repr__(self):
        return f'{self.name} ({self.type}) @ {self.ip_address}'


class DavinciNetworkDatabase(DavinciPostgreSQLDatabase):
    def __init__(self, *args, **kwargs):
        super(DavinciNetworkDatabase, self).__init__(*args, **kwargs)
    
    def get_all_render_jobs(self):
        raise NotImplementedError

class DavinciCloudDatabase(DavinciPostgreSQLDatabase):
    def __init__(self, *args, **kwargs):
        super(DavinciCloudDatabase, self).__init__(*args, **kwargs)


