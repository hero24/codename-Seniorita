import os

"""
    Dirlister system independent module
    Returns listing of current directory
    
    "The Dutchman sails as its captain commands!" ~ Davy Joness
"""

def run(**args):
    print("[*] In dirlister module.")
    files = os.listdir(".")
    return str(files)
