from __future__ import annotations

from enumerific import anno

from tiffdata.enumerations.datatype import DataType
from tiffdata.enumerations.tifftag import TIFFTag


class EXIFTag(TIFFTag, aliased=True):
    """The EXIFTag class provides enumerations for the EXIFTag type."""

    SelfTimerMode = anno(
        34859,
        type=DataType.Short,
        name="SelfTimerMode",
    )

    SensitivityType = anno(
        34864,
        name="SensitivityType",
    )

    StandardOutputSensitivity = anno(
        34865,
        type=DataType.Long,
        name="StandardOutputSensitivity",
    )

    RecommendedExposureIndex = anno(
        34866,
        type=DataType.Long,
        name="RecommendedExposureIndex",
    )

    ISOSpeed = anno(
        34867,
        name="ISOSpeed",
    )

    ISOSpeedLatitudeYYY = anno(
        34868,
        name="ISOSpeedLatitudeYYY",
    )

    ISOSpeedLatitudeZZZ = anno(
        34869,
        type=DataType.Long,
        name="ISOSpeedLatitudeZZZ",
    )

    ExifVersion = anno(
        36864,
        type=DataType.Undefined,
        name="ExifVersion",
    )

    CreateDate = anno(
        36868,
        type=DataType.ASCII,
        name="CreateDate",
    )

    DateTimeDigitized = CreateDate

    GooglePlusUploadCode = anno(
        36873,
        name="GooglePlusUploadCode",
    )

    OffsetTime = anno(
        36880,
        type=DataType.ASCII,
        name="OffsetTime",
    )

    OffsetTimeOriginal = anno(
        36881,
        type=DataType.ASCII,
        name="OffsetTimeOriginal",
    )

    OffsetTimeDigitized = anno(
        36882,
        type=DataType.ASCII,
        name="OffsetTimeDigitized",
    )

    ComponentsConfiguration = anno(
        37121,
        type=DataType.Undefined,
        count=4,
        name="ComponentsConfiguration",
    )

    MaxApertureValue = anno(
        37381,
        type=DataType.Rational,
        count=1,
        name="MaxApertureValue",
    )

    SubjectArea = anno(
        37396,
        type=DataType.Short,
        name="SubjectArea",
    )

    MakerNote = anno(
        37500,
        type=DataType.Undefined,
        name="MakerNote",
    )

    UserComment = anno(
        37510,
        type=DataType.Undefined,
        name="UserComment",
    )

    SubSecondTime = anno(
        37520,
        type=DataType.ASCII,
        name="SubSecTime",
    )

    SubSecondTimeOriginal = anno(
        37521,
        type=DataType.ASCII,
        name="SubSecTimeOriginal",
    )

    SubSecondTimeDigitized = anno(
        37522,
        type=DataType.ASCII,
        name="SubSecTimeDigitized",
    )

    AmbientTemperature = anno(
        37888,
        type=DataType.SRational,
        name="AmbientTemperature",
    )

    Temperature = AmbientTemperature

    Humidity = anno(
        37889,
        type=DataType.Rational,
        name="Humidity",
    )

    Pressure = anno(
        37890,
        type=DataType.Rational,
        name="Pressure",
    )

    WaterDepth = anno(
        37891,
        type=DataType.SRational,
        name="WaterDepth",
    )

    Acceleration = anno(
        37892,
        type=DataType.Rational,
        name="Acceleration",
    )

    CameraElevationAngle = anno(
        37893,
        type=DataType.SRational,
        name="CameraElevationAngle",
    )

    FlashpixVersion = anno(
        40960,
        type=DataType.Undefined,
        count=4,
        name="FlashpixVersion",
    )

    ColorSpace = anno(
        40961,
        type=DataType.Short,
        count=1,
        name="ColorSpace",
    )

    PixelXDimension = anno(
        40962,
        type=(DataType.Short, DataType.Long),
        count=1,
        name="PixelXDimension",
    )

    PixelYDimension = anno(
        40963,
        type=(DataType.Short, DataType.Long),
        count=1,
        name="PixelYDimension",
    )

    RelatedSoundFile = anno(
        40964,
        type=DataType.ASCII,
        count=13,
        name="RelatedSoundFile",
    )

    FileSource = anno(
        41728,
        type=DataType.Undefined,
        count=1,
        name="FileSource",
    )

    SceneType = anno(
        41729,
        type=DataType.Undefined,
        count=1,
        name="SceneType",
    )

    CustomRendered = anno(
        41985,
        type=DataType.Short,
        count=1,
        name="CustomRendered",
    )

    ExposureMode = anno(
        41986,
        type=DataType.Short,
        count=1,
        name="ExposureMode",
    )

    WhiteBalance = anno(
        65102,
        type=DataType.ASCII,
        name="WhiteBalance",
    )

    DigitalZoomRatio = anno(
        41988,
        type=DataType.Rational,
        count=1,
        name="DigitalZoomRatio",
    )

    FocalLengthIn35mmFilm = anno(
        41989,
        type=DataType.Short,
        count=1,
        name="FocalLengthIn35mmFilm",
    )

    SceneCaptureType = anno(
        41990,
        type=DataType.Short,
        count=1,
        name="SceneCaptureType",
    )

    GainControl = anno(
        41991,
        type=DataType.Rational,
        count=1,
        name="GainControl",
    )

    Contrast = anno(
        65108,
        type=DataType.ASCII,
        name="Contrast",
    )

    Saturation = anno(
        65109,
        type=DataType.ASCII,
        name="Saturation",
    )

    Sharpness = anno(
        65110,
        type=DataType.ASCII,
        name="Sharpness",
    )

    DeviceSettingDescription = anno(
        41995,
        type=DataType.Undefined,
        name="DeviceSettingDescription",
    )

    SubjectDistanceRange = anno(
        41996,
        type=DataType.Short,
        count=1,
        name="SubjectDistanceRange",
    )

    ImageUniqueID = anno(
        42016,
        type=DataType.ASCII,
        count=33,
        name="ImageUniqueID",
    )

    OwnerName = anno(
        65000,
        type=DataType.ASCII,
        name="OwnerName",
    )

    SerialNumber = anno(
        65001,
        type=DataType.ASCII,
        name="SerialNumber",
    )

    LensMake = anno(
        42035,
        type=DataType.ASCII,
        name="LensMake",
    )

    LensModel = anno(
        42036,
        type=DataType.ASCII,
        name="LensModel",
    )

    LensSerialNumber = anno(
        42037,
        type=DataType.ASCII,
        name="LensSerialNumber",
    )

    Photographer = anno(
        42039,
        type=DataType.ASCII,
        name="Photographer",
    )

    ImageEditor = anno(
        42040,
        type=DataType.ASCII,
        name="ImageEditor",
    )

    CameraFirmware = anno(
        42041,
        type=DataType.ASCII,
        name="CameraFirmware",
    )

    RAWDevelopingSoftware = anno(
        42042,
        type=DataType.ASCII,
        name="RAWDevelopingSoftware",
    )

    ImageEditingSoftware = anno(
        42043,
        type=DataType.ASCII,
        name="ImageEditingSoftware",
    )

    CompositeImage = anno(
        42080,
        type=DataType.Short,
        name="CompositeImage",
    )

    CompositeImageCount = anno(
        42081,
        type=DataType.Short,
        name="CompositeImageCount",
    )

    SourceImageNumberOfCompositeImage = CompositeImageCount

    CompositeImageExposureTimes = anno(
        42082,
        name="CompositeImageExposureTimes",
    )

    SourceExposureTimesOfCompositeImage = CompositeImageExposureTimes

    Gamma = anno(
        42240,
        type=DataType.Rational,
        name="Gamma",
    )

    Padding = anno(
        59932,
        name="Padding",
    )

    OffsetSchema = anno(
        59933,
        type=DataType.SLong,
        name="OffsetSchema",
    )

    Lens = anno(
        65002,
        type=DataType.ASCII,
        name="Lens",
    )

    RawFile = anno(
        65100,
        type=DataType.ASCII,
        name="RawFile",
    )

    Converter = anno(
        65101,
        type=DataType.ASCII,
        name="Converter",
    )

    Exposure = anno(
        65105,
        type=DataType.ASCII,
        name="Exposure",
    )

    Shadows = anno(
        65106,
        type=DataType.ASCII,
        name="Shadows",
    )

    Brightness = anno(
        65107,
        type=DataType.ASCII,
        name="Brightness",
    )

    Smoothness = anno(
        65111,
        type=DataType.ASCII,
        name="Smoothness",
    )

    MoireFilter = anno(
        65112,
        type=DataType.ASCII,
        name="MoireFilter",
    )
