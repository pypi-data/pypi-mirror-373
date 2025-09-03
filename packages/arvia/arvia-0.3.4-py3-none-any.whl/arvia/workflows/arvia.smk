import pandas as pd
import glob
import json
import re
import traceback
from pathlib import Path
import logging
from snakemake.logging import logger
import warnings
import datetime
from pprint import pprint

from arvia.arvia import ARVIA_DIR
from arvia.utils.process_user_input import associate_user_input_files, input_file_dict_from_yaml, check_input_file_dict_and_decide_pipeline, input_files_dict_to_df
from arvia.utils.aeruginosa_snippy import filter_snippy_result
from arvia.utils.process_mlst import process_mlst_result
from arvia.utils.process_amrfinder import process_amrfinder_result
from arvia.utils.console_log import CONSOLE_STDOUT, CONSOLE_STDERR, log_error_and_raise, rich_display_dataframe
from arvia.utils.annotation_extraction import get_proteins_from_gbk
from arvia.utils.combine_snippy_results import get_default_snippy_combination, paeruginosa_combine_all_mutational_res, create_merged_xlsx_result
from arvia.utils.aeruginosa_truncations import check_truncations
from arvia.utils.aeruginosa_truncations import BLAST_OUTFMT
from arvia.utils.local_paths import OPRD_NUCL, OPRD_CONFIG
from arvia.utils.local_paths import PAERUGINOSA_GENOME_GBK#, PAERUGINOSA_GENOME_GFF, PAERUGINOSA_GENOME_FNA
from arvia.utils.local_paths import CONDA_ENVS
from arvia.utils.snakemake_common import get_snakemake_threads
from arvia.utils.prepare_files_for_igvreport import process_gff_and_muts
from arvia.utils.process_snippy_one_to_one import process_snippy_one_to_one

warnings.simplefilter(action='ignore', category=FutureWarning) # remove warning from pandas
warnings.simplefilter(action='ignore', category=UserWarning) # remove warning from deprecated package in setuptools
# ARVIA_DIR = arvia.__file__.replace("/__init__.py", "")  # get install directory of bactasys
DATETIME_OF_CALL = datetime.datetime.now()


#==================#
# ---- Logger ---- #
#==================#
if config:
    snakemake_console_log = config.get("snakemake_console_log")

    # # ---- Get parameters ----
    # # Input
    # SHORT_READS_INPUT = config["sr_folder"]
    # LONG_READS_INPUT = config["lr_folder"]
    # # READ_TYPE = ? # TODO: this

    # # Output
    # BASE_FOLDER = config["output_folder"]

    # # Filter barcodes
    # USER_BARCODES = config.get("barcodes")

# ---- Send snakemake log to custom file to parse with custom log ----
if snakemake_console_log is not None:
    handler = logging.FileHandler(snakemake_console_log, mode='a')
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    try:
        # For old snakemake versions
        logger.set_stream_handler(handler)
    except Exception as e:
        # For new snakemake versions
        from arvia.utils.snakemake_logger import LogHandler

        logger.handlers = [LogHandler(None,None)] 

#========================#
# ---- Input set-up ---- #
#========================#
# Generate dictionary INPUT_FILES depending if user gave a yaml (--input_yaml) or two list of files (--reads and --assemblies)
if config.get("input_yaml"):
    INPUT_FILES = input_file_dict_from_yaml(config.get("input_yaml"))
else:
    INPUT_FILES = associate_user_input_files(config)

# Check input and decide pipelines
INPUT_FILES = check_input_file_dict_and_decide_pipeline(INPUT_FILES)

# Filter samples if --barcodes was used
if config.get("barcodes"):
    bcs_without_files = [i for i in config["barcodes"] if i not in list(INPUT_FILES.keys())]
    assert len(bcs_without_files)==0, f"At least a barcode given with parameter --barcodes is not present in input files' expected IDs ({bcs_without_files}). \nExpected at least one of: {list(INPUT_FILES.keys())}\n\nAre you sure you gave the corred IDs?\n"
    INPUT_FILES = {k:v for k,v in INPUT_FILES.items() if k in config["barcodes"]}


#==========================#
# ---- Output folders ---- #
#==========================#

PIPELINE_OUTPUT = config["output_folder"]
PIPELINE_WD_OUTPUT = f"{PIPELINE_OUTPUT}/temp"

# Input
# GET_ASSEMBLIES_OUTPUT = f"{PIPELINE_WD_OUTPUT}/00_input_assemblies"
# GET_READS_OUTPUT = f"{PIPELINE_WD_OUTPUT}/00_input_reads"

# General snippy
PAERUGINOSA_MUTS_OUTPUT = f"{PIPELINE_WD_OUTPUT}/variant_calling/run"
PAERUGINOSA_MUTS_PROCESS_OUTPUT = f"{PIPELINE_WD_OUTPUT}/variant_calling/process"

# OprD
PAERUGINOSA_OPRD_OUTPUT = f"{PIPELINE_WD_OUTPUT}/oprd"
ALIGN_OPRD = f"{PAERUGINOSA_OPRD_OUTPUT}/01_align"
DECIDE_BEST_OPRD = f"{PAERUGINOSA_OPRD_OUTPUT}/02_decide"
SNIPPY_OPRD = f"{PAERUGINOSA_OPRD_OUTPUT}/03_snippy"

# Truncated genes
PAERUGINOSA_TRUNC_OUTPUT = f"{PIPELINE_WD_OUTPUT}/truncations"
EXTRACT_PAERUGINOSA_REF_GENES_OUTPUT = f"{PAERUGINOSA_TRUNC_OUTPUT}/01_extract_ref_genes"
MAKEBLASTDB_FROM_ASSEMBLY_OUTPUT = f"{PAERUGINOSA_TRUNC_OUTPUT}/02_blastdb"
BLAST_PAERUGINOSA_GENES_TO_ASSEMBLY_OUTPUT = f"{PAERUGINOSA_TRUNC_OUTPUT}/03_blast"
PROCESS_BLAST_TRUNCATIONS= f"{PAERUGINOSA_TRUNC_OUTPUT}/04_process"

