from typing                                                                     import List, Optional
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id              import Safe_Id
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt__FileSize             import Safe_UInt__FileSize
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.utils.Files                                                    import folder_create, parent_folder
from osbot_utils.utils.Json                                                     import bytes_to_json
from osbot_utils.helpers.sqlite.Sqlite__Database                                import Sqlite__Database
from osbot_utils.helpers.sqlite.Sqlite__Table                                   import Sqlite__Table
from osbot_utils.base_classes.Kwargs_To_Self                                    import Kwargs_To_Self
from osbot_utils.utils.Misc                                                     import timestamp_utc_now
from memory_fs.storage_fs.Storage_FS                                            import Storage_FS


class Schema__Storage_FS__Files(Kwargs_To_Self):
    path       : str                                                                    # File path as primary key
    data       : bytes                                                                  # File content as bytes
    created_at : int                                                                    # Creation timestamp
    updated_at : int                                                                    # Last update timestamp


class Schema__Storage_FS__Sqlite__Stats(Type_Safe):
    file_count         : int
    total_data_size    : Safe_UInt__FileSize
    database_file_size : Safe_UInt__FileSize
    database_path      : Safe_Str__File__Path


class Storage_FS__Sqlite(Storage_FS):
    db_path    : Safe_Str__File__Path                                                   # Path to SQLite database file
    table_name : Safe_Id = Safe_Id("memory_fs_files")                                   # Table name for storing files
    database   : Sqlite__Database                                                       # OSBot_Utils database instance
    table      : Sqlite__Table                                                          # OSBot_Utils table instance
    in_memory  : bool           = True                                                  # Defaults to an in-memory sqlite db

    def setup(self) -> 'Storage_FS__Sqlite':                                            # Initialize the database schema using OSBot_Utils
        if self.in_memory is False:
            folder_create(parent_folder(self.db_path))                                      # Ensure parent folder exists
        self.database            = Sqlite__Database(db_path=self.db_path)               # Create database instance
        self.database.in_memory  = self.in_memory                                       # Using file-based database
        self.table               = self.database.table(str(self.table_name))            # Get table instance
        self.table.row_schema    = Schema__Storage_FS__Files                            # Set the schema

        if self.table.not_exists():                                                     # Create table if it doesn't exist
            self.table.create()
            self.table.index_create('path')                                             # Create index for faster lookups

        return self

    @type_safe
    def file__bytes(self, path: Safe_Str__File__Path                                    # Read file content as bytes from database
                    ) -> Optional[bytes]:
        row = self.table.select_row_where(path=str(path))
        if row:
            return row.get('data')

    @type_safe
    def file__delete(self, path: Safe_Str__File__Path                                   # Delete a file from database
                     ) -> bool:
        if self.file__exists(path):
            self.table.rows_delete_where(path=str(path))
            return True
        return False

    @type_safe
    def file__exists(self, path: Safe_Str__File__Path                                   # Check if file exists in database
                      ) -> bool:
        return self.table.contains(path=str(path))


    @type_safe
    def file__json(self, path: Safe_Str__File__Path                                     # Read file content as JSON from database
                   ) -> Optional[dict]:
        file_bytes = self.file__bytes(path)
        if file_bytes:
            return bytes_to_json(file_bytes)

    @type_safe
    def file__save(self, path: Safe_Str__File__Path ,                                   # Save bytes to database
                         data: bytes
                   ) -> bool:
        current_time = timestamp_utc_now()

        if self.file__exists(path):                                                 # Update existing file
            update_fields     = {'data': data, 'updated_at': current_time}
            query_conditions  = {'path': str(path)}
            result           = self.table.row_update(update_fields, query_conditions)
            return result.get('status') == 'ok'
        else:                                                                        # Insert new file
            row_data = { 'path'       : str(path)     ,
                        'data'       : data           ,
                        'created_at' : current_time   ,
                        'updated_at' : current_time   }
            result = self.table.row_add_record(row_data)
            self.table.commit()
            return result.get('status') == 'ok'

    @type_safe
    def file__str(self, path: Safe_Str__File__Path                                      # Read file content as string from database
                  ) -> Optional[str]:
        file_bytes = self.file__bytes(path)
        if file_bytes is not None:
            return file_bytes.decode('utf-8')
        return None

    def files__paths(self) -> List[Safe_Str__File__Path]:                               # List all file paths in database
        paths = []
        path_values = self.table.select_field_values('path')
        for path_str in path_values:
            paths.append(Safe_Str__File__Path(path_str))
        return paths

    def clear(self) -> bool:                                                            # Clear all files in database
        result = self.table.clear()
        if result.get('status') == 'ok':
            self.database.vacuum()                                                  # Reclaim space after clearing
            return True
        return False

    # Additional utility methods for SQLite-specific features

    def optimize(self) -> bool:                                                         # Optimize the database (vacuum)
        result = self.database.vacuum()
        return result.get('status') == 'ok'

    def __del__(self):                                                                  # Cleanup on deletion
        if hasattr(self, 'database') and self.database:
            self.database.close()