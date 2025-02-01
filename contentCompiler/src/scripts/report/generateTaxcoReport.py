# Variables
from config import VERBOSE, taxcoReport, contentReport

# Constants
from config import LT, DT, OI, PI, FAIL_CIRCLE, SUCCESS, NOT_NECESSARY

# Functions
from report.table import generateMarkdownTable

# Update the taxco list with the new values
def updateProcessReportData(tc1, tc2):
    taxcoReport[tc1]['TC2'] = ['v' if tc2 == '1' and taxcoReport[tc1]['TC2'][0] != NOT_NECESSARY else taxcoReport[tc1]['TC2'][0], 'v' if tc2 == '2' and taxcoReport[tc1]['TC2'][1] != NOT_NECESSARY else taxcoReport[tc1]['TC2'][1], 'v' if tc2 == '3' and taxcoReport[tc1]['TC2'][2] != NOT_NECESSARY else taxcoReport[tc1]['TC2'][2]]

# Update the content list data with the new values.
def updateSubjectReportData(fileType, tc1, tc2, tc3):
    # Helper function to update the record with the new values
    def updateContentReportRow(tc3, tc1, tc2, fileType, searchType):
        contentReport[tc3][tc1][searchType] = [
            'v' if fileType == searchType and tc2 == '1' and contentReport[tc3][tc1][searchType][0] != NOT_NECESSARY else contentReport[tc3][tc1][searchType][0], 
            'v' if fileType == searchType and tc2 == '2' and contentReport[tc3][tc1][searchType][1] != NOT_NECESSARY else contentReport[tc3][tc1][searchType][1], 
            'v' if fileType == searchType and tc2 == '3' and contentReport[tc3][tc1][searchType][2] != NOT_NECESSARY else contentReport[tc3][tc1][searchType][2]
        ]

    contentReport[tc3][tc1]['TC2'] = ['v' if tc2 == '1' and contentReport[tc3][tc1]['TC2'][0] != NOT_NECESSARY else contentReport[tc3][tc1]['TC2'][0], 'v' if tc2 == '2' and contentReport[tc3][tc1]['TC2'][1] != NOT_NECESSARY else contentReport[tc3][tc1]['TC2'][1], 'v' if tc2 == '3' and contentReport[tc3][tc1]['TC2'][2] != NOT_NECESSARY else contentReport[tc3][tc1]['TC2'][2]]
    updateContentReportRow(tc3, tc1, tc2, fileType, LT)
    updateContentReportRow(tc3, tc1, tc2, fileType, OI)
    updateContentReportRow(tc3, tc1, tc2, fileType, PI)
    updateContentReportRow(tc3, tc1, tc2, fileType, DT)

# Generate the report based on the taxonomie report, success, and failed reports.
def generateTaxcoReport(reportPath):
    if VERBOSE: print("Generating report...")
    with open(reportPath, "w", encoding="utf-8") as f:
        f.write('---\ndraft: true\n---\n')
        
        f.write('## Rapport 1 - Processtappen\n')
        f.write('*Doel: achterhalen welke processtappen nog helemaal niet zijn geïmplementeerd*\n\n')
        f.write('- ✅ Er bestaat een bestand met deze taxonomiecode op dit niveau \n')
        f.write('- ⛔️ Er is geen enkel bestand met deze taxonomiecode op dit niveau \n')
        f.write('- 🏳️ De taxonomiecode wordt niet aangeboden op dit niveau (X in de Dataset) \n')
        f.write('\n')
        f.write(generateProcessTable())

        f.write('\n\n')

        f.write('## Rapport 2 - Onderwerpen Catalogus\n')
        f.write('*Doel: Lijst met onderwerpen + gekoppelde taxonomie code voor inzicht in aangeboden onderwerpen.*\n')
        f.write('Bij kolom *TC2*, *Leertaken*, *Ondersteunende informatie*, *Procedurele informatie* en *Deeltaken* zijn drie tekens aanwezig om de drie HBO-i niveaus weer te geven\n\n')
        f.write('- ✅ Het onderwerp met taxonomie code wordt aangeboden op het aangegeven niveau \n')
        f.write('- ⛔️ Het onderwerp met taxonomie code wordt **niet** aangeboden op het aangegeven niveau \n')
        f.write('- 🏳️ Het onderwerp hoeft met deze taxonomie code niet aangeboden te worden op het aangegeven niveau \n')
        f.write('\n')
        f.write(generateSubjectTable())

# Format the report table for the process table
def generateProcessTable():
    if VERBOSE: print("Generating process table...")

    headers = ["TC1", "Proces", "Processtap", "Niveau 1", "Niveau 2", "Niveau 3"]
    rows = []
    for tc, details in taxcoReport.items():
        proces = details.get('Proces', '')
        processtap = details.get('Processtap', '')
        tc2_levels = details.get('TC2', {})
        niveau_1 = FAIL_CIRCLE if tc2_levels[0] == 'x' else SUCCESS if tc2_levels[0] == 'v' or tc2_levels[0] == 'g' else NOT_NECESSARY
        niveau_2 = FAIL_CIRCLE if tc2_levels[1] == 'x' else SUCCESS if tc2_levels[1] == 'v' or tc2_levels[1] == 'g' else NOT_NECESSARY        
        niveau_3 = FAIL_CIRCLE if tc2_levels[2] == 'x' else SUCCESS if tc2_levels[2] == 'v' or tc2_levels[2] == 'g' else NOT_NECESSARY
        rows.append([tc, proces, processtap, niveau_1, niveau_2, niveau_3])

    table = generateMarkdownTable(headers, rows)
    if VERBOSE: print("Taxco report proces table generated.")
    return table

# Format the report for the subject table
def generateSubjectTable():
    if VERBOSE: print("Generating subject table...")

    headers = ["TC3", "TC1", "TC2", LT, OI, PI, DT]
    rows = []

    # Helper function to get the status of the value
    def getStatus(value):
        if value == 'v' or value == 'g':
            return SUCCESS
        elif value != NOT_NECESSARY:
            return FAIL_CIRCLE
        else:
            return NOT_NECESSARY

    # Loop through the content report and generate the table
    for tc3, row in contentReport.items():
        for tc1, other in row.items():
            tc2_levels = other.get('TC2', [''] * 3)
            tc2 = ' '.join([getStatus(level) for level in tc2_levels])

            leertaak_levels = other.get(LT, [''] * 3)
            leertaak = ' '.join([getStatus(level) for level in leertaak_levels])

            ondersteunende_informatie_levels = other.get(OI, [''] * 3)
            ondersteunende_informatie = ' '.join([getStatus(level) for level in ondersteunende_informatie_levels])
            
            procedurele_informatie_levels = other.get(PI, [''] * 3)
            procedurele_informatie = ' '.join([getStatus(level) for level in procedurele_informatie_levels])
            
            deeltaak_levels = other.get(DT, [''] * 3)
            deeltaak = ' '.join([getStatus(level) for level in deeltaak_levels])

            rows.append([tc3, tc1, tc2, leertaak, ondersteunende_informatie, procedurele_informatie, deeltaak])

    table = generateMarkdownTable(headers, rows)
    if VERBOSE: print("Taxco report content table generated.")
    
    return table