# Other
SNIPPY_ONE_TO_ONE_RUN = f"{PIPELINE_WD_OUTPUT}/one_to_one/run"
SNIPPY_ONE_TO_ONE = f"{PIPELINE_WD_OUTPUT}/one_to_one"
MLST_OUTPUT = f"{PIPELINE_WD_OUTPUT}/mlst/run"
MLST_PROCESS_OUTPUT = f"{PIPELINE_WD_OUTPUT}/mlst/process"
AMRFINDER_OUTPUT = f"{PIPELINE_WD_OUTPUT}/amrfinder/run"
AMRFINDER_PROCESS_OUTPUT = f"{PIPELINE_WD_OUTPUT}/amrfinder/process"
IGV_REPORTS_OUTPUT = f"{PIPELINE_WD_OUTPUT}/igvreports"

# Results
RESULTS_PER_SAMPLE_OUTPUT = f"{PIPELINE_OUTPUT}/results_per_sample"
SNIPPY_ONE_TO_ONE_RES = f"{PIPELINE_OUTPUT}/one_to_one"
RESULTS_MERGED_OUTPUT = f"{PIPELINE_WD_OUTPUT}/results_merged"
XLSX_WIDE_TABLE = f"{PIPELINE_OUTPUT}/ARVIA.xlsx"

#==================#
# ---- Params ---- #
#==================#
CLEAN_SNIPPY_FOLDERS = False

#================#
# --- Other ---- #
#================#
# Save file manifest
file_manifest_df = input_files_dict_to_df(INPUT_FILES)
shell(f"mkdir -p {PIPELINE_OUTPUT}/logs")
file_manifest_df.to_csv(f"{PIPELINE_OUTPUT}/logs/file_manifest.tsv", sep="\t", index=None)

onstart:
    # Print to screen file manifest
    rich_display_dataframe(file_manifest_df, "File manifest")
    
    # Delete previous result if it exists
    if Path(XLSX_WIDE_TABLE).exists():
        shell(f"rm {XLSX_WIDE_TABLE}")
        shell(f"rm {Path(XLSX_WIDE_TABLE).parent}/{Path(XLSX_WIDE_TABLE).stem}_wide.tsv")
        shell(f"rm {Path(XLSX_WIDE_TABLE).parent}/{Path(XLSX_WIDE_TABLE).stem}_long.tsv")
        shell(f"rm {Path(XLSX_WIDE_TABLE).parent}/{Path(XLSX_WIDE_TABLE).stem}_sc.xlsx")

# shell(f"conda env export > {PIPELINE_OUTPUT}/logs/environment.yml") # TODO: decide if this stays or not (can take a bit of time to export environment)

#========================================#
# --------------- Rules ---------------- #
#========================================#

####################
# ---- Common ---- #
####################
def get_if_use_assembly_or_reads(wc, bc):
    bc_reads_type = INPUT_FILES[bc]["reads_type"]
    return bc_reads_type if bc_reads_type else "assembly"

def get_input_assembly(wc, bc):
    return INPUT_FILES[bc]["assembly"]

def get_input_reads(wc, bc):
    return INPUT_FILES[bc]["reads"]

def get_input_gbk(wc, bc):
    return INPUT_FILES[bc]["gbk"]

rule snippy:
    input:
        assembly="",
        reads=[],
        ref_gbk=""
    output:
        folder=directory(Path("folder")),
        res=Path(".tab"),
        res_with_het=Path("snps.nofilt.tab"),
        gene_coverage=Path(".tsv"),
        bam=temp(Path(".bam")),
        ref_gff=temp(Path("reference/ref.gff")),
        ref_fna=temp(Path("reference/ref.fa")),
    params:
        selected_input=None, # "paired_end" | "single_end" | "assembly",
        min_depth=config.get("min_depth", 5),
        maxsoft=config.get("maxsoft", 1000),
        arvia_dir=ARVIA_DIR,
        cleanup=CLEAN_SNIPPY_FOLDERS,
    threads: 5
    conda:
        CONDA_ENVS["arvia"]
    log:
        Path("", "arvia.log")
    shell:
        """
        (
        if [[ {params.selected_input} == "paired_end" ]]; then
            reads=({input.reads})
            snippy --R1 ${{reads[0]}} --R2 ${{reads[1]}} --ref {input.ref_gbk} --mincov {params.min_depth} --maxsoft {params.maxsoft} --outdir {output.folder} --cpus {threads} --quiet --force

        elif [[ {params.selected_input} == "single_end" ]]; then
            snippy --se {input.reads} --ref {input.ref_gbk} --mincov {params.min_depth} --maxsoft {params.maxsoft} --outdir {output.folder} --cpus {threads} --quiet --force

        elif [[ {params.selected_input} == "assembly" ]]; then
            snippy --ctgs {input.assembly} --ref {input.ref_gbk} --mincov {params.min_depth} --maxsoft {params.maxsoft} --outdir {output.folder} --cpus {threads} --quiet --force
        else
            exit 1
        fi

        # Run fixed vcf-to-tab script
        {params.arvia_dir}/scripts/snippy-vcf_to_tab --ref {output.folder}/reference/ref.fa --gff {output.folder}/reference/ref.gff --vcf {output.folder}/snps.vcf > {output.folder}/snps.tab

        # ---- Get mixed variants (no filter) ----
        # Difference: quitar el FMT/GT="1/1" del bcftools view
        cd {output.folder}
        bcftools view --include 'QUAL>=100 && FMT/DP>=5 && (FMT/AO)/(FMT/DP)>=0.2' snps.raw.vcf  | vt normalize -r reference/ref.fa - | bcftools annotate --remove '^INFO/TYPE,^INFO/DP,^INFO/RO,^INFO/AO,^INFO/AB,^FORMAT/GT,^FORMAT/DP,^FORMAT/RO,^FORMAT/AO,^FORMAT/QR,^FORMAT/QA,^FORMAT/GL' > snps.nofilt.vcf 2>> snps.log
        snpEff ann -noLog -noStats -no-downstream -no-upstream -no-utr -c reference/snpeff.config -dataDir . ref snps.nofilt.vcf > snps.nofilt.final.vcf 2>> snps.log
        {params.arvia_dir}/scripts/snippy-vcf_to_tab --gff reference/ref.gff --ref reference/ref.fa --vcf snps.nofilt.final.vcf > snps.nofilt.tab 2>> snps.log

        # ---- Get gene coverage ----
        cd {output.folder}
        bash {params.arvia_dir}/scripts/snippy_add_missing_features.sh

        # ---- Clean up ----
        if [[ {params.cleanup} == True ]]; then
            rm {output.folder}/reference -r
            rm {output.folder}/*.bam {output.folder}/*.bai {output.folder}/*.html {output.folder}/*.gff {output.folder}/snps.subs.vcf {output.folder}/ref.fa.fai {output.folder}/*.fa
        fi
        ) &> {log}
        """

