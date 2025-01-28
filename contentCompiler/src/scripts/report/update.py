# Variables
from config import report1, report2

# Constants
from config import NOT_NECESSARY, LT, DT, OI, PI

"""
Update the Report 1 data with the new values.
Args:
    tc_1 (str): TC1 code.
    tc_2 (str): TC2 code.
"""
def updateProcessReportData(tc1, tc2):
    report1[tc1]['TC2'] = ['v' if tc2 == '1' and report1[tc1]['TC2'][0] != NOT_NECESSARY else report1[tc1]['TC2'][0], 'v' if tc2 == '2' and report1[tc1]['TC2'][1] != NOT_NECESSARY else report1[tc1]['TC2'][1], 'v' if tc2 == '3' and report1[tc1]['TC2'][2] != NOT_NECESSARY else report1[tc1]['TC2'][2]]

"""
Update the Report 2 data with the new values.
Args:
    file_type (str): File type.
    tc_1 (str): TC1 code.
    tc_2 (str): TC2 code.
    tc_3 (str): TC3 code.
"""
def updateSubjectReportData(fileType, tc1, tc2, tc3):
    # Update the record with the new values
    def updateReport2Row(tc3, tc1, tc2, fileType, searchType):
        report2[tc3][tc1][searchType] = [
            'v' if fileType == searchType and tc2 == '1' and report2[tc3][tc1][searchType][0] != NOT_NECESSARY else report2[tc3][tc1][searchType][0], 
            'v' if fileType == searchType and tc2 == '2' and report2[tc3][tc1][searchType][1] != NOT_NECESSARY else report2[tc3][tc1][searchType][1], 
            'v' if fileType == searchType and tc2 == '3' and report2[tc3][tc1][searchType][2] != NOT_NECESSARY else report2[tc3][tc1][searchType][2]
        ]

    report2[tc3][tc1]['TC2'] = ['v' if tc2 == '1' and report2[tc3][tc1]['TC2'][0] != NOT_NECESSARY else report2[tc3][tc1]['TC2'][0], 'v' if tc2 == '2' and report2[tc3][tc1]['TC2'][1] != NOT_NECESSARY else report2[tc3][tc1]['TC2'][1], 'v' if tc2 == '3' and report2[tc3][tc1]['TC2'][2] != NOT_NECESSARY else report2[tc3][tc1]['TC2'][2]]
    updateReport2Row(tc3, tc1, tc2, fileType, LT)
    updateReport2Row(tc3, tc1, tc2, fileType, OI)
    updateReport2Row(tc3, tc1, tc2, fileType, PI)
    updateReport2Row(tc3, tc1, tc2, fileType, DT)

