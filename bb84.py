from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

simulator = AerSimulator()

n = 32

# Generate the random number strings
aliceBinary = np.random.randint(2, size= n)
aliceBasis = np.random.randint(2, size= n)
bobBasis = np.random.randint(2, size= n)

def quantumSend(aBit, aBase, bBase):
    circuit = QuantumCircuit(1)

    if(aBit):
        circuit.initialize(1)
    
    if(aBase):
        circuit.h(0)
    
    if(bBase):
        circuit.h(0)
    
    circuit.measure_all()

    t = transpile(circuit, simulator)

    return simulator.run(t, shots=1, memory=True).result().get_counts(t)

for i in range(n):
    if(aliceBasis[i] == bobBasis[i]):
        print(quantumSend(aliceBinary[i], aliceBasis[i], bobBasis[i]))