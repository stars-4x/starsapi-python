'''
Created on Jul 19, 2014

@author: raptor
'''


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
    