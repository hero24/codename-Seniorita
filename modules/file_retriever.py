import os
import fnmatch
import zlib


def compress_(filename, location):
    with open(location, "rb") as f:
        return filename, zlib.compress(f.read())

def run(**args):
    if 'extension' not in args:
        args['extension'] = ""
    if 'dir' not in args:
        args['dir'] = "C:\\"
    files = []
    for parent, dir, filenames in os.walk(args['dir']):
        for filename in fnmatch.filter(filenames, "*%s"%args['extension']):
            doc_path = os.path.join(parent, filename)
            files += [compress_(filename, doc_path)]
    return files
