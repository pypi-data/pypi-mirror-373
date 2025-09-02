from __future__ import annotations

from enumerific import anno

from tiffdata.enumerations.datatype import DataType
from tiffdata.enumerations.tifftag import TIFFTag


class GPSTag(TIFFTag, aliased=True):
    """The GPSTag class provides enumerations for the GPSTag type."""

    GPSVersionID = anno(
        0,
        type=DataType.Byte,
        count=4,
        name="GPSVersionID",
    )

    VersionID = GPSVersionID

    GPSLatitudeReference = anno(
        1,
        type=DataType.ASCII,
        count=2,
        name="GPSLatitudeReference",
    )

    LatitudeReference = GPSLatitudeReference

    GPSLatitude = anno(
        2,
        type=DataType.Rational,
        count=3,
        name="GPSLatitude",
    )

    Latitude = GPSLatitude

    GPSLongitudeReference = anno(
        3,
        type=DataType.ASCII,
        count=2,
        name="GPSLongitudeReference",
    )

    LongitudeReference = GPSLongitudeReference

    GPSLongitude = anno(
        4,
        type=DataType.Rational,
        count=3,
        name="GPSLongitude",
    )

    Longitude = GPSLongitude

    GPSAltitudeReference = anno(
        5,
        type=DataType.Byte,
        count=1,
        name="GPSAltitudeReference",
    )

    AltitudeReference = GPSAltitudeReference

    GPSAltitude = anno(
        6,
        type=DataType.Rational,
        count=1,
        name="GPSAltitude",
    )

    Altitude = GPSAltitude

    GPSTimeStamp = anno(
        7,
        type=DataType.Rational,
        count=3,
        name="GPSTimeStamp",
    )

    TimeStamp = GPSTimeStamp

    GPSSatellites = anno(
        8,
        type=DataType.ASCII,
        name="GPSSatellites",
    )

    Satellites = GPSSatellites

    GPSStatus = anno(
        9,
        type=DataType.ASCII,
        count=2,
        name="GPSStatus",
    )

    Status = GPSStatus

    GPSMeasureMode = anno(
        10,
        type=DataType.ASCII,
        count=2,
        name="GPSMeasureMode",
    )

    MeasureMode = GPSMeasureMode

    GPSDOP = anno(
        11,
        type=DataType.Rational,
        count=1,
        name="GPSDOP",
    )

    DOP = GPSDOP

    GPSSpeedReference = anno(
        12,
        type=DataType.ASCII,
        count=2,
        name="GPSSpeedReference",
    )

    SpeedReference = GPSSpeedReference

    GPSSpeed = anno(
        13,
        type=DataType.Rational,
        count=1,
        name="GPSSpeed",
    )

    Speed = GPSSpeed

    GPSTrackReference = anno(
        14,
        type=DataType.ASCII,
        count=2,
        name="GPSTrackReference",
    )

    TrackReference = GPSTrackReference

    GPSTrack = anno(
        15,
        type=DataType.Rational,
        count=1,
        name="GPSTrack",
    )

    Track = GPSTrack

    GPSImageDirectionReference = anno(
        16,
        type=DataType.ASCII,
        count=2,
        name="GPSImageDirectionReference",
    )

    ImageDirectionReference = GPSImageDirectionReference

    GPSImageDirection = anno(
        17,
        type=DataType.Rational,
        count=1,
        name="GPSImageDirection",
    )

    ImageDirection = GPSImageDirection

    GPSMapDatum = anno(
        18,
        type=DataType.ASCII,
        name="GPSMapDatum",
    )

    MapDatum = GPSMapDatum

    GPSDestLatitudeReference = anno(
        19,
        type=DataType.ASCII,
        count=2,
        name="GPSDestLatitudeReference",
    )

    DestLatitudeReference = GPSDestLatitudeReference

    GPSDestLatitude = anno(
        20,
        type=DataType.Rational,
        count=3,
        name="GPSDestLatitude",
    )

    DestLatitude = GPSDestLatitude

    GPSDestLongitudeReference = anno(
        21,
        type=DataType.ASCII,
        count=2,
        name="GPSDestLongitudeReference",
    )

    DestLongitudeReference = GPSDestLongitudeReference

    GPSDestLongitude = anno(
        22,
        type=DataType.Rational,
        count=3,
        name="GPSDestLongitude",
    )

    DestLongitude = GPSDestLongitude

    GPSDestBearingReference = anno(
        23,
        type=DataType.ASCII,
        count=2,
        name="GPSDestBearingReference",
    )

    DestBearingReference = GPSDestBearingReference

    GPSDestBearing = anno(
        24,
        type=DataType.Rational,
        count=1,
        name="GPSDestBearing",
    )

    DestBearing = GPSDestBearing

    GPSDestDistanceReference = anno(
        25,
        type=DataType.ASCII,
        count=2,
        name="GPSDestDistanceRef",
    )

    DestDistanceReference = GPSDestDistanceReference

    GPSDestDistance = anno(
        26,
        type=DataType.Rational,
        count=1,
        name="GPSDestDistance",
    )

    DestDistance = GPSDestDistance

    GPSProcessingMethod = anno(
        27,
        type=DataType.Undefined,
        name="GPSProcessingMethod",
    )

    ProcessingMethod = GPSProcessingMethod

    GPSAreaInformation = anno(
        28,
        type=DataType.Undefined,
        name="GPSAreaInformation",
    )

    AreaInformation = GPSAreaInformation

    GPSDateStamp = anno(
        29,
        type=DataType.ASCII,
        count=11,
        name="GPSDateStamp",
    )

    DateStamp = GPSDateStamp

    GPSDifferential = anno(
        30,
        type=DataType.Short,
        count=1,
        name="GPSDifferential",
    )

    Differential = GPSDifferential

    GPSPositioningError = anno(
        31,
        name="GPSPositioningError",
    )

    PositioningError = GPSPositioningError
