import pandas as pd
from pathlib import Path
from arvia.utils.aeruginosa_snippy import AERUGINOSA_GENES_DF, filter_snippy_result
import json


def process_gff_and_muts(snippy_muts_f: Path, ref_gff_f: Path):
    """
    Generate a bed file with gene regions and mutation regions for igv-reports
    Additionally, adapt a snippy result to igv-report and bed format
    """

    # ---- Read input ----
    gff_df = pd.read_csv(
        ref_gff_f,
        sep="\t",
        header=None,
        comment="#",
    )
    mutations_df = filter_snippy_result(snippy_muts_f)

    # ---- Save gff again without "region"  ----
    # gff_df[~gff_df[2].isin(["region"])].to_csv("/home/usuario/Proyectos/Results/ref.gff",sep="\t", header=None, index=None)

    # ---- Generate regions ----
    gff_df.columns = ["chrom", "ref", "type", "start", "end", "x", "strand", "xx", "values"]

    l = []
    for record in gff_df.to_dict("records"):
        values = {i.split("=")[0]: i.split("=")[1] for i in record["values"].split(";") if i}
        record = {**record, **values}
        l.append(record)


    gff_df = pd.DataFrame(l)
    gff_df = gff_df[gff_df["type"] == "CDS"]
    gff_df = gff_df[["chrom", "start", "end", "locus_tag", "gene", "product"]]
    gene_side_space = 50
    gff_df["start"] = gff_df["start"] - gene_side_space - 1  # add space and turn into bed 0 based position
    gff_df["end"] = gff_df["end"] + gene_side_space - 1  # add space and turn into bed 0 based position


    gff_df = gff_df[
        (gff_df["locus_tag"].isin(AERUGINOSA_GENES_DF["LOCUS_TAG"])) | (gff_df["gene"].isin(AERUGINOSA_GENES_DF["GENE"]))
    ]
    gff_df = gff_df.fillna("")


    # ---- Get mutations and transform to bed ----
    mutations_df["POS"] = mutations_df["POS"] - 1  # turn into bed 0 based position
    mutations_df["END"] = mutations_df.apply(
        lambda row: row["POS"] + len(row["REF"]) if row["EFFECT"]!="possible_missing_feature" else gff_df[gff_df["locus_tag"]==row["LOCUS_TAG"]]["end"].values[0] - gene_side_space, axis=1
    ) 

    mutations_df["value"] = "-->" + mutations_df["LOCUS_TAG"] + " " + mutations_df["EFFECT"] + " (" + mutations_df["EVIDENCE"] + ")"
    mutations_df["value"] = mutations_df["value"].str.replace(" ", "_")
    mutation_count = (
        mutations_df.value_counts("LOCUS_TAG").reset_index(name="mutation_count").rename(columns={"LOCUS_TAG": "locus_tag"})
    )
    mutations_bed = mutations_df[["CHROM", "POS", "END", "value"]]
    assert len(list(mutations_bed["CHROM"].unique())) == 1
    if list(mutations_bed["CHROM"].unique())[0] == "NC_002516":
        mutations_bed["CHROM"] = "NC_002516.2"

    # ---- Finish ----
    gff_df = pd.merge(gff_df, mutation_count, on="locus_tag", how="left")
    gff_df["mutation_count"] = gff_df["mutation_count"].fillna(0).astype(int)
    gff_df["x"] = (
        gff_df["locus_tag"]
        + " - "
        + gff_df["gene"]
        + " - "
        + gff_df["product"]
        + " ("
        + gff_df["mutation_count"].astype(str)
        + " non-synonymous reported mutations)"
    )
    gff_df = gff_df[["chrom", "start", "end", "x"]]

    # Concat positions
    merged_bed = pd.concat(
        [gff_df.rename(columns={"chrom": "CHROM", "start": "POS", "end": "END", "x": "value"}), mutations_bed]
    ).sort_values(["CHROM", "POS"])



    return merged_bed, mutations_bed 




"""
ref_fasta="/home/usuario/Proyectos/Innova/data/db/references/genomes/pseudomonas_aeruginosa/fasta/GCF_000006765.1_ASM676v1_genomic.fna"
ref_gff="/home/usuario/Proyectos/Innova/data/db/references/genomes/pseudomonas_aeruginosa/gff/GCF_000006765.1_ASM676v1_genomic.gff"
bams="/home/usuario/Proyectos/Results/tests/arvia/arvia/temp/variant_calling/run/ARGA00043/snps.bam"
merged_bed="/home/usuario/Proyectos/Results/tests/arvia/arvia/temp/igvreports2/ARGA00043/regions.bed"

create_report $merged_bed \
--fasta $ref_fasta \
--flanking 500 \
--track-config /home/usuario/Proyectos/Results/tests/arvia/arvia/temp/igvreports2/ARGA00043/igvreports.json \
--translate-sequence-track \
--standalone --output igv.html

"""
