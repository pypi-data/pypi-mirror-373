import os
import subprocess
import sys

import karabo_cpp


PACKAGE_PATH = os.path.abspath(karabo_cpp.__path__[0])


def get_path(cmd : str) -> str:
    return f"{PACKAGE_PATH}/bin/{cmd}"


def karabo_cppserver() -> None:
    # we cannot use subprocess.xyz here. We need to replace the python process with 
    # the underlying daemontools command for it to run correctly!
    os.execvp(get_path("karabo-cppserver"), sys.argv)


def karabo_brokermessagelogger() -> None:
    # we cannot use subprocess.xyz here. We need to replace the python process with 
    # the underlying daemontools command for it to run correctly!
    os.execvp(get_path("karabo-brokermessagelogger"), sys.argv)


def karabo_brokerrates() -> None:
    # we cannot use subprocess.xyz here. We need to replace the python process with 
    # the underlying daemontools command for it to run correctly!
    os.execvp(get_path("karabo-brokerrates"), sys.argv)
