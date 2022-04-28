#!/usr/bin/env python3
"""
Clean up a BibTeX file by:
1. Making journal titles their CASSI abbreviation (and warning if not found)
2. Changing article titles to Title Case
3. Removing preceding hyperlink information from DOI fields (and warning if
   a DOI does not start with `10.`)
4. Ensuring page ranges use en-dashes
5. Deleting requested fields from the file (if any)
6. Printing with indentation in a user-specified field order

28 Apr 2022 by Emmett Leddin
"""

#------------------ Import Modules ----------------------

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
import pandas as pd
import re
from titlecase import titlecase

# Set up global variables before definition
global lower_list, upper_list, ignore_list

#------------------ Variable Set-Up ----------------------

# The CSV with Abbreviation, Publication Name, and CODEN
cassi_csv = 'cassi_coden.csv'
# BibTeX input file
bib_in="demo_references.bib"
# Name for cleaned BibTeX file
bib_out="demo_references_clean.bib"

# A list of any words in titles that should be lowercase
#  Defined as prepositions and articles
lower_list = ['for', 'or', 'and', 'a', 'the', 'along', 'is']
# A list of any words in titles that should maintain capitalization
upper_list = ['DNA', 'RNA']
# A list of words in titles that shouldn't have capitalization modified
ignore_list = ["ff19SB"]

# A list in order of how to write lines within a BibTeX entry.
# Extras are appended to the end alphabetically
bib_write_order = ['author', 'title', 'journal',  'year', 'volume', 'number',
    'pages', 'doi']

# Do you want to remove any groups of info in the `.bib`?
marked_for_removal_bool = True
# Case-insensitive list of the groups to remove
marked_for_removal = ['abstract', 'eprint', 'file', 'pmid', 'pdf',
    'mendeley-groups']

# Do you want to remove all comments from the `.bib`? If `False`, they will all
#  be clumped together at the top of the output!
remove_comments = True

# Do you want to put the output in alphabetical order? If `False`, they will
#  be in the same order as the original `.bib`.
# alpha_out = True
alpha_out = False

#------------------ Function Set-Up ----------------------

def create_cassi_dict(cassi_csv):
    """
    Initialize the CASSI dictionary from CSV.

    Parameters
    ----------
    cassi_csv : CSV file
        CSV file with header "Abbreviation,PubTitle,CODEN".

    Returns
    -------
    cassi_dict : dict
        Dictionary with `PublicationName` as keys and `Abbreviations` as values.
        This way several titles or title variations can produce the same result.
    """
    c_df = pd.read_csv(cassi_csv, header=0)
    cassi_dict = dict(zip(c_df.PubTitle, c_df.Abbreviation))
    return cassi_dict

def read_bib(bib_in):
    """
    Parse the BibTeX file.

    Parameters
    ----------
    bib_in : BibTeX file
        Input BibTeX file.

    Returns
    -------
    bib_data: bibtexparser.bibdatabase.BibDatabase
        Database of information from the BibTeX file.
    """
    parser = BibTexParser()
    # Use False to keep stuff like @software
    parser.ignore_nonstandard_types = False
    # Sanitize fields and convert to lowercase
    parser.homogenize_fields = True
    # Abbreviate months
    parser.common_strings = True
    with open(bib_in) as my_bib:
        bib_data = bibtexparser.load(my_bib, parser)
    return bib_data

def fix_journal(entry, record, type, cassi_dict):
    """
    Update journal titles to the CASSI abbreviation.

    Parameters
    ----------
    entry : dict
        Fields as keys and entry values as values from the BibTeX file.
    record : entry.values()
        The value for a given field in the BibTeX file.
    type : entry.keys()
        The field type from the BibTeX file (e.g., 'authors').
    cassi_dict : dict
        `PublicationName` as keys and `Abbreviations` as values.
    """
    # Skip anything that's already right
    if record in cassi_dict.values():
        pass
    # Get anything from the dictionary
    elif record in cassi_dict.keys():
        record = cassi_dict[record]
        entry.update({type: record})
    else:
        # Check if uppercasing value works (case of jctc)
        x = ''.join(cassi_dict[p.upper()] if p.upper() in
         cassi_dict else p for p in re.split(r'(\W+)', record))
        # If the uppercase does work, update the dictionary
        if record.upper() in str(cassi_dict.keys()).upper():
            entry.update({type: x})
        # Not a known match; print a warning
        elif x not in cassi_dict.keys():
            print("\nWARNING: JOURNAL abbreviation for\n    "
            + f"'{record}' in entry {entry['ID']}\n  "
            + "is unknown. Please check CASSI directly.")
    return entry

def title_check(word, all_caps):
    """
    Check through the list of lowercase and uppercase words when fixing titles.

    Parameters
    ----------
    word : str
        The word to check capitalization rules for.
    all_caps : bool
        True for entire string in all caps. Required for callback function.
    """
    if word in ignore_list:
        return word
    elif word.upper() in upper_list:
        return word.upper()
    elif word.lower() in lower_list:
        return word.lower()
    elif all_caps == True:
        # Ignore if word is encased in braces (common in BibTeX files)
        if re.search(r'\{\w+\}', word):
            return word
        else:
            return word.lower().capitalize()

