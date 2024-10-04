import numpy as np
import unittest
import bb84_eaves
import bb84

class defineVaribles():
    # Defining variables
    nBits = 32
    sampleDivisor = 8

    # Generate the random number strings
    aBits = np.random.randint(2, size= nBits)
    aBase = np.random.randint(2, size= nBits)
    bBase = np.random.randint(2, size= nBits)
    # Eavesdropper
    eBase = np.random.randint(2, size= nBits)

class test(unittest.TestCase, defineVaribles):

#Case 1 (bb84 without noise and eavesdropping)
    def test01(self):
        print("\n" + "Case 1 (bb84: Wo[Noise, Eavesdropping]")
        bb84.main(defineVaribles, False)

#Case 2 (bb84 with noise, but without eavesdropping)
    def test02(self):
        print("\n" + "Case 2 (bb84: W[Noise] Wo[Eavesdropping]")
        bb84.main(defineVaribles, True)

#Case 3 (bb84 with no noise, but with eavesdropping)
    def test03(self):
        print("\n" + "Case 3 (bb84: W[Eavesdropping] Wo[Noise]")
        bb84_eaves.main(defineVaribles, 0.5, False)

    # Case 4 (bb84 with noise and eavesdropping)
    def test04(self):
        print("\n" + "Case 4 (bb84: W[Noise, Eavesdropping]")
        bb84_eaves.main(defineVaribles, 0.5, True)

if __name__ == '__main__':
    unittest.main()