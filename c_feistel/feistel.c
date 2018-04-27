#include "feistel.h"

#define HASH_BLOCKSIZE 1024
#define FEISTEL_ROUNDS 4
#define strlen(x) strlen((char *) x)

typedef string (*hash_func)(string in, int out_bytes);


void xor (string a, string b, string o) {
    for (unsigned int i = 0; i < o.len; i++)
        o.str[i] = a.str[i] ^ b.str[i];
}


string new_string(int len) {
    string s;
    s = (string) {
        .len = (unsigned long long) len,
        .str = calloc(sizeof(s.str), len)
    };
    return s;
}


void free_string(string s) {
    free(s.str);
}


string hash_feistel_block(string input, string key, string output, hash_func hash, bool forward) {
    assert(input.len == HASH_BLOCKSIZE);
    string buffer = new_string(2 * input.len);
    string left, right, *in, *out, hashed;
    memcpy(output.str, input.str, input.len);
    for (int round_nmbr = forward? 0:FEISTEL_ROUNDS-1;
         forward? round_nmbr<FEISTEL_ROUNDS:round_nmbr>=0;
         forward? round_nmbr++:round_nmbr--) {
        left = (string) {
            .str = output.str,
            .len = output.len / 2
        };
        right = (string) {
            .str = output.str + left.len,
            .len = left.len
        };
        in = round_nmbr % 2 ? &left : &right; out = round_nmbr % 2 ? &right : &left;
        
        memcpy(buffer.str, key.str, key.len);
        memcpy(buffer.str + key.len, in->str, in->len);
        buffer.len = key.len + in->len;
        hashed = hash(buffer, HASH_BLOCKSIZE);
        xor(hashed, *out, *out);
        free(hashed.str);
    }
    return output;
}


string c_encrypt(string plaintext, string key, string iv, enum cipher_mode mode) {
    assert(plaintext.len % HASH_BLOCKSIZE == 0);
    string ciphertext = new_string(plaintext.len), temp = new_string(HASH_BLOCKSIZE);
    string sub_text;
    for (unsigned int i = 0; i < plaintext.len / HASH_BLOCKSIZE; i++) {
        sub_text = (string) {
            .str = plaintext.str + i * plaintext.len / HASH_BLOCKSIZE,
            .len = HASH_BLOCKSIZE
        };
        
        switch (mode) {
            case ECB:
                hash_feistel_block(sub_text, key, temp, c_hash, true);
                memcpy(ciphertext.str + i * HASH_BLOCKSIZE, temp.str, HASH_BLOCKSIZE);
                break;
                
            case CBC:
                xor(iv, sub_text, iv);
                hash_feistel_block(iv, key, temp, c_hash, true);
                memcpy(ciphertext.str + i * HASH_BLOCKSIZE, temp.str, HASH_BLOCKSIZE);
                break;
                
            case PCBC:
                xor(iv, sub_text, iv);
                hash_feistel_block(iv, key, temp, c_hash, true);
                memcpy(ciphertext.str + i * HASH_BLOCKSIZE, temp.str, HASH_BLOCKSIZE);
                xor(temp, sub_text, iv);
                break;
                
            case CFB:
                hash_feistel_block(iv, key, temp, c_hash, true);
                xor(sub_text, temp, iv);
                memcpy(ciphertext.str + i * HASH_BLOCKSIZE, iv.str, HASH_BLOCKSIZE);
                break;
            
            case OFB:
                hash_feistel_block(iv, key, temp, c_hash, true);
                memcpy(iv.str, temp.str, HASH_BLOCKSIZE);
                xor(sub_text, temp, temp);
                memcpy(ciphertext.str + i * HASH_BLOCKSIZE, temp.str, HASH_BLOCKSIZE);
                break;
        }
    }
    free_string(temp);
    return ciphertext;
}
char *encrypt_(char *input_ptr, char *key_ptr, char *iv_ptr, int mode) {
    assert(0 <= mode && mode <= 4);
    string input = (string) {
        .len = strlen(input_ptr),
        .str = input_ptr
    };
    string key = (string) {
        .len = strlen(key_ptr),
        .str = key_ptr
    };
    string iv = (string) {
        .len = strlen(iv_ptr),
        .str = iv_ptr
    };
    return c_encrypt(input, key, iv, mode).str;
}


string c_decrypt(string ciphertext, string key, string iv, enum cipher_mode mode) {
    assert(ciphertext.len % HASH_BLOCKSIZE == 0);
    string plaintext = new_string(ciphertext.len), temp = new_string(HASH_BLOCKSIZE);
    string sub_text;
    for (unsigned int i = 0; i < ciphertext.len / HASH_BLOCKSIZE; i++) {
        sub_text = (string) {
            .str = ciphertext.str + i * ciphertext.len / HASH_BLOCKSIZE,
            .len = HASH_BLOCKSIZE
        };
        
        switch (mode) {
            case ECB:
                hash_feistel_block(sub_text, key, temp, c_hash, false);
                memcpy(plaintext.str + i * HASH_BLOCKSIZE, temp.str, HASH_BLOCKSIZE);
                break;
                
            case CBC:
                hash_feistel_block(sub_text, key, temp, c_hash, false);
                xor(iv, temp, temp);
                memcpy(iv.str, sub_text.str, HASH_BLOCKSIZE);
                memcpy(plaintext.str + i * HASH_BLOCKSIZE, temp.str, HASH_BLOCKSIZE);
                break;
                
            case PCBC:
                hash_feistel_block(sub_text, key, temp, c_hash, false);
                xor(iv, temp, temp);
                xor(sub_text, temp, iv);
                memcpy(plaintext.str + i * HASH_BLOCKSIZE, temp.str, HASH_BLOCKSIZE);
                break;
                
            case CFB:
                hash_feistel_block(iv, key, temp, c_hash, true);
                xor(sub_text, temp, iv);
                memcpy(plaintext.str + i * HASH_BLOCKSIZE, iv.str, HASH_BLOCKSIZE);
                memcpy(iv.str, sub_text.str, HASH_BLOCKSIZE);
                break;
            
            case OFB:
                hash_feistel_block(iv, key, temp, c_hash, true);
                memcpy(iv.str, temp.str, HASH_BLOCKSIZE);
                xor(sub_text, temp, temp);
                memcpy(plaintext.str + i * HASH_BLOCKSIZE, temp.str, HASH_BLOCKSIZE);
                break;
        }
    }
    free_string(temp);
    return plaintext;
}
char *decrypt_(char *input_ptr, char *key_ptr, char *iv_ptr, int mode) {
    assert(0 <= mode && mode <= 4);
    string input = (string) {
        .len = strlen(input_ptr),
        .str = input_ptr
    };
    string key = (string) {
        .len = strlen(key_ptr),
        .str = key_ptr
    };
    string iv = (string) {
        .len = strlen(iv_ptr),
        .str = iv_ptr
    };
    return c_decrypt(input, key, iv, mode).str;
}
