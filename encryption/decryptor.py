'''
Created on Jul 7, 2014

@author: raptor
'''
import logging

import util
import blocks
from blocks.FileHeaderBlock import FileHeaderBlock
from blocks.PlanetsBlock import PlanetsBlock


# loggingLevel = logging.INFO
loggingLevel = logging.DEBUG

logging.basicConfig(level=loggingLevel)

    

"""
Stars random number generator class used for encryption
"""
class StarsRandom:
    def __init__(self, seed1, seed2, initRounds):
        self.seedA = seed1
        self.seedB = seed2
        self.rounds = initRounds
        
        logging.debug("seed1: " + str(self.seedA) + "; seed2: " + str(self.seedB))
        logging.debug("rounds: " + str(self.rounds))
        
        # Now initialize a few rounds
        for _ in xrange(initRounds):
            self.nextRandom()
        
    def nextRandom(self):
        # First, calculate new seeds using some constants
        seedApartA = (self.seedA % 53668) * 40014
        seedApartB = (self.seedA / 53668) * 12211 # integer division OK
        newSeedA = seedApartA - seedApartB;
        
        seedBpartA = (self.seedB % 52774) * 40692
        seedBpartB = (self.seedB / 52774) * 3791
        newSeedB = seedBpartA - seedBpartB
        
        # If negative add a whole bunch (there's probably some weird bit math
        # going on here that the disassembler didn't make obvious)
        if newSeedA < 0:
            newSeedA += 0x7fffffab

        if newSeedB < 0:
            newSeedB += 0x7fffff07;
        
        # Set our new seeds
        self.seedA = newSeedA;
        self.seedB = newSeedB;
        
        # Generate "random" number.  This will fit into an unsigned 32bit integer
        randomNumber = self.seedA - self.seedB
        if self.seedA < self.seedB:
            randomNumber += 0x100000000l;  # 2^32

#         print "seed1: " + str(self.seedA) + "; seed2: " + str(self.seedB)
#         print "rand: " + str(randomNumber)
        
        # Now return our random number
        return randomNumber;
        
        
        
class Decryptor():
    def __init__(self):
        self.random = None
        
        # Initial seeds for our Random Number Generator
        # 279 is not prime
        self.primes = [ 
                3, 5, 7, 11, 13, 17, 19, 23, 
                29, 31, 37, 41, 43, 47, 53, 59,
                61, 67, 71, 73, 79, 83, 89, 97,
                101, 103, 107, 109, 113, 127, 131, 137,
                139, 149, 151, 157, 163, 167, 173, 179,
                181, 191, 193, 197, 199, 211, 223, 227,
                229, 233, 239, 241, 251, 257, 263, 279,
                271, 277, 281, 283, 293, 307, 311, 313 
        ]
        
        pass
    
    
    def initDecryption(self, salt, gameId, turn, playerIndex, shareware):
        # Use two prime numbers as random seeds.
        # First one comes from the lower 5 bits of the salt
        index1 = salt & 0x1F;
        # Second index comes from the next higher 5 bits
        index2 = (salt >> 5) & 0x1F;
        
        # Adjust our indexes if the highest bit (bit 11) is set
        # If set, change index1 to use the upper half of our primes table
        if (salt >> 10) == 1:
            index1 += 32
        # Else index2 uses the upper half of the primes table
        else:
            index2 += 32
        
        # Determine the number of initialization rounds from 4 other data points
        # 0 or 1 if shareware (I think this is correct, but may not be - so far
        # I have not encountered a shareware flag)
        part1 = shareware
        
        # Lower 2 bits of player number, plus 1
        part2 = (playerIndex & 0x3) + 1;
        
        # Lower 2 bits of turn number, plus 1
        part3 = (turn & 0x3) + 1;
        
        # Lower 2 bits of gameId, plus 1
        part4 = (gameId & 0x3) + 1;
        
        # Now put them all together, this could conceivably generate up to 65 
        # rounds  (4 * 4 * 4) + 1
        rounds = (part4 * part3 * part2) + part1;
        
        # Now initialize our random number generator
        seed1 = self.primes[index1]
        seed2 = self.primes[index2]
        
        self.random = StarsRandom(seed1, seed2, rounds)
        
        pass
    
    
    def decryptBytes(self, byteArray):
        # Add padding to 4 bytes
        size = len(byteArray)
        paddedSize = (size + 3) & ~3  # This trick only works on powers of 2
        padding = paddedSize - size
        
        for _ in xrange(padding):
            byteArray.append(0x0)
        
        decryptedBytes = bytearray()
        
        # Now decrypt, processing 4 bytes at a time
        for i in xrange(0, paddedSize, 4):   
            # Swap bytes using indexes in this order:  4 3 2 1
            chunk = (byteArray[i+3] << 24) | (byteArray[i+2] << 16) | (byteArray[i+1] << 8) | byteArray[i];
           
           
