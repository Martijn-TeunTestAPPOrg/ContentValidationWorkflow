# Imports
import re
from pathlib import Path
import shutil
import os
import sys
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Variables and functions
from config import failedFiles
from files.images import fillFailedImages
from report.generateTaxcoReport import generateTaxcoReport
from report.generateContentReport import generateContentReport
from files.parse import parseMarkdownFiles
from files.dataset import parseDatasetFile
from tests.evaluate import evaluateTests
from report.populate import populateTaxcoReport, populateContentReport

class TestRunner:
    def __init__(self):
        self.setupPaths()
        self.setupLogging()

    @staticmethod
    def setupLogging() -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setupPaths(self) -> None:
        self.SRC_DIR = Path(__file__).resolve().parents[0] / 'test_cases'
        self.DEST_DIR = Path(__file__).resolve().parents[0] / 'test_cases_build'
        self.DATASET = Path(__file__).resolve().parents[0] / 'test_dataset.xlsx'
        self.TAXCO_REPORT_PATH = Path(__file__).resolve().parents[0] / 'reports/actual_taxco_test_report.md'
        self.CONTENT_REPORT_PATH = Path(__file__).resolve().parents[0] / 'reports/actual_content_test_report.md'
        self.EXPECTED_TAXCO_TEST_REPORT_PATH = 'tests/reports/expected_taxco_test_report.md'
        self.ACTUAL_TAXCO_TEST_REPORT_PATH = 'tests/reports/actual_taxco_test_report.md'
        self.EXPECTED_CONTENT_TEST_REPORT_PATH = 'tests/reports/expected_content_test_report.md'
        self.ACTUAL_CONTENT_TEST_REPORT_PATH = 'tests/reports/actual_content_test_report.md'

    def validateTestReport(self, expected: str, actual: str) -> bool:
        expectedTestReportPath = Path(__file__).resolve().parents[1] / expected
        actualTestReportPath = Path(__file__).resolve().parents[1] / actual
        
        with open(expectedTestReportPath, 'r') as f1, open(actualTestReportPath, 'r') as f2:
            expectedTestReportContent = f1.read()
            actualTestReportContent = f2.read()

        return expectedTestReportContent == actualTestReportContent

    def validateDraft(self) -> bool:
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
                logging.error(f"Error: The file at '{fullPath}' does not exist.")
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                
        return expectedAmountOfDraftFiles == actualAmountOfDraftFiles

    def validatePaths(self) -> None:
        if not os.path.exists(self.DATASET):
            raise FileNotFoundError(f"Dataset file {self.DATASET} not found.")
        if not os.path.exists(self.SRC_DIR):
            raise FileNotFoundError(f"Source directory {self.SRC_DIR} not found.")

    def initializeDestDir(self) -> None:
        if os.path.exists(self.DEST_DIR):
            shutil.rmtree(self.DEST_DIR)
        os.mkdir(self.DEST_DIR)

    def run(self) -> None:
        try:
            self.validatePaths()
            self.initializeDestDir()
            
            logging.info("Starting test execution...")
            
            parseDatasetFile(self.DATASET)
            logging.info("Dataset parsed successfully")
            
            populateTaxcoReport()
            populateContentReport()
            logging.info("Reports populated")
            
            parseMarkdownFiles(self.SRC_DIR, self.DEST_DIR, False)
            logging.info("Markdown files parsed")
            
            fillFailedImages(self.SRC_DIR, self.DEST_DIR)
            logging.info("Failed images processed")
            
            generateTaxcoReport(self.TAXCO_REPORT_PATH)
            generateContentReport(self.CONTENT_REPORT_PATH)
            logging.info("Reports generated")

            if not self.validateTestReport(self.EXPECTED_TAXCO_TEST_REPORT_PATH, self.ACTUAL_TAXCO_TEST_REPORT_PATH):
                logging.error("Taxco Test report validation failed")
                sys.exit(11)

            if not self.validateTestReport(self.EXPECTED_CONTENT_TEST_REPORT_PATH, self.ACTUAL_CONTENT_TEST_REPORT_PATH):
                logging.error("Content Test report validation failed")
                sys.exit(12)

            if not evaluateTests():
                logging.error("Test evaluation failed")
                sys.exit(13)

            if not self.validateDraft():
                logging.error("Draft test failed")
                sys.exit(14)

            logging.info("Testing completed succesfully")
            sys.exit(0)
                
        except Exception as e:
            logging.error(f"Error during test execution: {str(e)}")
            raise

def main() -> None:
    try:
        runner = TestRunner()
        runner.run()
    except Exception as e:
        logging.error(f"Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()