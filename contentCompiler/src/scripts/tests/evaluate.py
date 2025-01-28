# Imports
import time
import os
import shutil
import sys
from pathlib import Path
import argparse

# Variables
from config import VERBOSE, failedImages

# Functions
from files.parse import parseMarkdownFiles

markdownCountCheck = False  


"""
returns the amount of markdown files in a folder
"""
def checkMarkdownFilesCount(folderPath):
    return len(list(folderPath.glob("*.md")))

"""
Evaluate the tests by using check_markdown_files_count and removing the build folder afterwards
"""
def evaluateTests():
    srcDir = Path(__file__).resolve().parents[2] / 'content'
    destDir = Path(__file__).resolve().parents[2] / 'temp_build'
    startTime = time.time()
    if os.path.exists(destDir):
        shutil.rmtree(destDir)
        os.mkdir(destDir)
        
    parseMarkdownFiles(srcDir, destDir, True)

    markdownCountCheck = checkMarkdownFilesCount(srcDir) == checkMarkdownFilesCount(destDir)

    shutil.rmtree(destDir) 
    endTime = time.time()
    if VERBOSE: 
        print(f"Execution time: {endTime - startTime:.2f} seconds")
        print("-----------")

    return markdownCountCheck   

