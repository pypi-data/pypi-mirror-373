'''
 script to create
 - cloner.py
 
 Bjoern Annighoefer 2023
'''

import os
import shutil

if __name__ == "__main__":
    GEN_FILE = "../cloner.py"
    GEN_TEMP = "cloner.py.mako"
    
    os.system("python -m eoq3conceptsgen.generatefromconceptscli -i %s -o %s"%(GEN_TEMP,GEN_FILE))