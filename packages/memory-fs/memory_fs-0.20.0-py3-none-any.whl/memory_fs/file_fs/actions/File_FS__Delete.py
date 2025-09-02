from memory_fs.file_fs.file.File_FS__Config             import File_FS__Config
from memory_fs.file_fs.file.File_FS__Content            import File_FS__Content
from memory_fs.file_fs.file.File_FS__Metadata           import File_FS__Metadata
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from memory_fs.storage_fs.Storage_FS                    import Storage_FS
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

class File_FS__Delete(Type_Safe):                                                       # todo: refactor to file_fs__create
    file__config: Schema__Memory_FS__File__Config
    storage_fs  : Storage_FS

    ###### File_FS__* methods #######

    @cache_on_self
    def file_fs__config(self):
        return File_FS__Config(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__content(self):
        return File_FS__Content(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__metadata(self):
        return File_FS__Metadata(file__config=self.file__config, storage_fs=self.storage_fs)

    ###### File_FS__Delete Methods #######

    def delete(self):
        files_deleted = (self.delete__config   () +
                         self.delete__content  () +
                         self.delete__metadata ())
        return sorted(files_deleted)

    def delete__config(self):
        return self.file_fs__config().delete()

    def delete__content(self):
        return self.file_fs__content().delete()

    def delete__metadata(self):
        return self.file_fs__metadata().delete()