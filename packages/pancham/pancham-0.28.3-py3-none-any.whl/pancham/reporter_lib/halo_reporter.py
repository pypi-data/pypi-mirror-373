import pandas as pd
from halo import Halo

from pancham.reporter import PrintReporter

class HaloReporter(PrintReporter):
    """
    Extends the PrintReporter to provide a visual spinner for loading progress.

    This class uses the `Halo` library to add a spinner animation while a file
    is being loaded. The spinner updates with the progress and indicates when
    the loading is complete. The spinners are managed in a dictionary where
    each spinner is associated with a specific file path.

    :ivar spinners: A dictionary mapping file paths to their corresponding
        `Halo` spinner instances.
    :type spinners: dict[str, Halo]
    """

    def __init__(self, debug: bool = False):
        super().__init__(debug)
        self.spinners: dict[str, Halo] = {}

    def report_start(self, file_path: str):
        self.spinners[file_path] = Halo(text=f"Loading {file_path}", spinner="dots")
        self.spinners[file_path].start()

    def report_end(self, file_path: str, data: pd.DataFrame):
        if file_path in self.spinners:
            self.spinners[file_path].text = f"{file_path} loaded {len(data)} rows"
            self.spinners[file_path].stop()



