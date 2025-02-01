# Imports
import re

# Variables
from config import dataset, contentReport

# Constants
from config import PROCES_COL, PROCESSTAP_COL, TC3_COL, TC2_COL, TAXONOMIE_PATTERN, TODO_PATTERN, VERBOSE, ERROR_INVALID_TAXCO
from config import ERROR_MISSING_TAXCO, NOT_NECESSARY, ERROR_TAXCO_NOT_FOUND

# Functions
from report.generateTaxcoReport import updateProcessReportData, updateSubjectReportData

"""
Generate tags based on the taxonomie values
Args:
    taxonomies (list): List of taxonomie values.
    filePath (str): Path to the file.
"""
def generateTags(taxonomies, existingTags):
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
                        if row[5] in contentReport and row[5] == tc3:
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
                            splittedRow =  row[TC2_COL].split(',')
                            if splittedRow[int(tc2)-1] == "X": 
                               tags.append(NOT_NECESSARY)


                            # Update the process report data with the new values
                            # This is needed so the report has the correct data
                            # Before the script runs it pre-fills the report with all the taxonomies
                            # This is done so the report has all the taxonomies even if they are not used
                            # After this the report is updated with the correct data
                            updateProcessReportData(tc1, tc2)
                            updateSubjectReportData(tc4, tc1, tc2, tc3)

            # If no tags were found, add an error
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
    return re.findall(TODO_PATTERN, content)
