from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np
import random
from qiskit_aer.noise import NoiseModel, ReadoutError
from qiskit_aer.noise.errors import depolarizing_error

simulator = AerSimulator()

# Number of qubits
n = 16
useNoise = False
evePresent = True
eveInterceptionRate = 1

aliceBasis = [] 
bobBasis = []

eveBasis = []
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
    aliceBasis.append(random.choice(["X", "Y", "Z"]))
    bobBasis.append(random.choice(["Y", "Z", "W"]))
    if evePresent:
        eveBasis.append(random.choice(["Y", "Z"])) # Optimal choice of bases, if not shared before than this would be way harder
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

    if useNoise:
        return simulator.run(t_bell, shots=1, memory=True, noise_model = noise_protocol()).result().get_memory(t_bell)[0]
    else:
        return simulator.run(t_bell, shots=1, memory=True).result().get_memory(t_bell)[0]

def measure_all_qubits(aliceBasis, bobBasis, eve_present = False, eveBasis = [], eveInterceptions = []):

    alicesMeasurement = []
    bobsMeasurement = []
    eveMeasurement = []

    for i in range(n):
        if(eve_present):
            output = send_qubit(aliceBasis[i],bobBasis[i], eve_present, eveBasis[i], eveInterceptions[i])
            alicesMeasurement.append(1 if not int (output[2]) else 0)
            bobsMeasurement.append(int (output[1]))
            if (eveIntercepts[i]):
                eveMeasurement.append(int (output[0]))
            else:
                eveMeasurement.append(np.nan)
        else:
            output = send_qubit(aliceBasis[i],bobBasis[i])
            alicesMeasurement.append(1 if not int (output[2]) else 0)
            bobsMeasurement.append(int (output[1]))
            

    return alicesMeasurement, bobsMeasurement, eveMeasurement

def sync_bases_and_build_keys(aliceBasis, bobBasis, eve_present = False, eveBasis = [], eveInterceptions = []):

    alicesMeasurement, bobsMeasurement, eveMeasurement = measure_all_qubits(aliceBasis, bobBasis, eve_present, eveBasis, eveInterceptions)

    print("Alice's bases: X, Y, Z")

    print("Bob's bases: Y, Z, W")

    aliceKey = []
    bobKey = []
    eveKey = []

    chsh_counts = np.zeros((4,4))
    

    # Compare bases 
    for i in range(n):
        if(aliceBasis[i] == bobBasis[i]):
            aliceKey.append(alicesMeasurement[i])
            bobKey.append(bobsMeasurement[i])   
            if(eve_present and eveBasis[i] == bobBasis[i]):
                eveKey.append(eveMeasurement[i])
            else:
                eveKey.append(np.nan)
        else:
            if(aliceBasis[i] == "X" and bobBasis[i] == "Y"):
                chsh_counts[0][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1
            elif(aliceBasis[i] == "X" and bobBasis[i] == "W"):
                chsh_counts[1][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1
            elif(aliceBasis[i] == "Z" and bobBasis[i] == "Y"):
                chsh_counts[2][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1
            elif(aliceBasis[i] == "Z" and bobBasis[i] == "W"):
                chsh_counts[3][2*alicesMeasurement[i]+bobsMeasurement[i]] += 1

    expectXY = (chsh_counts[0][0] - chsh_counts[0][1] - chsh_counts[0][2] + chsh_counts[0][3])/(sum(chsh_counts[0]) if sum(chsh_counts[0]) else 1)
    expectXW = (chsh_counts[1][0] - chsh_counts[1][1] - chsh_counts[1][2] + chsh_counts[1][3])/(sum(chsh_counts[1]) if sum(chsh_counts[1]) else 1)
    expectZY = (chsh_counts[2][0] - chsh_counts[2][1] - chsh_counts[2][2] + chsh_counts[2][3])/(sum(chsh_counts[2]) if sum(chsh_counts[2]) else 1)
    expectZW = (chsh_counts[3][0] - chsh_counts[3][1] - chsh_counts[3][2] + chsh_counts[3][3])/(sum(chsh_counts[3]) if sum(chsh_counts[3]) else 1)

    corr = expectXY - expectXW + expectZY + expectZW

    print("CHSH correlation value:", round(corr, 3), "diff from sqrt(pi)*2:", np.abs(round(np.sqrt(2)*2 -np.abs(corr), 3)))
            
    return aliceKey, bobKey, eveKey

aliceKey, bobKey, eveKey = sync_bases_and_build_keys(aliceBasis, bobBasis, evePresent, eveBasis, eveIntercepts)

print(f"Length of key: {len(aliceKey)}")
print(f"Alice's key: {aliceKey}")
print(f"Bob's key: {bobKey}")

if(evePresent):
    print(f"Eve's key: {eveKey}")

