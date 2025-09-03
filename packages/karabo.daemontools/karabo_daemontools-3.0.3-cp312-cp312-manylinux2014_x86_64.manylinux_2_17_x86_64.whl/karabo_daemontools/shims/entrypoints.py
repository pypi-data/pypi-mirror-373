import os
import subprocess
import sys

import karabo_daemontools

PACKAGE_PATH = os.path.abspath(karabo_daemontools.__path__[0])


def get_path(cmd : str) -> str:
    return f"{PACKAGE_PATH}/bin/{cmd}"


TO_SHIM = [
    "envdir",
    "envini",
    "envuidgid",
    "fghack",
    "multilog",
    "pgrphack",
    "readproctitle",
    "setlock",
    "setuidgid",
    "setuser",
    "softlimit",
    "supervise",
    "svc",
    "svok",
    "svscan",
    "svstat",
    "svup",
    "tai64n",
    "tai64nlocal",
]

def create_runner(cmd : str):
    def runner():
        # we cannot use subprocess.xyz here. We need to replace the python process with 
        # the underlying daemontools command for it to run correctly!
        os.execvp(get_path(cmd), sys.argv)
    return runner

for cmd in TO_SHIM:
    globals()[cmd] = create_runner(cmd)