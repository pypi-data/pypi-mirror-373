'''
 script to create textserializer with antlr4
 
 Bjoern Annighoefer 2024
'''

import os

if __name__ == "__main__":
    os.system('antlr4 ../eoq3.g4 -o ../ -Dlanguage=Python3 -encoding UTF-8 ')