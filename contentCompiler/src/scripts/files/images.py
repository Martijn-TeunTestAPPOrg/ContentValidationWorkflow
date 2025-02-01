# Imports
import os, re, shutil
from pathlib import Path

# Variables
from config import failedImages

# Constants
from config import NOT_NECESSARY, IGNORE_FOLDERS, ERROR_IMAGE_NOT_USED, ERROR_IMAGE_NOT_FOUND

# Functions
from report.table import createImageTableTow

"""
Search for image links in the markdown content, and copy the images from the source/
folder to the build/ folder, preserving the folder structure.

Args:
    content (str): Content of the markdown file.
    src_dir_name (str): Source directory (only the name of the folder itself)
    dest_dir_name (str): Destination directory (only the name of the folder itself)
"""
def copyImages(content, srcDir, destDir):
    errors = []
    if content is None:
        return errors
    
    imageLinks = re.findall(r'!\[\[([^\]]+)\]\]|\!\[([^\]]*)\]\(([^)]+)\)', content)

    for imageLink in imageLinks:
        if imageLink[0]:
            imagePath = imageLink[0].strip()
        elif imageLink[2]:
            imagePath = imageLink[2].strip()

        if not imagePath:
            continue

        if imagePath.startswith('http://') or imagePath.startswith('https://'):
            continue

        foundImagePath = None
        for root, dirs, files in os.walk(srcDir):
            if imagePath in files:
                foundImagePath = Path(root) / imagePath
                break

        if foundImagePath and foundImagePath.exists():
            relativePath = foundImagePath.relative_to(srcDir)
            newImagePath = destDir / relativePath
            newImagePath.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy(foundImagePath, newImagePath)
        else:
            print(ERROR_IMAGE_NOT_FOUND + imagePath)
            errors.append(ERROR_IMAGE_NOT_FOUND + ' `' + imagePath + '` ')

    return errors

"""
Fills the image Report with data from the images in the folders
Every unique TC3 and TC1 combination will be added to the Report 2 data.
"""
def fillFailedImages(srcDir, destDir):
    srcDirPath = Path(srcDir).resolve()
    destDirPath = Path(destDir).resolve()
    
    srcImages = getImagesInFolder(srcDirPath)
    destImages = getImagesInFolder(destDirPath)

    for image in srcImages: 
        if str(image.stem) not in {str(img.stem) for img in destImages}:
            failedImages.append(createImageTableTow(NOT_NECESSARY, image, srcDirPath, ERROR_IMAGE_NOT_USED))    

# Helper method to populate the image report
def getImagesInFolder(dir):
    folders = [folder for folder in Path(dir).rglob("src") if folder.is_dir()]

    images = set()
    
    for folder in folders:
        # Skip curtain folders
        if any(ignoreFolder in str(folder) for ignoreFolder in IGNORE_FOLDERS):
            continue
        
        images.update(filePath for filePath in folder.rglob("*")) 
    return images
