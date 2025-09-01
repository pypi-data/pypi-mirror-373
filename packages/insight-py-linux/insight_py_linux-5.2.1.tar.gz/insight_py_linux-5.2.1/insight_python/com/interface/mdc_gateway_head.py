#!/usr/bin/python3
import struct
from sys import platform as _sys_info
try:
    size = struct.calcsize('P')
except struct.error:
    # Older installations can only query longs
    size = struct.calcsize('l')
if _sys_info.__contains__("win32") or _sys_info.__contains__("Win32"):
    from sys import winver as _version_info
    print(_sys_info)
    print("python version :"+_version_info)
    # 64bits system
    if size == 8:
        pass
    # 32bits system
    elif size == 4:
        pass
else:
    import sys
    print(_sys_info)
    print('python version:' + sys.version)

    if sys.version.__contains__("3.6"):
        from ..libs.linux.python36 import mdc_gateway_client as mdc_gateway_client
    elif sys.version.__contains__("3.7"):
        from ..libs.linux.python37 import mdc_gateway_client as mdc_gateway_client
    elif sys.version.__contains__("3.8"):
        from ..libs.linux.python38 import mdc_gateway_client as mdc_gateway_client
    elif sys.version.__contains__("3.9"):
        from ..libs.linux.python39 import mdc_gateway_client as mdc_gateway_client
    elif sys.version.__contains__("3.10"):
        from ..libs.linux.python310 import mdc_gateway_client as mdc_gateway_client
