from __future__ import annotations

from enumerific import Enumeration, anno

from tiffdata.enumerations.cleanfaxdata import CleanFaxData
from tiffdata.enumerations.compression import Compression
from tiffdata.enumerations.datatype import DataType
from tiffdata.enumerations.extrasamples import ExtraSamples
from tiffdata.enumerations.fillorder import FillOrder
from tiffdata.enumerations.indexed import Indexed
from tiffdata.enumerations.inkset import InkSet
from tiffdata.enumerations.jpeglosslesspredictors import JPEGLosslessPredictors
from tiffdata.enumerations.jpegprocess import JPEGProcess
from tiffdata.enumerations.newsubfiletype import NewSubFileType
from tiffdata.enumerations.oldsubfiletype import OldSubFileType
from tiffdata.enumerations.orientation import Orientation
from tiffdata.enumerations.photometricinterpretation import PhotometricInterpretation
from tiffdata.enumerations.planarconfiguration import PlanarConfiguration
from tiffdata.enumerations.predictor import Predictor
from tiffdata.enumerations.resolutionunit import ResolutionUnit
from tiffdata.enumerations.sampleformat import SampleFormat
from tiffdata.enumerations.t4options import T4Options
from tiffdata.enumerations.t6options import T6Options
from tiffdata.enumerations.thresholding import Thresholding
from tiffdata.enumerations.ycbcrpositioning import YCbCrPositioning


