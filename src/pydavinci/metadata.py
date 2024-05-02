from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Generator

@dataclass
class MetadataFieldTypeMixin(Enum):
    _value: int
    type: type

class MetadataFieldTypes(MetadataFieldTypeMixin, Enum):
    BOOLEAN = auto(), bool
    CHOICE_PICKER = auto(), list[str]
    CLIP_COLOUR_PICKER = auto(), list[str]
    DATE = auto(), str
    FLAG_PICKER = auto(), list[str]
    FLOAT = auto(), float
    INTEGER = auto(), int
    MULTIPLE_ITEMS = auto(), list[str]
    TEXT_LONG = auto(), str
    TEXT_SHORT = auto(), str
    TIMECODE = auto(), str
    UNKNOWN = auto(), None

@dataclass
class MetadataGroupMixin(Enum):
    group_name: str
    order_gui: int

    def __init__(self, *args):
        super().__init__

class MetadataGroups(MetadataGroupMixin):
    group_name = field(repr=False)
    SHOT_SCENE          = 'Shot & Scene', 1
    CLIP_DETAILS        = 'Clip Details', 2
    CAMERA              = 'Camera', 3
    TECH_DETAILS        = 'Tech Details', 4
    STEREO3D_VFX        = 'Stereo3D & VFX', 5
    AUDIO               = 'Audio', 6
    AUDIO_TRACKS        = 'Audio Tracks', 7
    PRODUCTION          = 'Production', 8
    PRODUCTION_CREW     = 'Production Crew', 9
    REVIEWED_BY         = 'Reviewed By', 10

    @property
    def fields(self) -> Generator:
        """Get metadata fields in this group."""
        return ( f for f in MetadataFields if f.group == self)

@dataclass
class MetadataFieldMixin(Enum):
    field_name: str
    order_gui: int
    group: MetadataGroups
    type: MetadataFieldTypes
    user_editable: bool

