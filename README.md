# Quantum key distribution
### DD2394-Security-Project - Group 8
- Jonatan Tuvstedt
- Thi Huyen Trang Nguyen
- Anton Brömster
- Alex Shariat Zadeh

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

While quantum computing sounds like an intimidating topic, the concepts which we have used for this project are relatively simple.

Quantum computing works by applying quantum gates to a system of qubits and then evaluating the values of these qubits. Qubits are the quantum equivalent of a classical bit and can be represented as a two dimensional complex vector where the absolute values of the two complex numbers represents the probability of finding a 0 and a 1 respectively when measuring on the qubit.

For our protocols we only use a few different quantum gates:
- H gates simplified puts a qubit into a superposition with equal probability to measure 1 and 0. Or if it is already in one then it returns it to its classical state.
- X gate is a simpel not gate, switching the to numbers in the vector
- S and T gates rotates the complex vector in a way which doesn't directly affect the probability of measuring 0 or 1.
- CX gate is a conditional not gate, which switches the first qubit if and only if the second qubit evaluates to 1 (but if the second qubit only has a certain probability of evaluating to one then it only switches the first one with a certain probability).

#### Bell circuit
Finally for our protocols we need to introduce the bell circuit. It is a very simple two qubit system which will evaluate with equal odds to either 00 or 11, but never 10 or 01 (if we ignore noise). And it looks like this:

![alt text](image.png)

Basically what we do here is first use a H gate on qubit zero to put it into a superposition with equal likelihoods to evaluate to either 0 or 1. And then we apply a CX gate to both of them so that if qubit zero evaluates to 1 then we will set qubit one to 1. And this will hold even if we separate qubit zero and one by for example sending one to Alice and one to Bob, meaning they now have a shared secret bit.

### The assumptions of the project
The quantum protocols we use in this project require the following of our communication: The actual quantum communication is done over a completely open and unsecure channel. And the later comparison of bases as well as key reconciliation is done over an open but **authenticated** classical channel.

### BB84 
The BB84 protocol was devised by Charles H. Bennett and Gilles Brassard in 1984. It utilises a single qubit system, and works by first having both Alice and Bob randomly generating a series of bases (either no gate or a H gate), as well a Alice randomly generating a bit string. 

For each bit Alice will first encode it to the qubit, and then based on her base for that bit either apply a H gate or not. Bob then also either apply a H gate or not to the same qubit based on his base for that bit, before finally measuring its value. If both of them used the same base (either no H gate or two H gates where applies) then Bob will with a 100% certainty measure the same value as Alice wrote (disregarding noise). However if they have different bases then what Bob measures will be completely random. 

Finally Alice and Bob share their randomly generated bases, and discard any bits where they had different bases, and they now have two identical keys.

### E91
The E91 protocol was created by Artur Ekert in 1991 and is slightly more complex than BB84. It instead works based on a bell circuit which creates two qubits, one of which is sent to Alice and one to Bob. They both still generate a random series of bases (one for each bit sent), but now they choose between three bases which are different rotations of the qubits. For our example they only have two angles of the three in common, but they could theoretically chose these bases randomly out of a selection. 

For each bit both Alice and Bob now apply their base to the qubit they received before measuring it. Alice then flips her bit as if they have the same base then Alice's bit is guaranteed to be the opposite of Bob's (disregarding noise), while if they have different bases then their measurement's are a bit random.

Finally Alice and Bobs share their lists of bases and discard any bits where they don't share a base, and they now have two identical keys.

### Deliverables
The repository contains two protocols - BB84 and E91. The code for each protocol can be located within their corresponding folder [bb84](/bb84) and [e91](/e91). 

#### BB84
Within the [bb84](/bb84) folder, there are five python scripts - `bb84.py, bb84_eaves.py, bb84_test.py, noise.py, and spot_checking.py`. 

#### E91
Within the [e91](/e91) folder, one should find one python script - `e91.py`.


Describe the content of the repo (vilka filer har vi + vad gör dem + hur körs dem?) and how to navigate it (basically rewrite deliverables) - Anton
 - So what files do we have and what do they do
 - And how do you run the programs of the project

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
- [Cascade protocol](https://cascade-python.readthedocs.io/en/latest/protocol.html)
- [Quantum key distribution (Wikipedia)](https://en.wikipedia.org/wiki/Quantum_key_distribution#Information_reconciliation_and_privacy_amplification)
- [Quantum documentation (IBM)](https://docs.quantum.ibm.com/)

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
- **Key reconciliation in the BB84 and E91 protocol**: Implemented method that makes keys match since its uncertain if the keys are identical due to the noise or eavesdropping, reconciles the two keys to be the same, by comparing segments of their respective keys and correcting differences while revealing minimal information.
- **Privacy amplification in BB84 and E91**: Implemented using hash function to safeguard from potential eavesdropping
- **Test cases**: Implemented test cases for above
- **Documentation**:
### Jonatan Tuvstedt
