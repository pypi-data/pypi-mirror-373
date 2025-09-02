from typing                                             import List
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.file_fs.actions.File_FS__Name            import File_FS__Name
from osbot_utils.type_safe.type_safe_core.decorators.type_safe         import type_safe
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

# note:
#  content to be saved as {file_id}.{extension}
#  config to be saved as {file_id}.{extension}.config
#  metatada to be saved as {file_id}.{extension}.metadata

# todo: shared code below can be refactored into separate methods

class File_FS__Paths(Type_Safe):
    file__config: Schema__Memory_FS__File__Config

    @cache_on_self
    def file_fs__name(self):
        return File_FS__Name(file__config=self.file__config)

    @type_safe
    def paths(self) -> List[Safe_Str__File__Path]:
        return sorted(self.paths__config  () +
                      self.paths__content () +
                      self.paths__metadata())

    def paths__config(self) -> List[Safe_Str__File__Path]:
        full_file_paths = []
        full_file_name = self.file_fs__name().config()
        if self.file__config.file_paths:                                  # if we have file_paths define mapp them all
            for file_path in self.file__config.file_paths:
                content_path = self.file_fs__name().config__for_path(file_path)
                full_file_paths.append(content_path)
        else:
            full_file_paths.append(Safe_Str__File__Path(full_file_name))

        return full_file_paths

    def paths__content(self) -> List[Safe_Str__File__Path]:
        full_file_paths = []
        full_file_name = self.file_fs__name().content()
        if self.file__config.file_paths:                                  # if we have file_paths define map them all
            for file_path in self.file__config.file_paths:
                content_path = self.file_fs__name().content__for_path(file_path)
                full_file_paths.append(content_path)
        else:
            full_file_paths.append(Safe_Str__File__Path(full_file_name))

        return full_file_paths

    def paths__metadata(self) -> List[Safe_Str__File__Path]:
        full_file_paths = []
        full_file_name = self.file_fs__name().metadata()
        if self.file__config.file_paths:                                  # if we have file_paths define map them all
            for file_path in self.file__config.file_paths:
                metadata_path = self.file_fs__name().metadata__for_path(file_path)
                full_file_paths.append(metadata_path)
        else:
            full_file_paths.append(Safe_Str__File__Path(full_file_name))

        return full_file_paths