from typing                                                                     import List, Optional
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.utils.Json                                                     import bytes_to_json
from osbot_utils.utils.Files                                                    import file_exists, file_bytes, file_create_bytes, file_delete, parent_folder, folder_create
from osbot_utils.utils.Zip                                                      import (zip_bytes__add_file     ,
                                                                                        zip_bytes__file        ,
                                                                                        zip_bytes__file_list   ,
                                                                                        zip_bytes__remove_file ,
                                                                                        zip_bytes__replace_file,
                                                                                        zip_bytes__files       )
from memory_fs.storage_fs.Storage_FS                                            import Storage_FS


class Storage_FS__Zip(Storage_FS):
    zip_bytes : bytes                                                                   # In-memory zip content
    zip_path  : Optional[Safe_Str__File__Path] = None                                   # Optional path for disk persistence
    in_memory : bool                           = True                                   # when False this will auto-save to disk after each operation

    def setup(self) -> 'Storage_FS__Zip':                                               # Initialize storage, loading from disk if path provided
        if self.zip_path and file_exists(str(self.zip_path)):
            self.load_from_disk()
        elif self.zip_bytes is None:
            self.zip_bytes = b""
        return self

    def save_if_not_in_memory(self) -> bool:                                            # Save to disk if in_memory is set to false and zip_path set
        if self.in_memory is False and self.zip_path:
            return self.save_to_disk()
        return False

    @type_safe
    def file__bytes(self, path : Safe_Str__File__Path                                   # Read file content as bytes from zip
                    ) -> Optional[bytes]:
        if self.file__exists(path):
            file_bytes_data = zip_bytes__file(self.zip_bytes, str(path))
            if file_bytes_data is None:
                return b""
            return file_bytes_data
        return None

    @type_safe
    def file__delete(self, path : Safe_Str__File__Path                                  # Delete a file from zip
                     ) -> bool:
        if self.file__exists(path):
            self.zip_bytes = zip_bytes__remove_file(self.zip_bytes, str(path))
            self.save_if_not_in_memory()
            return True
        return False

    @type_safe
    def file__exists(self, path : Safe_Str__File__Path                                  # Check if file exists in zip
                     ) -> bool:
        if self.zip_bytes:
            files_in_zip = zip_bytes__file_list(self.zip_bytes)
            return str(path) in files_in_zip
        return False

    @type_safe
    def file__json(self, path : Safe_Str__File__Path                                    # Read file content as JSON from zip
                   ) -> Optional[dict]:
        file_bytes_data = self.file__bytes(path)
        if file_bytes_data:
            return bytes_to_json(file_bytes_data)
        return None

    @type_safe
    def file__save(self, path : Safe_Str__File__Path ,                                  # Save bytes to zip
                         data : bytes
                   ) -> bool:
        path_str = str(path)
        if self.file__exists(path):
            self.zip_bytes = zip_bytes__replace_file(self.zip_bytes, path_str, data)
        else:
            self.zip_bytes = zip_bytes__add_file(self.zip_bytes, path_str, data)
        self.save_if_not_in_memory()
        return True

    @type_safe
    def file__str(self, path : Safe_Str__File__Path                                     # Read file content as string from zip
                  ) -> Optional[str]:
        file_bytes_data = self.file__bytes(path)
        if file_bytes_data is not None:
            return file_bytes_data.decode('utf-8')
        return None

    def files__paths(self                                                               # List all file paths in zip
                     ) -> List[Safe_Str__File__Path]:
        if self.zip_bytes:
            files_list = zip_bytes__file_list(self.zip_bytes)
            return [Safe_Str__File__Path(file_path) for file_path in sorted(files_list)]
        return []

    def clear(self) -> bool:                                                                        # Clear all files (reset to empty zip)
        self.zip_bytes = b""
        self.save_if_not_in_memory()
        return True


    # Disk persistence methods

    @type_safe
    def save_to_disk(self, path : Optional[Safe_Str__File__Path] = None                 # Save the current zip to disk
                     ) -> bool:
        save_path = path or self.zip_path
        if not save_path:
            return False

        parent_dir = parent_folder(str(save_path))                                      # Ensure parent directory exists
        if parent_dir:
            folder_create(parent_dir)

        result_path = file_create_bytes(path=str(save_path), bytes=self.zip_bytes)     # Save zip bytes to file
        return result_path == str(save_path)

    @type_safe
    def load_from_disk(self, path : Optional[Safe_Str__File__Path] = None               # Load zip from disk
                       ) -> bool:
        load_path = path or self.zip_path
        if not load_path or not file_exists(str(load_path)):
            return False

        zip_data = file_bytes(str(load_path))
        if zip_data:
            try:                                                                         # Validate it's a valid zip
                zip_bytes__file_list(zip_data)
                self.zip_bytes = zip_data
                if path:                                                                 # Update zip_path if a new path was provided
                    self.zip_path = path
                return True
            except Exception:
                return False
        return False

    @type_safe
    def delete_from_disk(self                                                           # Delete the zip file from disk
                         ) -> bool:
        if self.zip_path and file_exists(str(self.zip_path)):
            return file_delete(str(self.zip_path))
        return False

    def sync_to_disk(self                                                               # Explicitly sync current state to disk
                     ) -> bool:
        return self.save_to_disk()


    # Additional utility methods

    def get_all_files(self                                                              # Get all files and their contents
                      ) -> dict:
        try:
            return zip_bytes__files(self.zip_bytes)
        except Exception:
            return {}

    def size_bytes(self                                                                 # Get the size of the zip in bytes
                   ) -> int:
        return len(self.zip_bytes)

    def file_count(self                                                                 # Get the number of files in the zip
                   ) -> int:
        return len(self.files__paths())

    def export_bytes(self                                                               # Export the entire zip as bytes
                     ) -> bytes:
        return self.zip_bytes

    @type_safe
    def import_bytes(self, zip_bytes : bytes          ,                                 # Import zip from bytes
                           merge     : bool = False                                      # If True, merge with existing files
                     ) -> bool:

        imported_files = zip_bytes__files(zip_bytes)                                    # Validate it's a valid zip

        if merge and self.zip_bytes:                                                    # Merge mode: add imported files to existing zip
            for file_path, file_data in imported_files.items():
                path = Safe_Str__File__Path(file_path)
                self.file__save(path, file_data)
        else:                                                                            # Replace mode: use imported zip as-is
            self.zip_bytes = zip_bytes
            self.save_if_not_in_memory()
        return True

    def is_in_memory_only(self                                                          # Check if this is in-memory only (no disk path)
                          ) -> bool:
        return self.zip_path is None

    def enable_in_memory(self                                                           # Disable auto-save to disk after each operation
                         ) -> 'Storage_FS__Zip':
        self.in_memory = True
        return self

    def disable_in_memory(self) -> 'Storage_FS__Zip':                                   # Enable auto-save to disk
        self.in_memory = False
        return self