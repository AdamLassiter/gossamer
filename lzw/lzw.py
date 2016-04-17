import struct
import itertools


CLEAR_CODE = 256
END_OF_INFO_CODE = 257

DEFAULT_MIN_BITS = 9
DEFAULT_MAX_BITS = 12




def compress(plaintext_bytes):
    encoder = ByteEncoder()
    return encoder.encodetobytes(plaintext_bytes)


def decompress(compressed_bytes):
    decoder = ByteDecoder()
    return decoder.decodefrombytes(compressed_bytes)





class ByteEncoder(object):
    
    def __init__(self, max_width=DEFAULT_MAX_BITS):
       self._encoder = Encoder(max_code_size=2**max_width)
       self._packer = BitPacker(initial_code_size=self._encoder.code_size())


    def encodetobytes(self, bytesource):
        codepoints = self._encoder.encode(bytesource)
        codebytes = self._packer.pack(codepoints)

        return codebytes


class ByteDecoder(object):
    
    def __init__(self):
       self._decoder = Decoder()
       self._unpacker = BitUnpacker(initial_code_size=self._decoder.code_size())
       self.remaining = []

    def decodefrombytes(self, bytesource):
       codepoints = self._unpacker.unpack(bytesource)
       clearbytes = self._decoder.decode(codepoints)
       
       return clearbytes


class BitPacker(object):
    
    def __init__(self, initial_code_size):
       self._initial_code_size = initial_code_size


    def pack(self, codepoints):
        tailbits = []
        codesize = self._initial_code_size

        minwidth = 8
        while (1 << minwidth) < codesize:
            minwidth = minwidth + 1

        nextwidth = minwidth

        for pt in codepoints:

            newbits = inttobits(pt, nextwidth)
            tailbits = tailbits + newbits

            codesize = codesize + 1

            if pt == END_OF_INFO_CODE:
               while len(tailbits) % 8:
                  tailbits.append(0)
                  
            if pt in [ CLEAR_CODE, END_OF_INFO_CODE ]:
                nextwidth = minwidth
                codesize = self._initial_code_size
            elif codesize >= (2 ** nextwidth):
                nextwidth = nextwidth + 1

            while len(tailbits) > 8:
                nextbits = tailbits[:8]
                nextbytes = bitstobytes(nextbits)
                for bt in nextbytes:
                    yield struct.pack("B", bt)

                tailbits = tailbits[8:]

                       
        if tailbits:
            tail = bitstobytes(tailbits)
            for bt in tail:
                yield struct.pack("B", bt)

                


class BitUnpacker(object):
    
    def __init__(self, initial_code_size):
       self._initial_code_size = initial_code_size


    def unpack(self, bytesource):
        bits = []
        offset = 0
        ignore = 0
        
        codesize = self._initial_code_size
        minwidth = 8
        while (1 << minwidth) < codesize:
            minwidth = minwidth + 1

        pointwidth = minwidth

        for nextbit in bytestobits(bytesource):

            offset = (offset + 1) % 8
            if ignore > 0:
                ignore = ignore - 1
                continue

            bits.append(nextbit)

            if len(bits) == pointwidth:
                codepoint = intfrombits(bits)
                bits = []

                yield codepoint

                codesize = codesize + 1

                if codepoint in [ CLEAR_CODE, END_OF_INFO_CODE ]:
                    codesize = self._initial_code_size
                    pointwidth = minwidth
                else:
                    # is this too late?
                    while codesize >= (2 ** pointwidth):
                        pointwidth = pointwidth + 1

                if codepoint == END_OF_INFO_CODE:
                    ignore = (8 - offset) % 8



class Decoder(object):
    
    def __init__(self):
       self._clear_codes()
       self.remainder = []


    def code_size(self):
       return len(self._codepoints)


    def decode(self, codepoints):
        codepoints = [ cp for cp in codepoints ]

        for cp in codepoints:
            decoded = self._decode_codepoint(cp)
            for character in decoded:
                yield character



    def _decode_codepoint(self, codepoint):
        ret = b""

        if codepoint == CLEAR_CODE:
            self._clear_codes()
        elif codepoint == END_OF_INFO_CODE:
            raise ValueError("End of information code not supported directly by this Decoder")
        else:
            if codepoint in self._codepoints:
                ret = self._codepoints[ codepoint ]
                if None != self._prefix:
                    self._codepoints[ len(self._codepoints) ] = self._prefix + ret[0]

            else:
                ret = self._prefix + self._prefix[0]
                self._codepoints[ len(self._codepoints) ] = ret

            self._prefix = ret

        return ret


    def _clear_codes(self):
        self._codepoints = dict( (pt, struct.pack("B", pt)) for pt in range(256) )
        self._codepoints[CLEAR_CODE] = CLEAR_CODE
        self._codepoints[END_OF_INFO_CODE] = END_OF_INFO_CODE
        self._prefix = None


