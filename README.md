# CASSI Bib Parser

This script cleans up the journal names in a `.bib` file to match the
[CASSI](https://cassi.cas.org/search.jsp) abbreviations.
Not all CASSI entries are included (please contribute more!); the majority
came from the
[Core Journals](https://www.cas.org/support/documentation/references/corejournals)
table.

The script will print a warning if an abbreviation was not found.

## Usage

There are several user-specified variables within the script toward the top.
These include:

- `cassi_csv`: the name of the CSV with columns for Abbreviations,
   Publication Names, and CODEN. A path may be included!
- `bib_in`: the input BibTeX file. A path may be included!
- `bib_out`: the name of the BibTeX file to output. A path may be included!
- `lower_list`: a list of words in `title` fields that should always be
   lowercase
- `upper_list`: a list of words in `title` fields that should always be
   uppercase
- `ignore_list`: a list of words in `title` fields that should retain their
   capitalization
- `bib_write_order`: a list specifying the order of fields written within a
   BibTeX entry. Anything not specified is appended at the end alphabetically.
- `marked_for_removal_bool`: a boolean operator for whether specific fields
   should not be included in the output BibTeX file
- `marked_for_removal`: a list of fields that should not be included in the
   output BibTeX file.
   If `marked_for_removal_bool = True`, this variable must be created!
- `remove_comments`: a boolean operator for whether to include comments in the
  output BibTeX file.
  If `False`, all comments will be in a block together at the top of the output.
- `alpha_out`: a boolean operator for whether to change the order of the
  entries to alphabetical by identifier (True) or leave them unsorted (False).

After modifying everything in the variable set-up, you can run the script!
```
python bibtex_parser.py
```

## Requirements

This script is written using Python3.
You can either install Python [on its own](https://www.python.org/downloads/)
or through [Anaconda](https://www.anaconda.com/products/distribution)
(recommended).

Dependencies:
- [bibtexparser](https://pypi.org/project/bibtexparser/)
- [pandas](https://pandas.pydata.org/getting_started.html)
- [titlecase](https://pypi.org/project/titlecase/)

These can be installed using the included `requirements.txt` file:
```
pip install -r requirements.txt
```

## TODO

- Check entries against CrossRef
- Print a warning for entries without DOIs
- Use `--` for page ranges
