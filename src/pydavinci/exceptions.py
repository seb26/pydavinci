from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PydavinciException(BaseException):
    message = None
    def __init__(self, *args: object, extra: Optional[str] = None) -> None:
        
        if extra:
            logger.error(extra)
        super().__init__(*args, self.message)

class ObjectNotFound(PydavinciException):
    pass

class RenderJobDataNotFound(PydavinciException):
    message = "Could not get render job data. Verify that the job ID is present in the selected database, and the database path is readable."

class TimelineNotFound(PydavinciException):
    message = "Couldn't find a valid timeline."