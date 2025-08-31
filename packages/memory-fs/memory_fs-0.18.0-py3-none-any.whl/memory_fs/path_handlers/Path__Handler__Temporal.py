from datetime                                                                   import datetime
from typing                                                                     import List
from memory_fs.path_handlers.Path__Handler                                      import Path__Handler
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id              import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path

DEFAULT__PATH_HANDLER__TEMPORAL__TIME_PATH = "%Y/%m/%d/%H"


class Path__Handler__Temporal(Path__Handler):                                           # Handler that stores files in temporal directory structure
    areas             : List[Safe_Id]
    name              : Safe_Id       = Safe_Id("temporal")
    time_path_pattern : str           = DEFAULT__PATH_HANDLER__TEMPORAL__TIME_PATH

    def generate_path(self) -> Safe_Str__File__Path:                                     # Generate temporal path with areas
        middle_segments = []

        # Add temporal component
        middle_segments.append(self.path_now())

        # Add areas if defined
        if self.areas:
            areas_path = "/".join(str(area) for area in self.areas)
            middle_segments.append(areas_path)

        return self.combine_paths(*middle_segments)

    def path_now(self) -> str:                                                           # Generate current time path
        now       = datetime.now()
        time_path = now.strftime(self.time_path_pattern)
        return time_path