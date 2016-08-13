from random import randint
from crypto import *
from ntruencrypt import *


def test_keccak():
    from keccak import Keccak224
    pt = """023D91AC532601C7CA3942D62827566D9268BB4276FCAA1AE927693A6961652676D
            BA09219A01B3D5ADFA12547A946E78F3C5C62DD880B02D2EEEB4B96636529C6B011
            20B23EFC49CCFB36B8497CD19767B53710A636683BC5E0E5C9534CFC004691E87D1
            BEE39B86B953572927BD668620EAB87836D9F3F8F28ACE41150776C0BC6657178EB
            F297FE1F7214EDD9F215FFB491B681B06AC2032D35E6FDF832A8B06056DA70D77F1
            E9B4D26AE712D8523C86F79250718405F91B0A87C725F2D3F52088965F887D8CF87
            206DFDE422386E58EDDA34DDE2783B3049B86917B4628027A05D4D1F429D2B49C4B
            1C898DDDCB82F343E145596DE11A54182F39F4718ECAE8F506BD9739F5CD5D5686D
            7FEFC834514CD1B2C91C33B381B45E2E5335D7A8720A8F17AFC8C2CB2BD88B14AA2
            DCA099B00AA575D0A0CCF099CDEC4870FB710D2680E60C48BFC291FF0CEF2EEBF9B
            36902E9FBA8C889BF6B4B9F5CE53A19B0D9399CD19D61BD08C0C2EC25E099959848
            E6A550CA7137B63F43138D7B651""".replace(' ', '').replace('\n', '').decode('hex')
    expect = '230620d710cf3ab835059e1aa170735db17cae74b345765ff02e8d89'
    h = Keccak224(pt).hexdigest()
    assert h == expect
    print 'test-keccak passed'


def test_ntru():
    from ntruencrypt import NTRUEncrypt80
    m1 = "".join([chr(randint(32, 127)) for _ in range(1 << 5)])
    c = NTRUEncrypt80()
    e = c.encrypt(m1)
    m2 = c.decrypt(e)
    assert m1 == m2
    print 'test-ntru passed'


def test_crypto():
    from crypto import Hash, SymmetricEncryption, AsymmetricEncryption, Signature

    def test_hash():
        m1 = ''.join([chr(randint(32, 127)) for _ in range(1 << 5)])
        m2 = ''.join([chr(randint(32, 127)) for _ in range(1 << 5)])
        h = Hash()
        assert h.digest(m1) == h.digest(m1)
        h_m1_xor_m2 = h.digest(''.join(chr(ord(a) ^ ord(b))
                                       for a, b in zip(m1, m2)))
        hm1_xor_hm2 = ''.join(chr(ord(a) ^ ord(b))
                              for a, b in zip(*map(h.digest, (m1, m2))))
        assert h_m1_xor_m2 != hm1_xor_hm2
        print ' test-hash passed'

    def test_symmetric():
        msg = ''.join([chr(randint(32, 127)) for _ in range(1 << 5)])
        symm = SymmetricEncryption()
        assert msg == symm.decrypt(symm.encrypt(msg))
        print ' test-symmetric passed'

    def test_asymmetric():
        msg = ''.join([chr(randint(32, 127)) for _ in range(1 << 5)])
        asym = AsymmetricEncryption()
        assert msg == asym.decrypt(asym.encrypt(msg))
        print ' test-asymmetric passed'

    def test_signature():
        msg = ''.join([chr(randint(32, 127)) for _ in range(1 << 5)])
        sig = Signature()
        assert sig.verify(sig.sign(msg), msg)
        print ' test-signature passed'

    test_hash()
    test_symmetric()
    test_asymmetric()
    test_signature()
    print 'test-crypto passed'


def test_net():
    from socket import socket as ssocket, create_connection as socket, AF_INET, SOCK_STREAM
    from time import sleep
    from net import DumbChannel
    from concurrency import threaded

    @threaded
    def run_server(addr, msg):
        ssock = ssocket(AF_INET, SOCK_STREAM)
        ssock.bind(addr)
        ssock.listen(1)
        chan = DumbChannel(ssock.accept()[0])
        chan.send(msg)
        chan.sock.close()

    def test_client(addr, msg):
        sock = socket(addr)
        chan = DumbChannel(sock)
        assert msg == chan.recv()
        chan.sock.close()

    # FIXME: SecurreChannel does not like connecting :(

    addr = ('localhost', 4994)
    msg = ''.join([chr(randint(32, 127)) for _ in range(1 << 3)])
    run_server(addr, msg)
    sleep(1)
    test_client(addr, msg)
    print 'test-net passed'


def run():
    test_keccak()
    # test_ntru()
    test_crypto()
    test_net()
    print '\ntests passed'


if __name__ == '__main__':
    run()
