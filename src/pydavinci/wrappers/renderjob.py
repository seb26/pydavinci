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
    READY = 'Ready'
    FAILED = 'Failed'
    RENDERING = 'Rendering'
    COMPLETE = 'Complete'
    CANCELLED = 'Cancelled'
    UNDEFINED = 'Undefined'

class RenderJob(object):
    # Documentation:
    # https://docs.google.com/spreadsheets/d/1t2nrn5k0SBg8N1HYsXq-wPHxZOj1djVvJS7KnJuY6GQ/edit#gid=164036605
    _keys_api_GetRenderJobList = (
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

    _keys_api_GetRenderJobStatus = (
        # PyRemoteProject.GetRenderJobStatus()
        'CompletionPercentage',
        'EstimatedTimeRemainingInMs',
        'JobStatus',
        'TimeTakenToRenderInMs',
    )

    _keys_api = _keys_api_GetRenderJobStatus + _keys_api_GetRenderJobList

    _keys_db = (
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

    _common_fields =  {
        'filename': [ 'OutputFilename' ],
        'directory': [ 'TargetDir', 'RecordTargetDir', ],
        'fps': [ 'FrameRate' ],
        'height': [ 'FormatHeight' ],
        'name': [ 'RenderJobName' ],
        'progress': [ 'CompletionPercentage' ],
        'timeline_name': [ 'TimelineName', 'SessionName' ],
        'width': [ 'FormatWidth' ],
        'mark_in': [ 'MarkIn', 'RecordStartFrame' ],
        'mark_out': [ 'MarkOut', 'RecordEndFrame' ],
        'duration': [ 'RecordTotalFrame' ], 
        'time_elapsed': [ 'EstimatedTimeRemainingInMs' ],
        'time_remaining': [ 'TimeTakenToRenderInMs' ],
    }

    def __init__(
        self,
        source: dict | OrderedDict,
        id: str = None,
        database: 'DavinciDatabase' = None,
    ):
        self.database = None
        self.id = id
        self.project: 'Project' = Resolve().project
        self.status = RenderJobStatus.UNDEFINED
        self._api = False
        self._fields: dict = {}

        # Identify the job ID
        for source_id_key in [ '@DbId', 'SyRecordInfo_id', 'JobId' ]:
            if source.get(source_id_key):
                self.id = source.get(source_id_key)
                if source_id_key == 'JobId':
                    # Mark that we are initialising this RenderJob from an API source
                    self._api = True
                    # Add additional job status data
                    self._lookup_api_status(self.id)
                break
        if not self.id:
            raise PydavinciException('Invalid render job data, requires (1) contents of SyRecordInfo record originating from XML or db lookup; or (2) API job info from resolve().GetProjectManager().GetCurrentProject().GetRenderJobList()')
        # Work through the job data
        if source.get('Status'):
            self._set_status(source['Status'])
        # Store all keyvalues
        self._fields.update(**source)
        # Link to database instance
        self.database = database
        # Do a DB lookup if necessary
        if self.database is None:
            self._lookup_db()
        # Do an API lookup if necessary
        if self._api is False:
            self._lookup_api()
        # Parse binary fields in FieldsBlob
        # TODO
        # Assign some most commonly used fields as lowercase attribs directly on RenderJob
        for target_keyname, api_keynames in RenderJob._common_fields.items():
            value_set = False
            while value_set is False:
                for option in api_keynames:
                    if self._fields.get(option):
                        setattr(self, target_keyname, self._fields.get(option))
                        value_set = True
                break
        # If duration isn't available
        if not hasattr(self, 'duration') and hasattr(self, 'mark_in') and hasattr(self, 'mark_out'):
            self.duration = self.mark_out - self.mark_in + 1
                    
    def __getitem__(self, attr):
        """Make subscriptable like a dict result, for backwards compatibility"""
        return getattr(self, attr)

    def __getattr__(self, attr):
        """
        First look inside self._fields.
        Then, identify if tried to access an API/DB param on this RenderJob but there was none available,
        but softly return None and log a warning to stderr.

        Often because:
        * previous attempts to get data from API failed (i.e. job not in this project)
        * previous attempts to get data from DB failed (i.e. no DB path available or could not connect to network db)

        TODO:
        - Add a strict global somewhere to permit these moments to raise AttributeError or another exception
        """
        if attr in self._fields:
            return self._fields.get(attr)
        elif attr in RenderJob._keys_api:
            logger.warning(f"RenderJob ({self.id}): Tried to get API key value '{attr}' but no API data was accessible for this job")
            return None
        elif attr in RenderJob._keys_db:
            logger.warning(f"RenderJob ({self.id}): Tried to get DB key value '{attr}' but no DB data was accessible for this job")
            return None
        else:
            # Revert to normal behaviour for no attr found
            raise AttributeError("%r object has no attribute %r" % (self.__class__.__name__, attr))

    def __repr__(self):
        return f'RenderJob ({self.id})'
    
    def __str__(self):
        return self.id
    
    @property
    def fields(self) -> dict:
        return dict( sorted( self._fields.items() ) )
    
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
            # Store the fields
            self._fields.update(**this_job)
            # Have to get status thru separate API call
            self._lookup_api_status(self.id)
        else:
            logger.debug(f'Job {self.id} was not found in current project so could not get API data. Switch to current project and then call RenderJob.refresh().')
    
    def _lookup_api_status(self, id: str):
        status = self.project._obj.GetRenderJobStatus(self.id)
        if status.get('JobStatus'):
            # Valid status
            # Store these keyvalues while we are here so that the RenderJob stays current
            self._fields.update(**status)
            self._set_status(status['JobStatus'])

    def _lookup_db(self) -> bool:
        db: 'DavinciDatabase' = Resolve().project_manager.database
        if db:
            self.database = db
            try:
                db_data = self.database.get_render_job(
                    self.id,
                    _data_only = True,
                )
                # Store the data in our fields
                self._fields.update(**db_data)
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
