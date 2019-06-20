from math import floor

def stringXOR(stringX, stringY):    #performs a XOR operation on two binary numbers written as strings
    answer = ""
    for n in range(0, len(stringY)):
        if stringX[n] != stringY[n]: answer += '1'
        else: answer += '0'
    return answer

def measureBinaryString(entry):     #measures how many bits a binary number written as a string has, ignoring the trailing zeroes to the left
    answer = len(entry)
    for n in range(0, len(entry)):
        if entry[n] == '0': 
            answer -= 1
        else: break
    return answer

def xMODyUsingXOR(dividendInput, divisorInput):  #gets the CRC remainder (XOR instead of subtraction) of two binary numbers

    dividend = "{0:b}".format(dividendInput)    #converts value to string
    divisor = "{0:b}".format(divisorInput)      #converts value to string
    remainderSize = len(divisor) - 1            #get the final size the remainder should have at most, given how many trailing bits will be added to the checksum

    while len(divisor) < len(dividend) :        #adds zeroes to the right of the divisor to align it to the dividend's leftmost significant bit
        divisor = divisor + '0'

    while measureBinaryString(dividend) > remainderSize:    #tests whether the desired remainder has been found

        currentlength = measureBinaryString(dividend)       #takes the current length of the dividend to calculate the shrink factor
        dividend = stringXOR(dividend, divisor)             #XORs the dividend with the aligned divisor and updates the dividend

        newlength = measureBinaryString(dividend)           #takes the new length of the dividend to calculate the shrink factor
        shrinkfactor = currentlength - newlength            #calculate by how much the divisor will be shifted to the left to realign with the dividend since it has changed
        divisor = divisor[:-shrinkfactor]                   #removes zeroes to the left of the divisor to align it to the dividend's leftmost significant bit
        divisor = (shrinkfactor * '0') + divisor            #adds zeroes to the right of the divisor to align it to the dividend's leftmost significant bit

    remainder = int (dividend, 2)                           #converts the dividend to an int and uses it as the remainder, since all that's left from it IS the remainder
    return remainder    

def makeChecksum(data, polynomialGenerator):    #creates the checksum
                                #arguments:
                                    # - data - the data to be encoded with a checksum
                                    # - polynomialGenerator - the polynomial generator of the CRC, in numeric (int) form

                                    # !!! IMPORTANT !!!
                                    # The amount of bits to be checked in the data and added to the checksum's tail is always the amount of bits in the polynomial polynomialGeneratorerator minus 1.
    amountCRCBits = measureBinaryString("{0:b}".format(polynomialGenerator)) - 1    #calculates the amount of bits CRC will check and append
    data = data * (2 ** amountCRCBits)                              #shifts the data to create space for the CRC bits
    CRCRemainderTailBits = xMODyUsingXOR(data, polynomialGenerator)                               #gets the remainder to be added as CRC bits
    checksum = data ^ CRCRemainderTailBits                                     #adds the CRC bits to the data to create the checksum
    return checksum

def isCorrupt(checksum, polynomialGenerator):  #tests if the checksum is corrupt
                                        #arguments:
                                            # - checksum - the checksum to be tested
                                            # - polynomialGenerator - the polynomial generator of the CRC, in numeric (int) form
    if (xMODyUsingXOR(checksum, polynomialGenerator) == 0):    #tests of the reaminder of the checksum/polynomialGenerator division is zero
        return False                    #if yes, it's NOT corrupt
    return True                         #if not, it IS corrupt

#Uncomment and run everything below for debug. Put the appropriate data and gen(polynomial generator) to test it
# def debug():
#     data = 1251300042
#     gen = 4374732215

#     chk = makeChecksum(data, gen)
#     testresult = isCorrupt(chk, gen)

#     print ("Results!!")
#     print ("The checksum is", "{0:b}".format(chk))
#     print ("Is it corrupt?", testresult)

# debug()