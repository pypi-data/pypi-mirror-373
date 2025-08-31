from memory_fs.path_handlers.Path__Handler__Versioned import Path__Handler__Versioned
from memory_fs.path_handlers.Path__Handler__Latest    import Path__Handler__Latest

from memory_fs.Memory_FS import Memory_FS


class Memory_FS__Versioned_Latest(Memory_FS):                                           # Versioned + latest pattern
    handler__latest    : Path__Handler__Latest    = None
    handler__versioned : Path__Handler__Versioned = None

    def __init__(self, storage_fs = None,
                       **kwargs ):                                                      # params for Path__Handler):
        super().__init__(storage_fs=storage_fs)
        self.handler__latest    = self.add_handler__versioned(**kwargs)
        self.handler__versioned = self.add_handler__latest   (**kwargs)