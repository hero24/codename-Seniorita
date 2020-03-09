import win32con
import win32api
import win32security

import wmi
import sys
import os
from time import time

"""
    "I'm breaking in, shaping up, then checking out on the prison bus" ~ Imagine Dragons@Radioactive
"""

def log_to_file(msg, csv=[]):
    csv.append("%s\r\n" % msg)
    return csv


def get_process_privilages(pid):
    priv_list = ""
    try:
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
        htok  = win32security.OpenProcessToken(hproc, win32con.TOKEN_QUERY)
        privs = win32security.GetTokenInformation(htok, win32security.TokenPrivileges)
        for i in privs:
            if i[1] == 3:
                priv_list += "%s|" % win32security.LookupPrivilegeName(None, i[0])
    except Exception as e:
        priv_list += "N/A"
    return priv_list


def run(**args):
    if 'runtime' not in args:
        return
    mx_tm = int(args['runtime'])
    csv = log_to_file("Time, User, Executable, CommandLine, PID, Parent PID, Privilages")
    c = wmi.WMI()
    process_watcher = c.Win32_Process.watch_for("creation")
    strt_tm = time()
    while (time()-strt_tm) <= mx_tm:
        try:
            new_process = process_watcher()
            proc_owner  = new_process.GetOwner()
            proc_owner  = "%s\\%s" % (proc_owner[0], proc_owner[2])
            create_date = new_process.CreationDate
            executable  = new_process.ExecutablePath
            cmdline     = new_process.CommandLine
            pid         = new_process.ProcessId
            parent_pid  = new_process.ParentProcessId
            privilages  = get_process_privilages(pid)

            log_msg = "%s, %s, %s, %s, %s, %s, %s" % (
                  create_date, proc_owner, executable,
                  cmdline, pid, parent_pid, privilages
                 )
            log_to_file(log_msg)
        except Exception as e:
            log_to_file(str(e))
    return "".join(csv)
