'''
 Bjoern Annighoefer 2024
'''

from .cmdstream import EoqFileInStream

def ValidateEoqFile(infile:str)->None:
    '''Validates the syntax of an EOQ file
    '''
    tester = EoqFileInStream()
    tester.Begin()
    tester.LoadEoqFile(infile)
    tester.Flush()