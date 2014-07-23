'''
Created on Jul 19, 2014

@author: raptor
'''
from encryption import decryptor


def main():
    starsFile = "../../../../games/stars27j/games/difficultattempt.h1"
#     starsFile = "../../../../games/stars27j/share/archive/buckstealth/buckstealth.xy"
    
    # Retrieve a list of decrypted blocks from the file
    blocks = decryptor.readFile(starsFile)
    
    # Now do great and amazing things with the blocks!
    print "Printing detected blocks:"
    for block in blocks:
        print block
    
    
    pass


if __name__ == '__main__':
    main()