################################################
# ---- Pseudomonas aeruginosa Snippy PAO1 ---- #
################################################
use rule snippy as paeruginosa_mutations with:
    input:
        assembly=lambda wc: get_input_assembly(wc, wc.barcode),
        reads=lambda wc: get_input_reads(wc, wc.barcode),
        ref_gbk=PAERUGINOSA_GENOME_GBK,
    output:
        folder=directory(Path(PAERUGINOSA_MUTS_OUTPUT, "{barcode}")),
        res=Path(PAERUGINOSA_MUTS_OUTPUT, "{barcode}", "snps.tab"),
        res_with_het=Path(PAERUGINOSA_MUTS_OUTPUT, "{barcode}", "snps.nofilt.tab"),
        gene_coverage=Path(PAERUGINOSA_MUTS_OUTPUT, "{barcode}", "gene_coverage.tsv"),
        bam=temp(Path(PAERUGINOSA_MUTS_OUTPUT, "{barcode}", "snps.bam")),
        ref_gff=temp(Path(PAERUGINOSA_MUTS_OUTPUT, "{barcode}", "reference", "ref.gff")),
        ref_fna=temp(Path(PAERUGINOSA_MUTS_OUTPUT, "{barcode}", "reference", "ref.fa")),
    params:
        selected_input=lambda wc: get_if_use_assembly_or_reads(wc, wc.barcode), # "paired_end" | "single_end" | "assembly",
        min_depth=config.get("min_depth", 5),
        maxsoft=config.get("maxsoft", 1000),
        arvia_dir=ARVIA_DIR,
        cleanup=CLEAN_SNIPPY_FOLDERS,
    threads: get_snakemake_threads(recommended=5, samples=len(list(INPUT_FILES.keys())), available=workflow.cores)
    log:
        Path(PAERUGINOSA_MUTS_OUTPUT, "{barcode}", "arvia.log")

# def get_type_of_muts(wc, include_het_muts: bool = INLCUDE_HET_MUTS):
#     assert type(include_het_muts) == bool, f"Parameter include_het_muts is not a bool: {include_het_muts=}"
#     if include_het_muts:
#         return rules.paeruginosa_mutations.output.res_with_het
#     else:
#         return rules.paeruginosa_mutations.output.res_with

rule process_paeruginosa_mutations:
    input:
        res=rules.paeruginosa_mutations.output.res_with_het,
    output:
        folder=directory(Path(PAERUGINOSA_MUTS_PROCESS_OUTPUT, "{barcode}")),
        res=Path(PAERUGINOSA_MUTS_PROCESS_OUTPUT, "{barcode}", "{barcode}_filtered_snps.tab"),
    threads: 1
    run:
        df = filter_snippy_result(input.res, output.res)


#########################
# ---- igv-reports ---- #
#########################
rule igv_report:
    input:
        snippy_res = rules.process_paeruginosa_mutations.output.res,
        ref_gff = rules.paeruginosa_mutations.output.ref_gff,
        ref_fna = rules.paeruginosa_mutations.output.ref_fna,
        bams = rules.paeruginosa_mutations.output.bam,
    output:
        folder = directory(Path(IGV_REPORTS_OUTPUT, "{barcode}")),
        report = Path(IGV_REPORTS_OUTPUT, "{barcode}", "{barcode}.html"),
        regions_bed = temp(Path(IGV_REPORTS_OUTPUT, "{barcode}", "regions.bed")),
        mutations_bed=temp(Path(IGV_REPORTS_OUTPUT, "{barcode}", "mutations.bed")),
        json=temp(Path(IGV_REPORTS_OUTPUT, "{barcode}", "igvreports.json")),
    params:
        flanking = 500,
    threads: 1
    run:
        shell(f"mkdir -p {output.folder}")

        # Get bed format
        merged_bed, mutations_bed  = process_gff_and_muts(input.snippy_res, input.ref_gff)
        merged_bed.to_csv(output.regions_bed, sep="\t", index=None, header=None)
        mutations_bed.to_csv(output.mutations_bed, sep="\t", index=None, header=None)

        # Generate JSON for igv-reports
        igv_config = [
            {
                "name": "Snippy (NS)",
                "url": output.mutations_bed
            },
        ]
        bams = [input.bams] if type(input.bams)==str else input.bams
        igv_config += [
            {
                "name": f"Alignment {idx+1}",
                "url": f,
                "displayMode": "SQUISHED",
                "samplingDepth": 500,
                "height": 200,
            } for idx, f in enumerate(bams)
        ]
        igv_config += [
            {
                "name": "Reference GFF",
                "url": input.ref_gff
            },
        ]

        with open(output.json, "w") as fp:
            json.dump(igv_config, fp, indent=4)


        cmd = [
            f"create_report {output.regions_bed}",
            f"--fasta {input.ref_fna}",
            f"--flanking {params.flanking}",
            f"--track-config {output.json}",
            # f"--translate-sequence-track",
            f"--standalone --output {output.report}",
        ]
        cmd = ' '.join(cmd)
        shell(f"{cmd} &> {output.folder}/igvreport.log")


