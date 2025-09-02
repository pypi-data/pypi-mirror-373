# fix error explained in https://github.com/pytorch/pytorch/issues/131662
import os
import sys


def fix_error_torch():
    """
    deprecated
    """
    return
    # if ptyhon!=3.11 ignore
    if sys.version_info[0]!=3:
        return
    if sys.version_info[1] != 11:
        return
    if sys.platform!="win32":
        return
    dest=os.path.dirname(os.__file__).replace("\\","/")+"/site-packages/torch/lib/libomp140.x86_64.dll"
    if os.path.exists(dest):
        return
    source=os.path.dirname(__file__).replace("\\","/")+"/libomp140.x86_64.dll"
    with open(source, 'rb') as src, open(dest, 'wb') as dst:
        dst.write(src.read())
fix_error_torch()

