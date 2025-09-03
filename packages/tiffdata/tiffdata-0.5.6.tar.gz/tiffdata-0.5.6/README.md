# TIFFData

The TIFFData library for Python provides a streamlined way to work with TIFF image files
offering the ability to extract and modify metadata and tags without modifying any the
of image data held within the file itself.

The library can be used to support a range of use cases, including situations where it
is important to be able to read, modify and write TIFF image metadata without affecting
the visual quality and fidelity of any image canvases held within the file. This is
especially important in cases where a TIFF file holds one or more image canvases encoded
using a lossy compression algorithm such as JPEG encoding. Loading, modifying and
resaving such files using libraries which also load and decompress image canvas data
before recompressing and resaving the file will result in a reduction in image quality
and fidelity during each load-and-save cycle.

The TIFFData library does not provide any image canvas transformation capabilities, such
as resizing or rotation. For cases where one needs to perform such image transformation
operations, other libraries such as PyVIPS and Pillow are recommended. However, for use
cases related specifically to TIFF metadata and TIFF tag manipulation, the TIFFData
library offers many unique features. One can also develop workflows which leverage
functionality from libraries such as PyVIPS and Pillow, in combination with the metadata
inspection and modification capabilities offered by the TIFFData library.

### Requirements

The TIFFData library has been tested to work with Python 3.10, 3.11, 3.12 and 3.13, but
has not been tested, nor is its use supported with earlier versions of Python.

### Installation

The library is available from the PyPI repository, so may be added easily to a project's
dependencies via its `requirements.txt` file or similar by referencing the library's
name, `tiffdata`, or the library may be installed directly onto your local development
system using `pip install` by entering the following command:

	$ pip install tiffdata

### Introduction

The TIFFData library provides access to the embedded metadata within TIFF files as well
as the ability to modify certain metadata values within the file. The library does not
provide support for modifying image canvas data held within the file, and some metadata
fields are considered read-only as they are essential to describing the content of the
image data held in the file, and any modifications to those fields could affect the
ability of software, including the TIFFData library, to successfully load the image.

The TIFFData library supports Standard/Classic TIFF files, as well as Big TIFF files,
encoded using both big and little endian byte orders.

### TIFF File Format

The TIFF (Tagged Image File Format) is a flexible, adaptable image file format that is
widely used for storing high-quality raster (bitmapped) graphics. The file format was
originally developed by Aldus Corporation in the mid-1980s for desktop publishing and
scanning applications. Aldus was acquired by Adobe in 1994, and Adobe has continued to
lead development of the TIFF file format in the years since. The current version of the
TIFF specification, version 6.0, was released in 1992, and was supplemented in 2002, so
the format is considered stable and offers many features that help support long term use
and flexibility for a range of use cases, such as support for custom metadata tags and
the ability to add support for additional image compression algorithms as needs arise.

#### Key Features:

* Lossless Compression: The TIFF format supports lossless compression options, including
the LZW, ZIP, Deflate, and PackBits algorithms, as well as raw uncompressed data, which
preserves full image quality without any loss, as well as several lossy compression options
including JPEG compression.

* Multiple Images: The TIFF format can be used to store multiple images within a single
file, which is useful for multiple-page documents, such as scanned documents, as well as
cases where storing multiple resolutions of the same image in a pyramidal arrangement is
used to support dynamic image derivative generation and viewing.

* Metadata: Uses a system of tags (hence the format name) to describe image attributes,
such as width, height, resolution, colour depth, and many properties besides, as well as
providing support for embedding metadata payloads of other formats such as IPTC and XMP
into the file, which are also recorded using tags.

* Colour Support: The TIFF format can handle various colour spaces, including:

  * Black & White (1-bit)
  * Grayscale
  * Indexed colour (palette-based)
  * RGB
  * CMYK
  * YCbCr (used in video and photography)

* Bit Depths: Supports a range of bit depths – 1, 4, 8, 16, 24 or 32 bits per channel.

* Extensibility: Allows for custom tags and metadata, making it a highly extensible file
format for specialised applications, such as medical imaging and geospatial data.