##########################################################
# ---- Pseudomonas aeruginosa blast reference genes ---- #
##########################################################
rule extract_paeruginosa_ref_genes:
    input:
        ref_gbk=PAERUGINOSA_GENOME_GBK,
    output:
        folder=directory(Path(EXTRACT_PAERUGINOSA_REF_GENES_OUTPUT, "genes")),
        genes_ffn=Path(EXTRACT_PAERUGINOSA_REF_GENES_OUTPUT, "genes","genes.ffn"),
        genes_faa=Path(EXTRACT_PAERUGINOSA_REF_GENES_OUTPUT, "genes","genes.faa"),
    run:
        _ = get_proteins_from_gbk(input.ref_gbk, output.genes_ffn, output_aa=False)
        _ = get_proteins_from_gbk(input.ref_gbk, output.genes_faa, output_aa=True)


rule makeblastdb_from_assembly:
    input:
        ref=lambda wc: get_input_assembly(wc, wc.barcode),
    output:
        folder=directory(Path(MAKEBLASTDB_FROM_ASSEMBLY_OUTPUT, "{barcode}")),
    params:
        blast_db="db",
        dbtype="nucl",  # nucl | prot
    conda:
        CONDA_ENVS["arvia"] # uses this but it just needs blast
    threads: get_snakemake_threads(recommended=5, samples=len(list(INPUT_FILES.keys())), available=workflow.cores)
    log:
        Path(MAKEBLASTDB_FROM_ASSEMBLY_OUTPUT, "{barcode}", "arvia.log")
    shell:
        """
        mkdir -p {output.folder}
        (
        cat {input.ref} | makeblastdb -dbtype {params.dbtype} -parse_seqids -title {output.folder} -out {output.folder}/{params.blast_db}
        ) &> {log}
        """


rule blast_paeruginosa_genes_to_assembly:
    input:
        query=rules.extract_paeruginosa_ref_genes.output.genes_ffn,
        db=rules.makeblastdb_from_assembly.output.folder,
    output:
        folder=directory(Path(BLAST_PAERUGINOSA_GENES_TO_ASSEMBLY_OUTPUT,"{barcode}")),
        res=Path(BLAST_PAERUGINOSA_GENES_TO_ASSEMBLY_OUTPUT,"{barcode}","{barcode}.tsv"),
    threads: get_snakemake_threads(recommended=5, samples=len(list(INPUT_FILES.keys())), available=workflow.cores)
    conda:
        CONDA_ENVS["arvia"]
    params:
        outfmt=BLAST_OUTFMT, 
        blast_type="blastn",
        max_target_seqs=5,
    log:
        Path(BLAST_PAERUGINOSA_GENES_TO_ASSEMBLY_OUTPUT, "{barcode}", "arvia.log")
    shell:
        """
        mkdir -p {output.folder}
        (
        {params.blast_type} -query {input.query} -out {output.res} -max_target_seqs {params.max_target_seqs} -db {input.db}/db -subject_besthit -num_threads {threads} -outfmt "{params.outfmt}"
        ) &> {log}
        """

rule process_blast_truncations:
    input:
        res = rules.blast_paeruginosa_genes_to_assembly.output.res,
    output:
        folder=directory(Path(PROCESS_BLAST_TRUNCATIONS,"{barcode}")),
        res=Path(PROCESS_BLAST_TRUNCATIONS,"{barcode}","{barcode}.tsv"),
    run:
        df = check_truncations(input.res)
        df["bc"] = wildcards.barcode
        df = df[["bc", "locus_tag", "gene", "comment"]].drop_duplicates()
        df.to_csv(output.res, sep="\t", index=None)


########################################################
# ---- Pseudomonas aeruginosa Snippy Closest oprD ---- #
########################################################
rule align_oprd:
    input:
        ref = OPRD_NUCL,
        assembly=lambda wc: get_input_assembly(wc, wc.barcode),
        reads=lambda wc: get_input_reads(wc, wc.barcode),
    output:
        folder = directory(Path(ALIGN_OPRD, "{barcode}")),
        bam = temp(Path(ALIGN_OPRD, "{barcode}", "aln.bam")),
        coverage = Path(ALIGN_OPRD, "{barcode}", "coverage.tsv"),
    params:
        selected_input=lambda wc: get_if_use_assembly_or_reads(wc, wc.barcode), # "paired_end" | "single_end" | "assembly",
    threads: get_snakemake_threads(recommended=5, samples=len(list(INPUT_FILES.keys())), available=workflow.cores)
    conda:
        CONDA_ENVS["arvia"]
    log:
        Path(ALIGN_OPRD, "{barcode}", "arvia.log")
    shell:
        """
        mkdir -p {output.folder}

        (
        # Align
        cp {input.ref} {output.folder}/ref.fasta


        if [[ {params.selected_input} == "paired_end" ]]; then
            bwa index {output.folder}/ref.fasta;     
            bwa mem -t {threads} {output.folder}/ref.fasta {input.reads} | samtools view --threads {threads} -b - | samtools sort --threads {threads} - > {output.bam} 

        elif [[ {params.selected_input} == "single_end" ]]; then
            minimap2 -a -x map-hifi -t {threads} {output.folder}/ref.fasta {input.reads} | samtools view --threads {threads} -b - | samtools sort --threads {threads} - > {output.bam} 

        elif [[ {params.selected_input} == "assembly" ]]; then
            minimap2 -a -x asm10 -t {threads} {output.folder}/ref.fasta {input.assembly} | samtools view --threads {threads} -b - | samtools sort --threads {threads} - > {output.bam} 

        else
            exit 1
        fi

        samtools index {output.bam} 

        # Decide best reference
        samtools coverage {output.bam} > {output.coverage}

        # Clean 
        rm {output.folder}/ref.fast* {output.folder}/*.bai
        ) &> {log}
        """

