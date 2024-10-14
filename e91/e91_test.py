import numpy as np
import unittest
import e91
import key_reconciliation
import math

class config():
    nBits = 1024
    eveInterceptionRate = 0.5
    aBase, bBase, eBase, eIntercepts = e91.createBases(nBits, True, eveInterceptionRate)

class test(unittest.TestCase, config):
     #Case 1 (e91 without noise and eavesdropping)
    def test01(self):
         print("\nCase 1 (e91: Wo[Noise, Eavesdropping]")

         chsh, missmatchedBits, aKey, bKey, _ = e91.sync_bases_and_build_keys(config.aBase, config.bBase)
         self.assertEqual(aKey, bKey)
    #Case 2 (e91 with noise, but without eavesdropping)
    def test02(self):
        print("\n\n-------------------------------------------------------------------")
        print("\n" + "Case 2 (e91: W[Noise] Wo[Eavesdropping]")
        _, _, aKey, bKey, _ = e91.sync_bases_and_build_keys(config.aBase, config.bBase, useNoise=True)
        fKey, newBKey, newAKey = key_reconciliation.key_reconciliation(aKey, bKey)
        self.assertEqual(aKey, fKey)
        self.assertEqual(newAKey, newBKey)

    #Case 3 (e91 with no noise, but with eavesdropping on 50% of the bits)
    def test03(self):
        print("\n\n-------------------------------------------------------------------")
        print("\n" + "Case 3 (e91: W[Eavesdropping 50\% of the time] Wo[Noise]")
        chsh, missmatchedBits, aKey, bKey, eKey = e91.sync_bases_and_build_keys(config.aBase, config.bBase, eve_present=True, eveBases=config.eBase, eveInterceptions=config.eIntercepts, useNoise=False)
        fKey, newBKey, newAKey = key_reconciliation.key_reconciliation(aKey, bKey)
        self.assertEqual(aKey, fKey)
        self.assertEqual(newAKey, newBKey)

        for i in range(len(aKey)):
            if(not math.isnan(eKey[i])):
                self.assertEqual(aKey[i], eKey[i])
    
    #Case 4 (e91 with no noise, but with eavesdropping on 100% of the bits)
    def test04(self):
        print("\n\n-------------------------------------------------------------------")
        print("\n" + "Case 4 (e91: W[Eavesdropping 100\% of the time]  Wo[Noise]")
        chsh, missmatchedBits, aKey, bKey, eKey = e91.sync_bases_and_build_keys(config.aBase, config.bBase, eve_present=True, eveBases=config.eBase, eveInterceptions=np.ones(config.nBits), useNoise=False)
        fKey, newBKey, newAKey = key_reconciliation.key_reconciliation(aKey, bKey)
        self.assertEqual(aKey, fKey)
        self.assertEqual(newAKey, newBKey)

        for i in range(len(aKey)):
            if(not math.isnan(eKey[i])):
                self.assertEqual(aKey[i], eKey[i])
    

    #Case 5 (e91 with with eavesdropping and noise)
    def test05(self):
        print("\n\n-------------------------------------------------------------------")
        print("\n" + "Case 5 (e91: W[Eavesdropping 100\% of the time Noise]")
        chsh, missmatchedBits, aKey, bKey, eKey = e91.sync_bases_and_build_keys(config.aBase, config.bBase, eve_present=True, eveBases=config.eBase, eveInterceptions=np.ones(config.nBits), useNoise=True)
        fKey, newBKey, newAKey = key_reconciliation.key_reconciliation(aKey, bKey)
        self.assertEqual(aKey, fKey)
        self.assertEqual(newAKey, newBKey)

if __name__ == '__main__':
    unittest.main()
