


def specimen_csv_to_dict(csvfilepath: str,
                         label: str=None, width: float=None,
                         thick: float=None) -> dict[str, object]:
    readmeta = True
    metadict = {}
    if label is not None:
        metadict["label"] = label
    if width is not None:
        metadict["width"] = width
    if thick is not None:
        metadict["thick"] = thick
    readtest = False
    testdict = {}
    testcount = 0
    with open(csvfilepath, 'rt') as csvfile:
        for line in csvfile:
            line = line.rstrip('\n')
            if line.strip() == '':
                readmeta = False
                readtest = True
            elif readmeta:
                linesplit = line.split(',')
                param = linesplit[0]
                value = linesplit[1].strip('"')
                if len(linesplit) > 2:
                    unit = linesplit[2].strip()
                else:
                    unit = None
                if value.strip() == '':
                    value = None
                else:
                    if unit is not None:
                        value = float(value)
                metadict[param] = {}
                if unit is None:
                    metadict[param]['value'] = value
                elif unit == 'kN':
                    metadict[param]['value'] = value*1000
                    metadict[param]['unit'] = 'N'
                else:
                    metadict[param]['value'] = value
                    metadict[param]['unit'] = unit
            elif readtest:
                testcount += 1
                linesplit = line.split(',')
                if testcount == 1:
                    testdict = {ls: {'data': []} for ls in linesplit}
                elif testcount == 2:
                    for hd, ls in zip(list(testdict), linesplit):
                        testdict[hd]['unit'] = ls.lstrip('(').rstrip(')')
                else:
                    for hd, ls in zip(list(testdict), linesplit):
                        value = float(ls.strip('"'))
                        if testdict[hd]['unit'] == 'kN':
                            testdict[hd]['data'].append(value*1000)
                        else:
                            testdict[hd]['data'].append(value)
    for hd in testdict:
        if testdict[hd]['unit'] == 'kN':
            testdict[hd]['unit'] = 'N'

    specdict = {'meta': metadict, 'test': testdict}
    return specdict