rule decide_best_oprd_ref:
    input:
        coverage = rules.align_oprd.output.coverage,
    output:
        folder = directory(Path(DECIDE_BEST_OPRD, "{barcode}")),
        selected_ref = temp(Path(DECIDE_BEST_OPRD, "{barcode}", "ref.gbk")),
        selected_ref_txt = Path(DECIDE_BEST_OPRD, "{barcode}", "selected_ref.txt"),
    params:
        oprd_config = OPRD_CONFIG
    run:
        df = pd.read_csv(input.coverage, sep="\t")
        df = df.sort_values(["coverage","meandepth"], ascending=False)

        locus_tag = df.iloc[0]["#rname"]
        coverage = df.iloc[0]["coverage"]
        meandepth = df.iloc[0]["meandepth"]

        strain = params.oprd_config["oprD"][locus_tag]["strain"]
        gbk = params.oprd_config["oprD"][locus_tag]["gbk"]

        # CONSOLE_STDOUT.log(f"Best match is {locus_tag} ({strain}) at {coverage}% and {int(meandepth)}x. GBK: {gbk}")
        shell("cp {gbk} {output.selected_ref}")

        with open(output.selected_ref_txt, "wt") as handle:
            handle.write(f"{wildcards.barcode}\t{locus_tag}\t{strain}\t{coverage}\t{int(meandepth)}\n")

use rule snippy as paeruginosa_oprd with:
    input:
        assembly=lambda wc: get_input_assembly(wc, wc.barcode),
        reads=lambda wc: get_input_reads(wc, wc.barcode),
        ref_gbk=rules.decide_best_oprd_ref.output.selected_ref,
    output:
        folder = directory(Path(SNIPPY_OPRD, "{barcode}")),
        res = Path(SNIPPY_OPRD, "{barcode}", "snps.tab"),
        res_with_het=Path(SNIPPY_OPRD, "{barcode}", "snps.nofilt.tab"),
        gene_coverage=Path(SNIPPY_OPRD, "{barcode}", "gene_coverage.tsv"),
        bam=temp(Path(SNIPPY_OPRD, "{barcode}", "snps.bam")),
        ref_gff=temp(Path(SNIPPY_OPRD, "{barcode}", "reference", "ref.gff")),
        ref_fna=temp(Path(SNIPPY_OPRD, "{barcode}", "reference", "ref.fa")),
    params:
        selected_input=lambda wc: get_if_use_assembly_or_reads(wc, wc.barcode), # "paired_end" | "single_end" | "assembly",
        min_depth=config.get("min_depth", 5),
        maxsoft=config.get("maxsoft", 1000),
        arvia_dir=ARVIA_DIR,
        cleanup=CLEAN_SNIPPY_FOLDERS,
    threads: get_snakemake_threads(recommended=5, samples=len(list(INPUT_FILES.keys())), available=workflow.cores)
    log:
        Path(SNIPPY_OPRD, "{barcode}", "arvia.log")

##################
# ---- MLST ---- #
##################
rule mlst:
    input:
        assembly=lambda wc: get_input_assembly(wc, wc.barcode),
    output:
        folder=directory(Path(MLST_OUTPUT, "{barcode}")),
        res=Path(MLST_OUTPUT, "{barcode}", "{barcode}.tsv"),
    params:
        mlst_scheme = "" #"paeruginosa"
    threads: get_snakemake_threads(recommended=1, samples=len(list(INPUT_FILES.keys())), available=workflow.cores)
    conda:
        CONDA_ENVS["arvia"]
    log:
        Path(MLST_OUTPUT, "{barcode}", "arvia.log")
    shell:
        """
        mkdir -p {output.folder}
        (
        mlst --threads {threads} --nopath {input.assembly} --scheme '{params.mlst_scheme}' > {output.res}
        ) &> {log}
        """

rule process_mlst:
    input:
        res=rules.mlst.output.res,
    output:
        folder=directory(Path(MLST_PROCESS_OUTPUT, "{barcode}")),
        res=Path(MLST_PROCESS_OUTPUT, "{barcode}", "{barcode}.tsv"),
    threads: 1
    run:
        # Get where mlst is installed
        mlst_tool = None
        for line in shell("which mlst", iterable=True):
            mlst_tool = line

        # Database folder relative to mlst binary 
        # should be ../../db/pubmlst
        mlst_dbs_folder = Path(Path(mlst_tool).parent.parent, "db", "pubmlst")
        assert mlst_dbs_folder.exists(), f"MLST database folder does not exist {mlst_dbs_folder=}"

        # Process mlst result
        _ = process_mlst_result(
            input_file=input.res,
            mlst_dbs_folder=mlst_dbs_folder,
            output_file=output.res
        )


#######################
# ---- AMRFinder ---- #
#######################
rule amrfinderplus:
    input:
        assembly=lambda wc: get_input_assembly(wc, wc.barcode),
    output:
        folder=directory(Path(AMRFINDER_OUTPUT, "{barcode}")),
        res=Path(AMRFINDER_OUTPUT, "{barcode}", "{barcode}.tsv"),
    threads: get_snakemake_threads(recommended=4, samples=len(list(INPUT_FILES.keys())), available=workflow.cores)
    conda:
        CONDA_ENVS["arvia"]
    log:
        Path(AMRFINDER_OUTPUT, "{barcode}", "arvia.log")
    shell:
        """
        mkdir -p {output.folder}
        (
        amrfinder -n {input.assembly} --threads {threads} -o {output.res}
        ) &> {log}
        """

