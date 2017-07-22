#include "keccak.h"

#define MIN(a, b) ((a) < (b) ? (a) : (b))


KeccakHash *from_PyObject(PyObject *pyObject) {
    unsigned int rate = PyLong_AsUnsignedLong(PyObject_GetAttrString(pyObject, "rate")),
                 blockSize = PyLong_AsUnsignedLong(PyObject_GetAttrString(pyObject, "blockSize")),
                 capacity = PyLong_AsUnsignedLong(PyObject_GetAttrString(pyObject, "capacity"));
    KeccakHash *ret = new_hash(rate, capacity);
    ret->blockSize = blockSize;
    PyObject *state = PyObject_GetAttrString(pyObject, "state"), *stateItem;
    int stateSize = PySequence_Size(state);
    if (stateSize != sizeof(ret->state)) {
        printf("Error: sequence is of invalid size");
        exit(1);
    }
    for (int i = 0; i < stateSize; i++) {
        stateItem = PySequence_GetItem(state, i);
        if (PyLong_Check(stateItem))
            ret->state[i] = PyLong_AsUnsignedLong(stateItem);
        else {
            printf("Error: sequence contains a non-int value");
            exit(1);
        }
    }
    return ret;
}

void to_PyObject(PyObject *pyObject, KeccakHash *hash) {
    PyObject_SetAttrString(pyObject, "rate", PyLong_FromUnsignedLong(hash->blockSize));
    PyObject *state = PyTuple_New(sizeof(hash->state));
    for (int i = 0; i < sizeof(hash->state); i++) {
        PySequence_SetItem(state, i, PyLong_FromUnsignedLong(hash->state[i]));
    }
    PyObject_SetAttrString(pyObject, "state", state);
    free(hash);
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


KeccakHash *new_hash(unsigned int rate, unsigned int capacity) {
    KeccakHash *hash = malloc(sizeof(hash));
    *hash = (KeccakHash) {
        .rate = rate,
        .rateInBytes = rate / 8,
        .blockSize = 0,
        .capacity = capacity,
        .outputByteLen = capacity / 8
    };

    /* Initialize the state */
    memset(hash->state, 0, sizeof(hash->state));
    return hash;
}


unsigned char *c_squeeze(KeccakHash *hash, unsigned char delimitedSuffix) {
    /* Do the padding and switch to the squeezing phase */
    /* Absorb the last few bits and add the first bit of padding (which coincides with the delimiter in delimitedSuffix) */
    hash->state[hash->blockSize] ^= delimitedSuffix;
    /* If the first bit of padding is at position rate-1, we need a whole new block for the second bit of padding */
    if (((delimitedSuffix & 0x80) != 0) && (hash->blockSize == (hash->rateInBytes-1)))
        permute(hash);
    /* Add the second bit of padding */
    hash->state[hash->rateInBytes-1] ^= 0x80;
    /* Switch to the squeezing phase */
    permute(hash);

    /* Squeeze out all the output blocks */
    unsigned int outputByteLen = hash->outputByteLen;
    unsigned char *output = malloc(hash->outputByteLen * sizeof(*output)), *outputPtr = output;
    while (outputByteLen > 0) {
        hash->blockSize = MIN(outputByteLen, hash->rateInBytes);
        memcpy(outputPtr, hash->state, hash->blockSize);
        outputPtr += hash->blockSize;
        outputByteLen -= hash->blockSize;

        if (outputByteLen > 0)
            permute(hash);
    }
    return output;
}
unsigned char *squeeze(PyObject *hashObject, unsigned char delimitedSuffix) {
    KeccakHash *hash = from_PyObject(hashObject);
    unsigned char *ret = c_squeeze(hash, delimitedSuffix);
    to_PyObject(hashObject, hash);
    return ret;
}


void c_absorb(KeccakHash *hash, unsigned char *input, unsigned long long int inputByteLen) {
    /* Absorb all the input blocks */
    while (inputByteLen > 0) {
        hash->blockSize = MIN(inputByteLen, hash->rateInBytes);
        for (int i = 0; i < hash->blockSize; i++)
            hash->state[i] ^= input[i];
        input += hash->blockSize;
        inputByteLen -= hash->blockSize;

        if (hash->blockSize == hash->rateInBytes) {
            permute(hash);
            hash->blockSize = 0;
        }
    }
}
void absorb(PyObject *hashObject, PyObject *unicodeObj) {
    if (PyUnicode_READY(unicodeObj) == 0) {
        int size = PyUnicode_GET_LENGTH(unicodeObj);
        switch (PyUnicode_KIND(unicodeObj)) {
            case PyUnicode_4BYTE_KIND:
                size *= 2;
            case PyUnicode_2BYTE_KIND:
                size *= 2;
            default:
                break;
        }
        unsigned char *input = PyUnicode_DATA(unicodeObj);
        KeccakHash *hash = from_PyObject(hashObject);
        c_absorb(hash, input, size);
        to_PyObject(hashObject, hash);
        return;
    } else {
        printf("Error: bad malloc call for unicode string");
        exit(1);
    }
}
