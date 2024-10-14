from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np
import random
from qiskit_aer.noise import NoiseModel, ReadoutError
from qiskit_aer.noise.errors import depolarizing_error

import key_reconciliation;

simulator = AerSimulator()

# Number of qubits
n = 64

useNoise = False
evePresent = False
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
def createBases( n, evePresent = False, eveInterceptionRate = 0):
    aliceBases = []
    bobBases = []

    eveBases = []
    eveIntercepts = []
    for i in range(n):
        aliceBases.append(random.choice(["X", "Y", "Z"]))
        bobBases.append(random.choice(["Y", "Z", "W"]))
        if evePresent:
            eveBases.append(random.choice(["Y", "Z"])) # Optimal choice of bases, if not shared before than this would be way harder
            eveIntercepts.append(0 if random.random() > eveInterceptionRate else 1)
    return aliceBases, bobBases, eveBases, eveIntercepts

def send_qubit(alice_base, bobs_base, eve_present = False, eve_base = "", eve_intercepts = 0, useNoise = False):
    
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

def measure_all_qubits(aliceBases, bobBases, eve_present = False, eveBases = [], eveInterceptions = [], useNoise = False):

    alicesMeasurement = []
    bobsMeasurement = []
    eveMeasurement = []

    for i in range(len(aliceBases)):
        if(eve_present):
            output = send_qubit(aliceBases[i],bobBases[i], eve_present, eveBases[i], eveInterceptions[i], useNoise)
            alicesMeasurement.append(1 if not int (output[2]) else 0)
            bobsMeasurement.append(int (output[1]))
            if (eveInterceptions[i]):
                eveMeasurement.append(int (output[0]))
            else:
                eveMeasurement.append(np.nan)
        else:
            output = send_qubit(aliceBases[i],bobBases[i])
            alicesMeasurement.append(1 if not int (output[2]) else 0)
            bobsMeasurement.append(int (output[1]))
            

    return alicesMeasurement, bobsMeasurement, eveMeasurement

def sync_bases_and_build_keys(aliceBases, bobBases, eve_present = False, eveBases = [], eveInterceptions = [], useNoise = False):
    alicesMeasurement, bobsMeasurement, eveMeasurement = measure_all_qubits(aliceBases, bobBases, eve_present, eveBases, eveInterceptions, useNoise)
    
    aliceKey = []
    bobKey = []
    eveKey = []
    

    chsh_counts = np.zeros((4,4))
    
    # Compare bases 
    for i in range(len(aliceBases)):
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

    misMatchedBits = 0
    for i in range(len(aliceKey)):
        if (aliceKey[i] != bobKey[i]):
            misMatchedBits += 1

    print(f"\nAlice's key: {aliceKey}")
    print(f"Bob's key  : {bobKey}")
    if evePresent: print(f"Eve's key  : {eveKey} \n\t(where NaN means eve's value was discarded as she knows it was incorrect)")

    print(f"\nNumber of bits sent: {len(aliceBases)}")
    print(f"Number of bits in sifted key: {len(aliceKey)}")
    print(f"Number of miss matched bits: {misMatchedBits}")

    print(f"CHSH test: {round(corr, 3)}\n\t(should be close to 2*sqrt(2) ~ 2.828 if there is no interference)")

    if evePresent or useNoise:
        fixed_key, newAliceKey, newBobKey = key_reconciliation.key_reconciliation(aliceKey, bobKey)

        print(f"\nBob's fixed key: {fixed_key}")
        print(f"Final shared key: {newAliceKey}")
        
    return round(corr, 3), misMatchedBits, aliceKey, bobKey, eveKey

# aliceBases, bobBases, eveBases, eveIntercepts = createBases(evePresent, eveInterceptionRate)

# chsh, missmatchedBits, aliceKey, bobKey, eveKey = sync_bases_and_build_keys(aliceBases, bobBases, evePresent, eveBases, eveIntercepts)

# fixedBobKey, newBobKey, newAliceKey = key_reconciliation.key_reconciliation(aliceKey, bobKey)

