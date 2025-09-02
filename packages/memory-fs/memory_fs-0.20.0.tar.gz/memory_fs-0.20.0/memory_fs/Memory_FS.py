from typing                                                                     import List, Type, Optional
from memory_fs.file_types.Memory_FS__File__Type__Binary                         import Memory_FS__File__Type__Binary
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id              import Safe_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from memory_fs.file_fs.File_FS                                                  import File_FS
from memory_fs.storage_fs.Storage_FS                                            import Storage_FS
from memory_fs.storage_fs.providers.Storage_FS__Memory                          import Storage_FS__Memory
from memory_fs.storage_fs.providers.Storage_FS__Local_Disk                      import Storage_FS__Local_Disk
from memory_fs.storage_fs.providers.Storage_FS__Sqlite                          import Storage_FS__Sqlite
from memory_fs.storage_fs.providers.Storage_FS__Zip                             import Storage_FS__Zip
from memory_fs.path_handlers.Path__Handler                                      import Path__Handler
from memory_fs.path_handlers.Path__Handler__Latest                              import Path__Handler__Latest
from memory_fs.path_handlers.Path__Handler__Temporal                            import Path__Handler__Temporal
from memory_fs.path_handlers.Path__Handler__Versioned                           import Path__Handler__Versioned
from memory_fs.path_handlers.Path__Handler__Custom                              import Path__Handler__Custom
from memory_fs.schemas.Schema__Memory_FS__File__Config                          import Schema__Memory_FS__File__Config
from memory_fs.schemas.Schema__Memory_FS__File__Type                            import Schema__Memory_FS__File__Type
from memory_fs.file_types.Memory_FS__File__Type__Json                           import Memory_FS__File__Type__Json
from memory_fs.file_types.Memory_FS__File__Type__Text                           import Memory_FS__File__Type__Text
from memory_fs.file_types.Memory_FS__File__Type__Data                           import Memory_FS__File__Type__Data


class Memory_FS(Type_Safe):
    storage_fs    : Storage_FS          = None
    path_handlers : List[Path__Handler]

    def __init__(self, storage_fs : Storage_FS = None):
        super().__init__()
        if storage_fs:
            self.storage_fs = storage_fs

    # Storage addition methods
    @type_safe
    def set_storage(self, storage_fs: Storage_FS
                     ) -> Storage_FS:
        self.storage_fs = storage_fs
        return self.storage_fs

    def set_storage__memory(self) -> Storage_FS__Memory:                                            # Use in-memory storage
        storage_fs__memory = Storage_FS__Memory()
        return self.set_storage(storage_fs__memory)

    def set_storage__local_disk(self, root_path : Safe_Str__File__Path
                                 ) -> Storage_FS__Local_Disk:                                      # Use local filesystem storage
        storage_fs__local_disk = Storage_FS__Local_Disk(root_path=root_path)
        return self.set_storage(storage_fs__local_disk)

    def set_storage__sqlite(self, db_path   : Safe_Str__File__Path = None ,                         # Use SQLite storage
                                  in_memory : bool                 = True                           # Default to in-memory database
                             ) -> Storage_FS__Sqlite:
        storage_fs__sqlite = Storage_FS__Sqlite(db_path=db_path, in_memory=in_memory).setup()
        return self.set_storage(storage_fs__sqlite)

    def set_storage__zip(self, zip_path  : Safe_Str__File__Path = None ,                  # Use ZIP file storage
                               in_memory : bool                 = True                    # Default to in-memory ZIP
                          ) -> Storage_FS__Zip:
        storage_fs_zip = Storage_FS__Zip(zip_path=zip_path, in_memory=in_memory).setup()
        return self.set_storage(storage_fs_zip)

    # Path handler addition methods
    @type_safe
    def add_handler(self, path_handler: Path__Handler
                     ) -> Path__Handler:
        self.path_handlers.append(path_handler)
        return path_handler

    def add_handler__latest(self, **kwargs
                             ) -> Path__Handler__Latest:                                            # Add latest path handler
        return self.add_handler(Path__Handler__Latest(**kwargs))                                    # params for Path__Handler

    def add_handler__temporal(self, areas : List[Safe_Id] = None,                                   # Add temporal path handler
                                    **kwargs                                                        # params for Path__Handler
                               ) -> Path__Handler__Temporal:
        return self.add_handler(Path__Handler__Temporal(areas=areas, **kwargs))

    def add_handler__versioned(self, **kwargs
                                ) -> Path__Handler__Versioned:                                      # Add versioned path handler
        return  self.add_handler(Path__Handler__Versioned(**kwargs))

    def add_handler__custom(self, custom_path : Safe_Str__File__Path ,                              # Add custom path handler
                                  **kwargs
                            ) ->  Path__Handler__Custom:
        return self.add_handler(Path__Handler__Custom(custom_path=custom_path, **kwargs))

    # File creation methods
    def file(self, file_id   : Safe_Id                      ,                             # Create file with specified type
                   file_type : Type[Schema__Memory_FS__File__Type] = None                 # Default to JSON if not specified
              ) -> File_FS:
        if not self.storage_fs:
            raise ValueError("No storage configured. Use add_storage__* methods first.")

        file_paths = [handler.generate_path(file_id=file_id) for handler in self.path_handlers]

        file_config = Schema__Memory_FS__File__Config(file_id    = file_id    ,
                                                      file_paths = file_paths ,
                                                      file_type  = (file_type or Memory_FS__File__Type__Json)())

        return File_FS(file__config=file_config, storage_fs=self.storage_fs)

    def file__json(self, file_id : Safe_Id                                                # Create JSON file
                  ) -> File_FS:
        return self.file(file_id, Memory_FS__File__Type__Json)

    def file__text(self, file_id : Safe_Id                                                # Create text file
                  ) -> File_FS:
        return self.file(file_id, Memory_FS__File__Type__Text)

    def file__binary(self, file_id: Safe_Id                                               # Create binary file
                      ) -> File_FS:
        return self.file(file_id, Memory_FS__File__Type__Binary)


    def file__data(self, file_id : Safe_Id                                                # Create data file
                  ) -> File_FS:
        return self.file(file_id, Memory_FS__File__Type__Data)

    # Helper methods
    def get_handler(self, handler_type : Type[Path__Handler]                              # Get handler by type
                   ) -> Optional[Path__Handler]:
        for handler in self.path_handlers:
            if isinstance(handler, handler_type):
                return handler
        return None

    def clear_handlers(self) -> 'Memory_FS':                                              # Clear all path handlers
        self.path_handlers = []
        return self