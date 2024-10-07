from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from noise import noise_protocol
from spot_checking import spot_checking


simulator = AerSimulator()

def quantumSend(aBit, aBase, bBase, use_noise=False):
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
    
    # Bob's basis
    if(bBase):
        # Add Hadamard gate to qubit 0
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
            result = quantumSend(vObject.aBits[i], vObject.aBase[i], vObject.bBase[i], use_noise)
            aKey.append(int(vObject.aBits[i]))
            bKey.append(int(list(result.keys())[0][0]))
    return aKey, bKey

def main(vObject, use_noise=False):
    # Call protocol

    (aKey, bKey) = bb84_protocol(vObject, use_noise)
    
    # Spot check
    (error, aSample, bSample) = spot_checking(aKey, bKey, int(len(aKey)/vObject.sampleDivisor))

    # Output data
    print(f"Alice's key: {aKey}")
    print(f"Bob's key  : {bKey}")
    print(f"Number of bits sent: {vObject.nBits}")
    print(f"Number of bits in key: {len(aKey)}")
    print(f"Error rate: {error}")
    print(f"Alice's sample: {aSample}")
    print(f"Bob's sample: {bSample}")
