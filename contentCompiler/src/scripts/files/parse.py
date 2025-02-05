import logging
from pathlib import Path
from config import failedFiles, parsedFiles, WIPFiles
from config import ERROR_NO_TAXCO_FOUND, FAIL_CROSS_ICON, WARNING_ICON, SUCCESS_ICON, TODO_ITEMS_ICON, IGNORE_FOLDERS, ERROR_WIP_FOUND, ERROR_TAXCO_NOT_NEEDED, NOT_NEEDED_ICON
from files.images import copyImages
from files.links import updateDynamicLinks
from report.table import createFileReportRow
from files.markdownUtils import extractHeaderValues, generateTags, findWIPItems


# Update markdown files in the source directory
def parseMarkdownFiles(srcDir, destDir, skipValidateDynamicLinks):
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
            logging.info(f"Skipping folder: {filePath}")
            continue

        with open(filePath, 'r', encoding='utf-8') as f:
            content = f.read()

        content, linkErrors = updateDynamicLinks(filePath, content, skipValidateDynamicLinks)
        imageErrors = copyImages(content, srcDirPath, destDirPath)
        existingTags = extractHeaderValues(content, 'tags')
        taxonomie = extractHeaderValues(content, 'taxonomie')
        newTags, tagErrors = generateTags(taxonomie, existingTags, filePath)
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
            WIPFiles.append(createFileReportRow(TODO_ITEMS_ICON, filePath, srcDir, taxonomie, tags, errors))
        elif(ERROR_NO_TAXCO_FOUND in errors): 
            failedFiles.append(createFileReportRow(FAIL_CROSS_ICON, filePath, srcDir, taxonomie, tags, errors))
        elif any(ERROR_TAXCO_NOT_NEEDED in error for error in errors):
            failedFiles.append(createFileReportRow(NOT_NEEDED_ICON, filePath, srcDir, taxonomie, tags, errors))
        else: 
            failedFiles.append(createFileReportRow(WARNING_ICON, filePath, srcDir, taxonomie, tags, errors))
    else:
        parsedFiles.append(createFileReportRow(SUCCESS_ICON, filePath, srcDir, taxonomie, tags, errors))

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
