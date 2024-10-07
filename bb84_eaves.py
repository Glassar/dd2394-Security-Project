from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from noise import noise_protocol
from spot_checking import spot_checking
import hashlib
import random as rand

simulator = AerSimulator()

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

def calc_risk(rate, threshold):
    return rate / threshold if rate <= threshold else 1

def key_reconciliation(aKey, bKey):
    fixedKey = error_correction(aKey, bKey)
    finalKey = privacy_amplification(fixedKey)
    return fixedKey,finalKey

def error_correction(aKey, bKey):
    newKey = []
    for aBit, bBit in zip(aKey, bKey):
        if aBit != bBit: 
            newBit = 1 - bBit
            newKey.append(newBit)
        else:
            newKey.append(bBit)
    return newKey

def privacy_amplification(key):
    # hash
    hashKey = hashlib.sha256(''.join(map(str, key)).encode()).digest()
    binKey = bin(int.from_bytes(hashKey, 'little'))[2:]
    return [int(bit) for bit in str(binKey)]

def main(vObject, threshold, use_noise=False):
    # Call protocol
    (aKey, bKey) = bb84_protocol(vObject, use_noise)
    
    # Spot check
    (error_eve, aSample, bSample) = spot_checking(aKey, bKey, int(len(aKey)/vObject.sampleDivisor))

    # Calculate risk
    risk = calc_risk(error_eve, threshold)

    # key_reconciliation
    fixedKey, hashedKey = key_reconciliation(aKey, bKey)

    # Output data
    print(f"Alice's key: {aKey}")
    print(f"Bob's key  : {bKey}")
    print(f"Number of bits sent: {vObject.nBits}")
    print(f"Number of bits in sifted key: {len(aKey)}")
    print(f"Error rate: {error_eve}")
    print(f"Alice's sample: {aSample}")
    print(f"Bob's sample: {bSample}")
    print(f"Risk of eavesdropping: {risk}")
    

    return {
        "alice_key": aKey,
        "fixedKey": fixedKey,
        "hashedKey": hashedKey
    }

# Example of execution 
#main(32, 4, 0.25, False)
