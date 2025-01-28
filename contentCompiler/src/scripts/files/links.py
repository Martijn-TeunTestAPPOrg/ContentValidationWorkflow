# Imports
import re, os
from pathlib import Path

# Variables
from config import VALID_DYNAMIC_LINK_PREFIXES, ERROR_INVALID_DYNAMIC_LINK, VERBOSE

"""
Update dynamic links in the content of a markdown file.

Args:
    filePath (str): Path to the markdown file.
    content (str): Content of the markdown file.
"""
def updateDynamicLinks(filePath, content, skipValidateDynamicLinks):
    # Find all dynamic links in the content
    dynamicLinks = re.findall(r'\[\[[^"\[][^]]*?\]\]', content)

    errors = []
    
    for link in dynamicLinks:
        # Skip links that start with any of the valid prefixes
        cleanedLink = link.strip('[[]]')
        
        if any(cleanedLink.startswith(prefix) for prefix in VALID_DYNAMIC_LINK_PREFIXES):
            return content, errors
        
        # Strip 'content/' prefix if present
        newLink = link.replace('content/', '')
        
        # Replace the old link with the new link in the content
        content = content.replace(link, newLink)
        
        # Skip dynamic link check if flag is set
        # This is used in the PR validation check when only updated the content is being checked
        if(skipValidateDynamicLinks):
            continue

        # Check if the dynamic link is valid
        if not validateDynamicLink(filePath, newLink):
            if VERBOSE: print(ERROR_INVALID_DYNAMIC_LINK + newLink)
            errors.append(ERROR_INVALID_DYNAMIC_LINK + ' `' + newLink + '` ')

    return content, errors

"""
Checks if the dynamic link is valid and the file exists.

Args:
    source_filePath (str): Path to the source file.
    link (str): Dynamic link to validate.
"""
def validateDynamicLink(sourceFilePath, link):
    # Define the root content directory (assuming it is one level up from the current script)
    contentPath = sourceFilePath
    while Path(contentPath).name != 'content' and Path(contentPath).name != 'test_cases':
        contentPath = contentPath.parent
    
    # Verify that content_path exists
    if not contentPath.exists():
        print(f"Error: Content path '{contentPath}' does not exist.")
        return False

    # Clean up the link by removing the surrounding [[ and ]]
    cleanedLink = link.strip('[[]]')

    # If the link contains a section (anchor), split the link at '#'
    if '#' in cleanedLink:
        cleanedLink = cleanedLink.split('#')[0]  # Use only the part before '#'

    # Parse the base name from the cleaned link
    linkParts = cleanedLink.split('|')
    fileName = linkParts[0].strip().split('/')[-1]

    # Search for the file in all subdirectories within 'content' using os.walk
    foundFile = None
    for root, dirs, files in os.walk(contentPath):
        for file in files:
            if file.startswith(fileName):  # Check if the file name matches
                foundFile = os.path.join(root, file)
                return True

    # If no valid file is found, report error with details
    if not foundFile:
        if VERBOSE: print(f"Error: source file: {sourceFilePath}, target file '{fileName}' not found in content.")

    return False
