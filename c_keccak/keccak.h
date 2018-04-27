#include <Python.h>
#include <stdlib.h>
#include <string.h>

#ifndef KECCAK_H
    #define KECCAK_H

    typedef char UINT8;
    typedef unsigned long long int UINT64;
    typedef UINT64 tKeccakLane;

    #define ROL64(a, offset) ((((UINT64)a) << offset) ^ (((UINT64)a) >> (64-offset)))
    #define i(x, y) ((x)+5*(y))

    #ifndef LITTLE_ENDIAN
        static UINT64 load64(const UINT8 *x) {
            int i;
            UINT64 u=0;

            for (i = 7; i >= 0; --i) {
                u <<= 8;
                u |= x[i];
            }
            return u;
        }
        static void store64(UINT8 *x, UINT64 u) {
            unsigned int i;

            for (i = 0; i < 8; ++i) {
                x[i] = u;
                u >>= 8;
            }
        }
        static void xor64(UINT8 *x, UINT64 u) {
            unsigned int i;

            for (i = 0; i < 8; ++i) {
                x[i] ^= u;
                u >>= 8;
            }
        }
        #define readLane(h, x, y)          load64((UINT8*)h->state+sizeof(tKeccakLane)*i(x, y))
        #define writeLane(h, x, y, lane)   store64((UINT8*)h->state+sizeof(tKeccakLane)*i(x, y), lane)
        #define XORLane(h, x, y, lane)     xor64((UINT8*)h->state+sizeof(tKeccakLane)*i(x, y), lane)
    #else
        #define readLane(h, x, y)          (((tKeccakLane*)h->state)[i(x, y)])
        #define writeLane(h, x, y, lane)   (((tKeccakLane*)h->state)[i(x, y)]) = (lane)
        #define XORLane(h, x, y, lane)     (((tKeccakLane*)h->state)[i(x, y)]) ^= (lane)
    #endif


    typedef struct {
        UINT8 state[200];
        unsigned int rate, rate_bytes, block_size, capacity, digest_size;
    } KeccakHash;

    #ifndef STRUCT_STRING
        #define STRUCT_STRING
        
        typedef struct {
            char *str;
            unsigned long long int len;
        } string;
    
    #endif

    KeccakHash from_PyObject(PyObject *);
    void to_PyObject(PyObject *, KeccakHash);

    KeccakHash c_new_hash(unsigned int, unsigned int);
    void new_hash(PyObject *, unsigned int, unsigned int);

    string c_squeeze(KeccakHash);
    PyObject *squeeze(PyObject *);

    void c_absorb(KeccakHash, string);
    void absorb(PyObject *, PyObject *);

    string c_hash(string, int);

#endif /* end of include guard: KECCAK_H */
