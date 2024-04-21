# type: ignore
import logging
from enum import Enum
from collections import UserDict, OrderedDict
from typing import TYPE_CHECKING

from pydavinci.exceptions import PydavinciException

logger = logging.getLogger(__name__)


class DavinciRenderJobTypes(Enum):
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
        for source_id_key in [ '@DbId', 'SyRecordInfo_id' ]:
            if source.get(source_id_key):
                self.id = source.get(source_id_key)
                break
        if not self.id:
            raise PydavinciException('Invalid render job data, requires contents of SyRecordInfo record originating from XML or db lookup')
        # Work through the job data
        for k, v in source.items():
            # Enumerate - but also leave k='Status' as a string for posterity
            if k == 'Status':
                self.status = DavinciRenderJobTypes[v]
            # Apply all keyvalues
            setattr(self, k, v)
        # Link to database instance
        self.database = database