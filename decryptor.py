'''
Created on Jul 7, 2014

@author: dbuck
'''
import logging


# loggingLevel = logging.INFO
loggingLevel = logging.DEBUG
logging.basicConfig(level=loggingLevel)


"""
Generic Block class for Stars! blocks
"""
class Block:
    def __init__(self, typeId, size):
        self.data = bytearray()
        self.decryptedData = bytearray()
        self.typeId = typeId
        self.size = size
        
        pass


class FileHeaderBlock:
    def __init__(self, data):
        playerData = read16(data, 12)
        
        self.salt = playerData >> 5   # First 11 bits
        self.gameId = read32(data, 4)
        self.turn = read16(data, 10)
        self.playerIndex = playerData & 0x1F  # Last 5 bits
        self.shareware = (data[15] >> 4) & 1
        
        pass
    
    
class PlanetsBlock:
    def __init__(self, data):
        self.planetCount = read16(data, 10)
        self.planetsData = None
        
        pass


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


"""
Reads a 16 bit integer from a byte array.

The bytes are swapped because the byte stream is little endian
"""
def read16(byteArray, byteIndex):
    
    return (byteArray[byteIndex+1] << 8) | byteArray[byteIndex]


"""
Reads a 32 bit integer from a byte array.

The bytes are swapped because that's what's needed (I'm unsure if 32 bit
integer is written in this order on a Win16 platform)

Swapped as D C B A
"""
def read32(byteArray, byteIndex):
    
    return (byteArray[byteIndex+3] << 24) | (byteArray[byteIndex+2] << 16) | (byteArray[byteIndex+1] << 8) | byteArray[byteIndex]
    
    

def parseBlock(fileBytes, offset):

    blockHeader = read16(fileBytes, offset)
    
    typeId = blockHeader >> 10   # First 6 bits
    size = blockHeader & 0x3FF # Last 10 bits
            
    block = Block(typeId, size)
    
    block.data = fileBytes[offset+2:offset+2+size]
    
    return block;



def readFile(starsFile):
    with open(starsFile, "rb") as f:
        raw = f.read()
        
        fileBytes = bytearray(raw)
        
    
    blocks = []
    decryptor = Decryptor()
        
    offset = 0
    while offset < len(fileBytes):
        block = parseBlock(fileBytes, offset)
        
        # Advance our read index to skip the block header
        offset = offset + block.size + 2;
        
        # Do the decryption!  (handle exceptions)
        if block.typeId == 8:  # FileHeaderBlock
            h = FileHeaderBlock(block.data)
            decryptor.initDecryption(h.salt, h.gameId, h.turn, h.playerIndex, h.shareware)
            
        elif block.typeId == 7:  # PlanetsBlock
            block.decryptedData = decryptor.decryptBytes(block.data)
            
            p = PlanetsBlock(block.decryptedData)
            length = p.planetCount * 4
            
            p.planetsData = block.decryptedData[offset:offset+length]
            
            offset = offset + length
            
        else:  # Everything else decrypt like normal for now
            data = block.data
            block.decryptedData = decryptor.decryptBytes(data)
        
    
        logging.debug("typeId: " + str(block.typeId) + "; size: " + str(block.size) + "; data: ")
        logging.debug(list(block.data))
        logging.debug("decrypted data:")
        logging.debug(list(block.decryptedData))
        
    
        blocks.append(block)
        
    pass



def testing():
    starsFile = "/home/dbuck/games/stars27j/games/buckstealth.xy"
    
    readFile(starsFile)

"""
    test = [153, 84, 194, 234, 20, 219, 240, 41, 180, 5, 18, 236, 
            188, 38, 25, 0, 255, 118, 225, 61, 189, 175, 85, 56, 68, 30, 
            59, 71, 149, 252, 81, 230, 141, 114, 1, 37, 160, 168, 29, 207, 
            20, 53, 185, 174, 72, 162, 170, 13, 83, 189, 246, 28, 243, 110, 
            212, 197, 58, 234, 61, 57, 56, 51, 86, 40 ]

    d = Decryptor()
    d.initDecryption(1635, 12170179, 0, 31, 0)
    
    output = d.decryptBytes(byteArray[20:84])
    
    print len(output)
    print list(output)
"""



def main():
    testing()
    
    pass


if __name__ == '__main__':
    main()