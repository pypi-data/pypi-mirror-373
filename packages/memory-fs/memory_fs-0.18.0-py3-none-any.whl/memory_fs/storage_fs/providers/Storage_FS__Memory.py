from typing                                             import Dict
from osbot_utils.utils.Json                             import bytes_to_json
from osbot_utils.type_safe.type_safe_core.decorators.type_safe         import type_safe
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.storage_fs.Storage_FS                    import Storage_FS

# todo: see if this class shouldn't be leveraging the Serialisation and DeSerialisation classes/logic

class Storage_FS__Memory(Storage_FS):
    content_data: Dict[Safe_Str__File__Path, bytes]

    def clear(self):
        self.content_data.clear()
        return True

    @type_safe
    def file__bytes(self, path: Safe_Str__File__Path):
        return self.content_data.get(path)

    @type_safe
    def file__delete(self, path: Safe_Str__File__Path) -> bool:
        if path in self.content_data:
            del self.content_data[path]
            return True
        return False

    @type_safe
    def file__exists(self, path: Safe_Str__File__Path):
        return path in self.content_data

    @type_safe
    def file__json(self, path: Safe_Str__File__Path):
        file_bytes = self.file__bytes(path)
        if file_bytes:
            return bytes_to_json(file_bytes)

    @type_safe
    def file__save(self, path: Safe_Str__File__Path, data: bytes) -> bool:
        self.content_data[path] = data
        return True

    @type_safe
    def file__str(self, path: Safe_Str__File__Path):
        file_bytes = self.file__bytes(path)
        if file_bytes:
            return file_bytes.decode()                  # todo: add content type to this decode


    def files__paths(self):
        return self.content_data.keys()