# Content Compiler Script

This Python script automates the process of compiling and validating Markdown files based on taxonomy codes. It performs the following tasks:

1. **Dataset Parsing**: Reads and parses the dataset file containing taxonomy information.
2. **Markdown Parsing**: Parses Markdown files from the source directory, extracts metadata, and validates dynamic links.
3. **Image Handling**: Copies images referenced in the Markdown files to the build directory and checks for missing or unused images.
4. **Report Generation**: Generates reports summarizing the processing results, including failed files, work-in-progress items, and successfully processed files.
5. **Taxonomy Report**: Generates a taxonomy report detailing the implementation status of various taxonomy codes across different levels.

## Usage

To run the script, use the following command:

```sh
python compileContent.py
```

You can also skip the dynamic link validation by adding the --skip-link-check flag:
```sh
python compileContent.py --skip-link-check
```

## `config.py`
This is the config file which stores the different config options.
It's also used to save the state of the reports.

- Source Directory: src/cloned_repo/content
- Destination Directory: src/cloned_repo/build
- Dataset File: src/datasets/dataset.xlsx
- Taxonomy Report Path: src/cloned_repo/taxco_report.md
- Content Report Path: src/cloned_repo/content_report.md

## Validation steps
The following steps and methods are used to compile the md source files to build files

### `compileContent.py`
This is the main script file, this runs the show.

#### `def Main`
Main method which calls the other methods

```plantuml
sequenceDiagram
    participant User
    participant Main
    participant DatasetParser
    participant MarkdownParser
    participant ImageHandler
    participant ReportGenerator
    participant TaxonomyReport

    User->>Main: Run compileContent.py
    Main->>DatasetParser: Check if dataset file is found
    DatasetParser-->>Main: Dataset file found
    Main->>MarkdownParser: Parse Markdown files
    MarkdownParser-->>Main: Metadata extracted, links validated
    Main->>ImageHandler: Copy images to build directory
    ImageHandler-->>Main: Images copied, missing/unused images checked
    Main->>ReportGenerator: Generate processing reports
    ReportGenerator-->>Main: Reports generated
    Main->>TaxonomyReport: Generate taxonomy report
    TaxonomyReport-->>Main: Taxonomy report generated
    Main-->>User: Compilation and validation complete
```
