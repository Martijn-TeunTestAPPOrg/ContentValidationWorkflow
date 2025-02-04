# Variables
from config import NOT_NECESSARY_ICON

# Generate a markdown table string from a list of rows and headers.
def generateMarkdownTable(headers, rows):
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for row in rows:
        table += "| " + " | ".join(row) + " |\n"
    return table

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

# Create a row for the image report table
def createImageTableTow(status, filePath, srcDir, error):
    return {
        "status" : status,
        "image": filePath.stem,
        "path": str(filePath.relative_to(srcDir)),
        "error": error,
    }

# Format the image report table with specific headers and rows
def formatImageReportTable(imageReport):
    headers = ["Status", "Image", "Path", "Error"]
    rows = [[
        file['status'], 
        file['image'], 
        file['path'],
        file['error']
    ] for file in imageReport]

    table = generateMarkdownTable(headers, rows)
    return table
