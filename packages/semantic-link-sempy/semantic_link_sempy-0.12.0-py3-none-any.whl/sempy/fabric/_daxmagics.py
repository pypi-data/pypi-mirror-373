from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring)
from typing import Optional
import sempy.fabric as fabric


def unquote(arg) -> Optional[str]:
    if arg is None:
        return None

    if ((arg.startswith("'") and arg.endswith("'")) or
       (arg.startswith('"') and arg.endswith('"'))):
        arg = arg[1:-1]

    return arg


@magics_class
class DAXMagics(Magics):

    def __init__(self, shell: InteractiveShell):
        super(DAXMagics, self).__init__(shell)

    @cell_magic
    @magic_arguments()
    @argument("-w", "--workspace")
    @argument("-o", "--output")
    @argument("arg", type=str)
    def dax(self, line: str, cell: str):
        """
        Evaluate a DAX query and return the results as a FabricDataFrame.
        """
        # parse arguments
        args = parse_argstring(self.dax, line)

        dataset = unquote(args.arg)
        workspace = unquote(args.workspace)

        # variable expansion
        cell = cell.format(**self.shell.user_ns)  # type: ignore[attr-defined]

        # evaluate the dax
        df = fabric.evaluate_dax(dataset, cell, workspace=workspace)

        # store in output variable (following https://ipython.readthedocs.io/en/stable/interactive/magics.html#cellmagic-script)
        if args.output:
            self.shell.user_ns[args.output] = df  # type: ignore[attr-defined]

        return df
