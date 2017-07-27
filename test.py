#! /usr/bin/python3
import ntruencrypt
import keccak

import unittest
import doctest
import random


class TestNTRUEncryptMethods(unittest.TestCase):

    def setUp(self):
        self.ntru = ntruencrypt.NTRUEncrypt256()

    def test_keygen(self):
        self.assertTrue(self.ntru.keygen(self.ntru.params))

    def test_inverse(self):
        f = ntruencrypt.NTRUCipher.random_poly(self.ntru.params)
        g = f * self.ntru.params['p'] + 1
        h = g.inverse_modp(self.ntru.params['p'])
        i = (f * f.inverse_modp(3)) % 3
        self.assertTrue(h[0] == 1)
        self.assertFalse(any(h[1:]))
        self.assertEqual(h, i)

    def test_encrypt_poly(self):
        mesg = self.ntru.random_poly(self.ntru.params) % self.ntru.params['p']
        encr = self.ntru.encrypt_poly(mesg)
        decr = self.ntru.decrypt_poly(encr)
        self.assertEqual(mesg, decr)

    def test_encode(self):
        text = ''.join([chr(random.randint(64, 95)) for _ in range(256)])
        encd = ntruencrypt.str2base(text, self.ntru.params[
                                    'p'], self.ntru.params['N'])
        decd = ntruencrypt.base2str(encd, self.ntru.params['p'])
        self.assertEqual(text, decd)

    def test_encrypt(self):
        text = ''.join([chr(random.randint(64, 95)) for _ in range(256)])
        encr = self.ntru.encrypt(text)
        decr = self.ntru.decrypt(encr)
        self.assertEqual(text, decr)


class TestKeccakHashMethods(unittest.TestCase):

    def setUp(self):
        self.keccak = keccak.Keccak512()

    def test_consistency(self):
        text = ''.join([chr(random.randint(64, 95)) for _ in range(256)])
        k1 = keccak.Keccak512()
        k1.update(text)
        k2 = keccak.Keccak512(text)
        self.assertEqual(k1.digest(), k2.digest())


if __name__ == '__main__':
    unittest.main()
