include: "rules/common.smk"
#
# 
# Snakemake pipeline to produce quality stats for the input fastq files, using FALCO
# https://github.com/smithlabcode/falco
# Cite:
# de Sena Brandine G and Smith AD. Falco: high-speed FastQC emulation for quality control of sequencing data.
# F1000Research 2021, 8:1874 (https://doi.org/10.12688/f1000research.21142.2)
#
# Runs for multiple samples specified in samples.csv file:
# Sample ID, R1, R2
#
# Samples.csv file can be created automatically using the Python helper script
# "make_sample_csv.py" 
# 
# Made for the folder structure of our samples:
# Library -> Folders with SampleID for each sample, with fastq files within
#
#
# Armin Hinterwirth, 02-18-2021

# Specify data folder, relative to the snakemake script. This folder
# should contain symlinks to the samples, so results are actually written 
# to the linked directory
data_dir = 'data/reads' 
qc_sub_dir = 'qcreports'


# ##### Target rules: create html and text summary report #####
rule all:
    input:
        expand("{data_dir}/{sample}/{qc_sub_dir}/{sample}_fastqc_report_R1.html",
                        sample=samples.loc[:,'sample'],
                        data_dir=data_dir,
                        qc_sub_dir=qc_sub_dir ),
        expand("{data_dir}/{sample}/{qc_sub_dir}/{sample}_fastqc_report_R2.html",
                        sample=samples.loc[:,'sample'],
                        data_dir=data_dir,
                        qc_sub_dir=qc_sub_dir )
rule qc_report_R1:
    input:
        unpack(get_fastq),
    output:
        html="{data_dir}/{sample}/qcreports/{sample}_fastqc_report_R1.html"
    params:
        outdir='{data_dir}/{sample}/qcreports/R1',
        falcoargs=config['falco']['args']
    log:
        '{data_dir}/{sample}/qcreports/{sample}_falco_R1.log'
    shell:
        """
        
        falco {params.falcoargs} -o {params.outdir} {input.r1} &> {log}
        
        # move the tmp falco report to the final resting place
        mv {params.outdir}/fastqc_report.html {output.html}
        rm -rf {params.outdir} # clean up temporary file
        """

# Do the same kind of report for the reverse complement reads
rule qc_report_R2:
    input:
        unpack(get_fastq),
    output:
        html="{data_dir}/{sample}/qcreports/{sample}_fastqc_report_R2.html"
    params:
        outdir='{data_dir}/{sample}/qcreports/R2',
        falcoargs=config['falco']['args']
    log:
        '{data_dir}/{sample}/qcreports/{sample}_falco_R2.log'
    shell:
        """
        
        falco {params.falcoargs} --reverse-complement -o {params.outdir} {input.r2} &> {log}
        
        # move the tmp falco report to the final resting place
        mv {params.outdir}/fastqc_report.html {output.html}
        rm -rf {params.outdir} # clean up temporary file
        """
    
    
    