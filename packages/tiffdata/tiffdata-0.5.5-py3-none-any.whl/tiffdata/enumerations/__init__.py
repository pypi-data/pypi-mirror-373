from tiffdata.enumerations.cleanfaxdata import CleanFaxData
from tiffdata.enumerations.compression import Compression
from tiffdata.enumerations.datatype import DataType
from tiffdata.enumerations.exiftag import EXIFTag
from tiffdata.enumerations.extrasamples import ExtraSamples
from tiffdata.enumerations.fillorder import FillOrder
from tiffdata.enumerations.format import Format
from tiffdata.enumerations.gpstag import GPSTag
from tiffdata.enumerations.indexed import Indexed
from tiffdata.enumerations.inkset import InkSet
from tiffdata.enumerations.interoperabilitytag import InteroperabilityTag
from tiffdata.enumerations.jpeglosslesspredictors import JPEGLosslessPredictors
from tiffdata.enumerations.jpegprocess import JPEGProcess
from tiffdata.enumerations.newsubfiletype import NewSubFileType
from tiffdata.enumerations.oldsubfiletype import OldSubFileType
from tiffdata.enumerations.orientation import Orientation
from tiffdata.enumerations.photometricinterpretation import PhotometricInterpretation
from tiffdata.enumerations.predictor import Predictor
from tiffdata.enumerations.resolutionunit import ResolutionUnit
from tiffdata.enumerations.sampleformat import SampleFormat
from tiffdata.enumerations.t4options import T4Options
from tiffdata.enumerations.t6options import T6Options
from tiffdata.enumerations.thresholding import Thresholding
from tiffdata.enumerations.tifftag import TIFFTag
from tiffdata.enumerations.ycbcrpositioning import YCbCrPositioning


class TIFFTag(TIFFTag):
    @property
    def types(self) -> tuple[DataType]:
        if isinstance(types := self.get("type"), (list, tuple, set)):
            for type in types:
                if not isinstance(type, DataType):
                    raise TypeError(
                        "The 'type' argument can only reference DataType enumeration options!"
                    )
            return tuple(types)
        elif isinstance(types := self.get("type"), DataType):
            return tuple([types])
        else:
            return tuple()

    @property
    def isIFD(self) -> bool:
        """The isIFD property reports whether the tag has an IFD data type or not."""

        if isinstance(types := self.types, tuple):
            return DataType.ClassicIFD in types or DataType.BigIFD in types

        return False


__all__ = [
    "CleanFaxData",
    "Compression",
    "DataType",
    "EXIFTag",
    "ExtraSamples",
    "FillOrder",
    "Format",
    "GPSTag",
    "Indexed",
    "InkSet",
    "InteroperabilityTag",
    "JPEGLosslessPredictors",
    "JPEGProcess",
    "NewSubFileType",
    "OldSubFileType",
    "Orientation",
    "PhotometricInterpretation",
    "Predictor",
    "ResolutionUnit",
    "SampleFormat",
    "T4Options",
    "T6Options",
    "Thresholding",
    "TIFFTag",
    "Type",
    "YCbCrPositioning",
]
