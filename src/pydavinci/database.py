# type: ignore
from enum import auto, IntEnum
from pathlib import Path
from typing import TYPE_CHECKING, Generator
import logging
import os
import re
import sys

import xmltodict

from pydavinci.exceptions import *
from pydavinci.main import resolve_obj
from pydavinci.wrappers.project import Project

if TYPE_CHECKING:
    from pydavinci.wrappers._resolve_stubs import PyRemoteProjectManager

logger = logging.getLogger(__name__)



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
    def get(
        self,
        DbName: str,
        DbType: str,
        IpAddress: str | None = None,
        **kwargs,
    ):
        if DbType == 'Disk':
            db_instance = DavinciLocalDatabase
        elif DbType == 'PostgreSQL':
            # Blackmagic Cloud databases are still marked as 'PostgreSQL' by the API
            # At the moment, only way I can see to test for them is the IP address string
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
    
class DavinciLocalDatabase(DavinciDatabase):
    type_api = 'Disk'

    def __init__(self, **kwargs):
        super(DavinciLocalDatabase, self).__init__(**kwargs)
        if kwargs.get('disk_path'):
            self.disk_path = kwargs.pop('disk_path')
        else:
            # Runs disk_path.setter() to look for the OS default db disk path if relevant
            self.disk_path = None

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
    
    @property
    def disk_path(self):
        return self._disk_path
    
    @disk_path.setter
    def disk_path(self, path: str) -> bool:
        # Set according to user specified path
        if path:
            p = Path(path)
            if p.is_dir():
                self._disk_path = p
        if self._disk_path is None:
            # Look for a db path registered to the project manager
            # TODO
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
                        logger.error(f'No local disk database found at this path: {p}. Calls to interact with the database will fail. You may specify the path manually when calling projectmanager with `disk_path=`.')
                        return False
            else:
                logger.error(f'No path to this disk database was provided. Calls to interact with the database will fail. You must specify the path manually when calling projectmanager with `disk_path=`.')
                return False

        if isinstance(self._disk_path, Path):
            # Create a path to Projects
            self.disk_path_projects = self.disk_path.joinpath(
                'Resolve Projects', 'Users', 'guest', 'Projects',
            )
            return True
    
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


