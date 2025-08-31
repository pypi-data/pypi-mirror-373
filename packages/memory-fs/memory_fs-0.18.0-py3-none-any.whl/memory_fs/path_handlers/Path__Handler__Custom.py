from memory_fs.path_handlers.Path__Handler                                      import Path__Handler
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id              import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path


class Path__Handler__Custom(Path__Handler):                                             # Handler that uses a custom path
    custom_path : Safe_Str__File__Path
    name        : Safe_Id = Safe_Id("custom")

    def generate_path(self) -> Safe_Str__File__Path:                                    # Generate custom path
        if self.custom_path:
            return self.combine_paths(str(self.custom_path))
        return self.combine_paths()