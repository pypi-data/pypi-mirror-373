from typing                                                     import List
from memory_fs.schemas.Enum__Memory_FS__File__Exists_Strategy   import Enum__Memory_FS__File__Exists_Strategy
from osbot_utils.utils.Misc                                     import random_id_short
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path          import Safe_Str__File__Path
from memory_fs.schemas.Schema__Memory_FS__File__Type            import Schema__Memory_FS__File__Type
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                                import Safe_Id
from osbot_utils.type_safe.Type_Safe                            import Type_Safe

class Schema__Memory_FS__File__Config(Type_Safe):
    file_id          : Safe_Id
    file_paths       : List[Safe_Str__File__Path]
    file_type        : Schema__Memory_FS__File__Type
    exists_strategy  : Enum__Memory_FS__File__Exists_Strategy = Enum__Memory_FS__File__Exists_Strategy.FIRST

    def __init__(self, **kwargs):
        if 'file_id' not in kwargs:                                     # if a file_id value has not been provider
            self.file_id = Safe_Id(random_id_short('file-id'))          # assign a random value (with a 'file-id' prefix). Note: we can't add this to the type definition , but that doesn't work since it needs to be different every time it is invoked
        super().__init__(**kwargs)
