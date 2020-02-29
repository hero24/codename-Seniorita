import os

"""
    Environment system independent module
    Return environmental variables and their values
    
    "Time passes irrevocably" ~ Virgil
"""

def run(**args):
    print("[*] In environment module")
    return str(os.environ)
