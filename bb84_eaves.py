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

def quantumEavesDropping(aBit, aBase, eBase, use_noise=False):
    # Create a circuit with 1 qubit
    circuit = QuantumCircuit(1)

    # Alice's bit
    if(aBit):
        # Resets to |0> to then initialize according to the given parameter = |1>
        circuit.initialize(1)

    # Alice's basis
    if(aBase):
        # Add Hadamard gate to qubit
        circuit.h(0)
        
    # Eve's basis
    if(eBase):
        # Add Hadamard gate to qubit
        circuit.h(0)

    # Measure bits (before eve) 
    circuit.measure_all()
    
    t = transpile(circuit, simulator)
    if use_noise:
        noise_model = noise_protocol()
        eRes =  simulator.run(t, shots=1, memory=True, noise_model=noise_model).result().get_counts(t)
    else: 
        eRes = simulator.run(t, shots=1, memory=True).result().get_counts(t)
    return list(eRes)[0]
    
    

def quantumSend(aBit, aBase, bBase, eBase, use_noise=False):
    
    # Perform eavesdropping
    eBit = quantumEavesDropping(aBit, aBase, eBase, use_noise)
    
    # Reset circuit
    circuit = QuantumCircuit(1)  
    
    if(eBit):
        # Resets to |0> to then initialize according to the given parameter = |1>
        circuit.initialize(1)
    
    # Bob's basis
    if(bBase):
        # Add Hadamard gate to qubit 
        circuit.h(0)
        
    # Measure bits 
    circuit.measure_all()

    t = transpile(circuit, simulator)

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
    # Eavesdropper
    eveBasis = np.random.randint(2, size= n)

    # Key sifting
    for i in range(n):
        if(aliceBasis[i] == bobBasis[i]):
            result = quantumSend(aliceBinary[i], aliceBasis[i], bobBasis[i], eveBasis[i], use_noise)
            #result_no_eavesdropping = bb84.quantumSend(aliceBinary[i], aliceBasis[i], bobBasis[i], use_noise)
            #print(result)
            aliceKey.append(int(aliceBinary[i]))
            bobKey.append(int(list(result.keys())[0][0]))
            #bobKey_no_eavesdropping.append(int(list(result_no_eavesdropping.keys())[0][0]))

    return aliceKey, bobKey

def spot_checking(aliceKey, bobKey, numberOfBits):
    # Gather a sample
    checkIndex = np.random.randint(len(aliceKey), size=numberOfBits)
    # Compare sample
    totalErrors = sum(aliceKey[index] != bobKey[index] for index in checkIndex)
    # Remove sample 
    for index in sorted(checkIndex, reverse=True):
        del aliceKey[index]
        del bobKey[index]
    return totalErrors / numberOfBits

def calc_risk(rate, threshold):
    return rate / threshold if rate <= threshold else 1


def main(nBits, spotSample, threshhold, use_noise=False,):
    # Call protocol
    (aKey, bKey) = bb84_protocol(nBits, use_noise)

    # Spot check
    error_eve = spot_checking(aKey, bKey, spotSample)

    # Risk
    risk = calc_risk(error_eve, threshhold)

    # Keys
    print(f"Alice's key: {aKey}")
    print(f"Bob's key  : {bKey}")
    print(f"Number of bits sent: {nBits}")
    print(f"Number of bits in key: {len(aKey)}")
    print(f"Error rate: {error_eve}")
    print(f"Risk of eavesdropping: {risk}")

# Example: 

#main(32, 4, 0.25, False)