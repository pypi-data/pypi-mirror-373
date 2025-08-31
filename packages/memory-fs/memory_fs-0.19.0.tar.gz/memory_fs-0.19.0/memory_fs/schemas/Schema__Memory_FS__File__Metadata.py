from typing import Optional, Set, Dict, Any
from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now                        import Timestamp_Now
from osbot_utils.type_safe.primitives.safe_str.cryptography.hashes.Safe_Str__Hash   import Safe_Str__Hash
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                  import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path      import Safe_Str__File__Path
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt__FileSize                 import Safe_UInt__FileSize

class Schema__Memory_FS__File__Metadata(Type_Safe):
    content__hash        : Safe_Str__Hash                        = None
    content__size        : Safe_UInt__FileSize
    chain_hash           : Optional[Safe_Str__Hash]              = None
    previous_version_path: Optional[Safe_Str__File__Path]        = None         # todo: refactor this logic into a better naming convention and class structure
    tags                 : Set[Safe_Id]                                         # todo: should we move this into an 'user_data' section (since this is the only part of this data object that us editable by the user
    timestamp            : Timestamp_Now
    data                 : Dict[Safe_Id, Any]                                   # this is the area to store extra data about the file
