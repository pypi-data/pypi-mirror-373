import pathlib, dataclasses

@dataclasses.dataclass
class FileBaseConfigData:
    root_directory: pathlib.Path
    server_folder : bool
    
    def __post_init__(self):
        # Normalize root_directory to a pathlib.Path and resolve it
        root_path = self.root_directory
        if not isinstance(root_path, pathlib.Path):
            root_path = pathlib.Path(root_path)
        root_path = root_path.resolve()

        if not root_path.is_dir():
            raise NotADirectoryError(f"Root path is not a directory: {root_path}")

        self.root_directory = root_path
        # Ensure server_folder is a boolean
        self.server_folder = bool(self.server_folder)