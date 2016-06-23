from math import log, floor


def base_convert(digits, fromBase, toBase):
    n = 0
    for i in range(len(digits)):
        n += (digits[i] % fromBase) * (fromBase**i)
    if n == 0:
        return [0]
    newDigits = []
    while n:
        newDigits.append(int(n % toBase))
        n //= toBase
    return newDigits


def pad(unpadded_list, N):
    padded_lists = []
    for n in range(0, len(unpadded_list), N):
        padded_lists.append(unpadded_list[n:n + N])
    padded_lists[-1].extend([0 for n in range(N - len(padded_lists[-1]))])
    return padded_lists


def unpad(padded_lists):
    unpadded_list = []
    for l in padded_lists:
        unpadded_list.extend(l)
    while unpadded_list[-1] == 0:
        del unpadded_list[-1]
    return unpadded_list


def str_to_base(string, base, N):
    return pad(base_convert(list(bytearray(string)), 256, base), N)


def base_to_str(lists, base):
    return str(bytearray(base_convert(unpad(lists), base, 256)))
