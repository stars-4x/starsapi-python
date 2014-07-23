'''
Created on Jul 19, 2014

@author: raptor
'''

class Block():
    '''
    Generic Block class for Stars! blocks
    '''
    def __init__(self, typeId, size, data):
        self.typeId = typeId
        self.size = size
        self.data = data
        
    
    # Dump block
    def __str__(self):
        return """%s - typeId: %d; size: %d; data:
%s""" % (self.__class__.__name__, self.typeId, self.size, list(self.data))