rule process_amrfinderplus:
    input:
        res=rules.amrfinderplus.output.res,
    output:
        folder=directory(Path(AMRFINDER_PROCESS_OUTPUT, "{barcode}")),
        res=Path(AMRFINDER_PROCESS_OUTPUT, "{barcode}", "{barcode}.tsv"),
    threads: 1
    run:
        # Get where amrfinder_tool is installed
        amrfinder_tool = None
        for line in shell("which amrfinder", iterable=True):
            amrfinder_tool = line

        # Reference catalog relative to amrfinder binary 
        # should be in ../../share/amrfinderplus/data/latest/ReferenceGeneCatalog.txt
        amrfinder_catalog_file = Path(Path(amrfinder_tool).parent.parent, "share", "amrfinderplus", "data", "latest", "ReferenceGeneCatalog.txt")
        assert amrfinder_catalog_file.exists(), f"ReferenceGeneCatalog does not exist {amrfinder_catalog_file=}"

        # Process mlst result
        _ = process_amrfinder_result(
            input_file=input.res,
            amrfinder_catalog_file=amrfinder_catalog_file,
            output_file=output.res
        )


###############################
# ---- Snippy one to one ---- #
###############################
use rule snippy as snippy_one_to_one with:
    input:
        # ref_gbk=Path(BAKTA_OUTPUT, "{ref_barcode}", "{ref_barcode}.gbk"),
        # reads=[i.replace("{barcode}", "{query_barcode}") for i in READS_INPUT],
        assembly=lambda wc: get_input_assembly(wc, wc.query_barcode),
        reads=lambda wc: get_input_reads(wc, wc.query_barcode),
        ref_gbk=lambda wc: get_input_gbk(wc, wc.ref_barcode),
    output:
        folder = directory(Path(SNIPPY_ONE_TO_ONE_RUN, "ref_{ref_barcode}__vs__{query_barcode}")),
        res = Path(SNIPPY_ONE_TO_ONE_RUN, "ref_{ref_barcode}__vs__{query_barcode}", "snps.tab"),
        res_with_het=Path(SNIPPY_ONE_TO_ONE_RUN, "ref_{ref_barcode}__vs__{query_barcode}", "snps.nofilt.tab"),
        gene_coverage=Path(SNIPPY_ONE_TO_ONE_RUN, "ref_{ref_barcode}__vs__{query_barcode}", "gene_coverage.tsv"),
        bam=temp(Path(SNIPPY_ONE_TO_ONE_RUN, "ref_{ref_barcode}__vs__{query_barcode}", "snps.bam")),
        ref_gff=temp(Path(SNIPPY_ONE_TO_ONE_RUN, "ref_{ref_barcode}__vs__{query_barcode}", "reference", "ref.gff")),
        ref_fna=temp(Path(SNIPPY_ONE_TO_ONE_RUN, "ref_{ref_barcode}__vs__{query_barcode}", "reference", "ref.fa")),    
    params:
        selected_input=lambda wc: get_if_use_assembly_or_reads(wc, wc.query_barcode), # "paired_end" | "single_end" | "assembly",
        min_depth=config.get("min_depth", 5),
        maxsoft=config.get("maxsoft", 1000),
        arvia_dir=ARVIA_DIR,
        cleanup=CLEAN_SNIPPY_FOLDERS,
    threads: get_snakemake_threads(recommended=5, samples=len(list(INPUT_FILES.keys())), available=workflow.cores)
    conda:
        CONDA_ENVS["arvia"]
    log:
        Path(SNIPPY_ONE_TO_ONE_RUN, "ref_{ref_barcode}__vs__{query_barcode}", "arvia.log")


def get_ids_with_gbk(wc):
    ids = list(INPUT_FILES.keys())
    ids_with_gbk = [k for k,v in INPUT_FILES.items() if v.get("gbk") ]
    return ids, ids_with_gbk

def get_input_for_one_to_one(wc):
    """
    Get input for rule process_parallel_snippy
    only using samples with .gbk as reference
    """
    ids, ids_with_gbk = get_ids_with_gbk(wc)
    return expand(
        rules.snippy_one_to_one.output.folder, #Path(SNIPPY_ONE_TO_ONE, "run", "ref_{ref_barcode}__vs__{query_barcode}"), 
        ref_barcode=ids_with_gbk,
        query_barcode=ids
    )

rule process_snippy_one_to_one:
    input:
        folders=lambda wc: get_input_for_one_to_one(wc)
    output:
        folder = directory(SNIPPY_ONE_TO_ONE_RES),
        mutation_count = Path(SNIPPY_ONE_TO_ONE_RES, "mutation_count.tsv"),
    run:
        shell("mkdir -p {output.folder}")
        ids, ids_with_gbk = get_ids_with_gbk(wildcards)

        # Get mutation counts
        one_to_one_folder = list(set([str(Path(i).parent) for i in input.folders]))
        assert len(one_to_one_folder)==1, f"Unexpected list length: {one_to_one_folder}"
        one_to_one_folder = one_to_one_folder[0]
        _ = process_snippy_one_to_one(
            one_to_one_folder, 
            output.mutation_count, 
            ids_with_gbk, 
            ids
        )

        # Combine 
        # Default results with no truncation info or oprd
        # Rows are mutations and columns are samples
        for ref_id in ids_with_gbk:
            out_file = f"{output.folder}/ref_{ref_id}.xlsx"
            default_df, bcs = get_default_snippy_combination(
                [f"{one_to_one_folder}/ref_{ref_id}__vs__{i}/snps.nofilt.tab" for i in ids],
                out_file, 
                selected_bcs=[], 
                paeruginosa=False
            )
            default_df.to_csv(Path(Path(out_file).parent, Path(out_file).stem + ".tsv"), sep="\t", index=None)






