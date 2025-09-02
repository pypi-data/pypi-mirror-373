from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id     import Safe_Id
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Schema__Memory_FS__Path__Handler(Type_Safe):
    name            : Safe_Id
    enabled         : bool = True