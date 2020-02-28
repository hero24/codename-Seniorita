import os
import platform
from io import StringIO
import sys


def run(**args):
    s = []
    system = platform.system()
    s.append("System Family: %s" %  os.name)
    s.append("System: %s" % system)
    s.append("Release: %s" % platform.release())
    s.append("Platform architecture: %s" % platform.machine())
    #net_name = platform.node()
    s.append("Platform: %s" % platform.platform())
    s.append("CPU: %s" %  platform.processor())
    if system.lower() == 'windows':
        rel, ver, csd, ptype = platform.win32_ver()
        s.append("Windows release: %s" % rel)
        s.append("Windows version: %s" % ver)
        s.append("Windows SP: %s" % csd)
        s.append("Proc type: %s" % ptype)
        s.append("Windows Edition: %s" % platform.win32_edition())
        s.append("Is IOT: %s" % platform.win32_is_iot())
    if system.lower() == 'darwin':
        s.append(str(platform.mac_ver()))
    if system.lower() == 'linux':
        s.append("Libc ver: %s %s" % platform.libc_ver())
    old = sys.stdout
    new = sys.stdout = StringIO()
    exec('help("modules")')
    sys.stdout = old
    s.append(new.getvalue())
    return "\n".join(s)

