from memory_fs.schemas.Enum__Memory_FS__File__Content_Type import Enum__Memory_FS__File__Content_Type
from memory_fs.schemas.Enum__Memory_FS__File__Encoding     import Enum__Memory_FS__File__Encoding
from memory_fs.schemas.Enum__Memory_FS__Serialization      import Enum__Memory_FS__Serialization
from memory_fs.schemas.Schema__Memory_FS__File__Type       import Schema__Memory_FS__File__Type
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                           import Safe_Id


class Memory_FS__File__Type__Jpeg(Schema__Memory_FS__File__Type):
    name           = Safe_Id("jpeg")
    content_type   = Enum__Memory_FS__File__Content_Type.JPEG
    file_extension = Safe_Id("jpg")
    alt_extensions = [Safe_Id("jpeg")]
    encoding       = Enum__Memory_FS__File__Encoding.BINARY
    serialization  = Enum__Memory_FS__Serialization.BINARY