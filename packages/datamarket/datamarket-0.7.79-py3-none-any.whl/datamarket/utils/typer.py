########################################################################################################################
# IMPORTS

import json

import typer
from typing_extensions import Annotated

########################################################################################################################
# TYPES

class Dict(dict):
    def __init__(self, value: str):
        super().__init__(json.loads(value))

    def __repr__(self):
        return f"Dict({super().__repr__()})"


def parse_json_dict(value: str) -> Dict:
    try:
        return Dict(value)
    except json.JSONDecodeError as err:
        raise ValueError(f"Invalid JSON string: {value}") from err


DictArg = Annotated[Dict, typer.Argument(parser=parse_json_dict)]
DictOpt = Annotated[Dict, typer.Option(parser=parse_json_dict)]