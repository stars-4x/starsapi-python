'''
Created on Jul 19, 2014

@author: raptor
'''
from util import *
from blocks.Block import Block


class FileHeaderBlock(Block):
    def __init__(self, typeId, size, data):
        Block.__init__(self, typeId, size, data)
        
        self.magic = str(data[0:4])
        self.gameId = read32(data, 4)
        
        versionData = read16(data, 8)
        self.versionMajor = versionData >> 12          # First 4 bits
        self.versionMinor = (versionData >> 5) & 0x7F  # Middle 7 bits
        self.versionIncrement = versionData & 0x1F     # Last 5 bits
        
        self.turn = read16(data, 10)
        self.year = 2400 + self.turn
        
        playerData = read16(data, 12)
        self.salt = playerData >> 5           # First 11 bits
        self.playerIndex = playerData & 0x1F  # Last 5 bits
        
        flags = data[15]
        
        self.turnSubmitted = (flags & (1 << 0)) == 1
        self.hostUsing =     (flags & (1 << 1)) == 1
        self.multipleTurns = (flags & (1 << 2)) == 1
        self.gameOver =      (flags & (1 << 3)) == 1
        self.shareware =     (flags & (1 << 4)) == 1
        
        pass
