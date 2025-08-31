from typing                                             import List
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.file_fs.actions.File_FS__Exists          import File_FS__Exists
from memory_fs.file_fs.actions.File_FS__Name            import File_FS__Name
from memory_fs.file_fs.actions.File_FS__Paths           import File_FS__Paths
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from memory_fs.storage_fs.Storage_FS                    import Storage_FS
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class File_FS__File(Type_Safe):
    file__config : Schema__Memory_FS__File__Config
    storage_fs  : Storage_FS

    ###### File_FS__* methods #######
    @cache_on_self
    def file_fs__exists(self):
        return File_FS__Exists(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__name(self):
        return File_FS__Name(file__config=self.file__config)

    @cache_on_self
    def file_fs__paths(self):
        return File_FS__Paths(file__config=self.file__config)

    ###### File_FS__File methods #######

    def delete(self):
        files_deleted = []
        for file_path in self.paths():
            if self.storage_fs.file__delete(path=file_path):
                files_deleted.append(file_path)
        return files_deleted

    def data(self):
        return None

    def file_id(self):
        return self.file__config.file_id

    def file_name(self):                                                                                # todo: see if we need these methods in this class
        return self.file_fs__name().config()

    def exists(self) -> bool:
        return self.file_fs__exists().config()

    def not_exists(self) -> bool:
        return self.exists() is False

    def paths(self):
        return []

    def update(self, data: bytes) -> List[Safe_Str__File__Path]:
        files_to_save = self.paths()
        files_saved = []
        for file_to_save in files_to_save:
            if self.storage_fs.file__save(path=file_to_save, data=data):
                files_saved.append(file_to_save)
        return files_saved
