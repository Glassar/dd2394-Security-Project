import numpy as np
import unittest
import bb84_eaves
import bb84_noise

class defineVaribles():
    # Defining variables
    nBits = 36
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
         bb84_noise.main(defineVaribles, False)
    #Case 2 (bb84 with noise, but without eavesdropping)
    def test02(self):
         print("\n" + "Case 2 (bb84: W[Noise] Wo[Eavesdropping]")
         bb84_noise.main(defineVaribles, True)
    #Case 3 (bb84 with no noise, but with eavesdropping)
    def test03(self):
         print("\n" + "Case 3 (bb84: W[Eavesdropping] Wo[Noise]")
         bb84_eaves.main(defineVaribles, 0.5, False)
    # Case 4 (bb84 with noise and eavesdropping)
    def test04(self):
         print("\n" + "Case 4 (bb84: W[Noise, Eavesdropping]")
         bb84_eaves.main(defineVaribles, 0.5, True)

    
    def test05(self):
        print("\n" + "Case 5 (Key Reconciliation)")
        result = bb84_eaves.main(defineVaribles, 0.15, False)  # Use a non-zero threshold
    
    
        # Check if key reconciliation produces the same key for Alice and Bob
        alice_final = bb84_eaves.key_reconciliation(result['alice_key'], result['bob_key'], result['error_rate'])
        bob_final = bb84_eaves.key_reconciliation(result['bob_key'], result['alice_key'], result['error_rate'])
        self.assertEqual(alice_final, bob_final)
        self.assertEqual(result['final_key'], alice_final) 

        print('________________________________________________________________')
        print(f"Original Alice's key length: {len(result['alice_key'])}")
        print(f"Alice fin key: {(result['alice_key'])}")
        print(f"bob fin key  : {(result['bob_key'])}")
        print(f"Original Bob's key length: {len(result['bob_key'])}")
        print(f"Reconciled key length: {len(result['reconciled_key'])}")
        print(f"Final key length after privacy amplification: {len(result['final_key'])}")
        print(f"Error rate: {result['error_rate']}")
        print(f"Final key: {result['final_key']}")
if __name__ == '__main__':
    unittest.main()
