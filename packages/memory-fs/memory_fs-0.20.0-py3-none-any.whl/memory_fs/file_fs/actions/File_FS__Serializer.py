import json
from typing                                             import Any
from memory_fs.schemas.Enum__Memory_FS__Serialization   import Enum__Memory_FS__Serialization
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class File_FS__Serializer(Type_Safe):

    def deserialize(self, content_bytes: bytes, file_type) -> Any:                        # Deserialize data based on file type's serialization method
        if content_bytes is None:
            return None
        serialization = file_type.serialization

        if serialization == Enum__Memory_FS__Serialization.STRING:
            return content_bytes.decode(file_type.encoding.value)

        elif serialization == Enum__Memory_FS__Serialization.JSON:
            json_str = content_bytes.decode(file_type.encoding.value)
            return json.loads(json_str)

        elif serialization == Enum__Memory_FS__Serialization.BINARY:
            return content_bytes

        elif serialization == Enum__Memory_FS__Serialization.BASE64:
            import base64
            return base64.b64decode(content_bytes)

        elif serialization == Enum__Memory_FS__Serialization.TYPE_SAFE:                  # todo: need to add Type_Safe support
            raise NotImplementedError

        else:
            raise ValueError(f"Unknown serialization method: {serialization}")


    def serialize(self, data: Any, file_type) -> bytes:                                   # Serialize data based on file type's serialization method
        serialization = file_type.serialization

        if serialization == Enum__Memory_FS__Serialization.STRING:
            if isinstance(data, str):
                return data.encode(file_type.encoding.value)
            else:
                return str(data).encode(file_type.encoding.value)

        elif serialization == Enum__Memory_FS__Serialization.JSON:
            if type(data) is bytes:                                                             # todo: review this usage, since it doesn't look right to be doing this conversation from bytes to str here
                data = data.decode(file_type.encoding.value)
            json_str = json.dumps(data, indent=2)
            return json_str.encode(file_type.encoding.value)

        elif serialization == Enum__Memory_FS__Serialization.BINARY:
            if isinstance(data, bytes):
                return data
            else:
                raise ValueError(f"Binary serialization expects bytes, got {type(data)}")

        elif serialization == Enum__Memory_FS__Serialization.BASE64:
            import base64
            if isinstance(data, bytes):
                return base64.b64encode(data)
            else:
                return base64.b64encode(str(data).encode('utf-8'))

        elif serialization == Enum__Memory_FS__Serialization.TYPE_SAFE:             # todo: need to add Type_Safe support
            raise NotImplementedError
            # if hasattr(data, 'json'):
            #     json_str = data.json()
            #     return json_str.encode(file_type.encoding.value)
            # else:
            #     raise ValueError(f"TYPE_SAFE serialization requires object with json() method, got {type(data)}")

        else:
            raise ValueError(f"Unknown serialization method: {serialization}")