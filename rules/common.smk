import pandas as pd
# import time, datetime
# from snakemake.utils import validate
from snakemake.utils import min_version

min_version("5.18.0")

###### Config file and sample sheets #####
configfile: "config.yaml"


def create_symlinks_to_data(samples, smkdata='data/reads'):
    """
    Creates symlinks in the snakemake data directory, which point to the
    data elsewhere on the file system. Absolute data paths to arbitrary locations
    are specified in samples.csv file. 
    Sample_ID  - Sample_ID_fastq_R1.fastq.gz
               - Sample_ID_fastq_R2.fastq.gz
    """
    if not os.path.isdir(smkdata):
        os.makedirs(smkdata)
    # create symlinked folders to actual data in smkdata directory
    print('Trying to create symlinks to original data locations:')
    print('{} --> {}'.format( 'Link name', 'Target (abs. path to data folder)' ))
    print('')
    for s in samples.index:
        linkname = os.path.join(smkdata, s)
        target = samples.loc[s, 'basepath']        
        print('{} --> {}'.format( linkname, target ))
        try:
            os.symlink(target, linkname )
        except:
            print('Symlink not created. It might already exists.')
        print('')


# Prepare sample names and paths for snakemake run
# Read comma-delimited value (csv) file with samples:
samples = pd.read_table(config["samples"], sep=',').set_index("sample", drop=False)
# Samples CSV has to have 3 columns: sample,r1,r2
if len(samples.columns) != 3:
    raise ValueError('The CSV file listing the samples needs to have 3 columns: sample,r1,r2')
samples.columns = ['sample','r1','r2'] # rename for consistency
# drop rows in which first character is "#" so that samples can be commented out
dropidx = samples['sample'].str.startswith("#")
samples = samples.loc[ ~dropidx, :]
# Get basepath for each sample from R1 path:
samples['basepath'] = samples.loc[:,'r1'].apply( lambda x: os.path.split(x)[0] )

create_symlinks_to_data(samples)

##### Wildcard constraints #####
wildcard_constraints:
    sample="|".join(samples.index),
    
    
##### Helper functions #####    
def get_fastq(wildcards, path_prefix='data/reads'):
    """
    Get fastq file names of given sample. 
    r1 and r2 columns from samples.tsv file.
    Only file name, not path is returned.
    """
    fastqs = samples.loc[(wildcards.sample), ["r1", "r2"]].dropna()
    sample_id = samples.loc[(wildcards.sample), "sample"]
    if len(fastqs) != 2:
        raise ValueError("There don't appear to be files for R1 and R2. Check sample.csv file.")
        
    return { "r1": os.path.join( path_prefix, sample_id, os.path.split(fastqs.r1)[1]), 
             "r2": os.path.join( path_prefix, sample_id, os.path.split(fastqs.r2)[1])
            }
                
                