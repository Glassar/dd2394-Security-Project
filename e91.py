from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np
import random

simulator = AerSimulator()

# Number of qubits
n = 1024

aliceBasis = [] 
bobBasis = []

# Bases for Alice and Bob
for i in range(n):
    aliceBasis.append(random.choice(["X", "Y", "Z"]))
    bobBasis.append(random.choice(["Y", "Z", "W"]))


def send_qubit(alice_base, bobs_base):
    
    # Charlie generating entangled particles
    qbits = QuantumRegister(2, 'q')
    measure = ClassicalRegister(2, 'c')
    bell = QuantumCircuit(qbits, measure)

    # Creates singlet state
    bell.x(qbits[0])
    bell.x(qbits[1])
    bell.h(qbits[0])
    bell.cx(qbits[0], 1)

    # Alice's base 
    if(alice_base == "X"):                  # A1 direction
        bell.h(qbits[0])
        bell.measure(qbits[0], measure[0])
    elif(alice_base == "Y"):                # A2 direction
        bell.s(qbits[0])
        bell.h(qbits[0])
        bell.t(qbits[0])
        bell.h(qbits[0])
        bell.measure(qbits[0], measure[0])
    elif(alice_base == "Z"):                # A3 direction (standard Z basis)
        bell.measure(qbits[0], measure[0])

    # Bob's base 
    if(bobs_base == "Y"):                   # B1 direction
        bell.s(qbits[1])
        bell.h(qbits[1])
        bell.t(qbits[1])
        bell.h(qbits[1])
        bell.measure(qbits[1], measure[1])
    elif(bobs_base == "Z"):                 # B2 direction (standard Z basis)
        bell.measure(qbits[1], measure[1])
    elif(bobs_base == "W"):                 # B3 direction
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

    alicesMeasurement, bobsMeasurement = measure_all_qubits(aliceBasis, bobBasis)

    print("Alice's bases: X, Y, Z")
    print("Alice's measurements: ", aliceBasis)

    print("Bob's bases: Y, Z, W")
    print("Bob's measurements: ", bobBasis)

    aliceKey = []
    bobKey = []

    chsh_counts = np.zeros((4,4))
    

    # Compare bases 
    for i in range(n):
        if(aliceBasis[i] == bobBasis[i]):
            aliceKey.append(alicesMeasurement[i])
            bobKey.append(bobsMeasurement[i])   
        else:
            if(aliceBasis[i] == "X" and bobBasis[i] == "Y"):
                chsh_counts[0][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1
            elif(aliceBasis[i] == "X" and bobBasis[i] == "W"):
                chsh_counts[1][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1
            elif(aliceBasis[i] == "Z" and bobBasis[i] == "Y"):
                chsh_counts[2][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1
            elif(aliceBasis[i] == "Z" and bobBasis[i] == "W"):
                chsh_counts[3][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1

    expectXY = (chsh_counts[0][0] - chsh_counts[0][1] - chsh_counts[0][2] + chsh_counts[0][3])/sum(chsh_counts[0])
    expectXW = (chsh_counts[1][0] - chsh_counts[1][1] - chsh_counts[1][2] + chsh_counts[1][3])/sum(chsh_counts[1])
    expectZY = (chsh_counts[2][0] - chsh_counts[2][1] - chsh_counts[2][2] + chsh_counts[2][3])/sum(chsh_counts[2])
    expectZW = (chsh_counts[3][0] - chsh_counts[3][1] - chsh_counts[3][2] + chsh_counts[3][3])/sum(chsh_counts[3])

    corr = expectXY - expectXW + expectZY + expectZW

    print(round(corr, 3))
            
    return aliceKey, bobKey

aliceKey, bobKey = sync_bases_and_build_keys(aliceBasis, bobBasis)

print("Length of key: ", len(aliceKey))
print("Alice's key:", aliceKey)
print("Bob's key:", bobKey)
