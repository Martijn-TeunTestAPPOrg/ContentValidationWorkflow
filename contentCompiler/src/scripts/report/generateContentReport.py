# Variables
from config import VERBOSE, WIPFiles, failedFiles, failedImages, parsedFiles, SUCCESS, WARNING
# Functions
from report.table import formatFileReportTable, formatImageReportTable

# Generate the report based on the taxonomie report, success, and failed reports.
def generateContentReport(reportPath):
    if VERBOSE: print("Generating report...")
    with open(reportPath, "w", encoding="utf-8") as f:
        f.write('---\ndraft: true\n---\n')
        
        f.write("## Work-in-progress bestanden\n")
        f.write('Doel: De onderstaande bestanden hebben nog todo items in de markdown staan.\n')
        f.write('Deze todo items moeten nog worden afgehandeld.\n')
        f.write('\n')
        f.write(formatFileReportTable(sorted(WIPFiles, key=lambda x: x['file'])))

        f.write('\n\n')

        f.write("## Gefaalde bestanden\n")
        f.write("*Doel: De onderstaande bestanden zijn niet succesvol verwerkt.*\n\n")
        f.write(SUCCESS + ' Dit bestand bevat nog geen taxonomie code\n')
        f.write(WARNING + ' Dit bestand bevat fouten. Zie de *Errors* kolom\n')
        f.write('\n')
        f.write(formatFileReportTable(sorted(failedFiles, key=lambda x: x['file'])))

        f.write('\n\n')

        f.write("## Gefaalde images\n")
        f.write("*Doel: De onderstaande images missen een 4C/ID component.*\n\n")
        f.write('Als een image de error heeft over het niet gebruikt worden, betekent dit dat de image niet in build staat, maar nog wel in content.\n\n')
        f.write(formatImageReportTable(sorted(failedImages, key=lambda x: x['image'])))

        f.write('\n\n')

        f.write("## Geslaagde bestanden\n")
        f.write("De onderstaande bestanden zijn succesvol verwerkt.\n")
        f.write('\n')
        f.write(formatFileReportTable(sorted(parsedFiles, key=lambda x: x['file'])))