#### Common Use Cases:

* Scanning and archiving (due to high image fidelity and lossless storage options).

* Publishing and printing.

* Medical imaging, for example, the DICOM image file format uses the TIFF format internally.

* Geographic Information Systems (GIS), often in the form of GeoTIFF, which is based on the TIFF file format.

#### File Extensions:

 * The most common file extensions for TIFF files are `.tif` and `.tiff` – however, to
 identify TIFF files with certainty it is best to parse the contents of the files to
 ensure the expected TIFF magic number and other required file contents are present.

#### Format Variants:

* Baseline TIFF: A minimal standard that all TIFF readers must support.

* TIFF/EP: Enhanced version used in digital photography as the basis for most camera RAW
 image file formats.

* BigTIFF: Supports files larger than 4 GB by using 64-bit offsets.

TIFF is favoured where image quality and flexibility are paramount. However, due to often
large file sizes and limited browser support, TIFFs are not ideal for everyday web use.

### TIFF File Structure

TIFF files can contain one or more images, and are typically structured as illustrated
below, beginning with the TIFF file header which details the byte order used to encode
data structures within the file, followed by the file format specifier and the offset to
the first (known as the _zeroth_ or 0th) Image File Directory (IFD). Each IFD contains a
number of Tags and each tag contains data about or relating to the image within the IFD.

The Tags contain a tag ID, which identifies the type of tag, a data type specifier that
specifies the way that the data held within the tag is encoded, as well as a data count
which notes how many values the tag holds, followed by the data itself. As a Tag holds a
limited amount of data, four bytes for Standard/Classic TIFF files, and eight bytes for
Big TIFF files, the data field of a Tag may hold the actual data (if it will fit) or the
offset to the Tag's data that has been stored elsewhere in the file.

Some of the tags are essential to the IFD, and include information such as the offset of
the image data within the IFD, the compression format used, the pixel dimensions and the
resolution of the image, and much more besides. The values of these tags are considered
read-only as if changes were made to the data values of these tags without corresponding
changes to the associated image canvas data could affect the ability of software to read
the TIFF file after it was resaved.

Most IFDs carry metadata and image data, while others carry only metadata. Within a TIFF
file, at least one of the IFDs should carry image data, while there may be other IFDs
such as an EXIF IFD or GPS IFD that contain additional image related metadata. While the
"Next IFD Offset" field within an IFD is the main way that subsequent IFDs are specified,
certain tags are also used to specify the offsets of other IFDs, effectively supporting
a hierarchical structure of IFDs and tags. The offsets to any EXIF and GPS IFDs within
the file are specified in this way.

```
   ┌──────────────────────────────────────────────────────────────────────────────────┐
   │   TIFF File Header (contains byte order, file format, and first IFD offset)      |
   └──┬───────────────────────────────────────────────────────────────────────────────┘
   ┌──▼───────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
   │ Image File Directory │  ┌──▶│ Image File Directory │  ┌──▶│ Image File Directory │
   └──┬───────────────────┘  │   └──┬───────────────────┘  │   └──┬───────────────────┘
┌─────┤  ┌────────────────┐  │      │  ┌────────────────┐  │      │  ┌────────────────┐
│     ├──▶  Tag           │  │      ├──▶  Tag           │  │      ├──▶  Tag           │
│     │  └────────────────┘  │      │  └────────────────┘  │┌─────┤  └────────────────┘
│     │  ┌────────────────┐  │      │  ┌────────────────┐  ││     │  ┌────────────────┐
│     ├──▶  Tag           │  │      ├──▶  Tag           │  ││     ├──▶  Tag           │
│     │  └────────────────┘  │┌─────┤  └────────────────┘  ││     │  └────────────────┘
│     │  ┌────────────────┐  ││     │  ┌────────────────┐  ││     │  ┌────────────────┐
│     ├──▶  Tag           │  ││     ├──▶  Tag           │  ││     ├──▶  Tag           │
│     │  └────────────────┘  ││     │  └────────────────┘  ││     │  └────────────────┘
│  ┌──▼───────────────────┐  ││  ┌──▼───────────────────┐  ││  ┌──▼───────────────────┐
│  │ Next IFD Offset      │──┘│  │ Next IFD Offset      │──┘│  │ Zero Next IFD Offset │
│  └──────────────────────┘   │  └──────────────────────┘   │  └──────────────────────┘
│  ┌──────────────────────┐   │  ┌──────────────────────┐   │  ┌──────────────────────┐
└─▶│ Image Data           │   └─▶│ Image Data ‡         │   └─▶│ Image Data ‡         │
   └──────────────────────┘      └──────────────────────┘      └──────────────────────┘
```

