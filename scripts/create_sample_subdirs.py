#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A script to place fastq files downloaded from the sftp server into 
separate subfolders for each sample.

Created on Mon Jan 29 14:43:23 2018

@author: armin
"""

import os, shutil, sys
import argparse


def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    
    Source: http://code.activestate.com/recipes/577058/
    
    """
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def main():            
    # Go through current directory     
    PARSER = argparse.ArgumentParser(description='Create sub-directories (named after sample ID) for all sample fastq.gz files found in current folder.')
    PARSER.add_argument('-d', '--basedir', help='Base directory of samples. ' \
                        'Default is current working directory.',
                        default='.')  
    PARSER.add_argument('-e', '--extension', help='File extension to look for.',
                        default='fastq.gz')  
    PARSER.add_argument('-n', '--no_prompt', help='Do not show confirmation prompt for each sample',
                        action="store_true")
    PARSER.add_argument('-t', "--test", help="Dry run that doesn't actually move any files. Just shows resulting paths.", \
                        action="store_true")      
    ARGS = PARSER.parse_args()
    if ARGS.basedir == '.':
        d = os.getcwd()
    else:
        d = ARGS.basedir
     
    
    sys.stdout.write('Looking for files with the extension "{}" in the ' \
          'following directory:\n'.format(ARGS.extension))    
    sys.stdout.write(d + '\n')
    
    # look for all samples in current directory (fastq.gz ending by default)  
    target_files = []
    file_list = os.listdir(d)
    for file in file_list:
        if file.endswith(ARGS.extension):
            target_files.append(file)
    
    if len(target_files) == 0:
         sys.stdout.write('\nNo files with extension "{}" found in this folder.\n'.format(ARGS.extension))
         return
    # find sample_pairs
    names_R1 = []
    names_R2 = []
    
    for t in target_files:  
        t1 = t.split('_R1')
        if len(t1) > 1:
            names_R1.append(t1[0])
        t2 = t.split('_R2')
        if len(t2) > 1:
            names_R2.append(t2[0])
    # A "good" sample contains both R1 and R2, is therefore the intersection:
    sample_set = set(names_R1).intersection(set(names_R2))
    movecounter = 0
    if len(sample_set) == 0:
        sys.stdout.write('\nNo paired read samples found in this folder.\n'.format(ARGS.extension))
        return
    
    for s in sample_set:        
        sys.stdout.write('\nSAMPLE: {}\n'.format(s))
        # create abs. path
        s_folder = os.path.join(d, s)
        #check if directory for that sample already exists:
        if os.path.isdir(s_folder):
            sys.stdout.write('Sample directory "{}" already exists.\n'.format(s_folder))
        else:
            if not ARGS.test:
                os.mkdir(s_folder)
                sys.stdout.write('Directory {} created.\n'.format(s_folder))
            else:
                sys.stdout.write('Testing only. Directory not created.')
            
        # find files to move:
        sys.stdout.write('Finding files for sample {}\n'.format(s))
        movemap = {}
        movemap['source'] = []
        movemap['destination'] = []
        for file in file_list:
            if file.startswith(s) and file.endswith(ARGS.extension):
                sys.stdout.write('Found file: {}\n'.format(file))
                movemap['source'].append(os.path.join(d, file))
                movemap['destination'].append(os.path.join(d, s, file))
        if len(movemap['source']) != 2:
            sys.stdout.write('Error: there should be exactly 2 files for this sample\n')
        
        if not ARGS.test:
            if ARGS.no_prompt:
                a = 'yes'
            else:
                a = query_yes_no('Do you want to move these files into their own sub-folder?',
                            default='yes')
        if ARGS.test or a == 'yes':
            for i in range(2):
                print( movemap['source'][i] + ' ==> ' + movemap['destination'][i] )
                if os.path.isfile(movemap['destination'][i]):
                    print('Error: destination file already exists. File not moved.')
                else:
                    if not ARGS.test:
                        shutil.move( movemap['source'][i],  movemap['destination'][i] )
                    movecounter += 1
        else:
            print('Moving of this sample\'s files cancelled')
    if ARGS.test:
        print('TEST run only (-t argument supplied). Number of files that would have been moved: {}'.format(movecounter))
    else:
        print('Number of files moved: {}'.format(movecounter))
        

if __name__ == '__main__':
    main()
