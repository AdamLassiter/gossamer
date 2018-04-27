#! /usr/bin/env python3

import random
import string
import unittest


def asciistr(i: int):
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(i)])


class CipherTests:

    def test_encrypt(self):
        text = asciistr(64)
        encr = self.cipher.encrypt(text)
        decr = self.cipher.decrypt(encr)
        self.assertEqual(text, decr)


class TestNTRUEncryptMethods(unittest.TestCase, CipherTests):
    import ntruencrypt

    def setUp(self):
        self.cipher = self.ntruencrypt.NTRUEncrypt256()

    def test_keygen(self):
        self.assertTrue(self.cipher.keygen(self.cipher.params))

    def test_encode(self):
        text = bytes(asciistr(64), 'utf8')
        encd = self.ntruencrypt.bytes2base(text, self.cipher.params['p'], self.cipher.params['N'])
        decd = self.ntruencrypt.base2bytes(encd, self.cipher.params['p'])
        self.assertEqual(text, decd)


class TestKeccakHashMethods(unittest.TestCase):
    import keccak

    def test_consistency(self):
        text = asciistr(64)
        k1 = self.keccak.Keccak512()
        k1.update(text)
        k2 = self.keccak.Keccak512(text)
        self.assertEqual(k1.digest(), k2.digest())


class TestFeistelCipherMethods(CipherTests):
    import feistel

    def setUp(self):
        self.cipher = self.feistel.FeistelCipher()


if __name__ == '__main__':
    unittest.main(verbosity=2)
