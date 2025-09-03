import json
from dataclasses import dataclass
from typing import Optional, Union

DEFAULT_CHUNK_SIZE = 100000

@dataclass(kw_only=True)
class FileLoaderConfiguration:
    """
    Configuration class for handling file loading requirements.

    Provides attributes to specify details like the sheet name, a unique key, and file paths.
    It is utilized to configure and manage how file loading operations are handled within
    the program, allowing flexibility and modularity.

    :ivar sheet: Name of the sheet to load from the file, if applicable.
    :type sheet: Optional[str]
    :ivar key: Unique key to reference the specific configuration, if applicable.
    :type key: Optional[str]
    :ivar file_path: Path(s) to the file(s) to be loaded. Can accept a single file path
                     or a list of file paths.
    :type file_path: Optional[str | list[str]]
    """

    sheet: Optional[str] = None
    key: Optional[str] = None
    file_path: Optional[Union[str|list[str]]]
    file_type: Optional[str]
    use_iterator: bool = False
    chunk_size: int = DEFAULT_CHUNK_SIZE
    query: Optional[str] = None


    def __hash__(self):
        path = self.file_path

        if isinstance(path, list):
            path = json.dumps(path)

        return hash((self.key, self.file_type, self.sheet, path, self.query))