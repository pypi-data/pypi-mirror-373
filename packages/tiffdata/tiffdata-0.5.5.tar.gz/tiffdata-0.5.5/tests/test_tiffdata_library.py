from tiffdata import (
    TIFF,
    ClassicTIFF,
    BigTIFF,
    ByteOrder,
    Format,
)

import os


def test_tiffdata_library_initialisation(path: callable, caplog):
    """Test the initialisation of the TIFF class."""

    # Use the path fixture to assemble and return the absolute path for the test file
    filepath: str = path("classic.tiff")

    # Create an instance of the TIFF class for the file
    tiff = TIFF(filepath=filepath)

    # Ensure that the class instance is of the expected type
    assert isinstance(tiff, TIFF)

    # Ensure that the class instance is of the expected subclass type
    assert isinstance(tiff, ClassicTIFF)

    # Ensure that the class instance was created for the expected file path
    assert tiff.filepath == filepath

    # Ensure that the class instance determined the expected file size
    assert tiff.filesize == os.path.getsize(filepath)

    # Ensure that the byte order of the file is as expected
    assert tiff.order is ByteOrder.MSB

    # Ensure that the format of the file is as expected
    assert tiff.format is Format.ClassicTIFF


def test_tiffdata_library_parsing_classic(path: callable):
    """Test parsing a Classic TIFF file through the TIFF class."""

    # Use the path fixture to assemble and return the absolute path for the test file
    # The 'classic.tiff' test file is a Classic TIFF, encoded using MSB byte order, and
    # has a single IFD, and an image canvas of 3x3 pixels, and a resolution of 300
    filepath: str = path("classic.tiff")

    # Create an instance of the TIFF class for the file
    tiff = TIFF(filepath=filepath)

    # Ensure that the parsed TIFF file is of the expected type
    assert isinstance(tiff, TIFF)
    assert isinstance(tiff, ClassicTIFF)

    assert tiff.filepath == filepath
    assert tiff.filesize == os.path.getsize(filepath)

    assert tiff.order is ByteOrder.MSB
    assert tiff.format is Format.ClassicTIFF

    # Ensure that the parsed TIFF file contains the expected number of IFDs
    assert len(tiff) == 1

    # Ensure that the parsed metadata contained in the TIFF file is as expected
    assert tiff.imageWidth == 3
    assert tiff.imageLength == 3  # TIFF refers to Image Height as Image Length
    assert tiff.orientation == 1
    assert tiff.samplesPerPixel == 3
    assert tiff.sampleFormat == [1, 1, 1]
    assert tiff.bitsPerSample == [8, 8, 8]
    assert tiff.fillOrder == 1
    assert tiff.compression == 1
    assert tiff.photometricInterpretation == 2
    assert tiff.rowsPerStrip == 3
    assert tiff.stripOffsets == 38
    assert tiff.stripByteCounts == 27
    assert tiff.planarConfiguration == 1
    assert tiff.resolutionUnit == 2
    assert int(tiff.yResolution) == 300  # cast the rational number to an integer
    assert int(tiff.xResolution) == 300  # cast the rational number to an integer
    assert tiff.software == "Pixelmator Pro 3.7"


def test_tiffdata_library_parsing_big(path: callable):
    """Test parsing a Big TIFF file through the TIFF class."""

    # Use the path fixture to assemble and return the absolute path for the test file
    # The 'classic.tiff' test file is a Big TIFF, encoded using LSB byte order, and
    # has a single IFD, and an image canvas of 3x3 pixels, and a resolution of 300
    filepath: str = path("big.tiff")

    # Create an instance of the TIFF class for the file
    tiff = TIFF(filepath=filepath)

    # Ensure that the parsed TIFF file is of the expected type
    assert isinstance(tiff, TIFF)
    assert isinstance(tiff, BigTIFF)

    assert tiff.filepath == filepath
    assert tiff.filesize == os.path.getsize(filepath)

    assert tiff.order is ByteOrder.LSB
    assert tiff.format is Format.BigTIFF

    # Ensure that the parsed TIFF file contains the expected number of IFDs
    assert len(tiff) == 1

    # Ensure that the parsed metadata contained in the TIFF file is as expected
    assert tiff.imageWidth == 3
    assert tiff.imageLength == 3  # TIFF refers to Image Height as Image Length
    assert tiff.orientation == 1
    assert tiff.samplesPerPixel == 3
    assert tiff.sampleFormat == [1, 1, 1]
    assert tiff.bitsPerSample == [8, 8, 8]
    assert tiff.compression == 1
    assert tiff.photometricInterpretation == 2
    assert tiff.rowsPerStrip == 128
    assert tiff.stripOffsets == 16
    assert tiff.stripByteCounts == 27
    assert tiff.planarConfiguration == 1
    assert tiff.resolutionUnit == 2
    assert int(tiff.yResolution) == 300  # cast the rational number to an integer
    assert int(tiff.xResolution) == 300  # cast the rational number to an integer


def test_tiffdata_library_embedding(path: callable, data: callable):
    """Test loading a file via the TIFF class and embedding a metadata payload."""

    # Use the path fixture to assemble and return the absolute path for the test file
    # The 'empty.tiff' test file is a Classic TIFF, encoded using MSB byte order, with
    # a single IFD, an image canvas of 3x3 pixels, and a resolution of 300, but does
    # not have any other embedded metadata.
    filepath: str = path("empty.tiff")

    # Create an instance of the TIFF class for the file
    tiff = TIFF(filepath)

    # Ensure that the parsed TIFF file is of the expected type
    assert isinstance(tiff, TIFF)

    # Ensure that the parsed TIFF file contains the expected number of IFDs
    assert len(tiff) == 1

    # Obtain the example XMP payload from the payload.xml test file
    xmp: str = data("xmp.xml")

    assert isinstance(xmp, str)

    # Encode the XMP payload to bytes using the UTF-8 character set
    encodedxmp: bytes = xmp.encode("UTF-8")

    assert isinstance(encodedxmp, bytes)

    # The XMP Payload is stored in the XMLPacket tag:
    tiff.xmlPacket = encodedxmp

    # Create a save path for the new TIFF file
    savepath: str = path("embedded.tiff", exists=False)

    # Save the TIFF file to the save file path, overwriting the current file if needed
    tiff.save(filepath=savepath, overwrite=True)

    # Ensure that the new file exists
    assert os.path.exists(savepath)

    # Create an instance of the TIFF class for the newly saved file
    newtiff = TIFF(savepath)

    # Ensure that the TIFF class instance is of the expected type
    assert isinstance(newtiff, TIFF)

    # Ensure that the parsed TIFF file contains the expected number of IFDs
    assert len(newtiff) == 1

    # Ensure that the extracted XMLPacket data matches the encoded XMP payload
    assert isinstance(newtiff.xmlPacket, bytes)
    assert len(newtiff.xmlPacket) == len(encodedxmp)
    assert newtiff.xmlPacket == encodedxmp

    # Ensure that the decoded XMP payload is the same as the original payload
    decoded: str = encodedxmp.decode("UTF-8")
    assert isinstance(decoded, str)
    assert len(decoded) == len(xmp)
    assert decoded == xmp
