import platform

tcpPrefix = "tcp://0.0.0.0:"
ipcPrefix = "ipc:///tmp/feeds/"

def _getAddress(port, ipc):
    if ipc:
        return ipcPrefix + port
    else:
        system = platform.system()
        if system == "Windows":
            return "tcp://localhost:" + port
        else:
            return tcpPrefix + port