‡ As noted above, some IFDs within a TIFF file will only contain metadata tags, so image
data may not be present for every IFD.

#### Header Structure

The header for a valid Classic TIFF file will consist of the following elements:

| Element          | Description                                                      |
|:-----------------|:-----------------------------------------------------------------|
| Byte Order Mark  | The byte order mark notes the byte order that the TIFF file uses |
| Format Marker    | The format marker notes the file format used by the TIFF file    |
| First IFD Offset | The first IFD offset contains the offset to the first IFD        |

 * The byte order mark always occupies the first two bytes of a valid TIFF file and will
 contain either `MM` to denote the file is encoded using big-endian (Motorola) encoding
 or `II` to denote the file is encoded using little-endian (Intel) encoding. The byte
 order mark is always encoded within two single byte ASCII characters.

 * The format marker always occupies the next two bytes of a valid TIFF file and will
 contain either the value `42` for Classic TIFF files or `43` for Big TIFF files. The
 format marker value is encoded using an unsigned 16-bit integer, following the byte
 order established by the byte order marker field. The format marker is always encoded
 as an unsigned 16-bit integer, in both Classic and Big TIFF file formats.
 
 * The first IFD offset notes the absolute offset from the start of the file that the
 first IFD may be found. In a Classic TIFF file, the offset is encoded in an unsigned
 32-bit integer, following the byte order established by the byte order marker field.

The header for a valid Big TIFF file will consist of the following elements:

| Element          | Description                                                      |
|:-----------------|:-----------------------------------------------------------------|
| Byte Order Mark  | The byte order mark notes the byte order that the TIFF file uses |
| Format Marker    | The format marker notes the file format used by the TIFF file    |
| Offset Size      | The offset size notes how many bytes the offset field uses       |
| Reserved         | The reserved field is reserved for future use                    |
| First IFD Offset | The first IFD offset contains the offset to the first IFD        |

 * The byte order mark always occupies the first two bytes of a valid TIFF file and will
 contain either `MM` to denote the file is encoded using big-endian (Motorola) encoding
 or `II` to denote the file is encoded using little-endian (Intel) encoding. The byte
 order mark is always encoded within two single byte ASCII characters.

 * The format marker always occupies the next two bytes of a valid TIFF file and will
 contain either the value `42` for Classic TIFF files or `43` for Big TIFF files. The
 format marker value is encoded using an unsigned 16-bit integer, following the byte
 order established by the byte order marker field. The format marker is always encoded
 as an unsigned 16-bit integer, in both Classic and Big TIFF file formats.

 * The offset size notes how many bytes the first IFD offset field occupies; its value
 is encoded in an unsigned 16-bit integer, and for Big TIFF files, the value is always
 `8`, following the byte order established by the byte order marker field, while
 offering a path to support even larger TIFF files in the future such as files that
 could encode their offsets using 16 bytes (128-bits).

 * The reserved field occupies an unsigned 16-bit integer, and for Big TIFF files, the
 value is always `0`, following the byte order established by the byte order marker
 field, but may be used for other purposes for future variants of TIFF.

 * The first IFD offset notes the absolute offset from the start of the file that the
 first IFD may be found. In a Big TIFF file, the offset is encoded in an unsigned
 64-bit integer, following the byte order established by the byte order marker field.

#### IFD Structure

