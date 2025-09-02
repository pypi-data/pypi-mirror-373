from typing                                                     import List, Any
from memory_fs.file_fs.file.File_FS__Config                     import File_FS__Config
from memory_fs.file_fs.file.File_FS__Content                    import File_FS__Content
from memory_fs.file_fs.actions.File_FS__Serializer              import File_FS__Serializer
from memory_fs.file_fs.file.File_FS__Metadata                   import File_FS__Metadata
from memory_fs.storage_fs.Storage_FS                            import Storage_FS
from osbot_utils.type_safe.type_safe_core.decorators.type_safe  import type_safe
from osbot_utils.decorators.methods.cache_on_self               import cache_on_self
from memory_fs.schemas.Schema__Memory_FS__File__Config          import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                            import Type_Safe

class File_FS__Create(Type_Safe):
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

    @cache_on_self
    def file_fs__serializer(self):
        return File_FS__Serializer()


    ###### File_FS__Create Methods #######

    def create(self, file_data: Any=None) -> List:
        file_type     = self.file__config.file_type
        content_bytes = self.file_fs__serializer().serialize(file_data, file_type)              # we convert the file_data into bytes here so that we only do this once
        files_created = (self.create__config  () +
                         self.create__content (data=content_bytes) +                         # todo: see if we shouldn't rename the 'content' parameter name into 'content_bytes' (so that is not confused with the wired use of 'content()' in other places of the code-base
                         self.create__metadata(data=content_bytes))                          # note: we currently have a side effect here for strings and bytes, since hash will be done of the bytes not on the original content
        return sorted(files_created)

    def create__config(self):
        return self.file_fs__config().create()

    @type_safe
    def create__content(self, data: bytes):
        return self.file_fs__content().create(data=data)

    def create__metadata(self, data: bytes):
        return self.file_fs__metadata().create(data=data)