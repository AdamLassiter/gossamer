#! /usr/bin/env python3

import random
import string
import unittest


class TestSuiteMeta(type):
    full_suite = unittest.TestSuite()

    def __new__(metacls, name, bases, attr):
        def cls_init(self, *args, **kwargs):
            super(type(self), self).__init__(*args, **kwargs)
            for fname in filter(lambda x: x[:4] == 'test', dir(self)):
                def setUpBootstrap(func):
                    def setUp(self):
                        func()
                        print('\n', self.__class__.__name__)
                    return setUp
                cname = ''.join(x.title() for x in fname.split('_'))
                TestCase = type(
                    '.'.join([self.__class__.__name__, cname]),
                    (unittest.TestCase,),
                    {
                        'runTest': getattr(self, fname),
                        'setUp': setUpBootstrap(getattr(self, 'setUp')),
                    }
                )
                self.addTest(TestCase())

        def cls_run(self, *args, **kwargs):
            print('=' * 70)
            print(self.__class__.__name__)
            super(type(self), self).run(*args, **kwargs)
 
        cls_obj = super().__new__(
            metacls,
            name,
            bases + (unittest.TestSuite, unittest.TestCase),
            dict(attr, __init__=cls_init, run=cls_run)
        )
        TestSuiteMeta.full_suite.addTest(cls_obj())
        return cls_obj



def asciistr(i: int):
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(i)])



class CipherTests:

    def test_encrypt(self):
        text = asciistr(64)
        encr = self.cipher.encrypt(text)
        decr = self.cipher.decrypt(encr)
        assert text == decr



class TestNTRUEncryptMethods(CipherTests, metaclass=TestSuiteMeta):
    import ntruencrypt

    def setUp(self):
        self.cipher = self.ntruencrypt.NTRUEncrypt256()

    def test_keygen(self):
        assert self.cipher.keygen(self.cipher.params)

    def test_encode(self):
        text = bytes(asciistr(64), 'utf8')
        encd = self.ntruencrypt.bytes2base(text, self.cipher.params['p'], self.cipher.params['N'])
        decd = self.ntruencrypt.base2bytes(encd, self.cipher.params['p'])
        assert text == decd



class TestKeccakHashMethods(metaclass=TestSuiteMeta):
    import keccak

    def test_consistency(self):
        text = asciistr(64)
        k1 = self.keccak.Keccak512()
        k1.update(text)
        k2 = self.keccak.Keccak512(text)
        assert k1.digest() == k2.digest()



class TestFeistelCipherMethods(CipherTests, metaclass=TestSuiteMeta):
    import feistel

    def setUp(self):
        self.cipher = self.feistel.FeistelCipher()



if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    for suite in TestSuiteMeta.full_suite:
        runner.run(suite)