class MetadataFields(MetadataFieldMixin, Enum):
    Description              = 'Description', 1, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_LONG, True
    Comments                 = 'Comments', 2, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_LONG, True
    Keywords                 = 'Keywords', 3, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.MULTIPLE_ITEMS, True
    People                   = 'People', 4, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.MULTIPLE_ITEMS, True
    Clip_Color               = 'Clip Color', 5, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.CLIP_COLOUR_PICKER, True
    Shot                     = 'Shot', 6, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Scene                    = 'Scene', 7, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Take                     = 'Take', 8, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Angle                    = 'Angle', 9, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Move                     = 'Move', 10, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Day_Night                = 'Day / Night', 11, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Environment              = 'Environment', 12, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Shot_Type                = 'Shot Type', 13, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Flags                    = 'Flags', 14, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.FLAG_PICKER, True
    Good_Take                = 'Good Take', 15, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.BOOLEAN, True
    Shoot_Day                = 'Shoot Day', 16, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Date_Recorded            = 'Date Recorded', 17, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Camera_No                = 'Camera #', 18, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Roll_Card_No             = 'Roll Card #', 19, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Reel_Number              = 'Reel Number', 20, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Clip_Number              = 'Clip Number', 21, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Program_Name             = 'Program Name', 22, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Episode_No               = 'Episode #', 23, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Episode_Name             = 'Episode Name', 24, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Shot_During_Ep           = 'Shot During Ep', 25, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Location                 = 'Location', 26, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_LONG, True
    Unit_Name                = 'Unit Name', 27, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Setup                    = 'Setup', 28, MetadataGroups.SHOT_SCENE, MetadataFieldTypes.TEXT_SHORT, True
    Start_TC                 = 'Start TC', 29, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.TIMECODE, True
    End_TC                   = 'End TC', 30, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.TIMECODE, True
    Start_Frame              = 'Start Frame', 31, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.INTEGER, True
    End_Frame                = 'End Frame', 32, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.INTEGER, True
    Frames                   = 'Frames', 33, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.INTEGER, True
    Shot_Frame_Rate          = 'Shot Frame Rate', 34, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.FLOAT, True
    Bit_Depth                = 'Bit Depth', 35, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.INTEGER, True
    Field_Dominance          = 'Field Dominance', 36, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.UNKNOWN, True
    Data_Level               = 'Data Level', 37, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.UNKNOWN, True
    Audio_Channels           = 'Audio Channels', 38, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.INTEGER, True
    Audio_Bit_Depth          = 'Audio Bit Depth', 39, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.UNKNOWN, True
    Date_Modified            = 'Date Modified', 40, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.DATE, True
    KeyKode                  = 'KeyKode', 41, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.UNKNOWN, True
    EDL_Clip_Name            = 'EDL Clip Name', 42, MetadataGroups.CLIP_DETAILS, MetadataFieldTypes.UNKNOWN, True
    Camera_Type              = 'Camera Type', 43, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Manufacturer      = 'Camera Manufacturer', 44, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Serial_No         = 'Camera Serial #', 45, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_ID                = 'Camera ID', 46, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Notes             = 'Camera Notes', 47, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_LONG, True
    Camera_Format            = 'Camera Format', 48, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Media_Type               = 'Media Type', 49, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Timelapse_Interval       = 'Time-lapse Interval', 50, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_FPS               = 'Camera FPS', 51, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Shutter_Type             = 'Shutter Type', 52, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Shutter_Angle            = 'Shutter Angle', 53, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Shutter_Speed            = 'Shutter Speed', 54, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    ISO                      = 'ISO', 55, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    White_Point_Kelvin       = 'White Point (Kelvin)', 56, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    White_Balance_Tint       = 'White Balance Tint', 57, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_TC_Type           = 'Camera TC Type', 58, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Sensor                   = 'Sensor', 59, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Firmware          = 'Camera Firmware', 60, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Mon_Color_Space          = 'Mon Color Space', 61, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Monitor_LUT              = 'Monitor LUT', 62, MetadataGroups.CAMERA, MetadataFieldTypes.BOOLEAN, True
    LUT_Used                 = 'LUT Used', 63, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Lens_Type                = 'Lens Type', 64, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Lens_Number              = 'Lens Number', 65, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Lens_Notes               = 'Lens Notes', 66, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Aperture_Type     = 'Camera Aperture Type', 67, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Aperture          = 'Camera Aperture', 68, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Focal_Point_mm           = 'Focal Point (mm)', 69, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Distance                 = 'Distance', 70, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Filter                   = 'Filter', 71, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    ND_Filter                = 'ND Filter', 72, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Compression_Ratio        = 'Compression Ratio', 73, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Codec_Bitrate            = 'Codec Bitrate', 74, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Sensor_Area_Captured     = 'Sensor Area Captured', 75, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Pan_Angle         = 'Camera Pan Angle', 76, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Tilt_Angle        = 'Camera Tilt Angle', 77, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Roll_Angle        = 'Camera Roll Angle', 78, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Position          = 'Camera Position', 79, MetadataGroups.CAMERA, MetadataFieldTypes.TEXT_SHORT, True
    PAR_Notes                = 'PAR Notes', 80, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    Safe_Area                = 'Safe Area', 81, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    Aspect_Ratio_Notes       = 'Aspect Ratio Notes', 82, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    Gamma_Notes              = 'Gamma Notes', 83, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    Color_Space_Notes        = 'Color Space Notes', 84, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    RAW                      = 'RAW', 85, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    HFlip                    = 'H-Flip', 86, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.BOOLEAN, True
    VFlip                    = 'V-Flip', 87, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.BOOLEAN, True
    LUT_Used_On_Set          = 'LUT Used On Set', 88, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.BOOLEAN, True
    LUT_1                    = 'LUT 1', 89, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    LUT_2                    = 'LUT 2', 90, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    LUT_3                    = 'LUT 3', 91, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    Lab_Roll_No              = 'Lab Roll #', 92, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    Colorist_Notes           = 'Colorist Notes', 93, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    CDL_SOP                  = 'CDL SOP', 94, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    CDL_SAT                  = 'CDL SAT', 95, MetadataGroups.TECH_DETAILS, MetadataFieldTypes.TEXT_SHORT, True
    S_3D_Shot                = 'S3D Shot', 96, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.BOOLEAN, True
    S_3D_Eye                 = 'S3D Eye', 97, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    S_3D_Notes               = 'S3D Notes', 98, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_LONG, True
    IA_mm                    = 'IA (mm)', 99, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    FG_m                     = 'FG (m)', 100, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    CV_m                     = 'CV (m)', 101, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    BG_m                     = 'BG (m)', 102, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    Convergence_Adj          = 'Convergence Adj', 103, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    _3D_Rig_Type             = '3D Rig Type', 104, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    _3D_Rig_ID_No            = '3D Rig ID #', 105, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    Rig_Inverted             = 'Rig Inverted', 106, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    VFX_Shot_No              = 'VFX Shot #', 107, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    VFX_Markers              = 'VFX Markers', 108, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_SHORT, True
    VFX_Notes                = 'VFX Notes', 109, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.TEXT_LONG, True
    Framing_Chart            = 'Framing Chart', 110, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.BOOLEAN, True
    Color_Chart              = 'Color Chart', 111, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.BOOLEAN, True
    Grey_Chart               = 'Grey Chart', 112, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.BOOLEAN, True
    Lens_Chart               = 'Lens Chart', 113, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.BOOLEAN, True
    VFX_Grey_Ball            = 'VFX Grey Ball', 114, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.BOOLEAN, True
    VFX_Mirror_Ball          = 'VFX Mirror Ball', 115, MetadataGroups.STEREO3D_VFX, MetadataFieldTypes.BOOLEAN, True
    Audio_Recorder           = 'Audio Recorder', 116, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Deck_Serial_No           = 'Deck Serial #', 117, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Deck_Firmware            = 'Deck Firmware', 118, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Audio_Notes              = 'Audio Notes', 119, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Embedded_Audio           = 'Embedded Audio', 120, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Audio_File_Type          = 'Audio File Type', 121, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Audio_Media              = 'Audio Media', 122, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Sound_Roll_No            = 'Sound Roll #', 123, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Audio_TC_Type            = 'Audio TC Type', 124, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Audio_Start_TC           = 'Audio Start TC', 125, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Audio_End_TC             = 'Audio End TC', 126, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Audio_Duration_TC        = 'Audio Duration TC', 127, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Sample_Rate_KHz          = 'Sample Rate (KHz)', 128, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Tone                     = 'Tone', 129, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    FSD                      = 'FSD', 130, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Audio_FPS                = 'Audio FPS', 131, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Bit_Rate                 = 'Bit Rate', 132, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_SHORT, True
    Category                 = 'Category', 133, MetadataGroups.AUDIO, MetadataFieldTypes.CHOICE_PICKER, True
    Subcategory              = 'Subcategory', 134, MetadataGroups.AUDIO, MetadataFieldTypes.TEXT_LONG, True
    Track_1                  = 'Track 1', 135, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_2                  = 'Track 2', 136, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_3                  = 'Track 3', 137, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_4                  = 'Track 4', 138, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_5                  = 'Track 5', 139, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_6                  = 'Track 6', 140, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_7                  = 'Track 7', 141, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_8                  = 'Track 8', 142, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_9                  = 'Track 9', 143, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_10                 = 'Track 10', 144, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_11                 = 'Track 11', 145, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_12                 = 'Track 12', 146, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_13                 = 'Track 13', 147, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_14                 = 'Track 14', 148, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_15                 = 'Track 15', 149, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_16                 = 'Track 16', 150, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_17                 = 'Track 17', 151, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_18                 = 'Track 18', 152, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_19                 = 'Track 19', 153, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_20                 = 'Track 20', 154, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_21                 = 'Track 21', 155, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_22                 = 'Track 22', 156, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_23                 = 'Track 23', 157, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Track_24                 = 'Track 24', 158, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Aux_1                    = 'Aux 1', 159, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Aux_2                    = 'Aux 2', 160, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Start_Dialog_TC          = 'Start Dialog TC', 161, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    End_Dialog_TC            = 'End Dialog TC', 162, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Dialog_Duration          = 'Dialog Duration', 163, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Dialog_Starts_As         = 'Dialog Starts As', 164, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_SHORT, True
    Dialog_Notes             = 'Dialog Notes', 165, MetadataGroups.AUDIO_TRACKS, MetadataFieldTypes.TEXT_LONG, True
    Production_Name          = 'Production Name', 166, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Series_No                = 'Series #', 167, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Genre                    = 'Genre', 168, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Production_Company       = 'Production Company', 169, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Producer                 = 'Producer', 170, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Assistant_Producer       = 'Assistant Producer', 171, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Line_Producer            = 'Line Producer', 172, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Unit_Manager             = 'Unit Manager', 173, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Post_Producer            = 'Post Producer', 174, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Production_Asst          = 'Production Asst', 175, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Editor                   = 'Editor', 176, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Editing_Assistant        = 'Editing Assistant', 177, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Data_Wrangler            = 'Data Wrangler', 178, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Colorist                 = 'Colorist', 179, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Colorist_Assistant       = 'Colorist Assistant', 180, MetadataGroups.PRODUCTION, MetadataFieldTypes.TEXT_SHORT, True
    Director                 = 'Director', 181, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Assistant_Director       = 'Assistant Director', 182, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Script_Supervisor        = 'Script Supervisor', 183, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Continuity               = 'Continuity', 184, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    DOP                      = 'DOP', 185, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Operator          = 'Camera Operator', 186, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Camera_Assistant         = 'Camera Assistant', 187, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Focus_Puller             = 'Focus Puller', 188, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Key_Grip                 = 'Key Grip', 189, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Sound_Mixer              = 'Sound Mixer', 190, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Digital_Technician       = 'Digital Technician', 191, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Dailies_Colorist         = 'Dailies Colorist', 192, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    Crew_Comments            = 'Crew Comments', 193, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    _2nd_Dir                 = '2nd Dir', 194, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    _2nd_Dir_Asst            = '2nd Dir Asst', 195, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    _2nd_Continuity          = '2nd Continuity', 196, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    _2nd_DOP                 = '2nd DOP', 197, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    _2nd_Asst                = '2nd Asst', 198, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    _2nd_DIT                 = '2nd DIT', 199, MetadataGroups.PRODUCTION_CREW, MetadataFieldTypes.TEXT_SHORT, True
    DOP_Reviewed             = 'DOP Reviewed', 200, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    Director_Reviewed        = 'Director Reviewed', 201, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    Focus_Reviewed           = 'Focus Reviewed', 202, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    VFX_Svsr_Reviewed        = 'VFX Svsr Reviewed', 203, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    Colorist_Reviewed        = 'Colorist Reviewed', 204, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    _2nd_DOP_Reviewed        = '2nd DOP Reviewed', 205, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    _2nd_Dir_Reviewed        = '2nd Dir Reviewed', 206, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    Sound_Reviewed           = 'Sound Reviewed', 207, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    Continuity_Reviewed      = 'Continuity Reviewed', 208, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    Wardrobe_Reviewed        = 'Wardrobe Reviewed', 209, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    Send_to_Studio           = 'Send to Studio', 210, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.BOOLEAN, True
    Send_to                  = 'Send to', 211, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.TEXT_LONG, True
    Reviewers_Notes          = 'Reviewers Notes', 212, MetadataGroups.REVIEWED_BY, MetadataFieldTypes.TEXT_LONG, True



def _py_create():
    """For a CSV formatted like below:
    
    order_gui,group,name,user_editable,type
    1,Shot & Scene,Description,True,TEXT_LONG
    [...]
    """
    METADATA_FIELDS_CSV_PATH = 'src/bulk_edit_metadata/davinci_resolve_metadata_fields.csv'
    import csv
    with open(METADATA_FIELDS_CSV_PATH, 'r', encoding='utf-8') as f:
        contents = csv.DictReader(f)
        for item in contents:
            order_gui = int(item['order_gui'])
            group = (item['group']
                .upper()
                .replace(' & ', '_')
                .replace(' ', '_')
            )
            keyname = (item['name']
                .replace(' ', '_')
                .replace('#', 'No')
                .replace('(', '')
                .replace(')', '')
                .replace('-', '')
                .replace('/', '')
                .replace('__', '_')
                .replace('2nd', '_2nd')
                .replace('3D', '_3D')
            )
            name = item['name']
            t = item['type']
            user_editable = bool(item['user_editable'])
            py_string = f"""    {keyname:24} = '{name}', {order_gui}, MetadataGroups.{group}, MetadataFieldTypes.{t}, {user_editable}"""
            print(py_string)