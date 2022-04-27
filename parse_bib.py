#!/usr/bin/env python3
import pandas as pd
from pybtex.database import parse_file
from pybtex.database import BibliographyData, Entry
import re
import os

#------------------ Variable Set-Up ----------------------

cassi_csv = 'cassi_coden.csv'
bib_in = 'demo_references.bib'
bib_out = 'demo_references_clean.bib'

## Do you want to remove any groups of info in the `.bib`?
marked_for_removal_bool = True
## Case-insensitive list of the groups to remove
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
    # Won't parse file if any entry key is reused!
    bib_data = parse_file(bib_in)
    # bib_data.lower() will make everything lowercase, including the keys...
    return bib_data

def fix_bib(bib_data, cassi_dict):
    """
    Iterate through the existing BibTeX file, update journal titles to the
    CASSI abbreviation, and fix DOIs.
    """
    for key,info in bib_data.entries.items():
        for type,record in info.fields.items():
            # Process journal entries
            if type.lower() == "journal":
                # `record` here is the journal title
                # Skip anything that's already right
                if record in cassi_dict.values():
                    continue
                # Get anything from the dictionary
                if record in cassi_dict.keys():
                    record = cassi_dict[record]
                    info.fields.update({type: record})
                else:
                    # Check if uppercasing value works (case of jctc)
                    x = ''.join(cassi_dict[p.upper()] if p.upper() in
                     cassi_dict else p for p in re.split(r'(\W+)', record))
                    # If the uppercase does work, update the dictionary
                    if record.upper() in str(cassi_dict.keys()).upper():
                        info.fields.update({type: x})
                    # Not a known match; print a warning
                    elif x not in cassi_dict.keys():
                        print("\nWARNING: JOURNAL abbreviation for\n    "
                        + f"'{record}' in entry {key}\n  "
                        + "is unknown. Please check CASSI directly.")
            # Process DOIs
            elif type.lower() == "doi":
                # `record` here is the DOI
                # Remove hyperlink from DOI if present
                if record.startswith('https://dx.'):
                    record = record.replace("https://dx.doi.org/", "")
                    # Must update in dictionary!
                    info.fields.update({type: record})
                elif record.startswith('https://doi.'):
                    record = record.replace("https://doi.org/", "")
                    # Must update in dictionary!
                    info.fields.update({type: record})
                elif not record.startswith('10'):
                    print("\nWARNING: DOI does not start with '10.' for\n    "
                    + f"entry {key}. Please confirm its DOI.")
    return bib_data

# This function exists because pybtex does not currently allow field deletion
def remove_extraneous(bib_data, bib_out, marked_for_removal):
    """
    Write out the data to a temporary file and remove any bad fields.
    Note: if any keys match the bad fields, they will also be deleted!!!
    """
    bib_data.to_file("bib.tmp", bib_format="bibtex")
    with open("bib.tmp", 'r') as t, open(bib_out, 'w+') as f:
        for line in t:
            if not any(marked.lower() in line.lower() \
             for marked in marked_for_removal):
                f.write(line)
    os.remove("bib.tmp")

#------------------ Run the Script ----------------------

# Set up the CASSI
cassi_dict = create_cassi_dict(cassi_csv)

# Read the BibTeX
bib_data = read_bib(bib_in)

# Fix journal titles and DOIs
bib_data = fix_bib(bib_data, cassi_dict)

# Remove unnecessary categories and write out the new BibTeX data
if marked_for_removal_bool:
    remove_extraneous(bib_data, bib_out, marked_for_removal)
else:
    bib_data.to_file(bib_out, bib_format="bibtex")
