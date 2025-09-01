'''
 script to create
 - conceptwalker.py
 
 Bjoern Annighoefer 2023
'''

import os
import shutil

if __name__ == "__main__":
    GEN_FILE = "../conceptwalker.py"
    GEN_TEMP = "conceptwalker.py.mako"
    
    os.system("python -m eoq3conceptsgen.generatefromconceptscli -i %s -o %s"%(GEN_TEMP,GEN_FILE))