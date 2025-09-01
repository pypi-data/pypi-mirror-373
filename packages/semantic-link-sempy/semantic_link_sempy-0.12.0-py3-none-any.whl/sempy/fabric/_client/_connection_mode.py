from enum import Enum, auto


class ConnectionMode(Enum):
    XMLA = auto()
    REST = auto()
    ONELAKE_IMPORT_DATASET = auto()
    DIRECTLAKE_DATASET = auto()


def parse_connection_mode(mode: str) -> ConnectionMode:
    mode = mode.lower()
    if mode == "xmla":
        return ConnectionMode.XMLA
    elif mode == "rest":
        return ConnectionMode.REST
    # TODO: need to wait for marketing name
    elif mode == "onelake":
        return ConnectionMode.ONELAKE_IMPORT_DATASET
    elif mode == "directlake":
        return ConnectionMode.DIRECTLAKE_DATASET
    else:
        raise ValueError(f"Invalid connection mode '{mode}'")
