import win32gui
import win32ui
import win32con
import win32api
import os

"""
    Screen Shotter for Windows module
    Returns a current screen capture.
    Dependencies:
        pywin32
    
    "There are two sides to every story, and then there are the screenshots"
         ~ Unknown 
"""

TMP = "c:\\WINDOWS\\Temp\\screenshot.bmp"

def run(**args):
    hdesktop = win32gui.GetDesktopWindow()

    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)

    mem_dc = img_dc.CreateCompatibleDC()

    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)

    mem_dc.SelectObject(screenshot)
    mem_dc.BitBlt((0,0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

    screenshot.SaveBitmapFile(mem_dc, TMP)
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())
    f = open(TMP, "rb")
    fcnt = f.read()
    f.close()
    os.remove(TMP)
    return fcnt
