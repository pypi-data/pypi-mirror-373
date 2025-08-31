from memory_fs.path_handlers.Path__Handler                                      import Path__Handler
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id              import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path


class Path__Handler__Latest(Path__Handler):                                             # Handler that stores files in a 'latest' directory
    latest_folder : Safe_Str__File__Path = Safe_Str__File__Path("latest")                # Configurable latest folder name
    name          : Safe_Id               = Safe_Id("latest")

    def generate_path(self) -> Safe_Str__File__Path:                                     # Generate path with latest folder
        return self.combine_paths(str(self.latest_folder))