import tempfile
import threading
import win32file
import win32con as wcon
import os

# To fix: return collected data.
#

dirs_to_monitor = ["C:\\WINDOWS\\Temp", tempfile.gettempdir()]
output = []
action_log = lambda *args: output.append("[ %s ] %s %s" % args)

def modified_log(*args):
    action_log(args[0], args[1], args[2])
    action_log("vvv", "Dumping contents", "...")
    with open(args[2], "rb") as f:
        contents = f.read()
        output.append(contents)
        action_log("[^^^]", "Dump", "complete.")
    

ACTIONS = (
    (1, action_log,  ["+", "Created"]),
    (2, action_log,  ["-", "Deleted"]),
    (3, modified_log,["*", "Modified"]),
    (4, action_log,  [">", "Renamed from"]),
    (5, action_log,  ["<", "Renamed to"])
)

def start_monitor(watch_path):
    FILE_LIST_DIR = 0x0001
    h_dir = win32file.CreateFile(
        watch_path,
        FILE_LIST_DIR,
        wcon.FILE_SHARE_READ | wcon.FILE_SHARE_WRITE | wcon.FILE_SHARE_DELETE,
        None,
        wcon.OPEN_EXISTING,
        wcon.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    while 1:
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
                        func(*fargs, full_filename)
                        break
                else:
                    action_log("???", "Unknown:", full_filename)
        except Exception as e:
            output.append(e)

def run(**args):
    if 'dirmon' not in args:
        return
    for path in args['dirmon']:
        monitor_thread = threading.Thread(target=start_monitor, args=(path,))
        output.append("Spawning monitoring thread for path: %s" % path)
        monitor_thread.start()