# # ---- Get input stats ----
# rule get_estimated_coverage:
#     input:
#         reads=lambda wc: get_input_reads(wc),
#     output:
#         folder = directory(Path(ESTIMATED_COV_OUTPUT, "{barcode}")),
#         cov = Path(ESTIMATED_COV_OUTPUT, "{barcode}", "stats.tsv"),
#     params:
#         estimated_upper_genome_size_mb = 7
#         estimated_lower_genome_size_mb = 5.5
#     threads: 2
#     run:
#         shell("mkdir -p {output.folder}")
#         shell("seqkit stats -T -j {threads} {input} > {output.folder}/seqkit_stats.tsv")
#         df = pd.read_csv(f"{output.folder}/seqkit_stats.tsv", sep="\t")
#         df["bc"] = wildcards.barcode
#         df = df.groupby("bc")[["sum_len"]].sum().reset_index()
#         df["est_highest_coverage"] = df["sum_len"].apply(lambda x: int(x/(params.estimated_lower_genome_size_mb*1000000)))
#         df["est_lowest_coverage"] = df["sum_len"].apply(lambda x: int(x/(params.estimated_upper_genome_size_mb*1000000)))
#         df.to_csv(output.cov, sep="\t", index=None)

####################
# ---- Puller ---- #
####################
def decide_steps(wc):
    # use_assembly_or_reads = get_if_use_assembly_or_reads(wc)
    # bc_reads_type = INPUT_FILES[wc.barcode]["reads_type"]
    pipeline = INPUT_FILES[wc.barcode]["pipeline"] # full_pipeline | only_reads | only_assembly
    if pipeline in ["full_pipeline", "only_assembly"]:
        steps = {
            "paeruginosa_mutations": rules.paeruginosa_mutations.output.res_with_het,
            "paeruginosa_processed_mutations": rules.process_paeruginosa_mutations.output.res,
            "paeruginosa_gene_coverage": rules.paeruginosa_mutations.output.gene_coverage,
            "paeruginosa_oprd": rules.paeruginosa_oprd.output.res_with_het,
            "paeruginosa_oprd_refs": rules.decide_best_oprd_ref.output.selected_ref_txt,
            "paeruginosa_igv_report": rules.igv_report.output.report,
            "paeruginosa_assembly_truncations": rules.process_blast_truncations.output.res,
            "paeruginosa_assembly_blast": rules.blast_paeruginosa_genes_to_assembly.output.res,
            "amrfinderplus": rules.process_amrfinderplus.output.res,
            "mlst": rules.process_mlst.output.res,
        }
    elif pipeline == "only_reads":
        steps = {
            "paeruginosa_mutations": rules.paeruginosa_mutations.output.res_with_het,
            "paeruginosa_processed_mutations": rules.process_paeruginosa_mutations.output.res,
            "paeruginosa_gene_coverage": rules.paeruginosa_mutations.output.gene_coverage,
            "paeruginosa_oprd": rules.paeruginosa_oprd.output.res_with_het,
            "paeruginosa_oprd_refs": rules.decide_best_oprd_ref.output.selected_ref_txt,
            "paeruginosa_igv_report": rules.igv_report.output.report,
            # "paeruginosa_assembly_blast": NULL,
        }
    else:
        raise Exception

    # CONSOLE_STDOUT.print(steps)
    return steps

rule get_results_per_sample:
    input:
        unpack(lambda wc: decide_steps(wc))
    output:
        folder = directory(Path(RESULTS_PER_SAMPLE_OUTPUT, "{barcode}")),
    params:
        # Cant define all output files in output section as one file can be missing
        # but we place the expected paths here
        paeruginosa_mutations = Path(RESULTS_PER_SAMPLE_OUTPUT, "{barcode}", "{barcode}_paeruginosa_muts.tsv"),
        paeruginosa_processed_mutations = Path(RESULTS_PER_SAMPLE_OUTPUT, "{barcode}", "{barcode}_paeruginosa_muts_filtered.tsv"),
        paeruginosa_gene_coverage = Path(RESULTS_PER_SAMPLE_OUTPUT, "{barcode}", "{barcode}_paeruginosa_gene_coverage.tsv"),
        paeruginosa_oprd = Path(RESULTS_PER_SAMPLE_OUTPUT, "{barcode}", "{barcode}_selected_oprd_muts.tsv"),
        paeruginosa_oprd_refs = Path(RESULTS_PER_SAMPLE_OUTPUT, "{barcode}", "{barcode}_selected_oprd_ref.txt"),
        paeruginosa_igv_report = Path(RESULTS_PER_SAMPLE_OUTPUT, "{barcode}", "{barcode}_paeruginosa_muts_filtered.html"),
        paeruginosa_assembly_truncations = Path(RESULTS_PER_SAMPLE_OUTPUT, "{barcode}", "{barcode}_paeruginosa_assembly_truncations.tsv"),
        amrfinderplus = Path(RESULTS_PER_SAMPLE_OUTPUT, "{barcode}", "{barcode}_amrfinderplus.tsv"),
        mlst = Path(RESULTS_PER_SAMPLE_OUTPUT, "{barcode}", "{barcode}_mlst.tsv"),
    # log: Path(RESULTS_MERGED_OUTPUT, "arvia.log"),
    run:
        # Create folder
        shell("mkdir -p {output.folder}")
        # pprint(input.__dict__) # see contents of input_dict

        # Get input values 
        paeruginosa_mutations = input.__dict__.get("paeruginosa_mutations")
        paeruginosa_processed_mutations = input.__dict__.get("paeruginosa_processed_mutations")
        paeruginosa_gene_coverage = input.__dict__.get("paeruginosa_gene_coverage")
        paeruginosa_oprd = input.__dict__.get("paeruginosa_oprd")
        paeruginosa_oprd_refs = input.__dict__.get("paeruginosa_oprd_refs")
        paeruginosa_igv_report = input.__dict__.get("paeruginosa_igv_report")
        paeruginosa_assembly_truncations = input.__dict__.get("paeruginosa_assembly_truncations")
        amrfinderplus = input.__dict__.get("amrfinderplus")
        mlst = input.__dict__.get("mlst")

        # Assert the minimum input required
        assert paeruginosa_mutations and paeruginosa_processed_mutations and paeruginosa_gene_coverage and paeruginosa_oprd and paeruginosa_igv_report, f"One of these did not exist: {paeruginosa_mutations=}; {paeruginosa_processed_mutations=}; {paeruginosa_gene_coverage=}; {paeruginosa_oprd=}"

        # Modify names and save
        shell(f"cp {paeruginosa_mutations} {expand(params.paeruginosa_mutations, barcode=[wildcards.barcode])[0]}")
        shell(f"cp {paeruginosa_processed_mutations} {expand(params.paeruginosa_processed_mutations, barcode=[wildcards.barcode])[0]}")
        shell(f"cp {paeruginosa_gene_coverage} {expand(params.paeruginosa_gene_coverage, barcode=[wildcards.barcode])[0]}")
        shell(f"cp {paeruginosa_oprd} {expand(params.paeruginosa_oprd, barcode=[wildcards.barcode])[0]}")
        shell(f"cp {paeruginosa_oprd_refs} {expand(params.paeruginosa_oprd_refs, barcode=[wildcards.barcode])[0]}")
        shell(f"cp {paeruginosa_igv_report} {expand(params.paeruginosa_igv_report, barcode=[wildcards.barcode])[0]}")

        if paeruginosa_assembly_truncations:
            shell(f"cp {paeruginosa_assembly_truncations} {expand(params.paeruginosa_assembly_truncations, barcode=[wildcards.barcode])[0]}") # FIXME: format this table for user
            shell(f"cp {amrfinderplus} {expand(params.amrfinderplus, barcode=[wildcards.barcode])[0]}") 
            shell(f"cp {mlst} {expand(params.mlst, barcode=[wildcards.barcode])[0]}") 
            

