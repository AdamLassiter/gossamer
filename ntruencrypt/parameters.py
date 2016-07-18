dict_layout = ["N", "d", "Hw", "p", "q"]

# Obsolete since Sept. 2015, see ./params.pdf
k = {80:  [251,  8,  72, 3,  293],
     112: [347, 11, 132, 3,  541],
     128: [397, 12, 156, 3,  659],
     160: [491, 15, 210, 3,  967],
     192: [587, 17, 306, 3, 1229],
     256: [787, 22, 462, 3, 2027]}

for key, value in k.items():
    k[key] = dict(zip(dict_layout, value))
