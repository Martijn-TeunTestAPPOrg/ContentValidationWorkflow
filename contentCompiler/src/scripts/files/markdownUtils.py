# Imports
import re
from pathlib import Path

# Variables
from config import failedFiles, dataset, report2, WIPFiles

# Constants
from config import PROCES_COL, PROCESSTAP_COL, TC3_COL, TC2_COL, TAXONOMIE_PATTERN, TODO_PATTERN, FOLDERS_FOR_4CID, VERBOSE, ERROR_INVALID_TAXCO
from config import ERROR_MISSING_TAXCO, NOT_NECESSARY, ERROR_TAXCO_NOT_NEEDED, ERROR_TAXCO_NOT_FOUND, ERROR_TAXCO_IN_WRONG_4CID_COMPONENT

# Functions
from report.table import generateMarkdownTable
from report.update import updateProcessReportData, updateSubjectReportData


# Create a new row in the file report based on the status, file path, taxonomie, and tags.
def createFileReportRow(status, filePath, srcDir, taxonomie, tags, errors):
    return {
        "status": status,
        "file": filePath.stem,
        "path": str(filePath.relative_to(srcDir)),
        "taxonomie": '<br>'.join(taxonomie) if taxonomie else "N/A",
        "tags": '<br>'.join(tags) if tags else "N/A",
        "errors": '<br>'.join(errors) if errors else "N/A"
    }

# Format the success or failed report table based on a list.
def formatFileReportTable(fileReport):
    headers = ["Status", "File", "Path", "Taxonomie", "Tags", "Errors"]

    if fileReport == failedFiles or fileReport == WIPFiles : headers.append("Errors")
    rows = [[
        file['status'], 
        file['file'], 
        file['path'], 
        file['taxonomie'], 
        file['tags'],
        file['errors']
     ] for file in fileReport]

    table = generateMarkdownTable(headers, rows)
    return table

"""
Generate tags based on the taxonomie values
Args:
    taxonomies (list): List of taxonomie values.
    filePath (str): Path to the file.
"""
def generateTags(taxonomies, filePath, existingTags):
    tags = []
    errors = []
    combinedTags = []
    taxonomieTags = []

    if taxonomies is not None and taxonomies != ['None'] and taxonomies != [''] and taxonomies != []:
        for taxonomie in taxonomies:
            if VERBOSE : print(f"Generating tags for taxonomie: {taxonomie}")
            # Check if the taxonomie is in the correct format
            if not re.match(TAXONOMIE_PATTERN, taxonomie):
                errors.append(ERROR_INVALID_TAXCO + ' `' + taxonomie + '` ')
                print(ERROR_INVALID_TAXCO + taxonomie)
                continue

            # split the taxonomie in it's different parts
            tc1, tc2, tc3, tc4 = splitTaxonomie(taxonomie)
            # if the parts are all valid
            if tc1 and tc2 and tc3 and tc4:
                # Loop trough every row in the dataset
                for row in dataset[1:]:
                    # Check if the first part of the taxonomie is equal to the second column (TC1) in the dataset
                    if row[1] == tc1:
                        # Check if the second part of the taxonomie is equal to the third column (TC2) in the dataset
                        if row[5] in report2 and row[5] == tc3:
                            # Adds the taxonomie
                            newTag = "HBO-i/niveau-" + tc2
                            if newTag not in tags:
                                tags.append(newTag)
    
                            # Adds the proces
                            if row[PROCES_COL] not in tags:
                                tags.append(row[PROCES_COL])

                            # Adds the processtap
                            if row[PROCESSTAP_COL] not in tags:
                                tags.append(row[PROCESSTAP_COL])

                            # Check if the third part of the taxonomie is in the lookup table
                            if row[TC3_COL] not in tags:
                                tags.append(row[TC3_COL])

                            # Check if the taxonomie is not needed
                            splittedRow2 =  row[TC2_COL].split(',')
                            if splittedRow2[int(tc2)-1] == "X": 
                               tags.append(NOT_NECESSARY)
                            
                            # Checks if the fourth path has the matching 4C/ID component (looking at the folder and taxonomie code)
                            containsCorrectTaxcos = checkIfFileContainsWrong4cid(taxonomies, filePath)
                            if containsCorrectTaxcos:
                                updateProcessReportData(tc1, tc2)
                                updateSubjectReportData(getFileType(filePath), tc1, tc2, tc3)   
                            else:   
                                errors.append(ERROR_TAXCO_IN_WRONG_4CID_COMPONENT + ' `' + taxonomie + '` ')                        

                            taxonomieTags = sorted(list(set(taxonomies)))

        # If no tags were found, add an error
            if NOT_NECESSARY in tags: 
                tags.remove(NOT_NECESSARY)
                errors.append(ERROR_TAXCO_NOT_NEEDED + ' `' + taxonomie + '` ')   
            if tags == [] and not errors:
                errors.append(ERROR_TAXCO_NOT_FOUND + ' `' + taxonomie + '` ')   
                if VERBOSE: print(ERROR_TAXCO_NOT_FOUND + taxonomie)
    else:
        errors.append(ERROR_MISSING_TAXCO)
        if VERBOSE: print(ERROR_MISSING_TAXCO)  

    # Combine the existing tags with the new tags
    if existingTags: combinedTags += existingTags 
    if tags : combinedTags += tags 
    if taxonomieTags : combinedTags += taxonomieTags
    
    # Sort combined_tags so that "HBO-i/niveau-" tags are moved to the start
    combinedTags = sorted(combinedTags, key=lambda tag: (not tag.startswith("HBO-i/niveau-"), tag))

    return list(dict.fromkeys(combinedTags)), errors

