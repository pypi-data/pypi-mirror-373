from typing                                                                     import Any, List
from memory_fs.file_fs.actions.File_FS__Serializer                              import File_FS__Serializer
from memory_fs.file_fs.file.File_FS__Content                                    import File_FS__Content
from memory_fs.file_fs.file.File_FS__Metadata                                   import File_FS__Metadata
from osbot_utils.decorators.methods.cache_on_self                               import cache_on_self
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.schemas.Schema__Memory_FS__File__Config                          import Schema__Memory_FS__File__Config
from memory_fs.storage_fs.Storage_FS                                            import Storage_FS
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe



class File_FS__Update(Type_Safe):
    file__config: Schema__Memory_FS__File__Config
    storage_fs  : Storage_FS

    ###### File_FS__* methods #######

    @cache_on_self
    def file_fs__content(self):
        return File_FS__Content(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__metadata(self):
        return File_FS__Metadata(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__serializer(self):
        return File_FS__Serializer()


    ###### File_FS__Update methods #######

    def update(self, file_data: Any) -> List[Safe_Str__File__Path]:
        file_type     = self.file__config.file_type
        content       = self.file_fs__serializer().serialize(file_data, file_type)
        files_updated = (self.update__content (content=content) +                                   # we only update the content and metadata, because the config file cannot be updated
                         self.update__metadata(content=content) )
        return sorted(files_updated)

    def update__content(self, content: Any) -> List[Safe_Str__File__Path]:
        return self.file_fs__content().update(data=content)

    def update__metadata(self, content: Any) -> List[Safe_Str__File__Path]:
        return self.file_fs__metadata().paths()     # for now , simulate the save of the metadata file

        # todo: add the implementation of this: (we will need the bytes in order to do this, since update_metadata (which needs to be renamed) expects the file bytes (I think we should be doing this inside the self.file_fs__content().update(data=content) method, since that one has access to the bytes that are going to be saved)
        return self.file_fs__metadata().update_metadata(data=content)
