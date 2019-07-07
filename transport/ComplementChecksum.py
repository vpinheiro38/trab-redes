import pickle

def splitstring (segmentInput):                     # Separates the higher and the lower bits of a segment into two numbers. 
                                                    # The second number might receive additional ending bits to make both 
                                                    # halves the same size
    
    # segment = "{0:b}".format(segmentInput)          # Converts into a string (makes the high/low bit split easier).
    # firsthalf = ""
    # secondhalf = ""
    # for n in range(0, len(segment)):                # Separates the bits to their appropriate halves
    #     if (n <= int(len(segment)/2)):
    #         firsthalf += segment[n]
    #     else:
    #         secondhalf += segment[n]

    # while (len(firsthalf) > len(secondhalf)):       # Increments the length of the second one to equal their lengths
    #     secondhalf += '0'

    # firsthalfOutput = int(firsthalf, 2)             # The results are converted back to integers
    # secondhalfOutput = int(secondhalf, 2)           # The results are converted back to integers
    
    # return firsthalfOutput, secondhalfOutput

    segBytes = bin(segmentInput)
    firsthalf, secondhalf = segBytes[:round(len(segBytes)/2)], segBytes[round(len(segBytes)/2):]

    return int(firsthalf, 2), int(secondhalf, 2)

def sumsegments (first, second):                    # Adds two segments together. Should there be a carry beyond the bit 
                                                    # lengths of the original terms, it is removed from the highest bit 
                                                    # position and added in as a least significant bit
                                                 
    sumofhalves = first + second                    # Adds the segments

    if (sumofhalves.bit_length() > first.bit_length()):
        sumofhalves = -(2**(sumofhalves.bit_length()-1)) + sumofhalves + 1  #Carries the extra highest bit to add 
                                                                            # it to the least one if necessary
    return sumofhalves

def complement1 (value):                            # Gets the one complement
    mask = 2**(value.bit_length())-1                # Creates a mask that only bits 1, with the length of the number 
                                                    # from which to obtain the 1's complement (e.g: 1111111111111111)
    complement1sum = mask ^ value                   # The XOR operation of a value and its mask gives its complement
    return complement1sum
        
def makeChecksum(segment):
    segInt = int(pickle.dumps(segment).hex(), 16)
    return makeChecksumAsInt(segInt)

def makeChecksumAsInt (segmentInt):                                         # Makes the checksum. Takes the segment as an int.
    firsthalf, secondhalf = splitstring (segmentInt)                        # Splits the segment into two numbers to get the 1 compliment of the sum
    complement1sum = complement1 (sumsegments (firsthalf, secondhalf))      # Gets the one compliment of the sum

    return complement1sum

def isCorrupt(segment, complement1sum):
    segInt = int(pickle.dumps(segment).hex(), 16)

    return isCorruptAsInt(segInt, complement1sum)

def isCorruptAsInt(segmentInt, complement1sum):             # Tests the checksum. Takes the segmentand the comlement as ints.
    firsthalf, secondhalf = splitstring (segmentInt)   # Splits the segment into two numbers to get the 1 compliment of the sum
    complement1sum = complement1 (sumsegments (sumsegments(firsthalf, secondhalf), complement1sum)) # Gets the one compliment of the sum

    mask = 2**(complement1sum.bit_length())-1       # Creates a mask that only bits 1, with the length of the number 

    if (complement1sum ^ mask == 0): return False   # Tests if the compliment has only bits 1. If so, it's valid.
    else: return True                               # If not, it is corrupt