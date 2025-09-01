'''

2022 Bjoern Annighoefer
'''

from uuid import uuid4 #needed to generate session IDs

SESSION_ID_LENGTH = 36 #uuid4 standard

def GenerateSessionId()->str:
    return str(uuid4())