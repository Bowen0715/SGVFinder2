# ICRA and SGVFinder

This is a revised version of SGVFinder (https://github.com/segalab/SGVFinder). We replace the GEM Mapper with Bowtie2, fixed multiple bugs, and added methods for creating a custom database. 
This code first maps reads to a reference database of the choice. ICRA then corrects read assignments by coverage, based on re-distribution of ambiguously mapped reads. The corrected assignments are used to detect
structural variants that are either variable across a cohort or deleted across 25-75% of it. 

This code was addapted from the paper "Structural variation in the gut microbiome associates with host health" (Zeevi, D., Korem, T., Godneva, A. et al. Structural variation in the gut microbiome associates with host health. Nature 568, 43–48 (2019). https://doi.org/10.1038/s41586-019-1065-y.).


## Installation 
You can install this package using the following command `pip install --no-cache-dir git+https://github.com/korem-lab/SGVFinder2.git`

## Requirements

1. This package has the following dependencies:
    - python (tested with 3.10.12)
    - numpy (tested with 1.26.0)
    - pandas (tested with 2.1.0)
    - Cython (tested with 3.0.2)
    - ujson (tested with 5.8.0)
    - pysam (tested with 0.21.0)
    - scipy (tested with 1.11.2)
    - bokeh (tested with 3.2.2)
    - Bio (tested with 1.5.9)
    - bowtie2 (tested with 2.2.5)

    If you encounter issues, please try to run in an environment with these packages.
2. It additionally requires C++ 11 and Cython installed.
    
## Usage

**See the workflow.ipynb for a non-parallelized simple implementation.**

### Creating a database
ICRA will run against a database of reference genomes. The database created is carried out with a single command ```createdb.py```. 
The createdb.py command takes two arguments, the first is a directory with a single fasta file per genome and the second arguments is the prefix for the created database.
Please note that only accepted file extensions are ```.fasta```, ```.fa``` and ```.fa.gz```. 

### Please note!
Following the successfull run of this command the final fasta file should also be made into a bowtie2 index with the command ```bowtie2-build <db_prefix>.fasta <db_prefix>```. ***The code will not run without it!***

(Note: you can also use the default reference database published with SGVFinder1: https://github.com/segalab/SGVFinder#install)

There are two main algorithms here - ICRA and SGVFinder.

### ICRA
ICRA has just a single method needed to operate it - ```single_file```. You 
can use it directly from python (recommended). This method takes in a (/pair of) 
fastq files and outputs a jsdel file. This file is a json file saved
with python's ujson package. It's a dictionary whose keys are the fastq
read ids, and the values are mapping lists. Each such mapping list is
a list of tuples, where the items in the tuple are: the destination id
in the database, the position of the first read, the position of the 
second read (-1 if SE), the probablity ICRA gives to this mapping, 
and the mapping quality.
You should run that method on each and every sample in your cohort.

### SGVFinder
SGVFinder has two stages, and hence two methods:

```get_sample_map``` - generates coverage maps ber bacteria per sample. You 
can use it directly from python, or run it using the command-line 
wrapper ```SGVF_PerFile_cmd.py```. You should run this method on the jsdel file
of each and every sample in your cohort.

```work_on_collection``` - generates the SV dataframes. You can use it
directly from python or run it using the command-line wrapper ```SGVF_cmd.py```.
You should only run this method once. It takes as input a dictionary
whose keys are the sample names and whose values are the sample_maps 
generated using ```get_sample_map```. This is generated automatically from a
glob string with the command-line wrapper.

**NOTE:** SGVFinder WILL NOT work on a single sample. If you have a small 
cohort we recommend changing the ```min_samp_cutoff``` (min=2) or running with ```--byorig```.

### CLI

SGVFinder offers several built-in commands to help run each step through a command line environment:

- ```icra <args>``` runs ICRA's `single_file` command
- ```svfinder get_sample_map <args>``` runs SVFinder's `get_sample_map` command
- ```svfinder work_on_collection <args>``` runs SVFinder's `work_on_collection` command


Note, you will need to install this package using `pip install` in order for these commands to work.
