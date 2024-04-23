from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PydavinciException(Exception):
    message = None
    def __init__(self, *args: object, extra: Optional[str] = None) -> None:
        
        if extra:
            logger.error(extra)
        super().__init__(*args, self.message)

class ObjectNotFound(PydavinciException):
    pass

class RenderJobNotFound(PydavinciException):
    message = "Verify that the job ID is present in the selected database."

class TimelineNotFound(PydavinciException):
    message = "Couldn't find a valid timeline."

class CloudDatabaseNotSupported(PydavinciException):
    message = "Pydavinci cannot connect to cloud database - not yet implemented."