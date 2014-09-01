'''
Created on Jul 25, 2014

@author: raptor
'''

"""
Reads a 16 bit integer from a byte array.

The bytes are swapped because the byte stream is little endian
"""

import itertools
import string


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
    

"""
This will hash a password to match the 4 byte hash generated in a PlayerBlock
at data offset 12

FIXME: This fails for strings that generate numbers larger than 32 bits because
of python's implicit integer-overflow-to-long
"""
def hashRacePassword(inputString):
    charList = list(bytearray(inputString))

    # Start with first char value
    output = int(charList[0])
    
    # Now perform an arithmetic operation on each of the following char values
    for index, char in enumerate(charList[1:]):
        # if the character index is odd, multiply it against our hash
        if index & 1 == 0:
            output *= int(char)
        # else add it to our hash
        else:
            output += int(char)

    return output


"""
Guesses a race file's password by brute force.

NOTE: you will burn out your CPU if you have too liberal of settings here

Because the hashing algorithm is incredibly weak, this will most likely find
a number of alternative strings to use instead of the original password

Used like so:
   guessRacePassword(hash [,maxLength [,charset]])
   
maxLength = the length of characters in the password.

matchesAllowed = quit after this many matches are found

charset = array of ascii values to check, some common arrays:

    
Adapted from:
    https://stackoverflow.com/a/11747419
"""
def guessRacePassword(hash, maxLength = 5, matchesAllowed = 1, charset = string.ascii_lowercase):
    
    def bruteforce(charset):
        return (''.join(candidate)
            for candidate in itertools.chain.from_iterable(itertools.product(charset, repeat=i)
            for i in range(1, maxLength + 1)))
    
    matches = []
    
    for word in bruteforce(list(charset)):
        possibleHash = hashRacePassword(word)
        
        # We've reached our limit
        if len(matches) == matchesAllowed:
            break
        
        if (possibleHash == hash):
            matches.append(word)
            print "Found match [%s]" % word
            
    pass
