import logging
from pathlib import Path
from config import failedFiles, parsedFiles, WIPFiles, ignoredFiles
from config import ERROR_NO_TAXCO_FOUND, FAIL_CROSS_ICON, WARNING_ICON, SUCCESS_ICON, TODO_ITEMS_ICON, IGNORE_FOLDERS, ERROR_WIP_FOUND, ERROR_TAXCO_NOT_NEEDED, NOT_NEEDED_ICON, ERROR_IGNORE_TAG_USED
from files.images import copyImages
from files.links import updateDynamicLinks
from report.table import createFileReportRow
from files.markdownUtils import extractHeaderValues, generateTags, findWIPItems, hasIgnoreTag


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
        tagErrors = []
        todoItems = []
        taxonomie = []
        newTags = []
        isDraft = False
        isIgnore = False

        # Skip curtain folders
        if any(folder in str(filePath) for folder in IGNORE_FOLDERS):
            logging.info(f"Skipping folder: {filePath}")
            continue

        with open(filePath, 'r', encoding='utf-8') as f:
            content = f.read()

        content, linkErrors = updateDynamicLinks(filePath, content, skipValidateDynamicLinks)
        imageErrors = copyImages(content, srcDirPath, destDirPath)
        existingTags = extractHeaderValues(content, 'tags')
        difficulty = extractHeaderValues(content, 'difficulty')
            
        # Check if the file has a ignore tag
        if hasIgnoreTag(content, filePath):
            isIgnore = True
            errors.append(ERROR_IGNORE_TAG_USED)
        else:
            taxonomie = extractHeaderValues(content, 'taxonomie')
            newTags, tagErrors = generateTags(taxonomie, existingTags, filePath)
            todoItems = findWIPItems(content)

            if(todoItems):
                errors.append(ERROR_WIP_FOUND + "<br>" + '<br>'.join([f"{item}" for item in todoItems]))

        # Combine all errors
        errors = linkErrors + imageErrors + tagErrors + errors

        # If there are any errors, the file is considered a draft unless the ignore tag is used
        if(errors and not isIgnore):
            isDraft = True

        appendFileToSpecificList(errors, todoItems, filePath, srcDirPath, taxonomie, newTags)
        saveParsedFile(filePath, taxonomie, newTags, difficulty, isDraft, isIgnore, content, destAndRelativePath)

# Fill the different lists used for the report
def appendFileToSpecificList(errors, todoItems, filePath, srcDir, taxonomie, tags):
    if errors:
        icon, targetList = WARNING_ICON, failedFiles  # Default case

        if todoItems:
            icon, targetList = TODO_ITEMS_ICON, WIPFiles
        elif ERROR_NO_TAXCO_FOUND in errors:
            icon, targetList = FAIL_CROSS_ICON, failedFiles
        elif ERROR_TAXCO_NOT_NEEDED in errors:
            icon, targetList = NOT_NEEDED_ICON, failedFiles
        elif ERROR_IGNORE_TAG_USED in errors:
            icon, targetList = WARNING_ICON, ignoredFiles

        targetList.append(createFileReportRow(icon, filePath, srcDir, taxonomie, tags, errors))
    else:
        parsedFiles.append(createFileReportRow(SUCCESS_ICON, filePath, srcDir, taxonomie, tags, errors))


# Combines everything into a new md file
def saveParsedFile(filePath, taxonomie, tags, difficulty, isDraft, isIgnore, content, destPath):
    newContent = (
        f"---\ntitle: {filePath.stem}\ntaxonomie: {taxonomie}\ntags:\n" +
        '\n'.join([f"- {tag}" for tag in tags]) +
        "\n"
    )

    if difficulty:
        newContent += "difficulty: " + ''.join([f"{level}" for level in difficulty]) + "\n"
        
    if isDraft:
        newContent += "draft: true \n"
        
    if isIgnore:
        newContent += "ignore: true \n"

    newContent += "---" + content.split('---', 2)[-1]

    destPath.parent.mkdir(parents=True, exist_ok=True)

    with open(destPath, 'w', encoding='utf-8') as f:
        f.write(newContent)
