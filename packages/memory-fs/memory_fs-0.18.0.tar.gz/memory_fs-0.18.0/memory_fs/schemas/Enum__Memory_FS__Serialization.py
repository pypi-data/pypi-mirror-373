from enum import Enum


class Enum__Memory_FS__Serialization(Enum):
    STRING     = "string"      # Plain text
    JSON       = "json"        # JSON serialization of objects
    BINARY     = "binary"      # Raw bytes
    BASE64     = "base64"      # Base64 encoded
    TYPE_SAFE  = "type_safe"   # Use Type_Safe's json() method