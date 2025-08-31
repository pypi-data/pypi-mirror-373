from typing                                                                         import Any, List, Dict
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path      import Safe_Str__File__Path
from memory_fs.file_fs.actions.File_FS__Delete                                      import File_FS__Delete
from memory_fs.file_fs.actions.File_FS__Exists                                      import File_FS__Exists
from memory_fs.file_fs.actions.File_FS__Info                                        import File_FS__Info
from memory_fs.file_fs.actions.File_FS__Paths                                       import File_FS__Paths
from memory_fs.file_fs.actions.File_FS__Update                                      import File_FS__Update
from memory_fs.file_fs.file.File_FS__Config                                         import File_FS__Config
from memory_fs.file_fs.file.File_FS__Content                                        import File_FS__Content
from memory_fs.file_fs.file.File_FS__Metadata                                       import File_FS__Metadata
from memory_fs.storage_fs.Storage_FS                                                import Storage_FS
from memory_fs.file_fs.actions.File_FS__Create                                      import File_FS__Create
from memory_fs.schemas.Schema__Memory_FS__File__Config                              import Schema__Memory_FS__File__Config
from memory_fs.schemas.Schema__Memory_FS__File__Metadata                            import Schema__Memory_FS__File__Metadata
from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe


class File_FS(Type_Safe):
    file__config : Schema__Memory_FS__File__Config
    storage_fs  : Storage_FS

    ###### File_FS__* methods #######

    @cache_on_self
    def file_fs__create(self):
        return File_FS__Create(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__config(self):
        return File_FS__Config(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__content(self):
        return File_FS__Content(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__delete(self):
        return File_FS__Delete(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__exists(self):
        return File_FS__Exists(file__config=self.file__config, storage_fs= self.storage_fs)

    @cache_on_self
    def file_fs__info(self):
        return File_FS__Info(file__config=self.file__config, storage_fs= self.storage_fs)

    @cache_on_self
    def file_fs__metadata(self):
        return File_FS__Metadata(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__paths(self):
        return File_FS__Paths(file__config=self.file__config)

    @cache_on_self
    def file_fs__update(self):
        return File_FS__Update(file__config=self.file__config, storage_fs=self.storage_fs)


    ###### Class methods #######

    def create(self, file_data: Any=None):
        return self.file_fs__create().create(file_data=file_data)

    def config(self) -> Schema__Memory_FS__File__Config:
        return self.file_fs__config().config()

    def content(self) -> bytes:                                                                     # this is the deserialised data
        return self.file_fs__content().content()

    def delete(self):
        return self.file_fs__delete().delete()

    def exists(self):
        return self.file_fs__exists().config()                                                          # use the .config() existence as the 'file exists' metric

    def info(self):
        return self.file_fs__info().info()

    def file_id(self):
        return self.file__config.file_id

    def metadata(self) -> Schema__Memory_FS__File__Metadata:
        return self.file_fs__metadata().metadata()

    def metadata__update(self, data: Dict[str, Any]):                       # the callers can only update the data section of the metadata file
        return self.file_fs__metadata().update__data(data=data)

    def paths(self) -> List[Safe_Str__File__Path]:
        return self.file_fs__paths().paths()

    def update(self, file_data: Any):
        return self.file_fs__update().update(file_data=file_data)
