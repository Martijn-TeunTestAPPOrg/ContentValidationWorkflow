# Imports
from pathlib import Path

# Variables
from config import dataset, report1, report2

# Constants
from config import TC1_COL, TC2_COL, TC3_COL, PROCES_COL, PROCESSTAP_COL, NOT_NECESSARY, LT_COL, DT_COL, OI_COL, PI_COL, LT, DT, OI, PI


## Structure of report_1
#
# report_1 = {
#     'rv-8' : {
#         'Proces' : "Requirementanalyseproces"
#         'Processtap' : "Verzamelen requirements",
#         'TC2' : ['x', '~', 'x']
#     },
#     'pu-13' : {
#         'Proces' : "Pakketselectieproces"
#         'Processtap' : "Uitvoeren analyse",
#         'TC2' : ['x', 'x', 'x']
#     }
# }

## Structure of report_2
#
# report_2 = {
#     'functioneel-ontwerp' : {
#         'oo-15' : {
#             'TC2' : ['x', 'x', 'x'],
#             LT : ['x', 'x', 'x'],
#             OI : ['x', 'x', 'x'], 
#             PI : ['x', 'x', 'x'], 
#             DT : ['x', 'x', 'x']
#         },
#         'rs-10' : {
#             'TC2' : ['x', 'x', 'x'],
#             LT : ['x', 'x', 'x'],
#             OI : ['x', 'x', 'x'], 
#             PI : ['x', 'x', 'x'], 
#             DT : ['x', 'x', 'x']
#         },
#         'ra-9' : {
#             'TC2' : ['x', 'x', 'x'],
#             LT : ['x', 'x', 'x'],
#             OI : ['x', 'x', 'x'], 
#             PI : ['x', 'x', 'x'], 
#             DT : ['x', 'x', 'x']
#         }
#     },
#     "Technisch ontwerp": {
#         'oo-15' : {
#           'TC2' : ['x', 'x', 'x'],
#           LT : ['x', 'x', 'x'],
#           OI : ['x', 'x', 'x'], 
#           PI : ['x', 'x', 'x'], 
#           DT : ['x', 'x', 'x']
#       }
#    }
# }


"""
Fills the report 1 data with the data from the dataset
Every TC1 code is the unique identifier
"""
def populateReport1():
    global report1

    for row in dataset[1:]:
        tc1 = row[TC1_COL]
        tc2 = row[TC2_COL]
        proces = row[PROCES_COL]
        processtap = row[PROCESSTAP_COL]

        if tc1 in report1:
            if report1[tc1]['TC2'][1] == '🏳️' or report1[tc1]['TC2'][2] == '🏳️':
                splittedTc2 = tc2.split(',')
                for index in range(1, 3):
                    if report1[tc1]['TC2'][index] == '🏳️' and splittedTc2[index] != '🏳️':
                        report1[tc1]['TC2'][index] = splittedTc2[index]

        if tc1 not in report1: 
            splittedTc2 = tc2.split(',')

            report1[tc1] = {
                "Proces" : proces,
                "Processtap" : processtap,
                'TC2': [NOT_NECESSARY if splittedTc2[0] == 'X' else 'x', NOT_NECESSARY if splittedTc2[1] == 'X' else 'x', NOT_NECESSARY if splittedTc2[2] == 'X' else 'x']        
            }

"""
Fills the Report 2 data with the data from the dataset.
Every unique TC3 and TC1 combination will be added to the Report 2 data.
"""
def populateReport2():
    global report2

    for row in dataset[1:]:
        tc1 = row[TC1_COL]
        tc2 = row[TC2_COL]
        tc3 = row[TC3_COL]
        lt = row[LT_COL]
        oi = row[OI_COL]
        pi = row[PI_COL]
        dt = row[DT_COL]

        if tc3 not in report2:
            report2[tc3] = {}

        if tc1 not in report2[tc3]:
            splittedTc2 = tc2.split(',')
            splittedLT = lt.split(',')
            splittedOI = oi.split(',')
            splittedPI = pi.split(',')
            splittedDT = dt.split(',')
            
            report2[tc3][tc1] = {
                'TC2': [NOT_NECESSARY if splittedTc2[0] == 'X' else 'x', NOT_NECESSARY if splittedTc2[1] == 'X' else 'x', NOT_NECESSARY if splittedTc2[2] == 'X' else 'x'],
                LT: [NOT_NECESSARY if splittedLT[0] == 'X' else 'x', NOT_NECESSARY if splittedLT[1] == 'X' else 'x', NOT_NECESSARY if splittedLT[2] == 'X' else 'x'],
                OI: [NOT_NECESSARY if splittedOI[0] == 'X' else 'x', NOT_NECESSARY if splittedOI[1] == 'X' else 'x', NOT_NECESSARY if splittedOI[2] == 'X' else 'x'],
                PI: [NOT_NECESSARY if splittedPI[0] == 'X' else 'x', NOT_NECESSARY if splittedPI[1] == 'X' else 'x', NOT_NECESSARY if splittedPI[2] == 'X' else 'x'],
                DT: [NOT_NECESSARY if splittedDT[0] == 'X' else 'x', NOT_NECESSARY if splittedDT[1] == 'X' else 'x', NOT_NECESSARY if splittedDT[2] == 'X' else 'x'],
            }  
 