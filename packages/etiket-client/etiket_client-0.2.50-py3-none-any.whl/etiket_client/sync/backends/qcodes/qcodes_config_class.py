import pathlib, dataclasses, sqlite3
from typing import Optional

@dataclasses.dataclass
class QCoDeSConfigData:
    database_directory: pathlib.Path
    set_up : str
    extra_attributes : Optional[dict] = dataclasses.field(default_factory=dict)
    
    def __post_init__(self):
        """
        Post-initialization processing to validate the database directory.
        Note it is a file and not a directory, but this is how it is used in the code... (settings are stored in the database...)
        """
        self.database_directory = pathlib.Path(self.database_directory).resolve()
        
        # check if path exists and ends with .db
        if not self.database_directory.exists():
            raise ValueError(f"Database directory {self.database_directory} does not exist.")
        if self.database_directory.suffix != ".db":
            raise ValueError(f"A qCoDeS database should be a .db file, not {self.database_directory.suffix}.")
        
        # test with sqlite3
        try:
            conn = sqlite3.connect(self.database_directory)
            conn.close()
        except sqlite3.Error as e:
            raise ValueError(f"Error connecting to database {self.database_directory}: {e}")