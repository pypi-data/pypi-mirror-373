


def calculate_emod(stress: list[float], strain: list[float]):
    emodave = []
    for i in range(1, len(strain)):
        emodave.append((stress[i]-stress[i-1])/(strain[i]-strain[i-1]))
    emodave2 = []
    for i in range(1, len(emodave)):
        emodave2.append((emodave[i]+emodave[i-1])/2)
    emod = [emodave[0]] + emodave2 + [emodave[-1]]
    return emod

def fix_offset_strain(strain: list[float]):
    offset = 0.0
    newstrain = [strain[0]]
    for i in range(1, len(strain)):
        if strain[i] < strain[i-1]:
            offset += strain[i-1]-strain[i]
        newstrain.append(strain[i] + offset)
    return newstrain

def fix_offset_strain_v2(strain: list[float], tol: float=2.0):
    delta = [strain[i]-strain[i-1] for i in range(1, len(strain))]
    # for d in delta:
    #     print(d)
    gooddelta = delta[0]
    for i in range(len(delta)):
        if delta[i] <= (1.0+tol)*gooddelta and delta[i] >= (1.0-tol)*gooddelta:
            if delta[i] > 0.0:
                gooddelta = delta[i]
        else:
            # print(f'Bad delta at {i:d}.')
            delta[i] = gooddelta
    newstrain = [strain[0]]
    for i, d in enumerate(delta):
        newstrain.append(newstrain[i]+d)
    return newstrain

def trim_strain(strain: list[float], maxstrain: float=float('inf')):
    newstrain = []
    for strn in strain:
        if len(newstrain) > 0:
            if strn == newstrain[-1]:
                continue
        if strn > maxstrain:
            continue
        newstrain.append(strn)
    return newstrain
