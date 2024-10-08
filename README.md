# dd2394-Security-Project (Quantum cryptography)

## Problem statement

Quantum mechanics and quantum computing offers a new way of distributing keys for cryptography which is physically impossible to eavesdrop on without us knowing. This is because in quantum mechanics measuring a state changes said state. This means that if someone has measured our state before we get it, it will not be in the same state as when it was sent.

Using this quality multiple protocols have been created to distribute a secret key over an open insecure line, where the users will be able to physically guarantee that no one knows the key.

### Protocols
We have chosen to implement two different quantum key distribution protocols, namely the BB84 and E91 protocols. We will do this using the Qiskit python quantum programming library and run our quantum circuits on the quantum computing simulator QiskitAer.

### Interference tests
In addition to implementing the basic key distribution protocols we have also implement eavesdropping detection tests for both protocols. These use statistical methods to detect if the results of our two parties deviate from what would be expected if no interference was present.

This interference comes both in the form of noise, due to the fact that quantum computers are not infallible and sometimes a gate or measurement returns the wrong value. Or from someone eavesdropping on the key distribution and thereby modifying the states being sent.

If the detection protocol returns an interference larger than our safety threshold then we conclude that there has been eavesdropping and discard our results.

### Eavesdropping
Eavesdropping was implemented for both protocols with Eve intercepting some of the transmissions and measuring them. But then also making sure something is sent on for Bob to measure. But because there are random factors in how the information was sent which is not detectable in any way Eve can't do this perfectly meaning that there will be interference which we can detect. 

### Key reconciliation and privacy amplification
Finally because the quantum process is noise, Alice's and Bob's keys likely won't be completely identical even if there is no eavesdropping. To reconcile their keys an error correction protocol is used called *cascade protocol* which reveals minimal information while with high likelihood letting us reconcile the two keys.

But because this process require us to send information over an insecure connection we will finish of the key distribution with privacy amplification. This lets us effectively eliminate any knowledge about the key Eve might have gleaned through either eavesdropping on the key distribution, or from our key reconciliation. And this is done with a simpel hashing function.

## Background

### Crash course in quantum computing

### Deliverables

#### BB84
- Implement a basic BB84 protocol (without eavesdropping)
- Implement noise and spot checking
- Implement eavesdropping and risk of exposure
- Set up test cases (W & Wo eavesdropping, W & Wo noise)
#### E91
- Implement a basic E91 protocol 
- Implement CHSH of the protocol, and begin using noise
- Implement eavesdropping and risk of exposure
- Set up test cases (W & Wo eavesdropping, W & Wo noise)
#### Key reconciliation
- As it's uncertain whether the keys are identical (due to noise and/or eavesdropping), we need to reconcile the two keys to be  certain that they are the same.
#### Privacy amplification
- Take a key and run it through a hash function to minimize the information that eavesdropping can gather from the key. 

## References
- [BB84 protocol (1984)](https://github.com/qmunitytech/Tutorials/blob/main/intermediate/The%20BB84%20Quantum%20Cryptography%20algorithm.ipynb)
- [Qiskit tutorial - BB84 (2018)](https://github.com/qiskit-community/qiskit-community-tutorials/blob/master/awards/teach_me_qiskit_2018/quantum_cryptography_qkd/Quantum_Cryptography2.ipynb)
- [Qiskit tutorial - E91 (2018)](https://github.com/qiskit-community/qiskit-community-tutorials/blob/master/awards/teach_me_qiskit_2018/e91_qkd/e91_quantum_key_distribution_protocol.ipynb)
- [Qiskit noise](https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html)

## Documentation of the project

### BB84

### E91

## Documentation of testing the project

### Dependencies:
- Have python 3 installed
- `pip install qiskit`
- `pip install qiskit_aer`

#### BB84 
- Execute the test file `bb84_test.py` with `python3 bb84_test.py`

#### E91

## Contribution: 

To improve efficiency, we split the work into two parts based on the two protocols. While Alex and Anton worked on BB84, Trang and Jonatan worked on E91. 

### Anton Brömster
As mentioned previously, I worked on the BB84 protocol. But to be more specific, this is what I contributed:

- **Implementation of the BB84 protocol**: Updated the basic version of the protocol that was orginially made by Jonatan. This mostly consisted of making a new output format and altering the structure of the program.  
- **Eavesdropping and noise simulation**: Implemented features to simulate eavesdropping attempts and noise. This included changes in bb84.py and bb84_eaves.py. 
- **Test cases**: Implemented test cases for verification of the of the BB84 protocol. This included cases where eavedropping and noise wasn't used, and cases where they were used. 
- **Documentation**: Drafted the first version of the `README.md` page. This included sections: problem statement, deliverables and references. 

### Thi Huyen Trang Nguyen

### Alex Shariat Zadeh
- **Key reconciliation in the BB84 protocol**: Implemented method that makes keys match since its uncertain if the keys are identical because of the noise or eavesdropping, reconciles the two keys to be the same, by comparing segments of their respective keys and correcting any differences.
- **Privacy amplification in BB84**: Implemented using hash function to safeguard from potential eavesdropping
- **Test cases**: Implemented test cases for above
- **Documentation**:
### Jonatan Tuvstedt
