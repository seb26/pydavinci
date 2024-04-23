# type: ignore
from collections import UserDict, OrderedDict
from enum import Enum
from typing import TYPE_CHECKING
import logging

from pydavinci.wrappers.resolve import Resolve
from pydavinci.exceptions import PydavinciException

if TYPE_CHECKING:
    from pydavinci.wrappers._resolve_stubs import PyRemoteProject
    from pydavinci.wrappers.project import Project
    from pydavinci.database import DavinciDatabase

logger = logging.getLogger(__name__)

class RenderJobStatus(Enum):
    READY = 0
    FAILED = 1
    RENDERING = 2
    COMPLETE = 3
    CANCELLED = 4

class RenderJob(object):
    # Documentation:
    # https://docs.google.com/spreadsheets/d/1t2nrn5k0SBg8N1HYsXq-wPHxZOj1djVvJS7KnJuY6GQ/edit#gid=164036605
    __keys_api_GetRenderJobList__ = (
        # PyRemoteProject.GetRenderJobList()
        'AudioBitDepth',
        'AudioSampleRate',
        'ExportAlpha',
        'FormatHeight',
        'FormatWidth',
        'FrameRate',
        'IsExportAudio',
        'IsExportVideo',
        'JobId',
        'MarkIn',
        'MarkOut',
        'NetworkOptimization',
        'OutputFilename',
        'PixelAspectRatio',
        'PresetName',
        'RenderJobName',
        'RenderMode',
        'TargetDir',
        'TimelineName',
        'VideoCodec',
        'VideoFormat',
    )

    __keys__api_GetRenderJobStatus__ = (
        # PyRemoteProject.GetRenderJobStatus()
        'CompletionPercentage',
        'EstimatedTimeRemainingInMs',
        'JobStatus',
        'TimeTakenToRenderInMs',
    )

    __keys__api__ = __keys__api_GetRenderJobStatus__ + __keys_api_GetRenderJobList__

    __keys_db__ = (
        'AlternateInFolder',
        'AlternateOffset',
        'ApplyWfmDuringRecord',
        'ClipInFolder',
        'CompletionPercentage',
        'CreationTime',
        'CurSysId',
        'CustomClips',
        'DbType',
        'DestSuffix',
        'DisableCcDuringRecording',
        'DisablePtzDuringRecording',
        'DisplayOrder',
        'ErrorCode',
        'ErrorNotified',
        'ErrorStr',
        'EstimatedTimeRemainingInMs',
        'ExtraInfoMap',
        'ExtraInfoMap_vals',
        'FieldsBlob',
        'FolderName',
        'ForceHighestQualityDebayerRes',
        'ForceHighestQualitySizing',
        'FormatHeight',
        'FormatOption',
        'FormatPixelAspectRatio',
        'FormatWidth',
        'NumFramesOfHandles',
        'ProjectName',
        'RecordAllowDupImg',
        'RecordAsFloat',
        'RecordAudioBitDepth',
        'RecordAudioEnabled',
        'RecordAudioNumChannels',
        'RecordBitDepth',
        'RecordCancelled',
        'RecordClipStartFrame',
        'RecordClipUniqueName',
        'RecordClipUniqueNameStyle',
        'RecordDataLevel',
        'RecordDigit',
        'RecordEndFrame',
        'RecordFormatSubType',
        'RecordFormatType',
        'RecordFPS',
        'RecordInFieldMode',
        'RecordInfoName',
        'RecordMode',
        'RecordNewFrame',
        'RecordOldFrame',
        'RecordPrefix',
        'RecordQuality',
        'RecordSetTimelineTimecode',
        'RecordSlatePreset',
        'RecordSpeed',
        'RecordStartFrame',
        'RecordSuffix',
        'RecordTargetDir',
        'RecordTotalFrame',
        'RecordUseTgtTimeCode',
        'ReelInFolder',
        'RenderAtSourceResolution',
        'ReplaceHoleWithBlank',
        'Session',
        'SessionName',
        'SmDeliverPresetList_id',
        'SrcDirLevelsMode',
        'SrcDirPreserveLevel',
        'Status',
        'StereoRender',
        'StereoRenderBothEyesSeparately',
        'StereoRenderFrameMeshMode',
        'StereoRenderSourceType',
        'SyRecordInfo_id',
        'TgtSysId',
        'Timeline',
        'TimelineFilter',
        'TimeTakenToRenderInMs',
        'UniqueSequenceId',
        'UseCommercialWorkflow',
        'UsePrefixAndSuffixFromSrc',
        'UseProxyForRender',
        'UseRecordClipStartFrame',
        'UseRenderCachedImagesForRecording',
        'UserName',
        'UserWithLock',
        'UseVersionNameForFolder',
        'VersionIdList',
        'VersionNameList',
        'Workstation',
    )

    def __init__(
        self,
        source: dict | OrderedDict,
        id: str = None,
        database: 'DavinciDatabase' = None,
    ):
        self.api = False
        self.database = None
        self.id = id
        self.project: 'Project' = Resolve().project
        self.status = None

        # Identify the job ID
        for source_id_key in [ '@DbId', 'SyRecordInfo_id', 'JobId' ]:
            if source.get(source_id_key):
                self.id = source.get(source_id_key)
                if source_id_key == 'JobId':
                    # Mark that we are initialising this RenderJob from an API source
                    self.api = True
                    # Add additional job status data
                    self._lookup_api_status(self.id)
                break
        if not self.id:
            raise PydavinciException('Invalid render job data, requires (1) contents of SyRecordInfo record originating from XML or db lookup; or (2) API job info from resolve().GetProjectManager().GetCurrentProject().GetRenderJobList()')
        # Work through the job data
        for k, v in source.items():
            if k == 'Status':
                self._set_status(v)
            # Apply all keyvalues
            setattr(self, k, v)
        # Link to database instance
        self.database = database
        # Do a DB lookup if necessary
        if self.database is None:
            self._lookup_db()
        # Do an API lookup if necessary
        if self.api is False:
            self._lookup_api()
        # Parse binary fields in FieldsBlob
        # TODO

    def __getitem__(self, attr):
        """Make subscriptable like a dict result, for backwards compatibility"""
        return getattr(self, attr)

    def __getattr__(self, attr):
        """
        Recognise if tried to access an API/DB param on this RenderJob but there was none available,
        but softly return None and log a warning to stderr.

        Often because:
        * previous attempts to get data from API failed (i.e. job not in this project)
        * previous attempts to get data from DB failed (i.e. no DB path available or could not connect to network db)

        TODO:
        - Add a strict global somewhere to permit these moments to raise AttributeError or another exception
        """
        if attr in RenderJob.__keys__api__:
            logger.warning(f"RenderJob ({self.id}): Tried to get API key value '{attr}' but no API data was accessible for this job")
            return None
        elif attr in RenderJob.__keys__db__:
            logger.warning(f"RenderJob ({self.id}): Tried to get DB key value '{attr}' but no DB data was accessible for this job")
            return None
        else:
            raise AttributeError("%r object has no attribute %r" % (self.__class__.__name__, attr))

    def __repr__(self):
        return f'RenderJob ({self.id})'
    
    def __str__(self):
        return self.id

    def _lookup_api(self) -> bool:
        # Get current project's jobs and see if our ID is in there
        # API will not give data about jobs outside of the project
        this_project_jobs = self.project._obj.GetRenderJobList()
        this_job = None
        if this_project_jobs:
            for job in this_project_jobs:
                 if job.get('JobId') == self.id:
                     this_job = job
                     break
            if this_job is None:
                # Not in our project
                return False
            self.api = True
            for k, v in this_job.items():
                setattr(self, k, v)
            # Have to get status thru separate API call
            self._lookup_api_status(self.id)
        else:
            logger.debug(f'Job {self.id} was not found in current project so could not get API data. Switch to current project and then call RenderJob.refresh().')
    
    def _lookup_api_status(self, id: str):
        status = self.project._obj.GetRenderJobStatus(self.id)
        if status.get('JobStatus'):
            # Valid status
            # Update these params while we are here so that the RenderJob stays current
            for k, v in status.items():
                setattr(self, k, v)
            self._set_status(status['JobStatus'])

    def _lookup_db(self) -> bool:
        db: 'DavinciDatabase' = Resolve().project_manager.database
        if db:
            self.database = db
            try:
                db_data = next(
                    self.database.get_render_job(
                        self.id,
                        _data_only = True,
                    )
                )
                # Update self fields
                for k, v in db_data.items():
                    setattr(self, k, v)
                return True
            except Exception as e:
                # Don't let a bad DB fetch stop the initialisation of this RenderJob()
                # Since if we are coming from API, we have enough data to give to the user
                logger.error(e, exc_info=1)
        return False
    
    def _set_status(self, status: str):
        self.status = RenderJobStatus[status.upper()]

    def refresh(self):
        """
        Refreshes render job data from both DB and API
        """
        self._lookup_api()
        self._lookup_db()
