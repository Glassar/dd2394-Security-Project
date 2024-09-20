from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

simulator = AerSimulator()

bell = QuantumCircuit(2)

bell.h(0)
bell.cx(0, 1)
bell.measure_all()


t_bell = transpile(bell, simulator)
print(t_bell.draw())

result = simulator.run(t_bell, shots=1000, memory=True).result()

print(result.get_counts(t_bell))