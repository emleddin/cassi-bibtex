#!/usr/bin/env python3
import pandas as pd
from pybtex.database import parse_file
from pybtex.database import BibliographyData, Entry
import re

#------------------ Variable Set-Up ----------------------

cassi_csv = 'cassi_coden.csv'
bib_in = 'demo_references.bib'
bib_out = 'demo_references_clean.bib'

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


def replace_titles(bib_data, cassi_dict):
    """
    Iterate through the existing BibTeX file and update journal titles to the
    CASSI abbreviation.
    """
    for entry in bib_data.entries.values():
        for type,title in entry.fields.items():
            if type.lower() == "journal":
                x = ''.join(cassi_dict[p.upper()] if p.upper() in
                 cassi_dict else p for p in re.split(r'(\W+)', title))
                if x == title:
                    if title not in cassi_dict.values():
                        print("WARNING: Unknown journal abbreviation for "
                        + f"'{title}'.\n  Please check CASSI directly.")
    return bib_data

#------------------ Run the Script ----------------------

# Set up the CASSI
cassi_dict = create_cassi_dict(cassi_csv)

# Read the BibTeX and fix titles
bib_data = read_bib(bib_in)
bib_data = replace_titles(bib_data, cassi_dict)

# Write out the new BibTeX data
bib_data.to_file(bib_out, bib_format="bibtex")
