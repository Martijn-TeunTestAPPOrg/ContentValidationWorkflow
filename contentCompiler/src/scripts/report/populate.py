from config import dataset, taxcoReport, contentReport
from config import TC1_COL, TC2_COL, TC3_COL, PROCES_COL, PROCESSTAP_COL, NOT_NECESSARY_ICON, LT_COL, DT_COL, OI_COL, PI_COL, LT, DT, OI, PI


"""
Fills the taxco report with the data from the dataset
Every TC1 code is the unique identifier
"""
def populateTaxcoReport():
    global taxcoReport

    for row in dataset[1:]:
        tc1 = row[TC1_COL]
        tc2 = row[TC2_COL]
        proces = row[PROCES_COL]
        processtap = row[PROCESSTAP_COL]

        if tc1 in taxcoReport:
            if taxcoReport[tc1]['TC2'][1] == '🏳️' or taxcoReport[tc1]['TC2'][2] == '🏳️':
                splittedTc2 = tc2.split(',')
                for index in range(1, 3):
                    if taxcoReport[tc1]['TC2'][index] == '🏳️' and splittedTc2[index] != '🏳️':
                        taxcoReport[tc1]['TC2'][index] = splittedTc2[index]

        if tc1 not in taxcoReport: 
            splittedTc2 = tc2.split(',')

            taxcoReport[tc1] = {
                "Proces" : proces,
                "Processtap" : processtap,
                'TC2': [NOT_NECESSARY_ICON if splittedTc2[0] == 'X' else 'x', NOT_NECESSARY_ICON if splittedTc2[1] == 'X' else 'x', NOT_NECESSARY_ICON if splittedTc2[2] == 'X' else 'x']        
            }

"""
Fills the Report 2 data with the data from the dataset.
Every unique TC3 and TC1 combination will be added to the Report 2 data.
"""
def populateContentReport():
    global contentReport

    for row in dataset[1:]:
        tc1 = row[TC1_COL]
        tc2 = row[TC2_COL]
        tc3 = row[TC3_COL]
        lt = row[LT_COL]
        oi = row[OI_COL]
        pi = row[PI_COL]
        dt = row[DT_COL]

        if tc3 not in contentReport:
            contentReport[tc3] = {}

        if tc1 not in contentReport[tc3]:
            splittedTc2 = tc2.split(',')
            splittedLT = lt.split(',')
            splittedOI = oi.split(',')
            splittedPI = pi.split(',')
            splittedDT = dt.split(',')
            
            contentReport[tc3][tc1] = {
                'TC2': [NOT_NECESSARY_ICON if splittedTc2[0] == 'X' else 'x', NOT_NECESSARY_ICON if splittedTc2[1] == 'X' else 'x', NOT_NECESSARY_ICON if splittedTc2[2] == 'X' else 'x'],
                LT: [NOT_NECESSARY_ICON if splittedLT[0] == 'X' else 'x', NOT_NECESSARY_ICON if splittedLT[1] == 'X' else 'x', NOT_NECESSARY_ICON if splittedLT[2] == 'X' else 'x'],
                OI: [NOT_NECESSARY_ICON if splittedOI[0] == 'X' else 'x', NOT_NECESSARY_ICON if splittedOI[1] == 'X' else 'x', NOT_NECESSARY_ICON if splittedOI[2] == 'X' else 'x'],
                PI: [NOT_NECESSARY_ICON if splittedPI[0] == 'X' else 'x', NOT_NECESSARY_ICON if splittedPI[1] == 'X' else 'x', NOT_NECESSARY_ICON if splittedPI[2] == 'X' else 'x'],
                DT: [NOT_NECESSARY_ICON if splittedDT[0] == 'X' else 'x', NOT_NECESSARY_ICON if splittedDT[1] == 'X' else 'x', NOT_NECESSARY_ICON if splittedDT[2] == 'X' else 'x'],
            }  
 