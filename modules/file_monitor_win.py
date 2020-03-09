import tempfile
import threading
import win32file
import win32con as wcon
import os
from time import time
from time import sleep
from itertools import chain

"""
    "I'm waking up, I feel it in my bones
     Enough to make my systems blow" ~ Imagine Dragons@Radioactive
"""

dirs_to_monitor = ["C:\\WINDOWS\\Temp", tempfile.gettempdir()]
output = []
action_log = lambda *args: output[args[3]].append("[ %s ] %s %s" % args[:3])


def modified_log(*args):
    action_log(*args)
    action_log("vvv", "Dumping contents", "...", args[3])
    with open(args[2], "rb") as f:
        contents = f.read()
        output[args[3]].append(contents)
        action_log("[^^^]", "Dump", "complete.", args[3])
    

ACTIONS = (
    (1, action_log,  ["+", "Created"]),
    (2, action_log,  ["-", "Deleted"]),
    (3, modified_log,["*", "Modified"]),
    (4, action_log,  [">", "Renamed from"]),
    (5, action_log,  ["<", "Renamed to"])
)


def start_monitor(watch_path, mxtm, id_):
    FILE_LIST_DIR = 0x0001
    h_dir = None
    try:
        h_dir = win32file.CreateFile(
            watch_path,
            FILE_LIST_DIR,
            wcon.FILE_SHARE_READ | wcon.FILE_SHARE_WRITE | wcon.FILE_SHARE_DELETE,
            None,
            wcon.OPEN_EXISTING,
            wcon.FILE_FLAG_BACKUP_SEMANTICS,
            None
        )
    except Exception as e:
        output[id_].append(str(e))
        return
    
    strttm = time()
    while (strttm - time()) <= mxtm:
        try:
            results = win32file.ReadDirectoryChangesW(
                h_dir,
                1024,
                True,
                wcon.FILE_NOTIFY_CHANGE_FILE_NAME  |
                wcon.FILE_NOTIFY_CHANGE_DIR_NAME   |
                wcon.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                wcon.FILE_NOTIFY_CHANGE_SIZE       |
                wcon.FILE_NOTIFY_CHANGE_LAST_WRITE |
                wcon.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None
            )

            for action, fname in results:
                full_filename = os.path.join(watch_path, fname)

                for flag, func, fargs in ACTIONS:
                    if action == flag:
                        func(*fargs, full_filename, id_)
                        break
                else:
                    action_log("???", "Unknown:", full_filename, id_)
        except Exception as e:
            output[id_].append(str(e))
        return output


def run(**args):
    if 'dirmon' not in args or 'runtime' not in args:
        return
    global output
    output = [[] for _ in args['dirmon']]
    ts = []
    for id_, path in enumerate(args['dirmon']):
        output[id_].append("Spawning monitoring thread for path: %s" % path)
        monitor_thread = threading.Thread(target=start_monitor, args=(path,args['runtime'], id_))
        monitor_thread.start()
        ts.append(monitor_thread)
    for t in ts:
        t.join()

    return "\r\n".join(list(chain(*output)))