class Encoder(object):
    
    def __init__(self, max_code_size=(2**DEFAULT_MAX_BITS)):
        self.closed = False

        self._max_code_size = max_code_size
        self._buffer = ''
        self._clear_codes()            

        if max_code_size < self.code_size():
            raise ValueError("Max code size too small, (must be at least {0})".format(self.code_size()))


    def code_size(self):
        return len(self._prefixes)


    def flush(self):
        flushed = []

        if self._buffer:
            yield self._prefixes[ self._buffer ]
            self._buffer = ''            

        yield CLEAR_CODE
        self._clear_codes()

            


    def encode(self, bytesource):
        for b in bytesource:
            for point in self._encode_byte(b):
                yield point

            if self.code_size() >= self._max_code_size:
                for pt in self.flush():
                    yield pt
        
        for point in self.flush():
            yield point


    def _encode_byte(self, byte):
        new_prefix = self._buffer
        
        if new_prefix + byte in self._prefixes:
            new_prefix = new_prefix + byte
        elif new_prefix:
            encoded = self._prefixes[ new_prefix ]
            self._add_code(new_prefix + byte)
            new_prefix = byte

            yield encoded
        
        self._buffer = new_prefix




    def _clear_codes(self):
        self._prefixes = dict( (struct.pack("B", codept), codept) for codept in range(256) )
        self._prefixes[ CLEAR_CODE ] = CLEAR_CODE
        self._prefixes[ END_OF_INFO_CODE ] = END_OF_INFO_CODE


    def _add_code(self, newstring):
        self._prefixes[ newstring ] = len(self._prefixes)



class PagingEncoder(object):

    def __init__(self, initial_code_size, max_code_size):
        self._initial_code_size = initial_code_size
        self._max_code_size = max_code_size


    def encodepages(self, pages):
        for page in pages:

            encoder = Encoder(max_code_size=self._max_code_size)
            codepoints = encoder.encode(page)
            codes_and_eoi = itertools.chain([ CLEAR_CODE ], codepoints, [ END_OF_INFO_CODE ])

            packer = BitPacker(initial_code_size=encoder.code_size())
            packed = packer.pack(codes_and_eoi)

            for byte in packed: 
                yield byte


            

class PagingDecoder(object):

    def __init__(self, initial_code_size):
        self._initial_code_size = initial_code_size
        self._remains = []

    def next_page(self, codepoints):
        self._remains = []

        try:
            while 1:
                cp = codepoints.next()
                if cp != END_OF_INFO_CODE:
                    yield cp
                else:
                    self._remains = codepoints
                    break

        except StopIteration:
            pass
        

    def decodepages(self, bytesource):
        unpacker = BitUnpacker(initial_code_size=self._initial_code_size)
        codepoints = unpacker.unpack(bytesource)

        self._remains = codepoints
        while self._remains:
            nextpoints = self.next_page(self._remains)
            nextpoints = [ nx for nx in nextpoints ]

            decoder = Decoder()
            decoded = decoder.decode(nextpoints)
            decoded = [ dec for dec in decoded ]

            yield decoded

def unpackbyte(b):
   (ret,) = struct.unpack("B", b)
   return ret


def filebytes(fileobj, buffersize=1024):
    buff = fileobj.read(buffersize)
    while buff:
        for byte in buff: yield byte
        buff = fileobj.read(buffersize)

    
def readbytes(filename, buffersize=1024):
    with open(filename, "rb") as infile:
        for byte in filebytes(infile, buffersize):
            yield byte



def bytestostr(bytesource):
    string = ""
    for bt in bytesource:
        string += bytesource
    return string



def writebytes(filename, bytesource):
    with open(filename, "wb") as outfile:
        for bt in bytesource:
            outfile.write(bt)


def inttobits(anint, width=None):
    remains = anint
    retreverse = []
    while remains:
        retreverse.append(remains & 1)
        remains = remains >> 1

    retreverse.reverse()

    ret = retreverse
    if None != width:
        ret_head = [ 0 ] * (width - len(ret))
        ret = ret_head + ret

    return ret


def intfrombits(bits):
    ret = 0
    lsb_first = [ b for b in bits ]
    lsb_first.reverse()
    
    for bit_index in range(len(lsb_first)):
        if lsb_first[ bit_index ]:
            ret = ret | (1 << bit_index)

    return ret


def bytestobits(bytesource):
    for b in bytesource:

        value = unpackbyte(b)

        for bitplusone in range(8, 0, -1):
            bitindex = bitplusone - 1
            nextbit = 1 & (value >> bitindex)
            yield nextbit


def bitstobytes(bits):
    ret = []
    nextbyte = 0
    nextbit = 7
    for bit in bits:
        if bit:
            nextbyte = nextbyte | (1 << nextbit)

        if nextbit:
            nextbit = nextbit - 1
        else:
            ret.append(nextbyte)
            nextbit = 7
            nextbyte = 0

    if nextbit < 7: ret.append(nextbyte)
    return ret
