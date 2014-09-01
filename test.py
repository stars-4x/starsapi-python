'''
Created on Jul 19, 2014

@author: raptor
'''
import array
import string

from encryption import decryptor
import util




def main():
    starsFile = "../../../../games/stars27j/games/test3.r1"
#     starsFile = "../../../../games/stars27j/games/difficultattempt.h1"
#     starsFile = "../../../../games/stars27j/games/Game.xy"
#     starsFile = "../../../../games/stars27j/games/Game.h1"
#     starsFile = "../../../../games/stars27j/games/Game.m1"
#     starsFile = "../../../../games/stars27j/games/Game.hst"
    
    # Retrieve a list of decrypted blocks from the file
    blocks = decryptor.readFile(starsFile)
    
    # Now do great and amazing things with the blocks!
    print "Printing detected blocks:"
    for block in blocks:
        print block
        if block.typeId == 7:
            print block.planets
            print (bin(block.gameSettings)[2:] ).zfill(16)
            

    # Test race passwords and hashing
#     testRaceHash()

    pass


def testRaceHash():
    # The AI password and alternatives that show the weakness in the hash:
    print util.hashRacePassword("fymmgsd")
    print util.hashRacePassword("yfmmgsd")
    print util.hashRacePassword("iymtfi")
    print util.hashRacePassword("viewai")
    
    # This shows python's implicit integer overflow protection by returning a long integer :-/
    print util.hashRacePassword("aaaaaaaa")
    
    # Brute force the password
    util.guessRacePassword(util.read32([67, 18, 14, 0], 0), 5, 1, string.ascii_lowercase)

    # Current best found multiplayer AI password
    print util.hashRacePassword("TV+OdX+U")
    
    # Attempt to find a multiplayer AI password
#     util.guessRacePassword(4294967295, 5, 5, string.letters)
    

if __name__ == '__main__':
    main()