# Returns the folder name after the 'content' directory in the path.
def getFileType(filePath):
    # Convert to Path object if not already
    filePath = Path(filePath)
    # Find the 'content' directory in the path
    folderPath = filePath

    while folderPath.parent.name != 'content' and folderPath.parent.name != 'test_cases':
        folderPath = folderPath.parent
    if not folderPath.name.endswith('.md') :
        cleanedFolderName = re.sub(r'^\d+\.\s*', '', folderPath.name)
        return cleanedFolderName
    return None

def splitTaxonomie(taxonomie):
    return taxonomie.split('.')

# Helper function to extract specific values from the content of a markdown file.
def extractHeaderValues(content, fieldName):
    lines = content.splitlines()
    values = []

    for i, line in enumerate(lines):
        if line.startswith(f'{fieldName}:'):
            # Handle case where the field has a single value
            if ':' in line and len(line.split(':', 1)[1].strip()) > 0:
                values.append(line.split(':', 1)[1].strip())
            else:
                # Handle case where the field is a list
                for j in range(i + 1, len(lines)):
                    subLine = lines[j].strip()
                    if subLine.startswith('- '):
                        values.append(subLine.lstrip('- ').strip())
                    else:
                        break
            break

    return values if values else None

# Helper function to find all the To-Do items in the content of a markdown file.	
def findWIPItems(content):
    # Find all the todo items in the content
    todoItems = re.findall(TODO_PATTERN, content)
    return todoItems

# Checks if a file contains at least one wrong taxonomie code (based on incorrect placement of 4C/ID)
def checkIfFileContainsWrong4cid(taxonomies, filePath):
    containsOnlyCorrectTaxonomie = True
    for taxonomie in taxonomies:
        if not re.match(TAXONOMIE_PATTERN, taxonomie):
            continue
        tc1, tc2, tc3, tc4 = splitTaxonomie(taxonomie)  
        if tc1 and tc2 and tc3:
            if tc4 in FOLDERS_FOR_4CID:
                expectedFolder = FOLDERS_FOR_4CID[tc4]
                if expectedFolder not in str(filePath):
                    containsOnlyCorrectTaxonomie = False
    return containsOnlyCorrectTaxonomie            
