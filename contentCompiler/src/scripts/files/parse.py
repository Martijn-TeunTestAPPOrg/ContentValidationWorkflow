# Imports
from pathlib import Path
# Variables
from config import failedFiles, parsedFiles, WIPFiles
# Constants
from config import ERROR_MISSING_TAXCO, FAIL_CROSS, WARNING, SUCCESS, TODO_ITEMS, IGNORE_FOLDERS, VERBOSE, ERROR_WIP_FOUND
# Functions
from files.images import copyImages
from files.links import updateDynamicLinks
from files.markdownUtils import extractHeaderValues, generateTags, findWIPItems
from report.table import createFileReportRow

# Update markdown files in the source directory
def parseMarkdownFiles(srcDir, destDir, skipValidateDynamicLinks):
    if VERBOSE: print("Parsing markdown files...")

    destDirPath = Path(destDir).resolve()
    destDirPath.mkdir(parents=True, exist_ok=True)

    srcDirPath = Path(srcDir).resolve()

    # Loop through all markdown files in the source directory
    for filePath in Path(srcDirPath).rglob('*.md'):
        relativePath = filePath.relative_to(srcDirPath)
        destAndRelativePath = destDirPath / relativePath
        errors = []
        isDraft = False

        # Skip curtain folders
        if any(folder in str(filePath) for folder in IGNORE_FOLDERS):
            continue

        if VERBOSE: 
            print("*" * 50) 
            print(f"Parsing file: {filePath}")

        with open(filePath, 'r', encoding='utf-8') as f:
            content = f.read()

        content, linkErrors = updateDynamicLinks(filePath, content, skipValidateDynamicLinks)
        imageErrors = copyImages(content, srcDirPath, destDirPath)
        existingTags = extractHeaderValues(content, 'tags')
        taxonomie = extractHeaderValues(content, 'taxonomie')
        newTags, tagErrors = generateTags(taxonomie, existingTags)
        difficulty = extractHeaderValues(content, 'difficulty')
        todoItems = findWIPItems(content)

        if(todoItems):
            errors.append(ERROR_WIP_FOUND + "<br>" + '<br>'.join([f"{item}" for item in todoItems]))

        # Combine all errors
        errors = linkErrors + imageErrors + tagErrors + errors

        # If there are any errors, the file is considered a draft
        if(errors):
            isDraft = True

        appendFileToSpecificList(errors, todoItems, filePath, srcDirPath, taxonomie, newTags)
        saveParsedFile(filePath, taxonomie, newTags, difficulty, isDraft, content, destAndRelativePath)

# Fill the different lists used for the report
def appendFileToSpecificList(errors, todoItems, filePath, srcDir, taxonomie, tags):
    if errors:
        # Based on the type of error, add the file to the correct list
        if(todoItems):
            WIPFiles.append(createFileReportRow(TODO_ITEMS, filePath, srcDir, taxonomie, tags, errors))
        elif(ERROR_MISSING_TAXCO in errors): 
            failedFiles.append(createFileReportRow(FAIL_CROSS, filePath, srcDir, taxonomie, tags, errors))
        else: 
            failedFiles.append(createFileReportRow(WARNING, filePath, srcDir, taxonomie, tags, errors))

        if VERBOSE: print(f"Failed to parse file: {filePath}")
    else:
        parsedFiles.append(createFileReportRow(SUCCESS, filePath, srcDir, taxonomie, tags, errors))

# Combines everything into a new md file
def saveParsedFile(filePath, taxonomie, tags, difficulty, isDraft, content, destPath):
    newContent = (
        f"---\ntitle: {filePath.stem}\ntaxonomie: {taxonomie}\ntags:\n" +
        '\n'.join([f"- {tag}" for tag in tags]) +
        "\n"
    )

    if difficulty:
        newContent += "difficulty: " + ''.join([f"{level}" for level in difficulty]) + "\n"
        
    if isDraft:
        newContent += "draft: true \n"

    newContent += "---" + content.split('---', 2)[-1]

    destPath.parent.mkdir(parents=True, exist_ok=True)

    with open(destPath, 'w', encoding='utf-8') as f:
        f.write(newContent)

    if VERBOSE:
        print(f"File completed: {filePath}")
        print("-" * 50)
