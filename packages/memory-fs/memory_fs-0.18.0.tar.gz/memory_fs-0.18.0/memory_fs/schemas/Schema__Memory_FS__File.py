from osbot_utils.type_safe.Type_Safe                     import Type_Safe
from memory_fs.schemas.Schema__Memory_FS__File__Config   import Schema__Memory_FS__File__Config
from memory_fs.schemas.Schema__Memory_FS__File__Metadata import Schema__Memory_FS__File__Metadata


class Schema__Memory_FS__File(Type_Safe):       # todo: see if we still need this schema file, since we are going to have two files created
    config   : Schema__Memory_FS__File__Config
    metadata : Schema__Memory_FS__File__Metadata