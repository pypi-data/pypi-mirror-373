from memory_fs.schemas.Enum__Memory_FS__File__Content_Type import Enum__Memory_FS__File__Content_Type
from memory_fs.schemas.Enum__Memory_FS__File__Encoding     import Enum__Memory_FS__File__Encoding
from memory_fs.schemas.Enum__Memory_FS__Serialization      import Enum__Memory_FS__Serialization
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                           import Safe_Id
from osbot_utils.type_safe.Type_Safe                       import Type_Safe


class Schema__Memory_FS__File__Type(Type_Safe):
    name           : Safe_Id                             = None # Logical name: "json", "jpeg", "markdown"
    content_type   : Enum__Memory_FS__File__Content_Type = None # Validated HTTP content type
    file_extension : Safe_Id                             = None # Primary extension: "jpg", "md", "yml"
    encoding       : Enum__Memory_FS__File__Encoding     = None
    serialization  : Enum__Memory_FS__Serialization      = None