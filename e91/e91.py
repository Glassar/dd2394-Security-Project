from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np
import random
from qiskit_aer.noise import NoiseModel, ReadoutError
from qiskit_aer.noise.errors import depolarizing_error
import math

import key_reconciliation

simulator = AerSimulator()

# Number of qubits
n = 1024

useNoise = False
evePresent = True
eveInterceptionRate = 1

aliceBases = [] 
bobBases = []

eveBases = []
eveIntercepts = []

def noise_protocol():
    noise_model = NoiseModel()
    # Gate error
    error = depolarizing_error(0.01, 1)
    noise_model.add_all_qubit_quantum_error(error, ['x', 'h'])
    
    # Measurement error (5%)
    read_error = ReadoutError([[0.95, 0.05], [0.05, 0.95]])
    noise_model.add_all_qubit_readout_error(read_error)

    return noise_model

# Bases for Alice and Bob
for i in range(n):
    aliceBases.append(random.choice(["X", "Y", "Z"]))
    bobBases.append(random.choice(["Y", "Z", "W"]))
    if evePresent:
        eveBases.append(random.choice(["Y", "Z"])) # Optimal choice of bases, if not shared before than this would be way harder
        eveIntercepts.append(0 if random.random() > eveInterceptionRate else 1)

def send_qubit(alice_base, bobs_base, eve_present = False, eve_base = "", eve_intercepts = 0):
    
    # Charlie generating entangled particles
    qbits = QuantumRegister(2, 'q')
    measure = ClassicalRegister(3, 'c')
    bell = QuantumCircuit(qbits, measure)

    # Creates singlet state
    bell.x(qbits[0])
    bell.x(qbits[1])
    bell.h(qbits[0])
    bell.cx(qbits[0], 1)

    if eve_present and eve_intercepts == 1:
        if(eve_base == "Y"):
            bell.s(qbits[1])
            bell.h(qbits[1])
            bell.t(qbits[1])
            bell.h(qbits[1])
            bell.measure(qbits[1], measure[2])
        elif(eve_base == "Z"):
            bell.measure(qbits[1], measure[2])

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
    elif(alice_base == "Z"):                # A3 direction (standard Z bases)
        bell.measure(qbits[0], measure[0])

    # Bob's base 
    if(bobs_base == "Y"):                   # B1 direction
        bell.s(qbits[1])
        bell.h(qbits[1])
        bell.t(qbits[1])
        bell.h(qbits[1])
        bell.measure(qbits[1], measure[1])
    elif(bobs_base == "Z"):                 # B2 direction (standard Z bases)
        bell.measure(qbits[1], measure[1])
    elif(bobs_base == "W"):                 # B3 direction
        bell.s(qbits[1])
        bell.h(qbits[1])
        bell.tdg(qbits[1])
        bell.h(qbits[1])
        bell.measure(qbits[1], measure[1])

    t_bell = transpile(bell, simulator)

    if useNoise:
        return simulator.run(t_bell, shots=1, memory=True, noise_model = noise_protocol()).result().get_memory(t_bell)[0]
    else:
        return simulator.run(t_bell, shots=1, memory=True).result().get_memory(t_bell)[0]

def measure_all_qubits(aliceBases, bobBases, eve_present = False, eveBases = [], eveInterceptions = []):

    alicesMeasurement = []
    bobsMeasurement = []
    eveMeasurement = []

    for i in range(n):
        if(eve_present):
            output = send_qubit(aliceBases[i],bobBases[i], eve_present, eveBases[i], eveInterceptions[i])
            alicesMeasurement.append(1 if not int (output[2]) else 0)
            bobsMeasurement.append(int (output[1]))
            if (eveIntercepts[i]):
                eveMeasurement.append(int (output[0]))
            else:
                eveMeasurement.append(np.nan)
        else:
            output = send_qubit(aliceBases[i],bobBases[i])
            alicesMeasurement.append(1 if not int (output[2]) else 0)
            bobsMeasurement.append(int (output[1]))
            

    return alicesMeasurement, bobsMeasurement, eveMeasurement

def sync_bases_and_build_keys(aliceBases, bobBases, eve_present = False, eveBases = [], eveInterceptions = []):

    alicesMeasurement, bobsMeasurement, eveMeasurement = measure_all_qubits(aliceBases, bobBases, eve_present, eveBases, eveInterceptions)
    
    print("Alice's bases: X, Y, Z")
    print("Bob's bases: Y, Z, W")

    if(eve_present):
        print("Eve's bases: Y, Z")
    
    aliceKey = []
    bobKey = []
    eveKey = []
    misMatchedBits = 0

    chsh_counts = np.zeros((4,4))
    
    # Compare bases 
    for i in range(n):
        if(aliceBases[i] == bobBases[i]):
            aliceKey.append(alicesMeasurement[i])
            bobKey.append(bobsMeasurement[i])   
            if(eve_present and eveBases[i] == bobBases[i]):
                eveKey.append(eveMeasurement[i])
            else:
                eveKey.append(np.nan)
        else:
            if(aliceBases[i] == "X" and bobBases[i] == "Y"):
                chsh_counts[0][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1
            elif(aliceBases[i] == "X" and bobBases[i] == "W"):
                chsh_counts[1][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1
            elif(aliceBases[i] == "Z" and bobBases[i] == "Y"):
                chsh_counts[2][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1
            elif(aliceBases[i] == "Z" and bobBases[i] == "W"):
                chsh_counts[3][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1

    expectXY = (chsh_counts[0][0] - chsh_counts[0][1] - chsh_counts[0][2] + chsh_counts[0][3])/(sum(chsh_counts[0]) if sum(chsh_counts[0]) else 1)
    expectXW = (chsh_counts[1][0] - chsh_counts[1][1] - chsh_counts[1][2] + chsh_counts[1][3])/(sum(chsh_counts[1]) if sum(chsh_counts[1]) else 1)
    expectZY = (chsh_counts[2][0] - chsh_counts[2][1] - chsh_counts[2][2] + chsh_counts[2][3])/(sum(chsh_counts[2]) if sum(chsh_counts[2]) else 1)
    expectZW = (chsh_counts[3][0] - chsh_counts[3][1] - chsh_counts[3][2] + chsh_counts[3][3])/(sum(chsh_counts[3]) if sum(chsh_counts[3]) else 1)

    corr = expectXY - expectXW + expectZY + expectZW
    
    print("CHSH correlation value:", round(corr, 3))
    print("Diff from 2*sqrt(2):", round((2*math.sqrt(2) - corr), 3))
    
    print(f"Length of key: {len(aliceKey)}")
    print(f"Alice's key: {aliceKey}")
    print(f"Bob's key: {bobKey}")
    
    if (eve_present):
        for i in range(len(aliceKey)):
            if (aliceKey[i] != bobKey[i]):
                misMatchedBits += 1
        print(f"Eve's key: {eveKey}")
        print(f"Mismatched bits: {misMatchedBits}")
        
    return aliceKey, bobKey, eveKey

aliceKey, bobKey, eveKey = sync_bases_and_build_keys(aliceBases, bobBases, evePresent, eveBases, eveIntercepts)

fixedBobKey, newBobKey, newAliceKey = key_reconciliation.key_reconciliation(aliceKey, bobKey)

print(fixedBobKey)
misMatchedBits = 0
if (evePresent):
    for i in range(len(aliceKey)):
        if (aliceKey[i] != fixedBobKey[i]):
            misMatchedBits += 1

    print(f"Mismatched bits: {misMatchedBits}")

print(f"Shared key: {newBobKey}")