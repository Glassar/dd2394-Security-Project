from qiskit_aer.noise import NoiseModel, ReadoutError
from qiskit_aer.noise.errors import depolarizing_error

def noise_protocol():
    noise_model = NoiseModel()
    # Gate error
    error = depolarizing_error(0.05, 1)
    noise_model.add_all_qubit_quantum_error(error, ['x', 'h'])

    # Measurement error
    read_error = ReadoutError([[0.95, 0.05], [0.05, 0.95]])
    noise_model.add_all_qubit_readout_error(read_error)

    return noise_model