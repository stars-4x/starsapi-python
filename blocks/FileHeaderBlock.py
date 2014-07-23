'''
Created on Jul 19, 2014

@author: raptor
'''
from Util import *
from blocks.Block import Block


class FileHeaderBlock(Block):
    def __init__(self, typeId, size, data):
        Block.__init__(self, typeId, size, data)
        
        self.gameId = read32(data, 4)
        self.turn = read16(data, 10)
        playerData = read16(data, 12)
        
        self.salt = playerData >> 5   # First 11 bits
        self.playerIndex = playerData & 0x1F  # Last 5 bits
        self.shareware = (data[15] >> 4) & 1
        
        pass
