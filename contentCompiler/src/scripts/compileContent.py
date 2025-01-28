from doctest import SKIP
import os
import time
import shutil
from pathlib import Path

from config import DEST_DIR, SRC_DIR, TAXCO_REPORT_PATH, CONTENT_REPORT_PATH, DATASET

from files.parse import parseDatasetFile, parseMarkdownFiles
from files.images import fillFailedImages
from report.populate import populateReport1, populateReport2
from report.generateTaxcoReport import generateTaxcoReport
from report.generateContentReport import generateContentReport
import argparse

"""
Main entry point of the script.
"""
def main():    
    parser = argparse.ArgumentParser(description="Compile content script.")
    parser.add_argument('--skip-link-check', required=False, action='store_true', help='Skip link check in markdown files.')
    args = parser.parse_args()

    skipDynamicLinkCheck = args.skip_link_check

    if not os.path.exists(DATASET):
        print(f"Dataset file {DATASET} not found.")
        exit(404) 

    parseDatasetFile(DATASET)

    populateReport1() 
    populateReport2() 

    if not os.path.exists(SRC_DIR):
        print(f"Source directory {SRC_DIR} not found.")
        exit(404)
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
        os.mkdir(DEST_DIR)

    parseMarkdownFiles(SRC_DIR, DEST_DIR, skipDynamicLinkCheck) 
    
    fillFailedImages(SRC_DIR, DEST_DIR) 
    
    generateTaxcoReport(TAXCO_REPORT_PATH)
    generateContentReport(CONTENT_REPORT_PATH)

if __name__ == "__main__":
    startTime = time.time()

    main()

    endTime = time.time()
    elapsedTime = endTime - startTime
    print(f"Execution time: {elapsedTime:.2f} seconds")