class TIFFTag(Enumeration, aliased=True, backfill=True):
    """The TIFFTag class provides enumerations for the TIFFTag type."""

    NewSubFileType = anno(
        254,
        type=DataType.Long,
        count=1,
        enumeration=NewSubFileType,
        default=0,
        name="NewSubfileType",
    )

    SubfileType = NewSubFileType

    OSubFileType = NewSubFileType

    OldSubFileType = anno(
        255,
        type=DataType.Short,
        count=1,
        enumeration=OldSubFileType,
        name="OldSubfileType",
    )

    ImageWidth = anno(
        256,
        type=(DataType.Short, DataType.Long),
        count=1,
        name="ImageWidth",
    )

    ImageLength = anno(
        257,
        type=(DataType.Short, DataType.Long),
        count=1,
        name="ImageLength",
    )

    ImageHeight = ImageLength

    BitsPerSample = anno(
        258,
        type=DataType.Short,
        default=1,
        name="BitsPerSample",
    )

    Compression = anno(
        259,
        type=DataType.Short,
        count=1,
        enumeration=Compression,
        name="Compression",
    )

    PhotometricInterpretation = anno(
        262,
        type=DataType.Short,
        count=1,
        enumeration=PhotometricInterpretation,
        name="Photometric",
    )

    Threshholding = anno(
        263,
        type=DataType.Short,
        count=1,
        enumeration=Thresholding,
        name="Threshholding",
    )

    CellWidth = anno(
        264,
        type=DataType.Short,
        count=1,
        name="CellWidth",
    )

    CellLength = anno(
        265,
        type=DataType.Short,
        count=1,
        name="CellLength",
    )

    CellHeight = CellLength

    FillOrder = anno(
        266,
        type=DataType.Short,
        count=1,
        enumeration=FillOrder,
        name="FillOrder",
    )

    DocumentName = anno(
        269,
        type=DataType.ASCII,
        name="DocumentName",
    )

    ImageDescription = anno(
        270,
        type=DataType.ASCII,
        name="ImageDescription",
    )

    Make = anno(
        271,
        type=DataType.ASCII,
        name="Make",
    )

    Model = anno(
        272,
        type=DataType.ASCII,
        name="Model",
    )

    StripOffsets = anno(
        273,
        type=(DataType.Short, DataType.Long, DataType.LongLong),
        name="StripOffsets",
    )

    Orientation = anno(
        274,
        type=DataType.Short,
        count=1,
        enumeration=Orientation,
        name="Orientation",
    )

    SamplesPerPixel = anno(
        277,
        type=DataType.Short,
        count=1,
        name="SamplesPerPixel",
    )

    RowsPerStrip = anno(
        278,
        type=(DataType.Short, DataType.Long),
        count=1,
        name="RowsPerStrip",
    )

    StripByteCounts = anno(
        279,
        type=(DataType.Short, DataType.Long, DataType.LongLong),
        name="StripByteCounts",
    )

    MinSampleValue = anno(
        280,
        type=DataType.Short,
        name="MinSampleValue",
    )

    MaxSampleValue = anno(
        281,
        type=DataType.Short,
        name="MaxSampleValue",
    )

    XResolution = anno(
        282,
        type=DataType.Rational,
        count=1,
        name="XResolution",
    )

    YResolution = anno(
        283,
        type=DataType.Rational,
        count=1,
        name="YResolution",
    )

    PlanarConfiguration = anno(
        284,
        type=DataType.Short,
        count=1,
        enumeration=PlanarConfiguration,
        name="PlanarConfig",
    )

    PageName = anno(
        285,
        type=DataType.ASCII,
        name="PageName",
    )

    Xposition = anno(
        286,
        type=DataType.Rational,
        count=1,
        name="Xposition",
    )

    Yposition = anno(
        287,
        type=DataType.Rational,
        count=1,
        name="Yposition",
    )

    FreeOffsets = anno(
        288,
        type=(DataType.Long, DataType.LongLong),
        name="FreeOffsets",
    )

    FreeByteCounts = anno(
        289,
        type=(DataType.Long, DataType.LongLong),
        name="FreeByteCounts",
    )

    GrayResponseUnit = anno(
        290,
        type=DataType.Short,
        count=1,
        default=2,
        name="GrayResponseUnit",
    )

    GreyResponseUnit = GrayResponseUnit

    GrayResponseCurve = anno(
        291,
        type=DataType.Short,
        name="GrayResponseCurve",
    )

    GreyResponseCurve = GrayResponseCurve

    T4Options = anno(
        292,
        type=DataType.Long,
        count=1,
        enumeration=T4Options,
        default=0,
        name="T4Options",
    )

    Group3Options = T4Options

    T6Options = anno(
        293,
        type=DataType.Long,
        count=1,
        enumeration=T6Options,
        default=0,
        name="T6Options",
    )

    Group4Options = T6Options

    ResolutionUnit = anno(
        296,
        type=DataType.Short,
        count=1,
        enumeration=ResolutionUnit,
        default=2,
        name="ResolutionUnit",
    )

    PageNumber = anno(
        297,
        type=DataType.Short,
        count=2,
        name="PageNumber",
    )

    ColorResponseUnit = anno(
        300,
        type=DataType.Short,
        count=1,
        name="ColorResponseUnit",
    )

    TransferFunction = anno(
        301,
        type=DataType.Short,
        name="TransferFunction",
    )

    Software = anno(
        305,
        type=DataType.ASCII,
        name="Software",
    )

    DateTime = anno(
        306,
        type=DataType.ASCII,
        count=20,
        name="DateTime",
        format="%Y:%m:%d %H:%M:%S",
    )

    Artist = anno(
        315,
        type=DataType.ASCII,
        name="Artist",
    )

    HostComputer = anno(
        316,
        type=DataType.ASCII,
        name="HostComputer",
    )

    Predictor = anno(
        317,
        type=DataType.Short,
        count=1,
        enumeration=Predictor,
        default=1,
        name="Predictor",
    )

    WhitePoint = anno(
        318,
        type=DataType.Rational,
        count=2,
        name="WhitePoint",
    )

    PrimaryChromaticities = anno(
        319,
        type=DataType.Rational,
        count=6,
        name="PrimaryChromaticities",
    )

    ColorMap = anno(
        320,
        type=DataType.Short,
        name="ColorMap",
    )

    HalftoneHints = anno(
        321,
        type=DataType.Short,
        count=2,
        name="HalftoneHints",
    )

    TileWidth = anno(
        322,
        type=(DataType.Short, DataType.Long),
        name="TileWidth",
    )

    TileLength = anno(
        323,
        type=(DataType.Short, DataType.Long),
        name="TileLength",
    )

    TileHeight = TileLength

    TileOffsets = anno(
        324,
        type=(DataType.Long, DataType.LongLong),
        name="TileOffsets",
    )

    TileByteCounts = anno(
        325,
        type=(DataType.Long, DataType.LongLong),
        name="TileByteCounts",
    )

    BadFaxLines = anno(
        326,
        type=(DataType.Short, DataType.Long),
        name="BadFaxLines",
    )

    CleanFaxData = anno(
        327,
        type=DataType.Short,
        count=1,
        enumeration=CleanFaxData,
        name="CleanFaxData",
    )

    ConsecutiveBadFaxLines = anno(
        328,
        type=(DataType.Short, DataType.Long),
        name="ConsecutiveBadFaxLines",
    )

    SubIFD = anno(
        330,
        type=(DataType.ClassicIFD, DataType.BigIFD),
        name="SubIFD",
    )

    InkSet = anno(
        332,
        type=DataType.Short,
        count=1,
        enumeration=InkSet,
        name="InkSet",
    )

    InkNames = anno(
        333,
        type=DataType.ASCII,
        name="InkNames",
    )

    NumberOfInks = anno(
        334,
        type=DataType.Short,
        count=1,
        name="NumberOfInks",
    )

    DotRange = anno(
        336,
        type=(DataType.Byte, DataType.Short),
        name="DotRange",
    )

    TargetPrinter = anno(
        337,
        type=DataType.ASCII,
        name="TargetPrinter",
    )

    ExtraSamples = anno(
        338,
        type=DataType.Short,
        count=1,
        enumeration=ExtraSamples,
        name="ExtraSamples",
    )

    SampleFormat = anno(
        339,
        type=DataType.Short,
        enumeration=SampleFormat,
        default=1,
        name="SampleFormat",
    )

    SMinSampleValue = anno(
        340,
        name="SMinSampleValue",
    )

    SMaxSampleValue = anno(
        341,
        name="SMaxSampleValue",
    )

    ClipPath = anno(
        343,
        type=DataType.Byte,
        name="ClipPath",
    )

    XClipPathUnits = anno(
        344,
        type=DataType.Long,
        name="XClipPathUnits",
    )

    YClipPathUnits = anno(
        345,
        type=DataType.Long,
        name="YClipPathUnits",
    )

    Indexed = anno(
        346,
        type=DataType.Short,
        enumeration=Indexed,
        default=0,
        name="Indexed",
    )

    JPEGTables = anno(
        347,
        type=DataType.Undefined,
        name="JPEGTables",
    )

    OPIProxy = anno(
        351,
        name="OPIProxy",
    )

    GlobalParametersIFD = anno(
        400,
        type=(DataType.ClassicIFD, DataType.BigIFD),
        name="GlobalParametersIFD",
    )

    ProfileType = anno(
        401,
        name="ProfileType",
    )

    FaxProfile = anno(
        402,
        name="FaxProfile",
    )

    CodingMethods = anno(
        403,
        name="CodingMethods",
    )

    VersionYear = anno(
        404,
        name="VersionYear",
    )

    ModeNumber = anno(
        405,
        name="ModeNumber",
    )

    Decode = anno(
        433,
        name="Decode",
    )

    ImageBaseColor = anno(
        434,
        name="ImageBaseColor",
    )

    T82Options = anno(
        435,
        name="T82Options",
    )

    JPEGProcess = anno(
        512,
        type=DataType.Short,
        count=1,
        enumeration=JPEGProcess,
        name="JPEGProcess",
    )

    JPEGIFOffset = anno(
        513,
        type=(DataType.Long, DataType.LongLong),
        count=1,
        name="JPEGIFOffset",
    )

    JPEGIFByteCount = anno(
        514,
        type=(DataType.Long, DataType.LongLong),
        count=1,
        name="JPEGIFByteCount",
    )

    JPEGRestartInterval = anno(
        515,
        type=DataType.Short,
        count=1,
        name="JPEGRestartInterval",
    )

    JPEGLosslessPredictors = anno(
        517,
        type=DataType.Short,
        enumeration=JPEGLosslessPredictors,
        name="JPEGLosslessPredictors",
    )

    JPEGPointTransform = anno(
        518,
        type=DataType.Short,
        name="JPEGPointTransform",
    )

    JPEGQTables = anno(
        519,
        type=(DataType.Long, DataType.LongLong),
        name="JPEGQTables",
    )

    JPEGDCTables = anno(
        520,
        type=(DataType.Long, DataType.LongLong),
        name="JPEGDCTables",
    )

    JPEGACTables = anno(
        521,
        type=(DataType.Long, DataType.LongLong),
        name="JPEGACTables",
    )

    YCbCrCoefficients = anno(
        529,
        type=DataType.Rational,
        count=3,
        name="YCbCrCoefficients",
    )

    YCbCrSubsampling = anno(
        530,
        type=DataType.Short,
        count=2,
        name="YCbCrSubsampling",
    )

    YCbCrPositioning = anno(
        531,
        type=DataType.Short,
        count=1,
        enumeration=YCbCrPositioning,
        name="YCbCrPositioning",
    )

    ReferenceBlackWhite = anno(
        532,
        type=DataType.Rational,
        count=6,
        name="ReferenceBlackWhite",
    )

    StripRowCounts = anno(
        559,
        type=DataType.Long,
        name="StripRowCounts",
    )

    XMLPacket = anno(
        700,
        name="XMLPacket",
    )

    OPIImageID = anno(
        32781,
        name="OPIImageID",
    )

    WangAnnotation = anno(
        32932,
        name="WangAnnotation",
    )

    TiffAnnotationData = WangAnnotation

    ReferencePoints = anno(
        32953,
        name="RefPts",
    )

    RegionTackPoint = anno(
        32954,
        name="RegionTackPoint",
    )

    RegionWarpCorners = anno(
        32955,
        name="RegionWarpCorners",
    )

    RegionAffine = anno(
        32956,
        name="RegionAffine",
    )

    Matteing = anno(
        32995,
        name="Matteing",
    )

    Datatype = anno(
        32996,
        name="Datatype",
    )

    ImageDepth = anno(
        32997,
        name="ImageDepth",
    )

    TileDepth = anno(
        32998,
        name="TileDepth",
    )

    PixarImageFullWidth = anno(
        33300,
        name="PIXARImageFullWidth",
    )

    PixarImageFullLength = anno(
        33301,
        name="PIXARImageFullLength",
    )

    PIXARImageFullHeight = PixarImageFullLength

    PixarTextureFormat = anno(
        33302,
        name="PIXARTextureFormat",
    )

    PIXARWrapModes = anno(
        33303,
        name="PIXARWrapModes",
    )

    PixarFovCot = anno(
        33304,
        name="PixarFovCot",
    )

    PixarMatrixWorldToScreen = anno(
        33305,
        name="PixarMatrixWorldToScreen",
    )

    PIXARMatrixWorldToCamera = anno(
        33306,
        name="PIXARMatrixWorldToCamera",
    )

    WriterSerialNumber = anno(
        33405,
        name="WriterSerialNumber",
    )

    CFARepeatPatternDim = anno(
        33421,
        name="CFARepeatPatternDim",
    )

    BatteryLevel = anno(
        33423,
        name="BatteryLevel",
    )

    Copyright = anno(
        33432,
        type=DataType.ASCII,
        name="Copyright",
    )

    MDFileTag = anno(
        33445,
        name="MDFileTag",
    )

    MDScalePixel = anno(
        33446,
        name="MDScalePixel",
    )

    MDColorTable = anno(
        33447,
        name="MDColorTable",
    )

    MDLabName = anno(
        33448,
        name="MDLabName",
    )

    MDSampleInfo = anno(
        33449,
        name="MDSampleInfo",
    )

    MDPrepDate = anno(
        33450,
        name="MDPrepDate",
    )

    MDPrepTime = anno(
        33451,
        name="MDPrepTime",
    )

    MDFileUnits = anno(
        33452,
        name="MDFileUnits",
    )

    ModelPixelScaleTag = anno(
        33550,
        name="ModelPixelScaleTag",
    )

    RichTIFFIPTC = anno(
        33723,
        type=DataType.Undefined,
        name="RichTIFFIPTC",
    )

    IPTCNAA = RichTIFFIPTC

    INGRPacketDataTag = anno(
        33918,
        name="INGRPacketDataTag",
    )

    INGRFlagRegisters = anno(
        33919,
        name="INGRFlagRegisters",
    )

    IrasBTransformationMatrix = anno(
        33920,
        name="IrasBTransformationMatrix",
    )

    IrasBTransormationMatrix = IrasBTransformationMatrix

    ModelTiePointTag = anno(
        33922,
        name="ModelTiepointTag",
    )

    IT8Site = anno(
        34016,
        name="IT8Site",
    )

    IT8ColorSequence = anno(
        34017,
        name="IT8ColorSequence",
    )

    IT8Header = anno(
        34018,
        name="IT8Header",
    )

    IT8RasterPadding = anno(
        34019,
        name="IT8RasterPadding",
    )

    IT8BitsPerRunLength = anno(
        34020,
        name="IT8BitsPerRunLength",
    )

    IT8BitsPerExtendedRunLength = anno(
        34021,
        name="IT8BitsPerExtendedRunLength",
    )

    IT8ColorTable = anno(
        34022,
        name="IT8ColorTable",
    )

    IT8ImageColorIndicator = anno(
        34023,
        name="IT8ImageColorIndicator",
    )

    IT8BackgroundColorIndicator = anno(
        34024,
        name="IT8BkgColorIndicator",
    )

    IT8ImageColorValue = anno(
        34025,
        name="IT8ImageColorValue",
    )

    IT8BackgroundColorValue = anno(
        34026,
        name="IT8BkgColorValue",
    )

    IT8PixelIntensityRange = anno(
        34027,
        name="IT8PixelIntensityRange",
    )

    IT8TransparencyIndicator = anno(
        34028,
        name="IT8TransparencyIndicator",
    )

    IT8ColorCharacterization = anno(
        34029,
        name="IT8ColorCharacterization",
    )

    IT8HCUsage = anno(
        34030,
        name="IT8HCUsage",
    )

    IT8TrapIndicator = anno(
        34031,
        name="IT8TrapIndicator",
    )

    IT8CMYKEquivalent = anno(
        34032,
        name="IT8CMYKEquivalent",
    )

    FrameCount = anno(
        34232,
        name="FrameCount",
    )

    ModelTransformationTag = anno(
        34264,
        name="ModelTransformationTag",
    )

    Photoshop = anno(
        34377,
        name="Photoshop",
    )

    EXIFIFD = anno(
        34665,
        type=(DataType.ClassicIFD, DataType.BigIFD),
        name="EXIFIFD",
    )

    ICCProfile = anno(
        34675,
        name="ICCProfile",
    )

    ImageLayer = anno(
        34732,
        name="ImageLayer",
    )

    GeoKeyDirectoryTag = anno(
        34735,
        name="GeoKeyDirectoryTag",
    )

    GeoDoubleParamsTag = anno(
        34736,
        name="GeoDoubleParamsTag",
    )

    GeoAsciiParamsTag = anno(
        34737,
        name="GeoAsciiParamsTag",
    )

    JBIGOptions = anno(
        34750,
        name="JBIGOptions",
    )

    GPSIFD = anno(
        34853,
        type=(DataType.ClassicIFD, DataType.BigIFD),
        name="GPSIFD",
    )

    Interlace = anno(
        34857,
        name="Interlace",
    )

    SeflTimerMode = anno(
        34859,
        name="SeflTimerMode",
    )

    FaxReceiveParams = anno(
        34908,
        name="FaxReceiveParams",
    )

    FaxSubaddress = anno(
        34909,
        name="FaxSubaddress",
    )

    FaxReceiveTime = anno(
        34910,
        name="FaxReceiveTime",
    )

    FaxDCS = anno(
        34911,
        name="FaxDCS",
    )

    FedExEDR = anno(
        34929,
        name="FedExEDR",
    )

    MaximumApertureValue = anno(
        37381,
        name="MaximumApertureValue",
    )

    Noise = anno(
        37389,
        name="Noise",
    )

    StandardID = anno(
        37398,
        name="StandardID",
    )

    STONits = anno(
        37439,
        name="STONits",
    )

    ImageSourceData = anno(
        37724,
        name="ImageSourceData",
    )

    InteroperabilityIFD = anno(
        40965,
        type=(DataType.ClassicIFD, DataType.BigIFD),
        name="InteroperabilityIFD",
    )

    GDALMetadata = anno(
        42112,
        name="GDALMetadata",
    )

    GDALNoData = anno(
        42113,
        name="GDALNoData",
    )

    OCEScanJobDescription = anno(
        50215,
        name="OCEScanJobDescription",
    )

    OCEApplicationSelector = anno(
        50216,
        name="OCEApplicationSelector",
    )

    OCEIdentificationNumber = anno(
        50217,
        name="OCEIdentificationNumber",
    )

    OCEImageLogicCharacteristics = anno(
        50218,
        name="OCEImageLogicCharacteristics",
    )

    LERCParameters = anno(
        50674,
        name="LERCParameters",
    )

    DNGVersion = anno(
        50706,
        name="DNGVersion",
    )

    DNGBackwardVersion = anno(
        50707,
        name="DNGBackwardVersion",
    )

    UniqueCameraModel = anno(
        50708,
        name="UniqueCameraModel",
    )

    LocalizedCameraModel = anno(
        50709,
        name="LocalizedCameraModel",
    )

    CFAPlaneColor = anno(
        50710,
        name="CFAPlaneColor",
    )

    CFALayout = anno(
        50711,
        name="CFALayout",
    )

    LinearizationTable = anno(
        50712,
        name="LinearizationTable",
    )

    BlackLevelRepeatDim = anno(
        50713,
        name="BlackLevelRepeatDim",
    )

    BlackLevel = anno(
        50714,
        name="BlackLevel",
    )

    BlackLevelDeltaH = anno(
        50715,
        name="BlackLevelDeltaH",
    )

    BlackLevelDeltaV = anno(
        50716,
        name="BlackLevelDeltaV",
    )

    WhiteLevel = anno(
        50717,
        name="WhiteLevel",
    )

    DefaultScale = anno(
        50718,
        name="DefaultScale",
    )

    DefaultCropOrigin = anno(
        50719,
        name="DefaultCropOrigin",
    )

    DefaultCropSize = anno(
        50720,
        name="DefaultCropSize",
    )

    ColorMatrix1 = anno(
        50721,
        name="ColorMatrix1",
    )

    ColorMatrix2 = anno(
        50722,
        name="ColorMatrix2",
    )

    CameraCalibration1 = anno(
        50723,
        name="CameraCalibration1",
    )

    CameraCalibration2 = anno(
        50724,
        name="CameraCalibration2",
    )

    ReductionMatrix1 = anno(
        50725,
        name="ReductionMatrix1",
    )

    ReductionMatrix2 = anno(
        50726,
        name="ReductionMatrix2",
    )

    AnalogBalance = anno(
        50727,
        name="AnalogBalance",
    )

    AsShotNeutral = anno(
        50728,
        name="AsShotNeutral",
    )

    AsShotWhiteXY = anno(
        50729,
        name="AsShotWhiteXY",
    )

    BaselineExposure = anno(
        50730,
        name="BaselineExposure",
    )

    BaselineNoise = anno(
        50731,
        name="BaselineNoise",
    )

    BaselineSharpness = anno(
        50732,
        name="BaselineSharpness",
    )

    BayerGreenSplit = anno(
        50733,
        name="BayerGreenSplit",
    )

    LinearResponseLimit = anno(
        50734,
        name="LinearResponseLimit",
    )

    CameraSerialNumber = anno(
        50735,
        name="CameraSerialNumber",
    )

    ChromaBlurRadius = anno(
        50737,
        name="ChromaBlurRadius",
    )

    AntiAliasStrength = anno(
        50738,
        name="AntiAliasStrength",
    )

    ShadowScale = anno(
        50739,
        name="ShadowScale",
    )

    DNGPrivateData = anno(
        50740,
        name="DNGPrivateData",
    )

    MakerNoteSafety = anno(
        50741,
        name="MakerNoteSafety",
    )

    CalibrationIlluminant1 = anno(
        50778,
        name="CalibrationIlluminant1",
    )

    CalibrationIlluminant2 = anno(
        50779,
        name="CalibrationIlluminant2",
    )

    BestQualityScale = anno(
        50780,
        name="BestQualityScale",
    )

    RawDataUniqueID = anno(
        50781,
        name="RawDataUniqueID",
    )

    AliasLayerMetadata = anno(
        50784,
        name="AliasLayerMetadata",
    )

    OriginalRawFileName = anno(
        50827,
        name="OriginalRawFileName",
    )

    OriginalRawFileData = anno(
        50828,
        name="OriginalRawFileData",
    )

    ActiveArea = anno(
        50829,
        name="ActiveArea",
    )

    MaskedAreas = anno(
        50830,
        name="MaskedAreas",
    )

    AsShotICCProfile = anno(
        50831,
        name="AsShotICCProfile",
    )

    AsShotPreProfileMatrix = anno(
        50832,
        name="AsShotPreProfileMatrix",
    )

    CurrentICCProfile = anno(
        50833,
        name="CurrentICCProfile",
    )

    CurrentPreProfileMatrix = anno(
        50834,
        name="CurrentPreProfileMatrix",
    )

    ImageJMetadataByteCounts = anno(
        50838,
        type=(DataType.Short, DataType.Long, DataType.LongLong),
        name="ImageJMetadataByteCounts",
    )

    IJMetadataByteCounts = ImageJMetadataByteCounts

    ImageJMetadata = anno(
        50839,
        type=DataType.Byte,
        name="ImageJMetadata",
    )

    RPCCoefficient = anno(
        50844,
        name="RPCCoefficient",
    )

    ColorimetricReference = anno(
        50879,
        name="ColorimetricReference",
    )

    TIFFRSID = anno(
        50908,
        name="TIFFRSID",
    )

    GeoMetadata = anno(
        50909,
        name="GeoMetadata",
    )

    CameraCalibrationSignature = anno(
        50931,
        name="CameraCalibrationSignature",
    )

    ProfileCalibrationSignature = anno(
        50932,
        name="ProfileCalibrationSignature",
    )

    TIFFTagExtraCameraProfiles = anno(
        50933,
        name="TIFFTagExtraCameraProfiles",
    )

    ExtraCameraProfiles = TIFFTagExtraCameraProfiles

    AsShotProfileName = anno(
        50934,
        name="AsShotProfileName",
    )

    NoiseReductionApplied = anno(
        50935,
        name="NoiseReductionApplied",
    )

    ProfileName = anno(
        50936,
        name="ProfileName",
    )

    ProfileHueSatMapDims = anno(
        50937,
        name="ProfileHueSatMapDims",
    )

    ProfileHueSatMapData1 = anno(
        50938,
        name="ProfileHueSatMapData1",
    )

    ProfileHueSatMapData2 = anno(
        50939,
        name="ProfileHueSatMapData2",
    )

    ProfileToneCurve = anno(
        50940,
        name="ProfileToneCurve",
    )

    ProfileEmbedPolicy = anno(
        50941,
        name="ProfileEmbedPolicy",
    )

    ProfileCopyright = anno(
        50942,
        name="ProfileCopyright",
    )

    ForwardMatrix1 = anno(
        50964,
        name="ForwardMatrix1",
    )

    ForwardMatrix2 = anno(
        50965,
        name="ForwardMatrix2",
    )

    PreviewApplicationName = anno(
        50966,
        name="PreviewApplicationName",
    )

    PreviewApplicationVersion = anno(
        50967,
        name="PreviewApplicationVersion",
    )

    PreviewSettingsName = anno(
        50968,
        name="PreviewSettingsName",
    )

    PreviewSettingsDigest = anno(
        50969,
        name="PreviewSettingsDigest",
    )

    PreviewColorSpace = anno(
        50970,
        name="PreviewColorSpace",
    )

    PreviewDateTime = anno(
        50971,
        name="PreviewDateTime",
    )

    RawImageDigest = anno(
        50972,
        name="RawImageDigest",
    )

    OriginalRawFileDigest = anno(
        50973,
        name="OriginalRawFileDigest",
    )

    SubTileBlockSize = anno(
        50974,
        name="SubTileBlockSize",
    )

    RowInterleaveFactor = anno(
        50975,
        name="RowInterleaveFactor",
    )

    ProfileLookTableDims = anno(
        50981,
        name="ProfileLookTableDims",
    )

    ProfileLookTableData = anno(
        50982,
        name="ProfileLookTableData",
    )

    OPCodeList1 = anno(
        51008,
        name="OPCodeList1",
    )

    OPCodeList2 = anno(
        51009,
        name="OPCodeList2",
    )

    OPCodeList3 = anno(
        51022,
        name="OPCodeList3",
    )

    NoiseProfile = anno(
        51041,
        name="NoiseProfile",
    )

    OriginalDefaultFinalSize = anno(
        51089,
        name="OriginalDefaultFinalSize",
    )

    OriginalBestQualityFinalSize = anno(
        51090,
        name="OriginalBestQualityFinalSize",
    )

    OriginalDefaultCropSize = anno(
        51091,
        name="OriginalDefaultCropSize",
    )

    ProfileHueSatMapEncoding = anno(
        51107,
        name="ProfileHueSatMapEncoding",
    )

    ProfileLookTableEncoding = anno(
        51108,
        name="ProfileLookTableEncoding",
    )

    BaselineExposureOffset = anno(
        51109,
        name="BaselineExposureOffset",
    )

    DefaultBlackRender = anno(
        51110,
        name="DefaultBlackRender",
    )

    NewRawImageDigest = anno(
        51111,
        name="NewRawImageDigest",
    )

    RawTopReviewGain = anno(
        51112,
        name="RawTopReviewGain",
    )

    DefaultUserCrop = anno(
        51125,
        name="DefaultUserCrop",
    )

    DepthFormat = anno(
        51177,
        name="DepthFormat",
    )

    DepthNear = anno(
        51178,
        name="DepthNear",
    )

    DepthFar = anno(
        51179,
        name="DepthFar",
    )

    DepthUnits = anno(
        51180,
        name="DepthUnits",
    )

    DepthMeasureType = anno(
        51181,
        name="DepthMeasureType",
    )

    EnhanceParams = anno(
        51182,
        name="EnhanceParams",
    )

    ProfileGainTableMap = anno(
        52525,
        name="ProfileGainTableMap",
    )

    SemanticName = anno(
        52526,
        name="SemanticName",
    )

    SemanticInstanceID = anno(
        52528,
        name="SemanticInstanceID",
    )

    CalibrationIlluminant3 = anno(
        52529,
        name="CalibrationIlluminant3",
    )

    CameraCalibration3 = anno(
        52530,
        name="CameraCalibration3",
    )

    ColorMatrix3 = anno(
        52531,
        name="ColorMatrix3",
    )

    ForwardMatrix3 = anno(
        52532,
        name="ForwardMatrix3",
    )

    IlluminantData1 = anno(
        52533,
        name="IlluminantData1",
    )

    IlluminantData2 = anno(
        52534,
        name="IlluminantData2",
    )

    MaskSubArea = anno(
        52536,
        name="MaskSubArea",
    )

    ProfileHueSatMapData3 = anno(
        52537,
        name="ProfileHueSatMapData3",
    )

    ReductionMatrix3 = anno(
        52538,
        name="ReductionMatrix3",
    )

    RGBTables = anno(
        52543,
        name="RGBTables",
    )

    IlluminantData3 = anno(
        53535,
        name="IlluminantData3",
    )

    AperioUnknown55000 = anno(
        55000,
        type=DataType.SLong,
        name="AperioUnknown55000",
    )

    AperioMagnification = anno(
        55001,
        name="AperioMagnification",
    )

    AperioMPP = anno(
        55002,
        type=DataType.Double,
        name="AperioMPP",
    )

    AperioScanScopeID = anno(
        55003,
        name="AperioScanScopeID",
    )

    AperioDate = anno(
        55004,
        name="AperioDate",
    )

    NDPIOffsetHighBytes = anno(
        65324,
        name="NDPIOffsetHighBytes",
    )

    NDPIByteCountHighBytes = anno(
        65325,
        name="NDPIByteCountHighBytes",
    )

    NDPIFormatFlag = anno(
        65420,
        name="NDPIFormatFlag",
    )

    NDPISourceLens = anno(
        65421,
        name="NDPISourceLens",
    )

    NDPIMagnification = NDPISourceLens

    NDPIXOffset = anno(
        65422,
        name="NDPIXOffset",
    )

    NDPIYOffset = anno(
        65423,
        name="NDPIYOffset",
    )

    NDPIFocalPlane = anno(
        65424,
        name="NDPIFocalPlane",
    )

    NDPIZOffset = NDPIFocalPlane

    NDPITissueIndex = anno(
        65425,
        name="NDPITissueIndex",
    )

    NDPIMCUStarts = anno(
        65426,
        name="NDPIMCUStarts",
    )

    NDPIReference = anno(
        65427,
        name="NDPIReference",
    )

    NDPISlideLabel = NDPIReference

    NDPIAuthCode = anno(
        65428,
        name="NDPIAuthCode",
    )

    NDPIMCUStartsHighBytes = anno(
        65432,
        name="NDPIMCUStartsHighBytes",
    )

    NDPIChannel = anno(
        65434,
        name="NDPIChannel",
    )

    NDPIFluorescence = NDPIChannel

    NDPIExposureRatio = anno(
        65435,
        name="NDPIExposureRatio",
    )

    NDPIRedMultiplier = anno(
        65436,
        name="NDPIRedMultiplier",
    )

    NDPIGreenMultiplier = anno(
        65437,
        name="NDPIGreenMultiplier",
    )

    NDPIBlueMultiplier = anno(
        65438,
        name="NDPIBlueMultiplier",
    )

    NDPIFocusPoints = anno(
        65439,
        name="NDPIFocusPoints",
    )

    NDPIFocusPointRegions = anno(
        65440,
        name="NDPIFocusPointRegions",
    )

    NDPICaptureMode = anno(
        65441,
        name="NDPICaptureMode",
    )

    NDPINDPSN = anno(
        65442,
        name="NDPINDPSN",
    )

    NDPIScannerSerialNumber = NDPINDPSN

    NDPIJPEGQuality = anno(
        65444,
        name="NDPIJPEGQuality",
    )

    NDPIRefocusInterval = anno(
        65445,
        name="NDPIRefocusInterval",
    )

    NDPIFocusOffset = anno(
        65446,
        name="NDPIFocusOffset",
    )

    NDPIBlankLines = anno(
        65447,
        name="NDPIBlankLines",
    )

    NDPIFirmwareVersion = anno(
        65448,
        name="NDPIFirmwareVersion",
    )

    NDPIPropertyMap = anno(
        65449,
        name="NDPIPropertyMap",
    )

    NDPILabelObscured = anno(
        65450,
        name="NDPILabelObscured",
    )

    NDPIEmissionWavelength = anno(
        65451,
        name="NDPIEmissionWavelength",
    )

    NDPILampAge = anno(
        65453,
        name="NDPILampAge",
    )

    NDPIExposureTime = anno(
        65454,
        name="NDPIExposureTime",
    )

    NDPIFocusTime = anno(
        65455,
        name="NDPIFocusTime",
    )

    NDPIScanTime = anno(
        65456,
        name="NDPIScanTime",
    )

    NDPIWriteTime = anno(
        65457,
        name="NDPIWriteTime",
    )

    NDPIFullyAutoFocus = anno(
        65458,
        name="NDPIFullyAutoFocus",
    )

    NDPIDefaultGamma = anno(
        65500,
        name="NDPIDefaultGamma",
    )

    DCSHueShiftValues = anno(
        65535,
        name="DCSHueShiftValues",
    )


TIFFTag.EXIFIFD.tags = TIFFTag
TIFFTag.GPSIFD.tags = TIFFTag
TIFFTag.GlobalParametersIFD.tags = TIFFTag
TIFFTag.InteroperabilityIFD.tags = TIFFTag
TIFFTag.SubIFD.tags = TIFFTag
