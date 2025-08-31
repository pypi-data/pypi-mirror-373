from memory_fs.storage_fs.Storage_FS                    import Storage_FS
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.file_fs.actions.File_FS__Paths           import File_FS__Paths
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class File_FS__Exists(Type_Safe):
    file__config: Schema__Memory_FS__File__Config                   # todo: capture idea that one way to group these two vars together (file__config and storage) is to use the concept of 'targets' (i.e. a File_FS__Target would be a object with references to the file config and the way to store it)
    storage_fs  : Storage_FS

    @cache_on_self
    def file_fs__paths(self):
        return File_FS__Paths(file__config=self.file__config)

    def config(self) -> bool:
        config_paths = self.file_fs__paths().paths__config()
        return self.check_using_strategy(config_paths)

    def content(self) -> bool:
        config_paths = self.file_fs__paths().paths__content()
        return self.check_using_strategy(config_paths)

    def metadata(self) -> bool:
        metadata_paths = self.file_fs__paths().paths__metadata()
        return self.check_using_strategy(metadata_paths)

    def check_using_strategy(self, paths):
        for path in paths:                                                          # todo: add the exists_strategy since at the moment this is implementing the Enum__Memory_FS__File__Exists_Strategy.ANY
            if self.storage_fs.file__exists(path):
                return True                                                         # when Enum__Memory_FS__File__Exists_Strategy.ANY if we find at least one, return true
        return False                                                                # if none were found, return False