from typing                                                                     import List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path


class Storage_FS(Type_Safe):

    def clear        (self                                         ) -> bool                      : return False         # not all FS should implement this, since this is literally a delete all method
    def file__bytes  (self, path: Safe_Str__File__Path             ) -> bytes                     : return None
    def file__delete (self, path: Safe_Str__File__Path             ) -> bool                      : return False
    def file__exists (self, path: Safe_Str__File__Path             ) -> bool                      : return False
    def file__json   (self, path: Safe_Str__File__Path             ) -> dict                      : return None
    def file__save   (self, path: Safe_Str__File__Path, data: bytes) -> bool                      : return False
    def file__str    (self, path: Safe_Str__File__Path             ) -> str                       : return None

    def files__paths (self                                         ) -> List[Safe_Str__File__Path]: return []        # not all FS should implement this, since this is literally a list of all files in storage
