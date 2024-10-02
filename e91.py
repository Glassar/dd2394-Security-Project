from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np
import random

simulator = AerSimulator()

n = 32

aliceBasis = [] 
bobBasis = []

for i in range(n):
    aliceBasis.append(random.choice(["X", "Y", "Z"]))
    bobBasis.append(random.choice(["Y", "Z", "W"]))


def send_qubit(alice_base, bobs_base):
    
    # Charlie generating entangled particles
    qbits = QuantumRegister(2, 'q')
    measure = ClassicalRegister(2, 'c')
    bell = QuantumCircuit(qbits, measure)

    bell.initialize(3)

    bell.h(qbits[0])
    bell.cx(qbits[0], 1)

    # Alice's base
    if(alice_base == "X"):
        bell.h(qbits[0])
        bell.measure(qbits[0], measure[0])
    elif(alice_base == "Y"):
        bell.s(qbits[0])
        bell.h(qbits[0])
        bell.t(qbits[0])
        bell.h(qbits[0])
        bell.measure(qbits[0], measure[0])
    elif(alice_base == "Z"):
        bell.measure(qbits[0], measure[0])

    # Bob's base
    if(bobs_base == "Y"):
        bell.s(qbits[1])
        bell.h(qbits[1])
        bell.t(qbits[1])
        bell.h(qbits[1])
        bell.measure(qbits[1], measure[1])
    elif(bobs_base == "Z"):
        bell.measure(qbits[1], measure[1])
    elif(bobs_base == "W"):
        bell.measure(qbits[1], measure[1])
        bell.s(qbits[1])
        bell.h(qbits[1])
        bell.tdg(qbits[1])
        bell.h(qbits[1])
        bell.measure(qbits[1], measure[1])

    t_bell = transpile(bell, simulator)

    return simulator.run(t_bell, shots=1, memory=True).result().get_memory(t_bell)[0]


def measure_all_qubits(aliceBasis, bobBasis):

    alicesMeasurement = []
    bobsMeasurement = []

    for i in range(n):
        output = send_qubit(aliceBasis[i],bobBasis[i])
        alicesMeasurement.append(1 if not int (output[0]) else 0)
        bobsMeasurement.append(int (output[1]))

    return alicesMeasurement, bobsMeasurement

def sync_bases_and_build_keys(aliceBasis, bobBasis):

    spotCheck = []

    for i in range(n):
        spotCheck.append(0 if random.randint(0, 4) != 0 else 1)

    print("Spot checking array:", spotCheck)

    alicesMeasurement, bobsMeasurement = measure_all_qubits(aliceBasis, bobBasis)

    print("Alice: My bases are X, Y, Z")
    print("Alice: My random basis is:", aliceBasis)

    print("Bob: My bases are Y, Z, W")
    print("Bob: My random basis is:", bobBasis)

    aliceKey = []
    bobKey = []

    spotsToCheck = [[], []]

    for i in range(n):
        if(aliceBasis[i] == bobBasis[i]):
            if(spotCheck[i]):
                spotsToCheck[0].append(alicesMeasurement[i])
                spotsToCheck[1].append(bobsMeasurement[i])
            else:
                aliceKey.append(alicesMeasurement[i])
                bobKey.append(bobsMeasurement[i])

    print(spotsToCheck)

    return aliceKey, bobKey, spotsToCheck

aliceKey, bobKey, spotsToCheck = sync_bases_and_build_keys(aliceBasis, bobBasis)

def spotCheck(spotsToCheck):
    miss_matched_bits = 0
    for i in range(len(spotsToCheck[0])):
        if spotsToCheck[0][i] != spotsToCheck[1][i]:
            miss_matched_bits += 1

    print("Miss matched bits:", miss_matched_bits, "of", len(spotsToCheck[0]))

spotCheck(spotsToCheck)

print("Alice's key:", aliceKey)
print("Bob's key:", bobKey)