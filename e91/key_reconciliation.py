from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import hashlib
import random as rand

def key_reconciliation(alice_key, bob_key, block_size=1, rounds=4):
    fixed_key = cascade_error_correction(alice_key, bob_key, block_size, rounds)
    final_key = privacy_amplification(fixed_key)
    new_alice_key = privacy_amplification(alice_key)
    return fixed_key, final_key, new_alice_key

def cascade_error_correction(alice_key, bob_key, initial_block_size=1, rounds=4):
    key_length = len(alice_key)
    bob_key = bob_key.copy()  # Create a copy to avoid modifying the original

    for round in range(rounds):
        block_size = initial_block_size * (2 ** round)
     
        for i in range(0, key_length, block_size):
            alice_block = alice_key[i:i+block_size]
            bob_block = bob_key[i:i+block_size]
         
            if parity(alice_block) != parity(bob_block):
                error_index = binary_search_error(alice_block, bob_block)
                bob_key[i + error_index] = alice_key[i + error_index]
             
                # Cascade effect
                if round > 0:
                    cascade_to_previous_blocks(alice_key, bob_key, i + error_index, initial_block_size)
    return bob_key

def parity(block):
    return sum(block) % 2

def binary_search_error(alice_block, bob_block):
    start, end = 0, len(alice_block) - 1
    while start < end:
        mid = (start + end) // 2
        if parity(alice_block[:mid+1]) != parity(bob_block[:mid+1]):
            end = mid
        else:
            start = mid + 1
    return start

def cascade_to_previous_blocks(alice_key, bob_key, error_index, min_block_size):
    block_size = len(alice_key) // 2
    while block_size >= min_block_size:
        block_start = (error_index // block_size) * block_size
        alice_block = alice_key[block_start:block_start+block_size]
        bob_block = bob_key[block_start:block_start+block_size]      
        if parity(alice_block) != parity(bob_block):
            new_error_index = binary_search_error(alice_block, bob_block)
            bob_key[block_start + new_error_index] = alice_key[block_start + new_error_index]      
        block_size //= 2

def privacy_amplification(key):
    # hash
    seed = ''.join(map(str, key))
    hash_object = hashlib.md5(seed.encode())
    hashKey = hash_object.digest()
    binKey = bin(int.from_bytes(hashKey, 'little'))[2:]
    return [int(bit) for bit in str(binKey)]
