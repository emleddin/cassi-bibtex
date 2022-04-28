#!/usr/bin/env python3
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
import pandas as pd
import re

#------------------ Variable Set-Up ----------------------

# The CSV with Abbreviation, Publication Name, and CODEN
cassi_csv = 'cassi_coden.csv'
# BibTeX input file
bib_in="demo_references.bib"
# Name for cleaned BibTeX file
bib_out="demo_references_clean.bib"

# A list in order of how to write lines within a BibTeX entry.
# Extras are appended to the end alphabetically
bib_write_order = ['author', 'title', 'journal',  'year', 'volume', 'number',
    'pages', 'doi']

# Do you want to remove any groups of info in the `.bib`?
marked_for_removal_bool = True
# Case-insensitive list of the groups to remove
marked_for_removal = ['abstract', 'eprint', 'file', 'pmid', 'pdf',
    'mendeley-groups']

#------------------ Function Set-Up ----------------------

def create_cassi_dict(cassi_csv):
    """
    Initialize the CASSI dictionary from CSV.
    """
    c_df = pd.read_csv(cassi_csv, header=0)
    # Make Abbreviation the value, since several title variations should
    #  produce the same result
    cassi_dict = dict(zip(c_df.PubTitle, c_df.Abbreviation))
    return cassi_dict

def read_bib(bib_in):
    """
    Parse the BibTeX file.
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

def fix_doi(entry, record, type):
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

def fix_bib(bib_data, cassi_dict):
    """
    Iterate through the existing BibTeX file, update journal titles to the
    CASSI abbreviation, and fix DOIs.
    """
    for entry in bib_data.entries:
        for type,record in entry.items():
            # Process journal entries
            if type.lower() == "journal":
                # `record` here is the journal title
                entry = fix_journal(entry, record, type, cassi_dict)
            # Process DOIs
            elif type.lower() == "doi":
                # `record` here is the DOI
                entry = fix_doi(entry, record, type)
    return bib_data

def write_file(bib_out, bib_data, bib_write_order):
    writer = BibTexWriter()
    # Use 2 spaces for indent
    writer.indent = '  '
    # Use ACS order for fields within the BiBTeX file
    writer.display_order = bib_write_order
    # Create string for printing
    bibtex_str = writer.write(bib_data)
    # Write the string into outfile
    with open(bib_out, 'w+') as f:
        f.write(bibtex_str)

# This function exists because pybtex does not currently allow field deletion
def remove_extraneous(bib_data, marked_for_removal):
    """
    Remove any bad fields.
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
    write_file(bib_out, bib_data, bib_write_order)
else:
    write_file(bib_out, bib_data, bib_write_order)
