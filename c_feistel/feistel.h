#include "../c_keccak/keccak.h"
// FIXME: Is it bad to include relative (cousin) directories

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#ifndef FEISTEL_H
    #define FEISTEL_H

    #ifndef STRUCT_STRING
        #define STRUCT_STRING

        typedef struct {
            unsigned char *str;
            unsigned long long int len;
        } string;

    #endif

    enum cipher_mode {
        ECB = 0, CBC = 1, PCBC = 2, CFB = 3, OFB = 4
    } cipher_mode;

    typedef void (*round_func)(string sub_key, string in, string out);

    string new_string(int len);
    void free_string(string s);

    unsigned char *encrypt_(unsigned char *text, unsigned char *key, unsigned char *iv, int mode);
    unsigned char *decrypt_(unsigned char *text, unsigned char *key, unsigned char *iv, int mode);
    
#endif /* end of include guard: FEISTEL_H */
