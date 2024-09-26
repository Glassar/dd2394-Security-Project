from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np

simulator = AerSimulator()

n = 32

aliceBasis = np.random.randint(3, size= n)
bobBasis = np.random.randint(3, size= n)


def send_measure_bits(alice_base, bobs_base):
    
    # Charlie generating entangled particles
    qbits = QuantumRegister(2, 'q')
    measure = ClassicalRegister(2, 'c')
    bell = QuantumCircuit(qbits, measure)

    bell.initialize(3)

    bell.h(qbits[0])
    bell.cx(qbits[0], 1)

    # Alice's base
    if(alice_base == 0):
        bell.h(qbits[0])
        bell.measure(qbits[0], measure[0])
    elif(alice_base == 1):
        bell.s(qbits[0])
        bell.h(qbits[0])
        bell.t(qbits[0])
        bell.h(qbits[0])
        bell.measure(qbits[0], measure[0])
    elif(alice_base == 2):
        bell.measure(qbits[0], measure[0])

    # Bob's base
    if(bobs_base == 0):
        bell.s(qbits[1])
        bell.h(qbits[1])
        bell.t(qbits[1])
        bell.h(qbits[1])
        bell.measure(qbits[1], measure[1])
    elif(bobs_base == 1):
        bell.measure(qbits[1], measure[1])
    elif(bobs_base == 2):
        bell.measure(qbits[1], measure[1])
        bell.s(qbits[1])
        bell.h(qbits[1])
        bell.tdg(qbits[1])
        bell.h(qbits[1])
        bell.measure(qbits[1], measure[1])

    t_bell = transpile(bell, simulator)

    return simulator.run(t_bell, shots=1, memory=True).result().get_counts(t_bell)

for i in range(n):
    print(send_measure_bits(aliceBasis[i],bobBasis[i]), aliceBasis[i], bobBasis[i])