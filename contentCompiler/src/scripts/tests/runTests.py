# Imports
import re
from pathlib import Path
import shutil
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#variables
from config import failedFiles

# Functions
from files.images import fillFailedImages
from report.generateTaxcoReport import generateTaxcoReport
from report.generateContentReport import generateContentReport
from files.parse import parseMarkdownFiles
from files.dataset import parseDatasetFile
from tests.evaluate import evaluateTests
from report.populate import populateTaxcoReport, populateContentReport

def validateTestReport(expected, actual):

    expectedTestReportPath =  Path(__file__).resolve().parents[1] / expected
    actualTestReportPath = Path(__file__).resolve().parents[1] / actual
    with open(expectedTestReportPath, 'r') as f1, open(actualTestReportPath, 'r') as f2:
        expectedTestReportContent = f1.read()
        actualTestReportContent = f2.read()

    if expectedTestReportContent == actualTestReportContent:
        return True
    else:
        return False
    
def validateDraft():
    expectedAmountOfDraftFiles = len(failedFiles)
    actualAmountOfDraftFiles = 0
    for file in failedFiles:
        fullPath = "src/scripts/tests/test_cases_build/" + file['path']
        try:
            with open(fullPath, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip().startswith('draft:'):
                        draft_value = line.strip().split(':', 1)[1].strip().lower()
                        if draft_value == 'true':
                            actualAmountOfDraftFiles += 1
        except FileNotFoundError:
            print(f"Error: The file at '{fullPath}' does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")
    return expectedAmountOfDraftFiles == actualAmountOfDraftFiles

"""
Runs the tests for the pipeline
"""
def test():
    global SRC_DIR, DEST_DIR, DATASET

    SRC_DIR = Path(__file__).resolve().parents[0] / 'test_cases'
    DEST_DIR = Path(__file__).resolve().parents[0] / 'test_cases_build'
    DATASET = Path(__file__).resolve().parents[0] / 'test_dataset.xlsx'
    TAXCO_REPORT_PATH = Path(__file__).resolve().parents[0] / 'reports/actual_taxco_test_report.md'
    CONTENT_REPORT_PATH = Path(__file__).resolve().parents[0] / 'reports/actual_content_test_report.md'
    EXPECTED_TAXCO_TEST_REPORT_PATH = 'tests/reports/expected_taxco_test_report.md'
    ACTUAL_TAXCO_TEST_REPORT_PATH = 'tests/reports/actual_taxco_test_report.md'
    EXPECTED_CONTENT_TEST_REPORT_PATH = 'tests/reports/expected_content_test_report.md'
    ACTUAL_CONTENT_TEST_REPORT_PATH = 'tests/reports/actual_content_test_report.md'

    if not os.path.exists(DATASET):
        print(f"Dataset file {DATASET} not found.")
        exit(404) 

    if not os.path.exists(SRC_DIR):
        print(f"Source directory {SRC_DIR} not found.")
        exit(404)
    

    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
        os.mkdir(DEST_DIR)

    parseDatasetFile(DATASET)
    populateTaxcoReport()
    populateContentReport()

    parseMarkdownFiles(SRC_DIR, DEST_DIR, False) 
    
    fillFailedImages(SRC_DIR, DEST_DIR) 

    generateTaxcoReport(TAXCO_REPORT_PATH)
    generateContentReport(CONTENT_REPORT_PATH) 

    if validateTestReport(EXPECTED_TAXCO_TEST_REPORT_PATH, ACTUAL_TAXCO_TEST_REPORT_PATH): 
        print("Taxco test report validation successful")
        if validateTestReport(EXPECTED_CONTENT_TEST_REPORT_PATH, ACTUAL_CONTENT_TEST_REPORT_PATH):
            print("Content Test report validation successful")
            if evaluateTests():
                print("Test evaluation successful")
                if(validateDraft()):
                    print("Draft test successful")
                    sys.exit(0)
                else:
                    print("Draft test failed")
                    sys.exit(14)
            else : 
                print("Test evaluation failed")
                sys.exit(13)  
        else:
            print("Content Test report validation failed")
            sys.exit(12)
    else : 
        print("Taxco Test report validation failed")
        sys.exit(11)

if __name__ == "__main__":
    test()
    
