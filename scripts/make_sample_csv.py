#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Helper script to create a sample.csv file with the following columns:
sample_id, R1 fastq file, R2 fastq file

This sample csv file can then be used for the snakemake workflow
to run falco on all samples.

Created on Thu, Feb 18, 2021

@author: armin
"""

DEFAULT_OUTPUT='samples.csv'

DESCRIPTION="""
Helper script to create a 'sample.csv' file with the following columns:
sample, r1, r2 (where sample is the Sample_ID, and r1 and r2 are the
absolute paths to the fastq.gz files for the fwd and reverse reads, 
respectively)

This sample csv file can then be used for the snakemake workflow
to run falco on all samples.
"""



import argparse, os
import pandas as pd

def loadSampleListFile(fn):
    """
    Read a list of samples from a text file (fn).
    To create a quick list of folders in the sample directory do this:
        
        ls > folderlist.txt
        
        Then, remove any lines in folderlist.txt that aren't sample folders
        
    """
    samples = []
    with open(fn, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                samples.append(line.rstrip())
    return samples
    

def main():
    PARSER = argparse.ArgumentParser(description=DESCRIPTION)
    # PARSER.add_argument('sample_list_file', nargs=1, type=str,
    #                     help='Path of a text file containing sample IDs. '\
    #                     'One sample per line.')
    PARSER.add_argument('samplelist', 
                        nargs='+', 
                        type=str, 
                        help='Either space-separated list of sampleIDs, or text file '\
                        'with sample list: one line per sample ID')
    PARSER.add_argument('-o', '--output', help='Output file. Default: "{}".'.format(DEFAULT_OUTPUT), 
                        default=DEFAULT_OUTPUT)
    ARGS = PARSER.parse_args()
    # load list of samples from sample list file:
    if len(ARGS.samplelist) == 1 and ARGS.samplelist[0].endswith('.txt'):
        samples = loadSampleListFile( ARGS.samplelist[0] )
    else:
        samples = ARGS.samplelist
        
    rowdict = {}
    basepath=os.getcwd() 
    for s in samples:
        rowdict[s] = {}
        # Find fastq.gz files for this sample
        spath = os.path.join(basepath, s)
        for f in os.listdir(spath):
            if f.startswith(s+'_R1') and f.endswith('.fastq.gz'):
                rowdict[s]['r1'] = os.path.join(spath,f)
            elif f.startswith(s+'_R2') and f.endswith('.fastq.gz'):
                rowdict[s]['r2'] = os.path.join(spath,f)
            else:
                pass
                
    out_df = pd.DataFrame.from_dict(rowdict, orient='index')
    out_df.index.name = 'sample'
    # print('\nThe following files were found:')
    # print(out_df)
    # print('')
    if ARGS.output:
        out_df.to_csv( ARGS.output )
        print('File saved as: {}'.format( ARGS.output))
    
if __name__=='__main__':
    main()