#include "keccak.h"

#define MIN(a, b) ((a) < (b) ? (a) : (b))


KeccakHash from_PyObject(PyObject *pyObject) {
    unsigned int rate = PyLong_AsUnsignedLong(PyObject_GetAttrString(pyObject, "rate")),
                 block_size = PyLong_AsUnsignedLong(PyObject_GetAttrString(pyObject, "block_size")),
                 capacity = PyLong_AsUnsignedLong(PyObject_GetAttrString(pyObject, "capacity"));
    KeccakHash ret = c_new_hash(rate, capacity);
    ret.block_size = block_size;
    PyObject *state = PyObject_GetAttrString(pyObject, "state"), *stateItem;
    int stateSize = PyTuple_Size(state);
    if (stateSize != sizeof(ret.state)) {
        printf("Error: sequence is of invalid size (%d)\n", stateSize);
        exit(1);
    }
    for (int i = 0; i < stateSize; i++) {
        stateItem = PyTuple_GetItem(state, i);
        if (PyLong_Check(stateItem))
            ret.state[i] = PyLong_AsUnsignedLong(stateItem);
        else {
            printf("Error: sequence contains a non-int value");
            exit(1);
        }
    }
    return ret;
}

void to_PyObject(PyObject *pyObject, KeccakHash hash) {
    PyObject_SetAttrString(pyObject, "rate", PyLong_FromUnsignedLong(hash.rate));
    PyObject_SetAttrString(pyObject, "block_size", PyLong_FromUnsignedLong(hash.block_size));
    PyObject_SetAttrString(pyObject, "capacity", PyLong_FromUnsignedLong(hash.capacity));
    PyObject *stateObj = PyTuple_New(sizeof(hash.state));
    for (int i = 0; i < sizeof(hash.state); i++) {
        PyTuple_SetItem(stateObj, i, PyLong_FromUnsignedLong(hash.state[i]));
    }
    PyObject_SetAttrString(pyObject, "state", stateObj);
}


int LFSR86540(UINT8 *LFSR) {
    int result = ((*LFSR) & 0x01) != 0;
    if (((*LFSR) & 0x80) != 0)
        /* Primitive polynomial over GF(2): x^8+x^6+x^5+x^4+1 */
        (*LFSR) = ((*LFSR) << 1) ^ 0x71;
    else
        (*LFSR) <<= 1;
    return result;
}

void permute(KeccakHash *hash) {
    UINT8 LFSRstate = 0x01;

    for (unsigned int round = 0; round < 24; round++) {
        {   /* theta-step */
            tKeccakLane C[5], D;
            /* Compute the parity of the columns */
            for (unsigned int x = 0; x < 5; x++)
                C[x] = readLane(hash, x, 0) ^ readLane(hash, x, 1) ^ readLane(hash, x, 2) ^ readLane(hash, x, 3) ^ readLane(hash, x, 4);
            for (unsigned int x = 0; x < 5; x++) {
                /* Compute the θ effect for a given column */
                D = C[(x+4)%5] ^ ROL64(C[(x+1)%5], 1);
                /* Add the θ effect to the whole column */
                for (unsigned int y = 0; y < 5; y++)
                    XORLane(hash, x, y, D);
            }
        }

        {   /* rho-step and pi-step */
            tKeccakLane current, temp;
            /* Start at coordinates (1 0) */
            unsigned int x = 1, y = 0;
            current = readLane(hash, x, y);
            /* Iterate over ((0 1)(2 3))^t * (1 0) for 0 ≤ t ≤ 23 */
            for (unsigned int t = 0; t < 24; t++) {
                /* Compute the rotation constant r = (t+1)(t+2)/2 */
                unsigned int r = ((t + 1) * (t + 2) / 2) % 64;
                /* Compute ((0 1)(2 3)) * (x y) */
                unsigned int Y = (2 * x + 3 * y) % 5; x = y; y = Y;
                /* Swap current and state(x,y), and rotate */
                temp = readLane(hash, x, y);
                writeLane(hash, x, y, ROL64(current, r));
                current = temp;
            }
        }

        {   /* chi-step */
            tKeccakLane temp[5];
            for (unsigned int y = 0; y < 5; y++) {
                /* Take a copy of the plane */
                for (unsigned int x = 0; x < 5; x++)
                    temp[x] = readLane(hash, x, y);
                /* Compute χ on the plane */
                for (unsigned int x = 0; x < 5; x++)
                    writeLane(hash, x, y, temp[x] ^((~temp[(x+1)%5]) & temp[(x+2)%5]));
            }
        }

        {   /* iota-step */
            for (unsigned int j = 0; j < 7; j++) {
                unsigned int bitPosition = (1<<j)-1; /* 2^j-1 */
                if (LFSR86540(&LFSRstate))
                    XORLane(hash, 0, 0, (tKeccakLane)1<<bitPosition);
            }
        }
    }
}


