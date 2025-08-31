from typing                                             import Optional, Dict, Any
from memory_fs.file_fs.file.File_FS__Config             import File_FS__Config
from memory_fs.file_fs.file.File_FS__Metadata           import File_FS__Metadata
from memory_fs.storage_fs.Storage_FS                    import Storage_FS
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                        import Safe_Id
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class File_FS__Info(Type_Safe):
    file__config: Schema__Memory_FS__File__Config
    storage_fs  : Storage_FS

    ###### File_FS__* methods #######
    @cache_on_self
    def file_fs__config(self):
        return File_FS__Config(file__config=self.file__config, storage_fs=self.storage_fs)

    @cache_on_self
    def file_fs__metadata(self):
        return File_FS__Metadata(file__config=self.file__config, storage_fs=self.storage_fs)

    ###### File_FS__Info methods #######

    # todo: this method should return a strongly typed class (ideally one from the file)
    def info(self) -> Optional[Dict[Safe_Id, Any]]:

        if self.file_fs__config().not_exists():
            return None

        config   = self.file_fs__config  ().config  ()
        metadata = self.file_fs__metadata().metadata()


        content_size = int(metadata.content__size)                                # Get size from metadata
        return {Safe_Id("exists")       : True                                          ,
                Safe_Id("size")         : content_size                                  ,
                Safe_Id("content_hash") : metadata.content__hash                   ,
                Safe_Id("timestamp")    : metadata.timestamp                       ,
                Safe_Id("content_type") : config.file_type.content_type.value      }