# type: ignore
from base64 import b64decode
from collections import UserDict, OrderedDict
from enum import Enum
from typing import TYPE_CHECKING
import logging

from pydavinci.exceptions import PydavinciException

logger = logging.getLogger(__name__)


class DavinciRenderJobStatus(Enum):
    READY = 0
    FAILED = 1
    RENDERING = 2
    COMPLETE = 3
    CANCELLED = 4

class DavinciRenderJob(UserDict):
    database = None

    def __init__(
        self,
        source: dict | OrderedDict,
        id: str = None,
        database = None,
    ):
        self.id = id
        # Identify the job ID
        for source_id_key in [ '@DbId', 'SyRecordInfo_id', 'JobId' ]:
            if source.get(source_id_key):
                self.id = source.get(source_id_key)
                break
        if not self.id:
            raise PydavinciException('Invalid render job data, requires contents of SyRecordInfo record originating from XML or db lookup')
        # Link to database instance
        self.database = database
        # Work through the job data
        for k, v in source.items():
            # Enumerate - but also leave k='Status' as a string for posterity
            if k == 'Status':
                self.status = DavinciRenderJobStatus[v]
            # Apply all keyvalues
            setattr(self, k, v)
        # Parse binary fields
