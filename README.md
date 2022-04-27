# Bib Parser

This script cleans up the journal names in a `.bib` file to match the
[CASSI](https://cassi.cas.org/search.jsp) abbreviations.
Not all CASSI entries are included (please contribute more!); the majority
came from the
[Core Journals](https://www.cas.org/support/documentation/references/corejournals)
table.

The script will print a warning if an abbreviation was not found.

## Requirements

Python3 with:
- pandas
- pybtex
- re

## TODO

- Check entries against CrossRef
- Ensure entries have DOIs
- Use `--` for page ranges
- Titlecase for article titles
- Pretty printing?
