from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError
from qiskit_aer.noise.errors import depolarizing_error
import numpy as np

import unittest
import bb84_eaves

class test(unittest.TestCase):
    # Example: 
    nBits = 16
    spotSample = int(nBits / 4)
    
    def test01(self):
        print("--test1--")
        bb84_eaves.main(self.nBits, self.spotSample, 0.15, False)
    def test02(self):
        print("--test2--")
        bb84_eaves.main(self.nBits, self.spotSample, 0.45, False)
    def test03(self):
        print("--test3--")
        bb84_eaves.main(self.nBits, self.spotSample, 0.75, False)

if __name__ == '__main__':
    unittest.main()