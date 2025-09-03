<p align="left">
  <!-- <img src="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/arvia_header.png" height="70" > -->
  <a href="https://github.com/pablo-aja-macaya/ARVIA">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/arvia_header_bb.png">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/arvia_header_wb.png">
      <img alt="ARVIA Logo" src="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/arvia_header_wb.png" style='width: 30%; object-fit: contain'>
  </picture>
  </a>
</p>

## Summary

ARVIA (**A**ntibiotic **R**esistance **V**ariant **I**dentifier for *Pseudomonas **a**eruginosa*) takes **single-end/paired-end reads (long or short)** and/or an **assembly** per sample to perform exhaustive **variant calling** of genes related to antibiotic resistance in *Pseudomonas aeruginosa*. Additionally, it can extract **acquired resistance genes** and **MLST** from assemblies, or use **each one of your samples as reference to the rest** in variant calling. You can see an example of the main outputs [here](https://github.com/pablo-aja-macaya/ARVIA/raw/refs/heads/main/arvia/data/examples/example_result.xlsx) and [here](https://github.com/pablo-aja-macaya/ARVIA/raw/refs/heads/main/arvia/data/examples/example_result_sc.xlsx) (it also returns easily processable .tsv files). See [Usage](#usage) and [Installation](#installation) sections for more information. 

Its main functions are:
- **Variant calling in PAO1**:
  - **Point mutations** (Single Nucleotide Variants or SNV, indels, frameshifts) 
  - Possible **missing features** (e.g. lost genes due to chromosomic rearrangement).
  - Possible **truncated genes** due to big chromosomic rearrangements (only with assembly!).
  - **Mixed positions** (e.g. 50% of reads indicate C and the other 50% T).
  - Possible **SNV polymorphisms** that do not influence antibiotic resistance.
- **Variant calling of closest oprD reference**. 
- **Acquired resistance genes** (only with assembly!).
- **MLST identification** (only with assembly!).
- Creation of **comparative tables** to more easily assess the cause of different phenotypes between samples. This includes **comparisons using PAO1 or any of the input samples as reference**, if given at least one `.gbk` file as input. 
- **Interactive HTML IGV reports** to visualize point mutations in important genes.




<p align="center">
  <img src="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/arvia_sp_v0.1.1.png" style='width: 100%; object-fit: contain'>
</p>


## Index
- [Usage](#usage)
- [Installation](#installation)
- [Input](#input)
  - [Input YAML convention](#input-yaml-convention)
  - [ARVIA's naming convention](#file-naming-convention)
- [Output](#output)
- [Rationale behind additional steps in variant calling](#rationale-behind-additional-steps-in-variant-calling)
- [Full command list](#full-command-list)
- [Citation](#citation) 



## Usage

You can **run ARVIA** easily with an `input.yaml` file (see [**Input YAML convention**](#input-yaml-convention)) containing the input files:

```sh
# Run ARVIA
arvia run --input_yaml input.yaml --output_folder arvia
```

You can also **previsualize** what the pipeline is going to do with `--previsualize`:
```sh
# Run ARVIA with preview
arvia run --input_yaml input.yaml --output_folder arvia --previsualize
```

And **subset to specific samples** with `--barcodes`:
```sh
# Run ARVIA selecting specific samples in input
arvia run --input_yaml input.yaml --output_folder arvia --barcodes sample1 sample2 sample3
```

If you want to do **one to one variant calling** in your input samples, using each one as reference for the others, add `.gbk` files for at least one sample in `input.yaml` and add `--one_to_one` in command line (see [**Input YAML convention**](#input-yaml-convention)). This can be very demanding depending on how many samples and references, reduce the cost by specifying `--barcodes`:
```sh
# Run ARVIA doing one to one comparisons
arvia run --input_yaml input.yaml --output_folder arvia --one_to_one
```

If your files follow [**ARVIA's naming convention**](#file-naming-convention), you can also give them all with `--reads` and/or `--assemblies` and/or `--gbks` and ARVIA will associate each file to their `sample_id`:

```sh
# Full pipeline (reads+assemblies)
arvia run --assemblies folder/*.fasta --reads folder/*.fastq.gz --output_folder arvia

# Full pipeline using only assemblies (no depth inference in variant calling)
arvia run --assemblies folder/*.fasta --output_folder arvia

# Partial pipeline using only reads (truncation information in assembly from assembly is missing)
arvia run --reads folder/*.fastq.gz --output_folder arvia
```

Check out more options, like `--cores`, in the [Full command list](#full-command-list).

## Installation

> [!NOTE]
> This application has been **designed for Linux systems** and tested in **Ubuntu 20.04.4**.

Installation through **mamba** is highly recommended. A conda release of ARVIA will hopefully happen soon but, for now, you can install it like this:

```sh
# Create main environment where ARVIA runs
mamba create -n arvia \
    snakemake==7.18.0 python=3.8 pandas==1.5.0 numpy==1.23.1 'biopython>=1.78' rich-argparse==1.6.0 'colorama==0.4.4' 'odfpy==1.4.1' 'setuptools<=70' toml==0.10.2 xlsxwriter openpyxl=3.1 ipykernel \
    seqkit==2.1.0 'pigz>=2.4' ncbi-amrfinderplus mlst unzip igv-reports \
    perl-bioperl snippy==4.6.0 snpEff==4.3.1t bcftools=1.21 openssl==3.5.0 samtools=1.18 vt=0.57721 blast=2.16.0
    
conda activate arvia

# Install ARVIA from pip
pip install arvia

# # OR install from github for development version
# git clone https://github.com/pablo-aja-macaya/ARVIA.git
# cd ARVIA
# python -m pip install -e . # "-e" allows for editable mode, else "python -m pip install ."
```

To finish installation and update/install the needed databases, please run:

```sh
arvia dbs
```

In order to test ARVIA's installation, execute the following command, which downloads a set of reads and assemblies from NCBI and tries to run the pipeline:

```sh
arvia test
```

<!-- 
In case you need help installing conda and mamba from scratch, this could help (although it is probably best you follow their installation guide):
```sh
# Download miniconda and install
wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Linux-x86_64.sh
bash Miniconda3-py38_4.10.3-Linux-x86_64.sh

# Reopen terminal so conda is activated

# Remove autoactivation to base environment (Optional)
conda config --set auto_activate_base false

# Add channels and install mamba
conda config --add channels defaults
conda config --add channels r
conda config --add channels bioconda
conda config --add channels conda-forge

# Set priority of channels
conda config --set channel_priority flexible

# Install mamba
conda install mamba -n base -c conda-forge
``` -->


## Input

ARVIA takes **single-end/paired-end reads (long or short)** and/or an **assembly** for each sample given. Single-end reads will be considered long reads such as PacBio or Oxford Nanopore Technologies (ONT). It needs at least one of the two types of files, with a maximum of 1 assembly and 2 reads files per sample. It can also take one annotated genome `.gbk` file per sample for `--one_to_one` comparisons, using each `.gbk` as reference for variant calling.

> [!IMPORTANT]
> Selected **pipeline depends on user input**. Every part is available for each input type except the detection of truncated genes caused by big reordenations, acquired resistance genes and MLST identification, which require an assembly. It is **recommended to provide reads and an assembly** for a more in-depth analysis!
>
> ARVIA gives an idea of coverage/depth of each gene, but **additional quality control of reads or of your assemblies with CheckM/CheckM2 is highly recommended**, as they will tell you how complete/contaminated your genome is.


### Input YAML convention

In order to use `--input_yaml` generate a YAML file with the following structure, where keys are unique sample_ids, containing at least one list named `reads` or `assembly` and an optional list named `gbk` (if you want to use `--one_to_one`) with their corresponding files (path can be relative from where ARVIA is executed):

```yaml
# -- Input template --
# SAMPLE_10: # <- Will be used as ID (file paths dont need to include the ID)
#   reads:
#     - path/to/blablabla_R1.fastq.gz
#     - path/to/blablabla_R2.fastq.gz
#   assembly:
#     - path/to/blablabla.fasta
#   gbk: # -> only if you want to do one to one comparisons between samples using this as reference
#     - path/to/blablabla.gbk

# -- Your samples --
# Complete example with paired reads, assembly and gbk (gbk for --one_to_one)
ARGA00024:
  reads:
    - input/ARGA00024_R2.fastq.gz
    - input/ARGA00024_R1.fastq.gz
  assembly:
    - input/ARGA00024.fasta
  gbk:
    - input/ARGA00024.gbk

# Example with only single-end long reads
# you dont need to specify assembly key if you dont have it
ARGA00461:
  reads:
    - input/ARGA00461.fastq.gz

# Example with only assembly
# you dont need to specify reads key if you dont have it
ARGA00461-a:
  assembly:
    - input/ARGA00461.fasta
```

You could also **create the YAML programatically**. Lets say you have a table `metadata.tsv`, your sample ids are in the column `sample_id` and your input files follow paths you know, the following is an example with Python:

```python
import pandas as pd
import glob
import yaml

# A tab separated table with
metadata_file = "metadata.tsv"

# The file where the YAML will be saved
input_yaml_file = "input.yaml"

# Read metadata and extract a list with your sample ids
df = pd.read_csv(metadata_file, sep="\t")
sample_ids = list(df["sample_id"].unique())

# Create a dictionary following the yaml format
d = {
    i: {
        "reads": sorted(glob.glob(f"path/to/reads/{i}/{i}_R*.fastq.gz")), # make sure both elements are lists
        "assembly": glob.glob(f"path/to/assemblies/{i}/{i}_assembly.fasta"), # make sure both elements are lists
    } for i in sample_ids
}

# Save the dictionary to YAML
with open(input_yaml_file, "w") as out_handle:
    for biosample_id, values in d.items():
        out_handle.write(f"# ---- {biosample_id} ----\n")  # section title
        yaml.dump(
            {f"{biosample_id}": values}, 
            out_handle, default_flow_style=False, sort_keys=False
        )
        out_handle.write(f"\n")
```


### File naming convention

You can see the convention expected for `--reads`, `--assemblies` and `--gbks` with `--help`:

```sh
-r, --reads path [path ...]         Input reads files. Can be paired-end or single-end and must follow one of these
                                    structures: '{sample_id}.fastq.gz' / '{sample_id}_R[1,2].fastq.gz' /
                                    '{sample_id}_[1,2].fastq.gz' / '{sample_id}_S\d+_L\d+_R[1,2]_\d+.fastq.gz'
-a, --assemblies path [path ...]    Input assembly files. Must follow one of these structures:
                                    '{sample_id}.{fasta,fna,fa,fas}' (default: None)
-g, --gbks path [path ...]          Input annotated assembly files in GBK format. Only used in 1 vs 1 comparisons 
                                    if given --one_to_one. Must follow one of these structures: '{sample_id}.{gbk}' (default: None)
```

## Output

ARVIA's main output in `--output_folder` is the following:
- **`ARVIA.xlsx`**: Formatted excel table containing **pipeline used, mlst, mlst model, PDC, acquired antibiotic resistance genes, variant calling and coverage of relevant chromosomic genes** ([example available here](https://github.com/pablo-aja-macaya/ARVIA/raw/refs/heads/main/arvia/data/examples/example_result.xlsx)). 
  - **Color** appears when a gene has **low coverage**, or if there are **structurally relevant mutations (*, ?, fs, frameshift, possible_missing_feature...)**. 
  - **Acquired resistance genes** can have suffixes like `*` (high identity and coverage, mutated) or `?` (high identity with low coverage, can indicate split protein). 
  -  In **MLST** if not all alleles match a specific profile the closest one will be signalled with `!`.
  - **Mixed positions** appear with `(Fails QC: {mut_prot}%, {depth}x)`.
  - **Possible SNV polymorphisms** appear as `(POLY)`.
  - Variant calling using **closest oprD** is available in section `PA0958-alt`.
  - **Gene coverage** appears for each gene as `NZC={nzc}% Depth={depth}x`, where NZC is non-zero coverage percentage (percentage of the gene that is covered at least once).

<p align="center">
  <img src="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/examples/example_arvia_result.png" style='width: 100%; object-fit: contain' >
</p>

- **`ARVIA_sc.xlsx`**: Formatted table containing a more **fine grained snippy comparison (SC) between samples** ([example available here](https://github.com/pablo-aja-macaya/ARVIA/raw/refs/heads/main/arvia/data/examples/example_result_sc.xlsx)). 
  - **Only snippy module's results are included: default snippy, possible missing features, mixed positions and polymorphisms**. Thus, variant calling using BLAST, closest oprD reference, acquired resistance genes or mlst is **not displayed here**. 
  - **Easier to detect differences** between sample mutations.
  - In this case **color** displays mutation quality.


<p align="center">
  <img src="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/examples/example_arvia_sc_result.png" style='width: 100%; object-fit: contain' >
</p>


- **`one_to_one/ref_{ID}.tsv`** : If given `--one_to_one` and at least a `.gbk` file for one sample ARVIA will run the variant calling module of each sample against the given references, in the same format as `ARVIA_sc.xlsx`. You will also find `mutation_count.tsv` in the same folder, where the distance of each sample (column) to each reference (row) is shown in the form of total variants (including SNVs, indels, synonymous variants...).


Other output in `--output_folder`:
- **`ARVIA_wide.tsv`**: Same as `ARVIA.xlsx` but in tsv format, more easily processable by other tools.
- **`ARVIA_long.tsv`**: Same as `ARVIA.xlsx` but in tsv and long format, more easily processable by other tools.
- **`results_per_sample/{ID}/`**: Folder with results from each sample
  - **`{ID}_amrfinderplus.tsv`**: Acquired resistance genes detected by amrfinderplus (only with assembly!).
  - **`{ID}_mlst.tsv`**: Closest MLST detected, important when assembly is not fully complete (only with assembly!). The model used with its allele combinations separated in all, new, partial, missing and mixed are also available. 
  - **`{ID}_paeruginosa_assembly_truncations.tsv`**: Variant calling using BLAST and the assembly. Detects mutations at nucleotide level, indels and big reordenations, including if the gene is split in multiple contigs. This helps in cases where large phages are inserted into the chromosome and genes break apart, where snippy would not be able to detect the change.
  - **`{ID}_paeruginosa_gene_coverage.tsv`**: Coverage of each gene.
  - **`{ID}_paeruginosa_muts.tsv`**: All mutations reported by snippy without any filters.
  - **`{ID}_paeruginosa_muts_filtered.tsv`**: All non-synonymous mutations reported by snippy in relevant genes related to antibiotic resistance.
  - **`{ID}_paeruginosa_muts_filtered.html`**: IGV-report of filtered mutations reported by snippy in relevant genes. Click on table entries to go to their position. Two types of entries are avilable, the locus itself with the number of mutations detected by snippy (e.g. `PA0931 - pirA - ferric enterobactin receptor PirA (1 non-synonymous reported mutations)`) and the mutations themselves starting with `-->` (e.g. `-->PA0931_missense_variant_c.1108G>A_p.Ala370Thr_(A:29_G:0)`). Only the surrounding area is loaded.
  - **`{ID}_selected_oprd_ref.txt`**: Closest oprD reference selected.
  - **`{ID}_selected_oprd_muts.tsv`**: Mutations detected in closest oprD reference. 
- `temp/`: Folder with intermediate steps

A full pipeline test of 125 P. aeruginosa samples with paired-end Illumina reads and assemblies takes around 42:57 minutes (<1 minute per sample) in a computer with 64 threads and 128 Gb of RAM.

## Rationale behind additional steps in variant calling

Normal variant calling with snippy works well enough for most cases, but there are certain instances where it might not be enough. Thats why the extra steps were implemented in ARVIA, with the rationale behind each of them in this section.

### Mixed positions

Mixed/heterogenous mutations (e.g. where 50% of reads indicate C and 50% indicate T) can occur due to various reasons: 1) more than one clone was sequenced in same sample; 2) Gene has multiple copies; 3) Low quality reads. Thus, it is important to detect them, as we could be missing antibiotic resistance determinants. However, these kind of variants are only seen if reads are used. 

In the following image we can see an example of mixed position, where the mutation occurs in 66% of reads:

<p align="center">
  <img src="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/examples/example_mixed_position.png" style='width: 70%; object-fit: contain' >
</p>


### Low coverage genes and possible missing features

Some genes influence antibiotic resistance when they are inactivated. One method is the loss of these genes due to chromosomic rearrengments (others include frameshifts, indels and SNVs). Thus, ARVIA detects which genes have low coverage and indicates them as `possible_missing_features`. An example can be seen below:

<p align="center">
  <img src="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/examples/example_missing_feature.png" style='width: 100%; object-fit: contain' >
</p>

### Chromosomic rearrengments

In some cases, large chromosomic rearrengments, such as the insertion of phages, can also inactivate genes that influence antibiotic resistance while keeping full apparent coverage of the gene, as the genes are split but their parts are mantained in the genome. Snippy does not detect these type of variants. 

For example, in the following sample we can see nalC with no apparent structural mutation:

<p align="center">
  <img src="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/examples/example_big_insertion.png" style='width: 100%; object-fit: contain'>
</p>

However, if we focus on the position marked by the red arrow and activate soft clipped sections (parts of reads that do not align to the selected region) we can see that these reads align somewhere else:

<p align="center">
  <img src="https://github.com/pablo-aja-macaya/ARVIA/raw/main/arvia/data/examples/example_big_insertion_with_soft_clips.png" style='width: 100%; object-fit: contain' >
</p>


Following the path of those reads results in finding a large phage (~40kbp) inserted inside nalC, breaking the gene and causing increased antibiotic resistance. Thus, ARVIA's BLAST variant calling method can be used to detect these kind of variants through the use of assemblies.


### Using closest oprD

The porin oprD is highly variable and very implicated in antibiotic resistance. The high variablity can cause snippy to miss important mutations (frameshifts, indels) if the reference used (by default PAO1) is phylogenetically distant. That's why ARVIA performs additional variant calling with the closest reference among the following: F23197_6110 (PGD60817628), FRD1_2621 (PGD23123403), LESB58_125 (PGD252821), MTB-1_210 (PGD11780772) and PAO1 (PA0958). This result will appear in `ARVIA.xlsx` in section `PA0958-alt`.

<!-- UCBPP-PA14_109 -->

### Possible polymorphisms

Sometimes mutations don't have any effect on antibiotic resistance and are just normal part of *P. aeruginosa* lineages. An article by [Cortes-Lara et al. (2021)](https://doi.org/10.1016/j.cmi.2021.05.011) defined possible polymorphisms in multiple genes, out of which ARVIA extracts SNV substitutions and indicates them with suffix `(POLY)`. This allows researchers to look out for the actual relevant mutations without checking each one.



## Full command list 
Full command list available with `arvia --help`. Here is `arvia run -h`:

```sh
Usage: arvia run [-i path] [-r path [path ...]] [-a path [path ...]] [-g path [path ...]] [-o path] [--one_to_one] [-d int] [-s int]
                 [-c int] [-p] [--use_conda] [--barcodes str [str ...]] [--draw_wf str] [-h]

ARVIA: Antibiotic Resistance Variant Identifier for Pseudomonas aeruginosa

Input/Output:
  -i, --input_yaml path                 Input files from a YAML. Each key is a sample_id containing two lists of paths with keys
                                        'reads' and 'assembly' (default: None)
  -r, --reads path [path ...]           Input reads files. Can be paired-end or single-end and must follow one of these
                                        structures: '{sample_id}.fastq.gz' / '{sample_id}_R[1,2].fastq.gz' /
                                        '{sample_id}_[1,2].fastq.gz' / '{sample_id}_S\d+_L\d+_R[1,2]_\d+.fastq.gz' (default:
                                        None)
  -a, --assemblies path [path ...]      Input assembly files. Must follow one of these structures:
                                        '{sample_id}.{fasta,fna,fa,fas}' (default: None)
  -g, --gbks path [path ...]            Input annotated assembly files in GBK format. Only used in 1 vs 1 comparisons if given
                                        --one_to_one. Must follow one of these structures: '{sample_id}.{gbk}' (default: None)
  -o, --output_folder path              Output folder (default: ./arvia)

Additional Arguments:
  --one_to_one                          Compare input samples between themselves using the assembly/annotated assembly of each
                                        one as reference. At least one assembly is neccessary. (default: False)
  -d, --min_depth int                   Minimum depth for mutation to pass (--mincov in snippy) (default: 5)
  -s, --maxsoft int                     Maximum soft clipping allowed (--maxsoft in snippy) (default: 1000)
  -c, --cores int                       Number of cores (default is available cores - 1) (default: 63)
  -p, --previsualize                    Previsualize pipeline to see if everything is as expected (default: False)
  --use_conda                           If True, use conda environment specified by snakefile (default: False)
  --barcodes str [str ...]              Space separated list of sample IDs. Only these samples will be processed (default: None)
  --draw_wf str                         Draw pipeline to this path (PDF) (default: None)
  -h, --help                            show this help message and exit
```



## Citation


### Tool
A button named **"Cite this repository" is available in a citation widget on the sidebar**.

You can also cite ARVIA with the following:

```
Aja-Macaya, P. (2025). ARVIA [Computer software]. https://github.com/pablo-aja-macaya/ARVIA
```

Or:

```
@software{
  Aja-Macaya_ARVIA_2025,
  author = {Aja-Macaya, Pablo},
  month = aug,
  title = {{ARVIA}},
  year = {2025},
  url = {https://github.com/pablo-aja-macaya/ARVIA}
}
```

### Other
Database from which PAO1 genome and oprD gene information are retrieved, **[Pseudomonas.com](https://www.pseudomonas.com)**:

```
Winsor GL, Griffiths EJ, Lo R, Dhillon BK, Shay JA, Brinkman FS (2016). Enhanced annotations and features for comparing thousands of Pseudomonas genomes in the Pseudomonas genome database. Nucleic Acids Res. (2016) doi: 10.1093/nar/gkv1227 (Database issue). Pubmed: 26578582
```

*P. aeruginosa* polymorphisms not related to antibiotic resistance by [Cortes-Lara et al. (2021)](https://doi.org/10.1016/j.cmi.2021.05.011):

```
Cortes-Lara, S., del Barrio-Tofiño, E., López-Causapé, C., Oliver, A., Martínez-Martínez, L., Bou, G., ... & Oteo, J. (2021). Predicting Pseudomonas aeruginosa susceptibility phenotypes from whole genome sequence resistome analysis. *Clinical Microbiology and Infection*, 27(11), 1631-1637.
```

## Development

### Upload to PyPi

```sh
cd ARVIA/
conda activate twine

# Create build dist
python -m build

# Upload to TestPyPi with twine
twine upload --repository pypi dist/*

# Now you can pip install
pip install arvia # -i https://test.pypi.org/simple/ 

```

### Upload/update to bioconda

Update conda-recipes
```sh
# Make sure our master is up to date with Bioconda
git checkout master
git pull upstream master
git push origin master

# Create and checkout a new branch for our work
git checkout -b update_arvia
```

Test recipe
```sh
cd bioconda-recipes
conda activate bioconda

# optional linting
bioconda-utils lint --git-range master --packages arvia

# build and test
bioconda-utils build --docker --mulled-test --git-range master --packages arvia

```


<!-- [hola][home] -->
<!-- 
# using this reference links slows down the page dont know why
[home]: https://github.com/pablo-aja-macaya/ARVIA
[usage]: https://github.com/Pablo-Aja-Macaya/ARVIA#usage
[installation]: https://github.com/Pablo-Aja-Macaya/ARVIA#installation
[input]: https://github.com/Pablo-Aja-Macaya/ARVIA#input
[input-yaml-convention]: https://github.com/Pablo-Aja-Macaya/ARVIA#input-yaml-convention
[file-naming-convention]: https://github.com/Pablo-Aja-Macaya/ARVIA#file-naming-convention
[output]: https://github.com/Pablo-Aja-Macaya/ARVIA#output
[rationale-behind-additional-steps-in-variant-calling]: https://github.com/Pablo-Aja-Macaya/ARVIA#rationale-behind-additional-steps-in-variant-calling
[full-command-list]: https://github.com/Pablo-Aja-Macaya/ARVIA#full-command-list
[test]: https://github.com/Pablo-Aja-Macaya/ARVIA#test
[citation]: https://github.com/Pablo-Aja-Macaya/ARVIA#citation -->





<!-- 
[home]: https://github.com/pablo-aja-macaya/ARVIA
[installation]: https://github.com/Pablo-Aja-Macaya/ARVIA/#installation
-->

 


<!-- 
- [] Herramienta variant calling p. aeruginosa    
    - Funciones:
        - [X] Input: paired reads, long reads or assembly
        - [] To-do    
            - [X] Doing arvia --version does not return version, it just shows help
            - [] in xlsx output check it looks good on every platform (breaks like \n dont work in windows)
            - [] igvreport add info on mutations (fails qc, poly, etc)
            - [] in sc table it would be cool to add mlst if available and sort columns by that first
            - [] pmf parameter 
            - [X] En ARGA00457 PA0004 GyrB sólo aparece "808" como mutación
            - [X] add parameters to command line (min_depth, maxsoft)
            - [X] tabla comparativa a lo largo
            - [X] arreglar el print de check_truncations en ciertos casos, ejemplos:
              - [X] ARGA00097 PA0929 pirR
              - [X] ARGA00457 PA0427 oprM
              - [X] ARGA00581 PA0929 pirR
              - [X] ARGA00534 PA0929 pirR
              - [X] ARGA00032 PA0424 mexR
              - [X] ARGA00086 PA0424 mexR
              - [X] ARGA00396 PA2057 sppR
              - [X] ARGA00104 PA3721 nalC
              - [X] ARGA00104 PA4522 ampD
              - [X] ARGA00395 PA4109 ampR
            - [nah] add approximate depth if using reads
            - [nah] hideable snakemake progress bar?
            - [X] use links in readme that work on pypi (relative links dont work)
            - [X] actualizar imagen pipeline
            - [X] automatic reference download (included)
            - [X] orden de columnas en xlsx que sea assembly, snippy, coverage
            - [X] informe html de igvvariant
            - [X] añadir funcion para incrementar cores por rule si hay menos muestras
            - [X] cuando los genes no encajen a la perfeción (tipo blaPDC* o blaPDC?) poner el alelo más cercano
              - Ej: blaPDC* -> blaPDC-30*; blaPDC? -> blaPDC-30?
            - [X] conseguir mlst más cercano si no tiene uno definido y poner el !
            - [X] tests
            - [X] amrfinder
            - [X] mlst
            - [X] en tabla final si no ha habido ningún cambio en un gen este no aparece, arreglar y meterlo sí o sí aunque esté vacío
            - [X] quitar lo de func en la tabla de parámetros no sé qué es
            - [X] en tabla resumen si se da assembly pero no detecta la PDC lo pone como si no se le hubiese dado ensamblaje, arreglar
            - [X] añadir modelo de mlst
            - [X] añadir mlst más cercano
            - [X] in results_per_sample
                - [X] format blast table (add header at least)
                - [X] add original muts without filters

      # Cambios para poner 1 vs 1
      - [X] recibir genomas anotados
          - --gbk *.gbk
          - Añadir gbk en yaml
          - Dejar que se pueda hacer sólo con ensamblaje? Sólo se verían cuántas mutaciones tienen pero no el efecto.
          - Si alguna no tiene ensamblaje avisar, pero hacer la comparación usando los que sí tienen?
      - [X] Añadir comando de comparación bool: --one_to_one
      - [] Se pueden usar ensamblajes o lecturas (habría que indicar cuál se ha usado?)
      - [X] Añadir rules de 1vs1
      - [X] Añadir resumen en tablas, idealmente un excel con una sheet por cada referencia 

      # Poner para cualquier referencia ?
      - [] Parametrizar gbk
      - [] Parametrizar loci de interes
      - [] Quitar el paeruginosa=TRUE (sólo usaría los genes de la PAO)
      - [] Quitar lo de oprD
      - [] Añadir más modelos de mlst
      - [] Revisar si hay alguna cosa más exclusiva de pseudomonas

    - Dependencies:
        - python
        - snakemake
        - snippy
        - bwa
        - samtools
        - makeblastdb y blast
        - minimap2 for long reads?
        - amrfinder
        - mlst
    - Paper: https://academic.oup.com/bioinformatics/pages/instructions_for_authors
        - [] paper
        - [] cover letter
        - [] Title page
        - [] .tif files (1200 d.p.i. for line drawings and 350 d.p.i. for colour and half-tone artwork). For online submission, please also prepare a second version of your figures at low-resolution for use in the review process; these versions of the figures can be saved in .jpg, .gif, .tif or .eps 
    - Nombres
        ARVIA: Antibiotic Resistance Variant Identifier for Pseudomonas aeruginosa
        PAVRA: Pseudomonas aeruginosa Variants and Resistance Analyzer
        PAVCRA: Pseudomonas Aeruginosa Variant Calling Resistance Analysis
        PARVI: P. Aeruginosa Resistance Variant Inspector
-->
