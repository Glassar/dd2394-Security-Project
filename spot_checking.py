import random

def spot_checking(aKey, bKey, numberOfBits):
    nErrors = 0
    # Sample set
    aSample = []
    bSample = []
    # Gather a sample
    checkIndex = random.sample(aKey, numberOfBits)
    # Remove sample 
    for index in sorted(checkIndex, reverse=True):
        if aKey[index] != bKey[index]: 
            nErrors += 1
        aSample.append(aKey[index])
        bSample.append(bKey[index])
        del aKey[index]
        del bKey[index]
    return nErrors / len(checkIndex), aSample, bSample