rule merge_results:
    input:
        folder = expand(rules.get_results_per_sample.output.folder, zip, barcode=list(INPUT_FILES.keys())),
    output:
        folder = directory(Path(RESULTS_MERGED_OUTPUT)),
        default_result = Path(RESULTS_MERGED_OUTPUT, "pao1_snippy_comparison.xlsx"),
        advanced_result = Path(RESULTS_MERGED_OUTPUT, "full_wide.xlsx"),
        advanced_result_tsv = Path(RESULTS_MERGED_OUTPUT, "full_wide.tsv"),
        advanced_result_long_tsv = Path(RESULTS_MERGED_OUTPUT, "full_wide.long.tsv"),
        combined_long = Path(RESULTS_MERGED_OUTPUT, "full_long.tsv"),
    params:
        barcodes = list(INPUT_FILES.keys()),
        final_result = Path(PIPELINE_OUTPUT, "arvia_results.xlsx")
    run:
        # Default results with no truncation info or oprd
        # Rows are mutations and columns are samples
        default_df, bcs = get_default_snippy_combination(
            expand(rules.get_results_per_sample.params.paeruginosa_processed_mutations, barcode=params.barcodes), 
            output.default_result, 
            selected_bcs=params.barcodes, 
            paeruginosa=True
        )

        # Second version where
        bcs_with_assembly = [k for k,v in INPUT_FILES.items() if v["pipeline"] in ["full_pipeline", "only_assembly"]]
        bcs_without_assembly = [k for k,v in INPUT_FILES.items() if v["pipeline"] in ["only_reads"]]

        _ = paeruginosa_combine_all_mutational_res(
            default_df=default_df,
            oprd_fs=expand(rules.get_results_per_sample.params.paeruginosa_oprd, barcode=params.barcodes),
            oprd_refs_fs=expand(rules.get_results_per_sample.params.paeruginosa_oprd_refs, barcode=params.barcodes),
            gene_coverage_fs=expand(rules.get_results_per_sample.params.paeruginosa_gene_coverage, barcode=params.barcodes),
            truncation_fs=expand(rules.get_results_per_sample.params.paeruginosa_assembly_truncations, barcode=bcs_with_assembly), # not all samples will have this file (it happens if no assembly was given)
            bcs=params.barcodes,
            output_file=output.combined_long,
            bcs_without_assembly=bcs_without_assembly,
            filter_poly=False,
        )
        
        _ = create_merged_xlsx_result(
            combined_long_f=output.combined_long,
            output_file=output.advanced_result,
            input_files_dict=INPUT_FILES,
            amrfinderplus_fs=expand(rules.get_results_per_sample.params.amrfinderplus, barcode=bcs_with_assembly),
            mlst_fs=expand(rules.get_results_per_sample.params.mlst, barcode=bcs_with_assembly),
        )


CAN_ONE_TO_ONE_BE_DONE = False
if config["one_to_one"] is True:
    if len([k for k,v in INPUT_FILES.items() if v.get("gbk")])>=1:
        CAN_ONE_TO_ONE_BE_DONE = True
    else:
        raise Exception("Error: --one_to_one used but no .gbk files in input")


rule all:
    input:
        results_per_sample_folders = expand(rules.get_results_per_sample.output.folder, zip, barcode=list(INPUT_FILES.keys())),
        combined_long = rules.merge_results.output.combined_long,
        merged_advanced_result = rules.merge_results.output.advanced_result,
        _ = rules.process_snippy_one_to_one.output.folder if CAN_ONE_TO_ONE_BE_DONE else [],
    default_target: True




onsuccess:
    default_result = rules.merge_results.output.default_result
    combined_advanced_result = rules.merge_results.output.advanced_result
    combined_advanced_result_tsv = rules.merge_results.output.advanced_result_tsv
    combined_advanced_result_long_tsv = rules.merge_results.output.advanced_result_long_tsv

    shell(f"cp {combined_advanced_result} {XLSX_WIDE_TABLE}")
    shell(f"cp {combined_advanced_result_tsv} {Path(XLSX_WIDE_TABLE).parent}/{Path(XLSX_WIDE_TABLE).stem}_wide.tsv")
    shell(f"cp {combined_advanced_result_long_tsv} {Path(XLSX_WIDE_TABLE).parent}/{Path(XLSX_WIDE_TABLE).stem}_long.tsv")
    shell(f"cp {default_result} {Path(XLSX_WIDE_TABLE).parent}/{Path(XLSX_WIDE_TABLE).stem}_sc.xlsx")