#             print "chunk  : " + hex(chunk)
            
            # XOR with a random number
            decryptedChunk = chunk ^ self.random.nextRandom()
            
#             print "dechunk: " + hex(decryptedChunk)
            
            # Write out the decrypted data, swapped back
            decryptedBytes.append(decryptedChunk & 0xFF)
            decryptedBytes.append((decryptedChunk >> 8)  & 0xFF)
            decryptedBytes.append((decryptedChunk >> 16)  & 0xFF)
            decryptedBytes.append((decryptedChunk >> 24)  & 0xFF)
            
        # Strip off any padding
        for _ in xrange(padding):
            byteArray.pop()
            decryptedBytes.pop()

        return decryptedBytes
        
        pass

    

def parseBlock(fileBytes, offset):
    '''
    This returns the 3 relevant parts of a block: typeId, size, raw data
    '''
    blockHeader = util.read16(fileBytes, offset)
    
    typeId = blockHeader >> 10   # First 6 bits
    size = blockHeader & 0x3FF # Last 10 bits
            
    data = fileBytes[offset+2:offset+2+size]
    
    
    return (typeId, size, data);



def readFile(starsFile):
    with open(starsFile, "rb") as f:
        raw = f.read()
        
        fileBytes = bytearray(raw)
        
    
    blockList = []
    decryptor = Decryptor()
        
    offset = 0
    while offset < len(fileBytes):
        # Get block info and data
        (typeId, size, data) = parseBlock(fileBytes, offset)
        
        logging.debug("BLOCK:\ntypeId: %d; size: %d; data:\n%s" % (typeId, size, list(data)))
    
        # Advance our read index to skip the block header
        offset = offset + size + 2;
        
        block = None
        
        # Do the decryption!  (handle exceptions)
        
        # FileHeaderBlock is not encrypted
        if typeId == 8:
            block = FileHeaderBlock(typeId, size, data)
            decryptor.initDecryption(block.salt, block.gameId, block.turn, block.playerIndex, block.shareware)
            
        # Everything else needs to be decrypted
        else:
            decryptedData = decryptor.decryptBytes(data)
            
            logging.debug("decrypted data:\n%s" % (list(decryptedData)))
            
            # PlanetsBlock is an exception in that it has more data tacked onto the end
            if typeId == 7: 
                block = PlanetsBlock(typeId, size, decryptedData)
                
                # A whole bunch of planets data is tacked onto the end of this block
                # We need to determine how much and parse it
                length = block.planetCount * 4  # 4 bytes per planet
                
                block.parsePlanetsData(fileBytes[offset:offset+length])
                
                # Adjust our offset to after the planet data
                offset = offset + length
                
            # Else dynamically create the block for this type
            else:
                block = blocks.createBlock(typeId, size, decryptedData)
                
        # End if

        # Add our block to the list
        blockList.append(block)
        
    return blockList

