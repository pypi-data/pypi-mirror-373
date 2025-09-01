# AES attacks

![test working](https://github.com/thomasperrot/aes-attacks/actions/workflows/testing.yml/badge.svg)

Homemade implementation of differential fault against AES using a single fault, written in Rust

## Overview

This crate contains an implementation of a Differential Fault Analysis on AES, using a single fault at eighth round. 
It is based on the research paper [Differential Fault Analysis of the Advanced Encryption Standard using a Single Fault](https://eprint.iacr.org/2009/575.pdf). 
This approach boils down to reducing the set of possible keys to `2^32` thanks to a first set of equations, then 
reducing this set to `2^8` possible keys thanks to a second set of equations. It relies on a single fault introduced in 
AES 8th round, before Sub Bytes.

**N.B**: The research paper contains several mistakes in the equations it provides. I corrected them in my source code.

I already implemented this attack in Python in this [repository](https://github.com/thomasperrot/aes-differential-fault-analysis),
and wanted to reimplement it in Rust.

## Usage

Install the package
```commandline
pip install aes-dfa
```
Then use it
```python
from aes_dfa import crack_key

keys: list[bytes] = crack_key(
    normal_cipher_text=b'\x81\xd6\xcd\xc3\xbd\x16\xfb\x8dr\xb9\xbb\x88\x81\x8b[\xe9',
    faulty_cipher_text=b'\xef\xf95\x08c\x01\x87\xb8\xd3IN\x8bp\xe6\x88~',
    nb_threads=3,
)
assert b'AAAAAAAAAAAAAAAA' in keys
```

## Performances

* In Python, the attack takes 8h to complete
* In Rust, the attack takes 45s to complete (using 3 threads)

So for this specific case, my Rust implementation is 640 times faster than my Python one.
