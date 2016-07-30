dict_layout = ["N", "d", "Hw", "p", "q"]

# Obsolete since Sept. 2015, see ./params.pdf
k = {80:  [251,  8,  72, 3,  256],
     112: [347, 11, 132, 3,  512],
     128: [397, 12, 156, 3, 1024],
     160: [491, 15, 210, 3, 1024],
     192: [587, 17, 306, 3, 1024],
     256: [787, 22, 462, 3, 2048]}

for key, value in k.items():
    k[key] = dict(zip(dict_layout, value))
