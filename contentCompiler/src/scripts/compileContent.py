import os
import time
import shutil
import argparse
import logging

from config import DEST_DIR, SRC_DIR, TAXCO_REPORT_PATH, CONTENT_REPORT_PATH, DATASET

from files.dataset import parseDatasetFile
from files.parse import parseMarkdownFiles
from files.images import fillFailedImages
from report.populate import populateTaxcoReport, populateContentReport
from report.generateTaxcoReport import generateTaxcoReport
from report.generateContentReport import generateContentReport

class ContentCompiler:
    def __init__(self, skipLinkCheck: bool = False):
        self.skipLinkCheck = skipLinkCheck
        self.setupLogging()

    @staticmethod
    def setupLogging() -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def validatePaths(self) -> None:
        if not os.path.exists(DATASET):
            raise FileNotFoundError(f"Dataset file {DATASET} not found.")
        if not os.path.exists(SRC_DIR):
            raise FileNotFoundError(f"Source directory {SRC_DIR} not found.")

    def initializeDestDir(self) -> None:
        if os.path.exists(DEST_DIR):
            shutil.rmtree(DEST_DIR)
        os.mkdir(DEST_DIR)

    def compile(self) -> None:
        try:
            self.validatePaths()
            self.initializeDestDir()
            
            logging.info("Starting content compilation...")
            
            parseDatasetFile(DATASET)
            logging.info("Dataset parsed successfully")
            
            populateTaxcoReport()
            populateContentReport()
            logging.info("Reports populated")
            
            parseMarkdownFiles(SRC_DIR, DEST_DIR, self.skipLinkCheck)
            logging.info("Markdown files parsed")
            
            fillFailedImages(SRC_DIR, DEST_DIR)
            logging.info("Failed images processed")
            
            generateTaxcoReport(TAXCO_REPORT_PATH)
            generateContentReport(CONTENT_REPORT_PATH)
            logging.info("Reports generated successfully")
            
        except Exception as e:
            logging.error(f"Error during compilation: {str(e)}")
            raise

def main() -> None:
    parser = argparse.ArgumentParser(description="Compile content script.")
    parser.add_argument('--skip-link-check', required=False, action='store_true', help='Skip link check in markdown files.')
    args = parser.parse_args()

    startTime = time.time()
    
    try:
        compiler = ContentCompiler(skipLinkCheck=args.skip_link_check)
        compiler.compile()
    except Exception as e:
        logging.error(f"Compilation failed: {str(e)}")
        exit(1)
    finally:
        elapsedTime = time.time() - startTime
        logging.info(f"Execution time: {elapsedTime:.2f} seconds")

if __name__ == "__main__":
    main()
