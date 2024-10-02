from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError
from qiskit_aer.noise.errors import depolarizing_error
import numpy as np

simulator = AerSimulator()

def noise_protocol():
    noise_model = NoiseModel()
    # Gate error
    error = depolarizing_error(0.05, 1)
    noise_model.add_all_qubit_quantum_error(error, ['x', 'h'])
    
    # Measurement error
    read_error = ReadoutError([[0.9, 0.1], [0.1, 0.9]])
    noise_model.add_all_qubit_readout_error(read_error)

    return noise_model

<<<<<<< HEAD
print(f"Alice's State:\t {np.array2string(aliceBinary)}")
print(f"Alice's Bases:\t {np.array2string(aliceBasis)}")
print(f"Bob's Bases:\t {np.array2string(bobBasis)}")
      
print("Shared key: ")
def quantumSend(aBit, aBase, bBase):
=======
def quantumSend(aBit, aBase, bBase, use_noise=False):
    # Create a circuit with 1 qubit
>>>>>>> ca7e97077ee86a1015f05b692c934479f4128719
    circuit = QuantumCircuit(1)

    # Alice's bit
    if(aBit):
        # Resets to |0> to then initialize according to the given parameter = |1>
        circuit.initialize(1)

    # Alice's basis
    if(aBase):
        # Add Hadamard gate to qubit
        circuit.h(0)
    
    # Bob's basis
    if(bBase):
        # Add Hadamard gate to qubit 0
        circuit.h(0)
    
    # Measure bits 
    circuit.measure_all()

    t = transpile(circuit, simulator)
<<<<<<< HEAD
    
    return simulator.run(t, shots=1, memory=True).result().get_counts(t)

for i in range(n):
    if(aliceBasis[i] == bobBasis[i]):
        print(quantumSend(aliceBinary[i], aliceBasis[i], bobBasis[i]))
        
=======

    if use_noise:
        noise_model = noise_protocol()
        return simulator.run(t, shots=1, memory=True, noise_model=noise_model).result().get_counts(t)
    else: 
        return simulator.run(t, shots=1, memory=True).result().get_counts(t)

def bb84_protocol(n, use_noise=False):
    aliceKey = []
    bobKey = []
    # Generate the random number strings
    aliceBinary = np.random.randint(2, size= n)
    aliceBasis = np.random.randint(2, size= n)
    bobBasis = np.random.randint(2, size= n)

    # Key sifting
    for i in range(n):
        if(aliceBasis[i] == bobBasis[i]):
            result = quantumSend(aliceBinary[i], aliceBasis[i], bobBasis[i], use_noise)
            #print(result)
            aliceKey.append(int(aliceBinary[i]))
            bobKey.append(int(list(result.keys())[0][0]))

    return aliceKey, bobKey

def spot_checking(aliceKey, bobKey, numberOfBits):
    checkIndex = np.random.randint(len(aliceKey), size=numberOfBits)
    totalErrors = sum(aliceKey[index] != bobKey[index] for index in checkIndex)
    return totalErrors / numberOfBits

# Main execution
numberOfBits = 32

# Call protocol
(aliceKey, bobKey) = bb84_protocol(numberOfBits, True)

# Spot check
error = spot_checking(aliceKey, bobKey, int(numberOfBits/2))

print(f"Alice key: {aliceKey}")
print(f"Bob key  : {bobKey}")
print(f"Error: {error}")
>>>>>>> ca7e97077ee86a1015f05b692c934479f4128719
