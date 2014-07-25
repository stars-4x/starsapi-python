'''
Created on Jul 19, 2014

@author: raptor
'''
from encryption import decryptor


def main():
    starsFile = "../../../../games/stars27j/games/difficultattempt.xy"
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
    
    
    pass


if __name__ == '__main__':
    main()