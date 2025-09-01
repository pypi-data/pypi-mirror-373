import os
import sys
from pathlib import Path
from typing import List, Optional, Union


def _init_dotnet_runtime(config: Union[str, Path],
                         assemblies: Optional[Union[List[str], List[Path]]] = None):
    """
    Initialize dotnet runtime with given config file, and load all specified assemblies.
    """
    from clr_loader import get_coreclr
    from pythonnet import set_runtime, get_runtime_info

    if get_runtime_info() is None:
        set_runtime(get_coreclr(runtime_config=os.fspath(config)))

    if assemblies is None:
        return

    import clr

    sys_path = set(sys.path)
    assemblies = [os.fspath(assembly) for assembly in assemblies]
    for dll_path in assemblies:
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"Assembly file not found: {dll_path}")
        dll_dir = os.path.dirname(dll_path)
        if dll_dir not in sys_path:
            sys.path.append(dll_dir)
        clr.AddReference(dll_path)
