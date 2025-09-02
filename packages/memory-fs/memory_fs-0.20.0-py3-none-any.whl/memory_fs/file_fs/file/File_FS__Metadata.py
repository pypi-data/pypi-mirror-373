from typing import List, Dict, Any

from osbot_utils.type_safe.primitives.safe_str.cryptography.hashes.Safe_Str__Hash import safe_str_hash

from memory_fs.file_fs.file.File_FS__File                                       import File_FS__File
from osbot_utils.utils.Json                                                     import json_to_bytes
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.schemas.Schema__Memory_FS__File__Metadata                        import Schema__Memory_FS__File__Metadata

# todo: review the pattern of not having a global object to hold the metadata value from disk (since we have some code complexity below caused by the fact that we don't have those values in memory)

class File_FS__Metadata(File_FS__File):

    def create(self, data: bytes) -> List[Safe_Str__File__Path]:                        # todo: see (or document) the side effect that the hash and size is of the bytes value (which by now has already been serialised into the current file type
        if self.exists() is False:                                                      #      this might actually be ok, but there could be cases (like raw binary strings or strings) where we will actually want to capture the raw hash
            return self.update_metadata(file_bytes=data)
        return []

    def default(self):
        return Schema__Memory_FS__File__Metadata()

    def exists(self) -> bool:
        return self.file_fs__exists().metadata()

    def load(self) -> Schema__Memory_FS__File__Metadata:                                                                # todo: see if for consistency this should be called .data()
        if self.exists() is False:
            return self.default()

        for path in self.file_fs__paths().paths__metadata():
            json_data = self.storage_fs.file__json(path)
            if json_data:
                return Schema__Memory_FS__File__Metadata.from_json(json_data)

    def metadata(self) -> Schema__Memory_FS__File__Metadata:
        return self.load()

    def paths(self):
        return self.file_fs__paths().paths__metadata()

    def update__data(self, data: Dict[str, Any]):        # this updates the data part of the metadata
        metadata = self.metadata()
        metadata.data = data
        json_data   = metadata.json()                   # todo: refactor with the code with update_metadata
        data        = json_to_bytes(json_data)
        files_updated = self.update(data=data)
        return files_updated

    # todo: this method needs a better name
    def update_metadata(self, file_bytes: bytes):        # this updates the non-data related values (like content__hash, content__size)
        file_metadata = self.load()
        self.update_metadata_obj(file_metadata=file_metadata, file_bytes=file_bytes)
        json_data   = file_metadata.json()              # todo: refactor with the code with update_metadata
        data        = json_to_bytes(json_data)
        files_updated = self.update(data=data)
        return files_updated

    def update_metadata_obj(self, file_metadata: Schema__Memory_FS__File__Metadata, file_bytes:bytes):         # figure out a better way to implement this
        content__hash = safe_str_hash(file_bytes)
        content__size = len(file_bytes)

        file_metadata.content__hash = content__hash
        file_metadata.content__size = content__size
