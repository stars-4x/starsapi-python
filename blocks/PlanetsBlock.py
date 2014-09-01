'''
Created on Jul 19, 2014

@author: raptor
'''

from util import *

from blocks import PLANET_NAMES
from blocks.Block import Block


class PlanetsBlock(Block):
    """
    Possible reference for probable meanings of unknown bytes:
       http://wiki.starsautohost.org/wiki/Game.def_files
    """
    def __init__(self, typeId, size, data):
        Block.__init__(self, typeId, size, data)
        
        # TODO bytes 0-3 
        
        self.universeSize = read16(data, 4) # Uses all 16 bits?
        self.density = read16(data, 6)      # Uses all 16 bits?
        self.playerCount = read16(data, 8)  # Uses all 16 bits?
        self.planetCount = read16(data, 10)
        self.startingDistance = read32(data, 12)

        # 16 bits?
        self.gameSettings = read16(data, 16)  
        """
        Determined bits of game settings:
        
        Max Minerals       - 0000000000000001
        Slow tech advances - 0000000000000010
        Accel. BBS play    - 0000000000100000
        No random events   - 0000000010000000
        Computer Alliances - 0000000000010000
        Public scores      - 0000000001000000
        Galaxy Clumping    - 0000000100000000
        Single player (?)  - 0000000000000100
        
        What is bit 4?       0000000000001000
        """
                
        # TODO bytes 18-31
        
        self.gameName = str(data[32:64])
        
        # This is a list of planets with their nameId, x, and y coordinates
        self.planets = []
        
        pass
    
    
    def parsePlanetsData(self, data):
        # Apparently the x coordinate is not stored, rather the offset from the 
        # previous planet in the list is stored...  Also, the X coordinate starts
        # at 1000 as shown in the Stars! viewer.  Oddities everywhere!
        x = 1000
            
        for i in xrange(self.planetCount):
            planetData = read32(data, i*4)
             
            nameId = planetData >> 22       # First 10 bits
            y = (planetData >> 10) & 0xFFF  # Middle 12 bits
            xOffset = planetData & 0x3FF    # Last 10 bits
            x = x + xOffset
            
            name = PLANET_NAMES[nameId]
            
            planetDecodedData = {
                         "id": i,
                         "displayId": i+1,
                         "nameId": nameId,
                         "name": name,
                         "y": y,
                         "x": x,
                         }
            
            self.planets.append(planetDecodedData)

        pass
    
    
    def getPlanets(self):
        return self.planets
    