# type: ignore
import logging
import os
import sys
from enum import auto, IntEnum
from pathlib import Path
from typing import TYPE_CHECKING, Generator

import xmltodict

from pydavinci.exceptions import RenderJobDataNotFound
from pydavinci.main import resolve_obj
from pydavinci.wrappers.project import Project

if TYPE_CHECKING:
    from pydavinci.wrappers._resolve_stubs import PyRemoteProjectManager

logger = logging.getLogger(__name__)

class DavinciDatabaseTypes(IntEnum):
    Disk = auto()
    PostgreSQL = auto()
    Cloud = auto()

class DavinciDatabase(object):
    def __init__(
        self,
        name: str,
        ip_address: str | None,
        type: str,
    ):
        self._project_manager: PyRemoteProjectManager = (
            resolve_obj.GetProjectManager()
        )
        # Assign db info directly to attribs
        self.name = name
        self.ip_address = ip_address
        self.type = DavinciDatabaseTypes[type]
        # And to an API friendly map
        self.db_info = dict(
            DbName = self.name,
            DbType = str(self.type),
        )
        if self.ip_address:
            self.db_info.update(IpAddress=self.ip_address)
        # Initialise paths
        self.db_path = None
        self.db_projects_path = None
        if self.type == DavinciDatabaseTypes.Disk:
            self._init_db_disk()

    def _init_db_disk(self, path: str = None):
        print('228', path)
        if path:
            db_path = Path(path)
            if db_path.is_dir():
                self.db_path = db_path
        else:
            if sys.platform.startswith("win32"):
                pass
            else:
                # Compose path to the local disk database location
                db_path = ( 
                    Path(os.environ['HOME'])
                    .joinpath('Library/Application Support/Blackmagic Design/DaVinci Resolve/Resolve Disk Database')
                )
                if db_path.is_dir():
                    self.db_path = db_path
                else:
                    logger.debug(f'No local disk database found at this path: {db_path}. Calls to interact with the database will fail. You may specify the path manually when calling projectmanager with `db_path=`.')
        if self.db_path is not None:
            # Subfolder for Projects
            self.db_projects_path = (
                Path(self.db_path)
                .joinpath('Resolve Projects', 'Users', 'guest', 'Projects')
            )
        print(252, self.db_path)
    
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
    
    def _get_all_batch_renders_in_disk_db(self) -> Generator:
        for f in self.db_projects_path.glob('**/Batch Renders/*.xml'):
            # Render jobs are saved with job ID UUID (36char)
            if len(f.stem) == 36:
                yield f
        
    def set_db_disk_path(self, db_path: str):
        self._init_db_disk(db_path)

    def get_render_job(
        self,
        job_id: str,
        project: Project | None = None,
    ):
        """
        look up with given project
        if no project given, walk and find all xmls in the database
        """
        if project:
            batch_render_xml_filepath = (
                Path(self.db_path)
                .joinpath(
                    'Projects',
                    project.folder_path,
                    'Batch Renders',
                    job_id + '.xml',
                )
            )
        else:
            # Look it up in our current disk database
            batch_render_xml_filepath = next(
                ( f for f in self._get_all_batch_renders_in_disk_db() if f.stem == job_id ),
                None,
            )
        if batch_render_xml_filepath is not None:
            if batch_render_xml_filepath.is_file():
                return self._parse_batch_render_xml(batch_render_xml_filepath)
            else:
                raise RenderJobDataNotFound(extra=(self.db_path, batch_render_xml_filepath))
        else:
            raise RenderJobDataNotFound
