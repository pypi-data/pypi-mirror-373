from aes_dfa import crack_key


def test_crack_key():
    keys: list[bytes] = crack_key(
        normal_cipher_text=b'\x81\xd6\xcd\xc3\xbd\x16\xfb\x8dr\xb9\xbb\x88\x81\x8b[\xe9',
        faulty_cipher_text=b'\xef\xf95\x08c\x01\x87\xb8\xd3IN\x8bp\xe6\x88~',
        nb_threads=3,
    )
    assert b'AAAAAAAAAAAAAAAA' in keys
