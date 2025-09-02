from typing                                                         import List
from memory_fs.path_handlers.Path__Handler__Temporal                import Path__Handler__Temporal
from memory_fs.path_handlers.Path__Handler__Latest                  import Path__Handler__Latest
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id  import Safe_Id
from memory_fs.Memory_FS                                            import Memory_FS


class Memory_FS__Latest_Temporal(Memory_FS):                                                # Latest + temporal pattern

    handler__latest   : Path__Handler__Latest    = None
    handler__temporal : Path__Handler__Temporal = None

    def __init__(self, storage_fs = None         ,
                       areas      : List[Safe_Id] = None,
                       **kwargs):                                                           # params for Path__Handler
        super().__init__(storage_fs=storage_fs)
        self.handler__latest   = self.add_handler__latest  (**kwargs             )
        self.handler__temporal = self.add_handler__temporal(areas=areas, **kwargs)