def fix_title(entry, record, type):
    """
    Convert 'title' entries to Title Case.
    """
    # Change case!
    record = titlecase(record, callback=title_check)
    entry.update({type: record})
    return entry

def fix_doi(entry, record, type):
    """
    Remove hyperlinks from DOIs and warn if a DOI does not start with '10.'.
    """
    # Remove hyperlink from DOI if present
    if record.startswith('https://dx.'):
        record = record.replace("https://dx.doi.org/", "")
        # Must update in dictionary!
        entry.update({type: record})
    elif record.startswith('https://doi.'):
        record = record.replace("https://doi.org/", "")
        # Must update in dictionary!
        entry.update({type: record})
    elif not record.startswith('10'):
        print("\nWARNING: DOI does not start with '10.' for\n    "
        + f"entry {entry['ID']}. Please confirm its DOI.")
    return entry

def fix_pages(entry, record, type):
    """
    Change page ranges to a en-dash.
    """
    # Hyphen
    if re.search('-', record) and not re.search('--', record):
        record = record.replace('-', '--')
        # Must update in dictionary!
        entry.update({type: record})
    # Space
    elif re.search(' ', record) and not re.search('--', record):
        record = record.replace(' ', '--')
        # Must update in dictionary!
        entry.update({type: record})
    return entry

def warn_author(entry, record):
    """
    Print a warning if the author list includes 'and others'.
    """
    if "and others" in record.lower():
        print(f"\nWARNING: Author list for {entry['ID']} may be incomplete.\n  "
        + "  Please check the authors for 'and others'.")

def fix_bib(bib_data, cassi_dict):
    """
    Iterate through the existing BibTeX file and correct entry formatting.
    """
    for entry in bib_data.entries:
        for type,record in entry.items():
            # Process journal entries
            if type.lower() == "journal":
                # `record` here is the journal title
                entry = fix_journal(entry, record, type, cassi_dict)
            # Process article titles --> provide Title Case
            elif type.lower() == "title":
                # `record` here is the article title
                entry = fix_title(entry, record, type)
            # Process DOIs
            elif type.lower() == "doi":
                # `record` here is the DOI
                entry = fix_doi(entry, record, type)
            # Process page ranges
            elif type.lower() == "pages":
                entry = fix_pages(entry, record, type)
            # Check author list for "and others"
            elif type.lower() == "author":
                warn_author(entry, record)
        if "doi" not in str(entry.keys()).lower():
             print(f"\nWARNING: No DOI field in entry {entry['ID']}")
    return bib_data

def write_file(bib_out, bib_data, bib_write_order, remove_comments, alpha_out):
    """
    Set up printing options for output and write to BibTeX (bib_out).

    Parameters
    ----------
    bib_out : str
        Name of the output file.
    bib_data: bibtexparser.bibdatabase.BibDatabase
        Database of information from the BibTeX file.
    bib_write_order : list
        Ordered list for writing fields in the output.
    remove_comments: bool
        True to remove comments, False to keep them.
    alpha_out : bool
        True for alphabetical, False to retain order from input.
    """
    writer = BibTexWriter()
    # Should comments be written?
    if remove_comments:
        writer.contents = ['entries']
    else:
        writer.contents = ['comments', 'entries']
    # Should output order be changed?
    if alpha_out:
        writer.order_entries_by = ['ID']
    else:
        writer.order_entries_by = None
    # Use 2 spaces for indent
    writer.indent = '  '
    # Use ACS order for fields within the BibTeX file
    writer.display_order = bib_write_order
    # Create string for printing
    bibtex_str = writer.write(bib_data)
    # Write the string into outfile
    with open(bib_out, 'w+') as f:
        f.write(bibtex_str)

def remove_extraneous(bib_data, marked_for_removal):
    """
    Remove any extraneous fields (ex: `mendeley-groups`).

    Parameters
    ----------
    bib_data: bibtexparser.bibdatabase.BibDatabase
        Database of information from the BibTeX file.
    marked_for_removal : list
        List of parameters to remove from the BibTeX file.
    """
    for entry in bib_data.entries:
        for marked in marked_for_removal:
            if marked.lower() in entry.keys():
                entry.pop(marked)
    return bib_data

#------------------ Run the Script ----------------------

# Set up the CASSI
cassi_dict = create_cassi_dict(cassi_csv)

# Read the BibTeX
bib_data = read_bib(bib_in)

# Fix journal titles and DOIs
bib_data = fix_bib(bib_data, cassi_dict)

# Remove unnecessary categories and write out the new BibTeX data
if marked_for_removal_bool:
    bib_data = remove_extraneous(bib_data, marked_for_removal)
    write_file(bib_out, bib_data, bib_write_order, remove_comments, alpha_out)
else:
    write_file(bib_out, bib_data, bib_write_order, remove_comments, alpha_out)
