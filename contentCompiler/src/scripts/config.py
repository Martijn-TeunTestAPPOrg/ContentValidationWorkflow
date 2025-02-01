#Global variables
dataset = list()												# Dataset list 
parsedFiles = []												# Track the status of each parsed file
failedFiles = []												# Track the status of each failed file
failedImages = []												# Track which images don't start with a 4C/ID component
WIPFiles = []													# Track the files that contain Work-in-progress items
taxcoReport = {}												# Report 1 data
contentReport = {}												# Report 2 data

# Constants
SRC_DIR = "src/cloned_repo/content"								# Source directory where the markdown files are located
DEST_DIR = "src/cloned_repo/build"								# Destination directory where the updated markdown files will be saved
TAXCO_REPORT_PATH = "src/cloned_repo/taxco_report.md"			# Taxco report path where the taxco report will be saved
CONTENT_REPORT_PATH = "src/cloned_repo/content_report.md"		# Content report path where the content report will be saved
DATASET = "src/datasets/dataset.xlsx" 							# Dataset containing the taxonomie information
TODO_PATTERN = r'-=[A-Z]+=-' 									# Regex pattern to find TODO items
TAXONOMIE_PATTERN = r'^[a-z]{2}-\d{1,3}\.[123]\.[^\s\.]+(-[^\s\.]+)*\.(?:OI|DT|PI|LT)$' # Taxonomie regex
VALID_DYNAMIC_LINK_PREFIXES = ['https://', 'http://', 'tags/'] 	# List of valid dynamic links
IGNORE_FOLDERS = ["schrijfwijze"] 								# Folders to ignore when parsing the markdown files

# VERBOSE output flag
VERBOSE = False 

# 4CID names
LT = "Leertaken"
OI = "Ondersteunende-informatie" 
PI = "Procedurele-informatie"
DT = "Deeltaken"

# Dataset columns numbers
TC1_COL = 1
TC2_COL = 2
TC3_COL = 5
PROCES_COL = 3
PROCESSTAP_COL = 4
LT_COL = 7
OI_COL = 8
PI_COL = 9
DT_COL = 10

# Error message for not including any taxonomy code
ERROR_INVALID_TAXCO = "Ongeldige taxonomiecode: "
ERROR_MISSING_TAXCO = "Geen taxonomiecode gevonden."
ERROR_TAXCO_NOT_FOUND = "Taxonomie niet gevonden in dataset: "

# Error message for images
ERROR_IMAGE_NOT_FOUND = "Afbeelding niet gevonden: "
ERROR_IMAGE_NOT_USED = "Afbeelding wordt in geen enkel bestand gebruikt"

# Error message for dynamic links
ERROR_INVALID_DYNAMIC_LINK = "Dynamische link fout: "

# WIP errors
ERROR_WIP_FOUND = "Work-in-progress items gevonden: "

# Icons
SUCCESS = "✅"
FAIL_CIRCLE = "⛔️"
FAIL_CROSS = "❌"
NOT_NECESSARY = "🏳️"
WARNING = "⚠️"
TODO_ITEMS = "🔨"
