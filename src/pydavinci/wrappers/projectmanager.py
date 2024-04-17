from typing import TYPE_CHECKING, Dict, List
from pathlib import Path

from pydavinci.database import DavinciDatabase, PydavinciDiskPathsMap
from pydavinci.exceptions import PydavinciException
from pydavinci.main import resolve_obj
from pydavinci.wrappers.project import Project

if TYPE_CHECKING:
    from pydavinci.wrappers._resolve_stubs import PyRemoteProjectManager


class ProjectManager(object):
    # try:  ## this is for when we do auto-launch
    #     _obj = resolve_obj.GetProjectManager()  # if using this one here, everything fails
    # except AttributeError:
    #     _obj = get_resolve().GetProjectManager()  # if using this here, closing projects fail

    def __init__(self) -> None:

        self._obj: PyRemoteProjectManager = resolve_obj.GetProjectManager()
        
        # Create map for database disk paths to be stored
        resolve_obj.context.db_disk_paths_map = PydavinciDiskPathsMap()

    def create_project(self, project_name: str) -> Project:
        """
        Creates a project with ``project_name``

        Args:
            project_name (str): project name

        Returns:
            Project: Project
        """
        created = self._obj.CreateProject(project_name)
        return Project(created)

    def delete_project(self, project_name: str) -> bool:
        """
        Deletes project ``project_name``

        Args:
            project_name (str): project name

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return self._obj.DeleteProject(project_name)

    def load_project(self, project_name: str) -> Project:
        """
        Loads project ``project_name``

        Args:
            project_name (str): project name

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return Project(self._obj.LoadProject(project_name))

    def close_project(self, project_name: Project) -> bool:
        """
        Closes project ``project_name``

        Args:
            project_name (str): project name

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return self._obj.CloseProject(project_name._obj)

    def create_folder(self, folder_name: str) -> bool:
        """
        Creates project manager folder ``folder_name``

        Args:
            folder_name (str): folder name

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return self._obj.CreateFolder(folder_name)

    def delete_folder(self, folder_name: str) -> bool:
        """
        Deletes project manager folder ``folder_name``

        Args:
            folder_name (str): folder name

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return self._obj.DeleteFolder(folder_name)

    @property
    def projects(self) -> List[str]:
        """
        Returns a list with project names in current project manager folder

        Returns:
            List[str]: list of project names
        """
        return self._obj.GetProjectListInCurrentFolder()

    @property
    def folders(self) -> List[str]:
        """
        Returns a list with project manager folder names

        Returns:
            List[str]: list of folder names
        """
        return self._obj.GetFolderListInCurrentFolder()

    def goto_root_folder(self) -> bool:
        """
        Goes to root project manager folder

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return self._obj.GotoRootFolder()

    def goto_parent_folder(self) -> bool:
        """
        Goes to parent of current project manager folder

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return self._obj.GotoParentFolder()

    @property
    def folder(self) -> str:
        """
        Returns current folder name

        Returns:
            str: folder name
        """
        return self._obj.GetCurrentFolder()

    def open_folder(self, folder_name: str) -> bool:
        """
        Open folder named ``folder_name``

        Args:
            folder_name (str): folder name

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return self._obj.OpenFolder(folder_name)
    
    def get_folder_path(self) -> str:
        """
        Determines the folder path of current project

        Returns:
            str: folder path separated by /
        """
        def _recurse(folder: str, tree: list):
            self._obj.OpenFolder(folder)
            tree.insert(0, folder)
            climb = self._obj.GotoParentFolder()
            if climb:
                parent = self._obj.GetCurrentFolder()
                if parent:
                    return _recurse(
                        parent,
                        tree,
                    )
        
        tree = []
        current = self._obj.GetCurrentFolder()
        print(f'Current folder at first run: {current}')
        _recurse(current, tree)
        # Reset the current project back to its value before we started
        print('current folder', current)
        self._obj.OpenFolder(current)
        return tree


    def import_project(self, path: str) -> bool:
        """
        Imports ``.drp`` project located at ``path``

        Args:
            path (str): path to ``.drp`` project

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return self._obj.ImportProject(path)

    def export_project(self, project_name: str, path: str, stills_and_luts: bool = False) -> bool:
        """
        Exports project

        Args:
            project_name (str): project to be exported
            path (str): path to export to
            stills_and_luts (bool, optional): whether to export with Stills and LUTs. Defaults to False.

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return self._obj.ExportProject(project_name, path, stills_and_luts)

    def restore_project(self, path: str) -> bool:
        """
        Restore project from ``path``

        Args:
            path (str): project path

        Returns:
            bool: ``True`` if successful, ``False`` otherwise
        """
        return self._obj.RestoreProject(path)

    @property
    def db(self) -> DavinciDatabase:
        db_from_api = self._obj.GetCurrentDatabase()
        return DavinciDatabase.make(**db_from_api)

    @db.setter
    def db(self, db: Dict[str, str] | DavinciDatabase) -> bool:
        """
        Sets current database according to ``db_info``

         Args:
             db (DavinciDatabase, dict): DavinciDatabase object or dict with ``db_info``

         Info:
             Valid dictionary:
             ```python
             ProjectManager.db = {
             'DbType': 'Disk',
             'DbName': 'Local Database'
             }
             ```
             For PostgresSQL:
             ```python
             ProjectManager.db = {
             'DbType': 'PostgreSQL',
             'DbName': 'PosgresDB',
             'IpAddress': '127.0.0.1'
             }
             ```

        Returns:
             bool: ``True`` if successful, ``False`` otherwise

        """
        if isinstance(db, DavinciDatabase):
            db_info = db.info
        elif isinstance(db, dict):
            db_info = db
        else:
            raise PydavinciException(f'Unrecognised info, cannot set the database with this - type({db})')
        return self._obj.SetCurrentDatabase(db_info)
    
    @property
    def db_list(self) -> List[Dict[str, str]]:
        """
        Returns list of all databases

        Returns:
            list of databases
        """
        return self._obj.GetDatabaseList()
    
    @property
    def databases(self) -> List[DavinciDatabase]:
        """
        Returns list of database objects using pydavinci classing, e.g. DavinciLocalDatabase
        """
        def _create_database_objects():
            for db_api_result in self._obj.GetDatabaseList():
                yield DavinciDatabase.make(
                    **db_api_result,
                )
        return list(
            _create_database_objects()
        )