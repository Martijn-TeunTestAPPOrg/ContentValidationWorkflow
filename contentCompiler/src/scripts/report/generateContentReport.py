# Variables
from config import VERBOSE, WIPFiles, failedFiles, failedImages, parsedFiles, WARNING_ICON, FAIL_CROSS_ICON, NOT_NEEDED_ICON, TODO_ITEMS_ICON
# Functions
from report.table import formatFileReportTable, formatImageReportTable

# Generate the report based on the taxonomie report, success, and failed reports.
def generateContentReport(reportPath):
    if VERBOSE: print("Generating report...")
    with open(reportPath, "w", encoding="utf-8") as f:
        f.write('---\ndraft: true\n---\n')
        
        f.write("## Work-in-progress bestanden\n")
        f.write('*Doel: De onderstaande bestanden hebben nog todo items in de markdown staan.*\n')
        f.write('Deze todo items moeten nog worden afgehandeld.\n')
        f.write('\n')
        f.write(formatFileReportTable(sorted(WIPFiles, key=lambda x: x['file'])))

        f.write('\n\n')

        f.write("## Gefaalde bestanden\n")
        f.write("*Doel: De onderstaande bestanden zijn niet succesvol verwerkt.*\n\n")
        f.write(FAIL_CROSS_ICON + ' Dit bestand bevat nog geen taxonomie codes.\n')
        f.write(WARNING_ICON + ' Dit bestand bevat fouten. Zie de *Errors* kolom.\n')
        f.write(NOT_NEEDED_ICON + 'Dit bestand bevat taxonomie codes die niet nodig zijn.\n')
        f.write('\n')
        f.write(formatFileReportTable(sorted(failedFiles, key=lambda x: x['file'])))

        f.write('\n\n')

        f.write("## Gefaalde images\n")
        f.write("*Doel: De onderstaande images worden niet gebruikt in een bestand.*\n\n")
        f.write(formatImageReportTable(sorted(failedImages, key=lambda x: x['image'])))

        f.write('\n\n')

        f.write("## Geslaagde bestanden\n")
        f.write("*Doel: De onderstaande bestanden zijn succesvol verwerkt.*\n")
        f.write('\n')
        f.write(formatFileReportTable(sorted(parsedFiles, key=lambda x: x['file'])))
