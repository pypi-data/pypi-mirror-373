from memory_fs.path_handlers.Path__Handler__Latest import Path__Handler__Latest
from memory_fs.Memory_FS                           import Memory_FS

class Memory_FS__Latest(Memory_FS):                                                     # Latest-only pattern
    handler__latest : Path__Handler__Latest = None

    def __init__(self, storage_fs = None,
                       **kwargs ):                                                      # params for Path__Handler
        super().__init__(storage_fs=storage_fs)
        self.handler__latest = self.add_handler__latest(**kwargs)                       # add_handler__latest and keep reference for later use

