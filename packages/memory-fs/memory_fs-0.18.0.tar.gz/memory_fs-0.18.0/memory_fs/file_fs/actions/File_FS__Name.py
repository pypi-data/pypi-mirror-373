from os                                                                         import path
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Name  import Safe_Str__File__Name
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.schemas.Schema__Memory_FS__File__Config                          import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe

FILE_EXTENSION__MEMORY_FS__FILE__CONFIG   = 'config'
FILE_EXTENSION__MEMORY_FS__FILE__METADATA = 'metadata'

class File_FS__Name(Type_Safe):
    file__config: Schema__Memory_FS__File__Config

    def build(self, elements) -> Safe_Str__File__Name:
        return Safe_Str__File__Name(".".join(elements))

    def config(self) -> Safe_Str__File__Name:
        elements = [self.content(), FILE_EXTENSION__MEMORY_FS__FILE__CONFIG]
        return self.build(elements)

    def config__for_path(self, file_path: Safe_Str__File__Path=None                     # support empty or non paths (which usually indicates that we are in the root folder)
                          ) -> Safe_Str__File__Path:                                    # return a strongly typed path
        return self.for_path(file_path=file_path, file_name=self.config())

    def for_path(self, file_path: Safe_Str__File__Path,
                       file_name: Safe_Str__File__Name
                  ) -> Safe_Str__File__Path:
        if file_path:                                                                               # check if a file_path was provided
            full_path = path.join(str(file_path), str(file_name))
            return Safe_Str__File__Path(full_path)
        else:
            return Safe_Str__File__Path(file_name)                                                  # if not file_path then just return the file_name as a path


    def content(self) -> Safe_Str__File__Path:
        elements = [self.file__config.file_id]     # BUG: need to handle null values in file_extension
        if self.file__config.file_type.file_extension:
            elements.append(str(self.file__config.file_type.file_extension))                        # todo: see if need the str(..) here
        return self.build(elements)

    def content__for_path(self, file_path: Safe_Str__File__Path=None                                # support empty or non paths (which usually indicates that we are in the root folder)
                          ) -> Safe_Str__File__Path:                                                # return a strongly typed path
        return self.for_path(file_path=file_path, file_name=self.content())

    def metadata(self) -> Safe_Str__File__Name:
        elements = [self.content(), FILE_EXTENSION__MEMORY_FS__FILE__METADATA]
        return self.build(elements)

    def metadata__for_path(self, file_path: Safe_Str__File__Path=None                     # support empty or non paths (which usually indicates that we are in the root folder)
                          ) -> Safe_Str__File__Path:                                    # return a strongly typed path
        return self.for_path(file_path=file_path, file_name=self.metadata())