IFD0 is always the first IFD in a TIFF file and contains the main image data, including
resolution, colour space, and other essential image attributes. It can also store EXIF
metadata like camera settings, date, and time, via its associated EXIF IFD.

IFD1 is often used to store information about a thumbnail image, which is a smaller
version of the main image, and is included to support faster previews. All tags from
IFD0 may also be present in IFD1.

IFD2 and onwards, while less common, may exist to store additional image data or
information about related images, such as linked images or other image formats. Within
multi-page TIFFs the additional IFDs will store the additional page images, and within
pyramidal TIFFs the additional IFDs will store additional resolutions of the main image.

All IFDs comprise the following components:

| Element          | Description                                                     |
|:-----------------|:----------------------------------------------------------------|
| Tag&nbsp;Count   | Two bytes holding the count of tags that follow.                |
| Tags             | One or more byte-encoded IFD Tag values, the length of which can be determined by multiplying the tag count by 12 bytes for Standard/Classic TIFF files, and by 20 bytes for Big TIFF files.           |
| Next&nbsp;Offset | Four or eight bytes holding the pointer to the next IFD or zero if no further IFD follows, depending on the file format; four bytes for Standard/Classic TIFFs and eight bytes for Big TIFF files. |

 * The tag count is always stored as a short integer (`UInt16`) comprised of 2 bytes or 16 bits.

 * The tags are encoded according to the format specified for an IFD Tag as noted below.

 * The next IFD offset is stored as a long integer (`UInt32`) comprised of 4 bytes or 32 bits
 in Standard/Classic TIFF files, or as a long long integer (`UInt64`) comprised of 8 bytes for Big TIFF files.

#### Tag Structure

An IFD Tag comprises of the following elements, consisting of 12 bytes within Standard/Classic TIFF files and 20 bytes in Big TIFF files:

| Element          | Description                                                      |
|:-----------------|:-----------------------------------------------------------------|
| Tag ID           | Two bytes holding the tag ID                                     |
| Data Type        | Two bytes holding the data type indicator (listed below)         |
| Data Count       | Four or eight bytes holding the count of values that follow      |
| Data / Offset    | Four or eight bytes holding the data or an offset to the data    |

 * The tag ID is used to identify the purpose of the tag, and its value is always
 encoded as an unsigned 16-bit integer (`UInt16`) regardless of the TIFF file format.

 * The data type field of each tag will have one of the following values, encoded using
 an unsigned 16-bit integer (`UInt16`), regardless of the TIFF file format.

 * The data count field of each tag is used to note how many values of the given type are
 held by the tag, and its value is encoded using an unsigned 32-bit integer (`UInt32`)
 for Classic TIFF files and an unsigned 64-bit integer (`UInt64`) for Big TIFF files.
 
 * The data / offset field of each tag is used to hold the data of the tag, if the data
 can fit within the available number of bytes (four bytes for Classic TIFF and eight for
 Big TIFF files) or if the data exceeds this length, then the offset to the data will be
 held in the tag instead, and the data will be stored outside of an IFD or Tag elsewhere
 in the file.

#### Tag Data Types

The data type field of each tag will have one of the following values, encoded using an
unsigned 16-bit integer, regardless of the TIFF file format:

