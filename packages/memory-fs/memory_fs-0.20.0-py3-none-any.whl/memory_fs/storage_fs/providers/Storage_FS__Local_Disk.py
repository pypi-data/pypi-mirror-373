from typing                                                                     import List, Optional
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.utils.Json                                                     import bytes_to_json, json_to_bytes
from osbot_utils.utils.Files                                                    import Files, file_bytes, file_contents, file_create_bytes, file_delete, file_exists, file_create, folder_create, folder_delete_all, path_combine, files_list__virtual_paths, parent_folder, folder_exists, folder_delete
from memory_fs.storage_fs.Storage_FS                                            import Storage_FS


class Storage_FS__Local_Disk(Storage_FS):
    root_path: Safe_Str__File__Path                                                                         # Base directory for all file operations

    def full_path(self, path: Safe_Str__File__Path                                                          # Convert Safe_Str__File__Path to full filesystem path
                   ) -> str:
        return path_combine(str(self.root_path), str(path))

    def ensure_parent_dirs(self, full_path: str                                                             # Ensure parent directories exist for a given path
                            ) -> None:
        parent_dir = parent_folder(full_path)
        if parent_dir:
            folder_create(parent_dir)

    @type_safe
    def file__bytes(self, path: Safe_Str__File__Path                                     # Read file content as bytes
                     ) -> Optional[bytes]:
        full_path = self.full_path(path)
        if file_exists(full_path):
            return file_bytes(full_path)
        return None

    @type_safe
    def file__delete(self, path: Safe_Str__File__Path                                    # Delete a file
                      ) -> bool:
        full_path = self.full_path(path)
        return file_delete(full_path)

    @type_safe
    def file__exists(self, path: Safe_Str__File__Path                                    # Check if file exists
                      ) -> bool:
        full_path = self.full_path(path)
        return file_exists(full_path)

    @type_safe
    def file__json(self, path: Safe_Str__File__Path                                      # Read file content as JSON
                   ) -> Optional[dict]:
        file_bytes_data = self.file__bytes(path)
        if file_bytes_data:
            return bytes_to_json(file_bytes_data)
        return None

    @type_safe
    def file__save(self, path: Safe_Str__File__Path ,                                    # Save bytes to file
                         data: bytes
                    ) -> bool:
        full_path = self.full_path(path)

        self.ensure_parent_dirs(full_path)
        result_path = file_create_bytes(path=full_path, bytes=data)
        return result_path == full_path

    @type_safe
    def file__str(self, path: Safe_Str__File__Path                                       # Read file content as string
                   ) -> Optional[str]:
        full_path = self.full_path(path)
        return file_contents(full_path)                                          # file_contents handles text decoding


    def files__paths(self) -> List[Safe_Str__File__Path]:                                # List all file paths in storage
        paths = []
        # Use Files.files to get all files recursively with virtual paths
        virtual_paths = files_list__virtual_paths(str(self.root_path), pattern='*', only_files=True)
        for path_str in virtual_paths:
            paths.append(path_str)                                                      # Already Safe_Str__File__Path from Files.files
        return sorted(paths)

    def clear(self) -> bool:                                                             # Clear all files in storage (use with caution!)
        # Get all items in root directory
        root_path_str = str(self.root_path)
        all_files     = Files.files(root_path_str, pattern='*', only_files=True)
        all_folders   = Files.folder_sub_folders(root_path_str)

        # Delete all files first
        for file_path in all_files:
            file_delete(str(file_path))

        # Delete all subdirectories
        for folder_path in sorted(all_folders, reverse=True):                       # Delete deepest folders first
            folder_delete_all(folder_path)

        return True