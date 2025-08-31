from typing                                             import Any, List
from memory_fs.file_fs.file.File_FS__File               import File_FS__File
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.file_fs.actions.File_FS__Serializer      import File_FS__Serializer
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self


class File_FS__Content(File_FS__File):

    ###### File_FS__* methods #######

    @cache_on_self
    def file_fs__serializer(self):                                              # todo: review the use of the serialised here, since one the patterns that we could be doing is that the 'data' classes all think and operate in bytes
        return File_FS__Serializer()

    ###### File_FS__Content Methods #######

    def bytes(self) -> bytes:
        for path in self.paths():                                               # todo: see if we need something like Enum__Memory_FS__File__Exists_Strategy here, since at the moment this is going to go through all files, and return when we find some data
            file_bytes = self.storage_fs.file__bytes(path)
            if file_bytes:                                                      # todo: see if we should get this info from the metadata, or if it is ok to just load the first one we find , or if we should be following the Enum__Memory_FS__File__Exists_Strategy strategy
                return file_bytes

    def create(self, data: bytes) -> List[Safe_Str__File__Path]:
        return self.update(data=data)

    def content(self) -> Any:
        return self.file_data()

    def file_data(self) -> Any:                                                                # todo: see if we should add the .serialise(...) method to this class since we are using the .deserialise here
        file_type     = self.file__config.file_type
        content_bytes = self.bytes()
        file_data     = self.file_fs__serializer().deserialize(content_bytes, file_type)       # todo: see if we shouldn't be using File_FS__Load here
        return file_data

    def paths(self):
        return self.file_fs__paths().paths__content()



