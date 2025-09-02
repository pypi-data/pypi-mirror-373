from enum import Enum


class Enum__Memory_FS__File__Encoding(Enum):
    UTF_8        = "utf-8"
    UTF_16       = "utf-16"
    UTF_16_BE    = "utf-16-be"
    UTF_16_LE    = "utf-16-le"
    UTF_32       = "utf-32"
    ASCII        = "ascii"
    LATIN_1      = "latin-1"        # ISO-8859-1
    WINDOWS_1252 = "windows-1252"   # Common Windows encoding
    BINARY       = None             # No encoding for binary files