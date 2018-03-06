#! /usr/bin/env python3

import unittest
import random


class TestNTRUEncryptMethods(unittest.TestCase):
    import ntruencrypt

    def setUp(self):
        self.ntru = self.ntruencrypt.NTRUEncrypt256()

    def test_keygen(self):
        self.assertTrue(self.ntru.keygen(self.ntru.params))

    def test_encode(self):
        text = ''.join([chr(random.randint(64, 95)) for _ in range(256)])
        encd = self.ntruencrypt.bytes2base(text, self.ntru.params['p'], self.ntru.params['N'])
        decd = self.ntruencrypt.base2bytes(encd, self.ntru.params['p'])
        self.assertEqual(text, decd)

    def test_encrypt(self):
        text = ''.join([chr(random.randint(64, 95)) for _ in range(256)])
        encr = self.ntru.encrypt(text)
        decr = self.ntru.decrypt(encr)
        self.assertEqual(text, decr)

"""
class TestKeccakHashMethods(unittest.TestCase):
    import keccak

    def test_consistency(self):
        text = ''.join([chr(random.randint(64, 95)) for _ in range(256)])
        k1 = self.keccak.Keccak512()
        k1.update(text)
        k2 = self.keccak.Keccak512(text)
        self.assertEqual(k1.digest(), k2.digest())
"""

if __name__ == '__main__':
    unittest.main()
