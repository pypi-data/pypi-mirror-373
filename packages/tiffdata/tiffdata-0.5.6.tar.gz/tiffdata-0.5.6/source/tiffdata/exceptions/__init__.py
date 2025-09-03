class TIFFDataError(RuntimeError):
    pass


class TIFFDataFileError(TIFFDataError):
    pass


class TIFFDataFileFormatError(TIFFDataFileError):
    pass


class TIFFDataReadError(TIFFDataError):
    pass


class TIFFDataParseError(TIFFDataError):
    pass


class TIFFDataWriteError(TIFFDataError):
    pass