KeccakHash c_new_hash(unsigned int rate, unsigned int capacity) {
    KeccakHash hash = (KeccakHash) {
        .state = {0},
        .rate = rate,
        .rate_bytes = rate / 8,
        .block_size = 0,
        .capacity = capacity,
        .digest_size = capacity / 8
    };

    return hash;
}
void new_hash(PyObject *hashObj, unsigned int rate, unsigned int capacity) {
    to_PyObject(hashObj, c_new_hash(rate, capacity));
}


string c_squeeze(KeccakHash hash) {
    /* Do the padding and switch to the squeezing phase */
    /* Absorb the last few bits and add the first bit of padding (which coincides with the delimiter 0x06) */
    hash.state[hash.block_size] ^= 0x06;
    /* Add the second bit of padding */
    hash.state[hash.rate_bytes-1] ^= 0x80;
    /* Switch to the squeezing phase */
    permute(&hash);

    /* Squeeze out all the output blocks */
    unsigned int digest_size = hash.digest_size;
    string output = (string) {
        .str = malloc(hash.digest_size + 1), 
        .len = hash.digest_size
    };
    unsigned char *outputPtr = output.str;
    while (digest_size > 0) {
        hash.block_size = MIN(digest_size, hash.rate_bytes);
        memcpy(outputPtr, hash.state, hash.block_size);
        outputPtr += hash.block_size;
        digest_size -= hash.block_size;

        if (digest_size > 0)
            permute(&hash);
    }
    return output;
}
PyObject *squeeze(PyObject *hashObject) {
    KeccakHash hash = from_PyObject(hashObject);
    string squeezed = c_squeeze(hash);
    PyObject *ret = PyBytes_FromStringAndSize((char*) squeezed.str, squeezed.len);
    to_PyObject(hashObject, hash);
    free(squeezed.str);
    return ret;
}


void c_absorb(KeccakHash hash, string input) {
    /* Absorb all the input blocks */
    while (input.len > 0) {
        hash.block_size = MIN(input.len, hash.rate_bytes);
        for (int i = 0; i < hash.block_size; i++)
            hash.state[i] ^= input.str[i];
        input.str += hash.block_size;
        input.len -= hash.block_size;

        if (hash.block_size == hash.rate_bytes) {
            permute(&hash);
            hash.block_size = 0;
        }
    }
}
void absorb(PyObject *hashObject, PyObject *bytesObj) {
    int size = PyBytes_Size(bytesObj);
    string input = (string) {
        .str = (unsigned char *) PyBytes_AsString(bytesObj),
        .len = size
    };
    KeccakHash hash = from_PyObject(hashObject);
    c_absorb(hash, input);
    to_PyObject(hashObject, hash);
    free(input.str);
}


string c_keccak(string input, int out_bytes) {
    KeccakHash hash = c_new_hash(input.len, out_bytes);
    c_absorb(hash, input);
    return c_squeeze(hash);
}