| Data Type ID | Type       | Description                                             |
|:-------------|:-----------|:--------------------------------------------------------|
| 0            | Empty      | An empty padded tag data value                          |
| 1            | Byte       | A 8-bit unsigned byte integer                           |
| 2            | ASCII      | A 8-bit holding 7-bit ASCII code, nul-terminated        |
| 3            | Short      | A 16-bit unsigned short integer                         |
| 4            | Long       | A 32-bit unsigned long integer                          |
| 5            | Rational   | Two unsigned longs; holding numerator and denominator   |
| 6            | SByte      | An 8-bit signed byte integer                            |
| 7            | Undefined  | A 8-bit byte holding any value per field specs          |
| 8            | SShort     | A 16-bit signed short integer                           |
| 9            | SLong      | A 32-bit signed integer (2's compliment)                |
| 10           | SRational  | A signed rational of two signed-longs                   |
| 11           | Float      | A signed 32-bit float (IEEE-754 single-precision)       |
| 12           | Double     | A signed 64-bit float (IEEE-754 double-precision)       |
| 13           | ClassicIFD | A 32-bit unsigned integer for sub IFD offset            |
| 16           | LongLong   | A 64-bit unsigned long long integer                     |
| 17           | SLongLong  | A 64-bit signed long long integer                       |
| 18           | BigIFD     | A 64-bit unsigned integer for sub IFD offset            |
| 129          | UTF-8      | An 8-bit byte UTF-8 string, nul-terminated              |

### Classes, Methods & Properties

The TIFFData library's main class is the `TIFF` class through which TIFF image files can
be loaded, modified via the supported actions, and saved. The library supports reading
both Classic TIFF and Big TIFF formatted files, in both big and little endianness.

The `TIFF` class offers the following methods:

* `TIFF(filepath: str)` – The `TIFF()` class constructor expects an absolute filepath at
a minimum for the TIFF file you wish to open. Upon initialising the class with the file,
the library will then attempt to load and parse the file. Assuming that the file is a 
valid TIFF file, the library will parse the file, identify any IFDs contained within the
file, and any tags associated with each of the IFDs, including any embedded metadata and
any image data, stored either as image strips or image tiles.

* `get(key: int | str, default: object = None)` (`object`) – The `get()` method can be
used to obtain the TIFF tag identified by the provided `key`, which can be provided as a
tag ID, tag name or `TIFFTag` enumeration option. A `default` value can also be provided
to use as a fallback. If the TIFF does not contain the specified tag, the default will
be returned instead. If tag does not exist and no `default` has been set, `None` will be
returned. ‡

* `set(key: int | str, value: object)` – The `set()` method can be used to set the value
of supported and writable TIFF tags. The tag is identified by the provided `key`, which
can be provided as a tag ID, tag name or `TIFFTag` enumeration option, and the provided
value must use a data type supported by the tag being set. The `set()` method returns a
reference to the `TIFF` class instance's `self` property, so that calls to `set()` can
be chained with calls to other `TIFF` class methods. ‡

* `remove(key: int | str)` (`bool`) – The `remove()` method can be used to remove tags
from the TIFF that support removal; certain tags are intrinsic to the TIFF, so cannot be
removed, as if they were absent, many applications would be unable to read the TIFF file.
The tag is identified by the provided `key` argument, which can be provided as a tag ID,
tag name or tag enumeration option. The `remove()` method returns `True` if the tag was
removed, and returns `False` if the tag does not exist or could not be removed. ‡

  ‡ By default the `get()`, `set()` and `remove()` methods will search for the specified
tag in the first (0th) IFD. This can be overridden by passing the optional `ifd` keyword
argument to the method and specifying a different IFD index, such as `1`, `2`, etc.,
according to the number of IFDs that are available in the file (the number of IFDs can
be determined via `len(tiff)` where `tiff` is an instance of the `TIFF` class).

  Alternatively, the `ifd` argument supports `True` and `False` values which result in
the following behaviours:
  * When `ifd` is set to `True`, calls to the `get()`, `set()` and `remove()` methods
  will consider all of the IFDs in the file:
     * When the `get()` method is called, all of the IFDs in the file will be searched
     for the specified tag, and upon encountering the first instance of the matching tag
     in any of the IFDs, that first tag's value will be returned. If no match is found,
     the `default` value will be returned instead.
     * When the `set()` method is called, the tag will be added/updated on all of the
     IFDs in the file.
     * When the `remove()` method is called, all IFDs will be searched for the specified
     tag, and it will be removed from all of the IFDs on which it is found.
  * When `ifd` is set to `False`, calls to the `get()`, `set()` and `remove()` methods
  will also consider all of the IFDs in the file, but with several behavioural differences:
     * When the `get()` method is called, the first IFD will be searched for the specified
    tag, and if found, its value will be returned, otherwise the `default` value will be
    returned instead. This behaviour is the same as the default behaviour for the `get()`
    method where `ifd` has a default value of `0` to match the first (0th) IFD only.
     * When the `set()` method is called, the specified tag and its associated value will
    be added/updated to the first (0th) IFD only, however, if the tag is present on any
    other IFDs in the file, it will be removed from all of the later IFDs.
     * When the `remove()` method is called, the specified tag will be removed only from
    the first (0th) IFD, and will be left unmodified on any subsequent IFDs in which it
    appears. This behaviour is the same as the default behaviour for the `remove()`
    method where `ifd` has a default value of `0` to match the first (0th) IFD only.

* `save(filepath: str = None, order: ByteOrder = None, format: Format = None)` – The
`save()` method supports saving the TIFF file back to storage after making any desired
changes to the TIFF. The `filepath` argument can be used to specify a destination path
to save the file to; if no `filepath` has been specified and if the optional `overwrite`
boolean argument has been set to `True`, the library will attempt to save the TIFF file
at the file path that it was loaded from, overwriting the original file.

  The `save()` method accepts an optional `order` argument that can be used to change the
the byte order of the saved file. Note that this option should be used with caution if
the TIFF file contains embedded data stored in unrecognised tags or custom data payloads
which the library may not be able to understand, as changing the byte order may affect
the ability to read data from those tags from the saved file for software that supports
parsing the custom data from such tags.

  The `save()` method accepts an optional `format` argument that can be used to change
the file format of the saved file, for example through loading a Classic TIFF formatted
file and saving it to a Big TIFF formatted file.

  The `save()` method accepts an optional `status` argument that can be used to enable
 save status progress reporting while the save is being performed. The status will be
 printed to the command line while the save is running, allowing progress to be monitored
 and for the save duration to be captured. The length of time needed to save a TIFF file
 depends on the complexity of the source TIFF file and its size, as well as what changes
 if any were made to the TIFF via the library after it was loaded.

  The `save()` method accepts an optional `buffer` (`int`) argument that can be used
 to control the size of the file read/write buffer used during file saves; the buffer is
 used to copy data from the source file to the destination file in blocks, and defaults
 to 16KB; it may be adjusted to a size between 1KB (1024 bytes) and 64KB (65,536 bytes);
 a larger buffer isn't necessarily better, with the optimal buffer size depending on the
 average size of the files being written and the runtime environment; the 16KB default
 should work well for most scenarios; to prevent buffered block reading and writing, set
 the `buffer` argument to `0`, which will result in the file save process allocating
 sufficient memory to read and write the full amount of data to be copied in a single
 operation. While this latter option requires less I/O method calls, the throughput can
 often be slower than performing a buffered block read and write, due to the amount of
 memory that needs to be allocated and used to copy potentially very large blocks from
 the source to the destination file.

  Save status progress reporting, if enabled, will look similar to the following:

 ```
 > Saving TIFF file to /path/to/file.tiff
 > Saving element 1515/1515 • 100.00% • 352100585/352100585 bytes • 5.880 seconds
 > Saving complete • 0.881 seconds
 ```

The `TIFF` class offers the following properties:

 * `info` (`Information`) – The `info` property can be used to access the `Information`
 class instance that is created when the `TIFF` class instance is created and the file is
 parsed. The `Information` class instance contains core information about the parsed file
 including the `filepath`, `filesize`, (byte) `order`, `format`, and first IFD offset.
 
  This property is used internally by the class to populate the corresponding top level
 properties of the same names noted below.

 * `filepath` (`str`) – The `filepath` property can be used to get the original file path
 that was specified at the time the class was initialised.

 * `filesize` (`int`) – The `filesize` property can be used to get the original file size
 of the file that was specified at the time the class was initialised.

 * `order` (`ByteOrder`) – The `order` property can be used to determine the byte order
 of the TIFF file. The property will report either `ByteOrder.MSB` for big endian files
 or `ByteOrder.LSB` for little endian files.

 * `format` (`Format`) – The `format` property can be used to determine the file format
 of the TIFF file. The property will report either `Format.ClassicTIFF` for Classic TIFF
 formatted files, or `Format.BigTIFF` for Big TIFF formatted files.

### Example of Use

To create an instance of the `TIFF` class, import the `TIFF` class from the library and
specify the absolute file path to the TIFF file you wish to open as the first argument.
If the specified file can be opened successfully, the library will return an instance of
either the `ClassicTIFF` or the `BigTIFF` subclass, depending on the file format of the
specified TIFF file; these classes are subclasses of the library's `TIFF` base class.

<!--pytest.mark.skip-->

```python
from tiffdata import TIFF

filepath = "/path/to/file.tiff"

# Initialise the library with the absolute file path of the TIFF file to load
tiff = TIFF(filepath=filepath)

# If desired, iterate through the IFDs held within the file, accessing the tags of each
for ifd in tiff:
    print(ifd)
    for tag in ifd:
        print(tag.id, tag.name, tag.values)

# Get the value of a specified TIFF tag
value = tiff.get(key=...)

# Set the value of a specified TIFF tag
tiff.set(key=..., value=...)

# Save the modified TIFF file back to the original file path, overwriting the original;
# alternatively provide a different file path for saving via the the `filepath` argument
tiff.save(overwrite=True)
```

In addition to the `get()` and `set()` methods, the `TIFF` class also provides access to
tag values on the first matching IFD via the attribute access pattern:

<!--pytest.mark.skip-->

```python
from tiffdata import TIFF

filepath = "/path/to/file.tiff"

# Initialise the library with the absolute file path of the TIFF file to load
tiff = TIFF(filepath=filepath)

print(tiff.imageWidth)
print(tiff.imageLength)
```

### Disclaimer

While every effort has been made to ensure that the library works reliably with TIFF
files and embedded metadata, you must ensure that all files are backed up before using
the TIFFData library with any files, especially as the library is in early development.

Furthermore, the library may not be able to read nor preserve all metadata or other data
within a TIFF file, especially if manufacturer specific, custom tags, or other "private"
data are present. As such, it is possible that loss of data could occur if an image is
loaded and is then overwritten by saving the file back to the same file path.

Use of the library is entirely at your own risk and the authors bear no responsibility
for losses of any kind. By using the software you assume all such risk and liability.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

### Credits & References

The TIFF file format, and the related EXIF, IPTC and XMP metadata model specifications
were researched across various sources. Please visit these valuable online resources to
learn more about the TIFF file format and related metadata model specifications and to
support these world class organisations and their products:

 * TIFF File Format
   * https://www.loc.gov/preservation/digital/formats/fdd/fdd000022.shtml (TIFF)
   * https://www.loc.gov/preservation/digital/formats/fdd/fdd000328.shtml (Big TIFF)
   * https://libtiff.gitlab.io/libtiff/specification/bigtiff.html (Big TIFF)
   * https://en.wikipedia.org/wiki/TIFF (TIFF)
   * https://www.fileformat.info/format/tiff/egff.htm (TIFF and Big TIFF)
   * https://www.itu.int/itudoc/itu-t/com16/tiff-fx/docs/tiff6.pdf (TIFF Specification)
   * https://github.com/DigitalSlideArchive/tifftools (TIFF Tags)

 * EXIF Metadata Model & Fields
   * https://www.cipa.jp/e/index.html
   * https://www.loc.gov/preservation/digital/formats/fdd/fdd000146.shtml
   * https://exiftool.org/TagNames/EXIF.html
   * https://www.media.mit.edu/pia/Research/deepview/exif.html
   * https://exiv2.org/tags.html

 * IPTC Metadata Model & Fields
   * https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata
   * https://exiftool.org/TagNames/IPTC.html

 * XMP Metadata Model & Fields
   * https://www.adobe.com/products/xmp.html
   * https://exiftool.org/TagNames/XMP.html

### Copyright & License Information

Copyright © 2025 Daniel Sissman; licensed under the MIT License.