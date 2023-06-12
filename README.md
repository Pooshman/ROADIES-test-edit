![ROADIES_logo](https://github.com/TurakhiaLab/wga-phylo/assets/114828525/05cd206e-542c-4ee4-bfd6-d4c03fed5984)
# Reference free Orthology free Alignment free DIscordant Aware Estimation of Species Tree (ROADIES)

## Table of Contents
- [Overview](#overview)
- [Getting Started](#gettingstarted) 
- [Using ROADIES](#usage)
  - [Step1: Configuring ROADIES](#configuration)
  - [Step2: Running the pipeline](#run)
  - [Step3: Analyzing output files](#output)
- [Example run](#example)
- [References](#references)

## <a name="overview"></a> Overview

Most phylogeny estimation methods use gene markers/gene trees which require computationally expensive, error-prone, and/or semi-automated steps to infer orthology.Our technique uses raw genomes to build phylogenies. <br>

WGA Pipeline steps:
- Take random sequences of fixed sized sampled from different genomes and treat them as genes
- Cluster species through alignments with those genes
- Build gene trees using these clusters
- Reconstruct a species tree using these gene trees using ASTRAL-PRO
- ASTRAL-pro can work with homology only, and does not require orthology

## <a name="gettingstarted"></a> Getting Started

### Install Snakemake

[Snakemake](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html) and Snakedeploy are best installed via the Mamba package manager (a drop-in replacement for conda). If you have neither Conda nor Mamba, it can be installed via [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge). 

Given that Mamba is installed, run 

```
mamba create -c conda-forge -c bioconda --name snakemake snakemake snakedeploy
``` 

to install both Snakemake and Snakedeploy in an isolated environment. 

Once snakemake is installed, it needs to be activated via

```
conda activate snakemake
```
### Install ASTRAL-Pro

In order to run the pipeline, a manual installation of ASTRAL-PRO (latest version) is required. If previous version of ASTER-Linux is installed, replace the ASTER-Linux directory with the ASTRAL-PRO git repository as mentioned below. 

```
rmdir ASTER-Linux
wget https://github.com/chaoszhang/ASTER/archive/refs/heads/Linux.zip
unzip Linux.zip
cd ASTER-Linux
make
cd ..
```

## <a name="usage"></a> Using ROADIES

## <a name="configuration"></a> Step 1: Configure ROADIES

All input genomic sequences should be in fasta format. 

Provide the path for input dataset, along with the input configuration parameters in `config/config.yaml` file before running the pipeline. Here is the list of available input configurations:

```yaml
#This file configures the parameters for ROADIES and converge
#Path for input genomes
GENOMES: "/home/roadies-datasets/drosophila"
#length of genes
LENGTH: 500
#number of genes
KREG: 100
#minimum % uppercase for genes
UPPER_CASE: 0.90
#ROADIES output directory
OUT_DIR: "results"
#minimum number of species in a gene fasta (4 min for ASTRAL-PRO)
MIN_ALIGN: 4 
#minimum % match in alignment
IDENTITY: 65
#minimum input sequence coverage
COVERAGE: 85
#max number of copies from a genome in an alignment
MAX_DUP: 100
#max msa input length
GAPS: 1.2
#reference tree for converge
REFERENCE: "trees/birds_48.nwk"
#maximum TreeDistance Threshold for stopping converge
DIST_THRESHOLD: 0.1
#number of bootstrapped trees for comparison
NUM_BOOTSTRAP: 10
#input ROADIES gene trees for converge
INPUT_GENE_TREES: null
#input ROADIES mapping file for converge
INPUT_MAP: null
#max converge runs before stopping
MAX_ITER: 50
#number of consecutive runs having to satisfy self_dist and iter_dist_bs thresholds before stopping
STOP_ITER: 1
```
## <a name="run"></a> Step 2: Running the pipeline

Once snakemake environment is activated and `config.yaml` is configured, run
```
snakemake --core [number of cores] --use-conda
```
For starting the run from an incomplete previous session instead of starting a fresh run everytime, run
```
snakemake --core [number of cores] --use-conda --rerun-incomplete
```
## <a name="output"></a> Step 3: Analyzing output files

After completing the run, the output files (along with all intermediate output files for each stage of the pipeline) will be saved in a separate `results` folder mentioned in `OUT_DIR` parameter, which contains the following subfolders:

- `alignments` - contains the sampled output of each species in `<species_name>.maf` format generated by the sampling step
- `genes`- contains the fasta files of all highest scoring genes which is filtered after LASTZ step in `gene_<id>.fa` format
- `geneTree` - contains all gene trees merged together in a single `gene_tree_merged.nwk` file 
- `msa`- contains the MSA filtered output for all gene fasta files in `gene_aln_<id>.fa` format
- `plots` - 
- `samples` - 
- `statistics`- contains the list of input species in `num_genes.csv`, number of gene trees in `num_gt.txt`, number of homologues with corresponding genes in `homologues.csv`

`converge.py` is a script that iteratively runs ROADIES, wherein after each run, the resultant gene trees are concatenated into a master file, bootstrapped, and input into `ASTRAL-PRO`. These bootstrapped trees are then compared within the same run (self_dist), with the previous run (iter_dist_bs), and also with the reference if given (ref_dist). The program stops after either running converge for `MAX_ITER` or satisfying the distance threshold `DIST_THRESHOLD` for `STOP_ITER` consecutive runs for both self_dist and iter_dists_bs. 

To run the convergence, follow the steps below:

- Activate conda environment (make sure that ete3 is present in snakemake conda environment)
- Configure input parameters like `MAX_ITER`, `STOP_ITER`, `DIST_THRESHOLD`, `NUM_BOOTSTRAP` in `config.yaml` file
- Provide input reference tree for the species in `trees` folder (make sure that the reference tree is in newick format) and add the path as `REFERENCE` in `config.yaml` file
- Run
```
python workflow/scripts/converge.py --ref trees/flies_ref_11.nwk -c 16
```
The above command runs the convergence script on 16 cores by taking 11 drosophila species tree as reference. 

The output after the converge run is saved in a separate `converge` folder, which has the following files:

- 

`trees` folder contain the following reference trees (along with their sources mentioned below)

- 11 Drosophila species - `flies_ref_11.nwk` ([Source](http://timetree.org/))
- 100 Drosophila species - `flies_ref_100.nwk` ([Source](https://github.com/flyseq/drosophila_assembly_pipelines/blob/master/figure_data/figure5/busco_species_astral.tree))


## <a name="example"></a> Example run

## <a name="references"></a> References





