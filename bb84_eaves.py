from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError
from qiskit_aer.noise.errors import depolarizing_error
import numpy as np
import hashlib
import random

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

def bb84_protocol(vObject, use_noise=False):
    aKey = []
    bKey = []
    # Key sifting
    for i in range(vObject.nBits):
        if(vObject.aBase[i] == vObject.bBase[i]):
            result = quantumSend(vObject.aBits[i], vObject.aBase[i], vObject.bBase[i], vObject.eBase[i], use_noise)
            aKey.append(int(vObject.aBits[i]))
            bKey.append(int(list(result.keys())[0][0]))
    return aKey, bKey

def spot_checking(aKey, bKey, numberOfBits):
    nErrors = 0
    # test
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


def calc_risk(rate, threshold):
    return rate / threshold if rate <= threshold else 1

def key_reconciliation(alice_key, bob_key, error_rate):
    # Step 1: Error Correction
    corrected_key = error_correction(alice_key, bob_key)
    
    # Step 2: Privacy Amplification
    final_key = privacy_amplification(corrected_key, error_rate)
    
    return final_key

def error_correction(alice_key, bob_key):
    corrected_key = []
    for a, b in zip(alice_key, bob_key):
        if a == b:
            corrected_key.append(a)  # If bits match, keep the bit
        else:
            # If bits don't match, use a predetermined rule
            # For example, use a random choice or always choose '0'
            corrected_key.append(0)
    return corrected_key

def privacy_amplification(key, error_rate):
    # Use a deterministic seed for the hash function
    seed = ''.join(map(str, key))
    hash_object = hashlib.sha256(seed.encode())
    hashed_key = hash_object.digest()
    
    # Convert hash to bit string
    bit_string = ''.join(format(byte, '08b') for byte in hashed_key)
    
    # Reduce key length based on error rate
    reduction_factor = max(0.5, 1 - 2 * error_rate)  # Ensure we keep at least half the bits
    new_length = max(1, int(len(key) * reduction_factor))
    
    final_key = [int(bit) for bit in bit_string[:new_length]]
    return final_key

def main(vObject, threshold, use_noise=False):
    # Call protocol
    (aKey, bKey) = bb84_protocol(vObject, use_noise)
    
    # Spot check
    (error_eve, aSample, bSample) = spot_checking(aKey, bKey, int(len(aKey)/vObject.sampleDivisor))

    # Calculate risk
    risk = calc_risk(error_eve, threshold)

    # Key reconciliation
    reconciled_key = error_correction(aKey, bKey)

    # Privacy amplification
    final_key = privacy_amplification(reconciled_key, error_eve)


    # Output data
    print(f"Alice's key: {aKey}")
    print(f"Bob's key  : {bKey}")
    print(f"Reconciled key: {reconciled_key}")
    print(f"Final key after privacy amplification: {final_key}")
    print(f"Number of bits sent: {vObject.nBits}")
    print(f"Number of bits in sifted key: {len(aKey)}")
    print(f"Number of bits in final key: {len(final_key)}")
    print(f"Error rate: {error_eve}")
    print(f"Alice's sample: {aSample}")
    print(f"Bob's sample: {bSample}")
    print(f"Risk of eavesdropping: {risk}")

    return {
        "alice_key": aKey,
        "bob_key": bKey,
        "reconciled_key": reconciled_key,
        "final_key": final_key,
        "bits_sent": vObject.nBits,
        "sifted_key_length": len(aKey),
        "final_key_length": len(final_key),
        "error_rate": error_eve,
        "risk": risk
    }

# Example of execution 
#main(32, 4, 0.25, False)
