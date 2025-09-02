import os
from typing import List, Optional, Tuple

from httomolibgpu import cupywrapper

cp = cupywrapper.cp


def load_cuda_module(
    file: str,
    name_expressions: Optional[List[str]] = None,
    options: Tuple[str, ...] = tuple(),
) -> cp.RawModule:
    """Load a CUDA module file, i.e. a .cu file, from the file system,
    compile it, and return is as a CuPy RawModule for further
    processing.
    """

    dir = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(dir, file + ".cu")
    # insert a preprocessor line directive to assist compiler errors (so line numbers show correctly in output)
    escaped = file.replace("\\", "\\\\")
    code = '#line 1 "{}"\n'.format(escaped)
    with open(file, "r") as f:
        code += f.read()

    return cp.RawModule(
        options=("-std=c++11", *options), code=code, name_expressions=name_expressions
    )
