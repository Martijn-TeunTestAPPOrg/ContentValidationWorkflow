from config import TC1_COL, TC2_COL, TC3_COL, PROCES_COL, PROCESSTAP_COL, LT_COL, OI_COL, PI_COL, DT_COL

def checkRowEmpty(row):
    row_indices = [TC1_COL, TC2_COL, TC3_COL, PROCES_COL, PROCESSTAP_COL, LT_COL, OI_COL, PI_COL, DT_COL]
    for index in row_indices:
        if index >= len(row) or row[index] == "" or row[index] is None:
            return True  
    return False