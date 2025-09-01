import pathlib, dataclasses

@dataclasses.dataclass
class QuantifyConfigData:
    quantify_directory: pathlib.Path
    set_up : str