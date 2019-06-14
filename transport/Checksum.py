from math import floor

def xmodyxor(dividend, divisor):
    remainder = dividend ^ (divisor * floor(dividend/divisor))
    return remainder

def makeChecksum(data, amountCheckBits, gen):
    data = data * (2 ** amountCheckBits)
    gen = gen & ((2 ** amountCheckBits) - 1)
    crcbits = xmodyxor(data, gen)
    chksum = data ^ crcbits
    return chksum

def isCorrupt(chksum, gen):
    if (xmodyxor(chksum, gen) == 0):
        return False
    return True