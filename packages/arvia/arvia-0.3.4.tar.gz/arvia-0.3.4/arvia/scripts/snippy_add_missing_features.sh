#!/usr/bin/env bash
set -euo pipefail

###################################################
# ---- Add missing features to snippy result ---- #
###################################################
# This script must be ran from inside a snippy result folder
# It generates coverage per locus tag in gene_coverage.tsv
# It then generates possible missing features (coverage<X or depth<Y) and appends them to snippy results


# -- Test folder at least contains certain files --
[ ! -f snps.log ] && echo "Folder does not look like snippy result folder (missing snps.log file). Exiting..." && exit 1 || true


# ---- Get gene coverage ----
# Extract bed from snippy-generated gff
# - Grep CDS entries
# - Replace %2C by "," (gff has special ASCII dont know why)
# - Regex match locus_tag, gene and product with awk. Print chrom,start,end,locus_tag,gene,product
# - Remove lines starting with "#"
grep CDS reference/ref.gff | \
    sed 's/%2C/,/g' | \
    awk -v FS='\t' -v OFS='\t' '{
        match($9, "ID=([^;]+)", locus_tag); 
        match($9, "gene=([^;]+)", gene); 
        match($9, "product=([^;]+)", product)}{
            print $1,$4,$5,locus_tag[1],gene[1],product[1]
        }' | grep --invert-match -E "^#" > ref_genes.bed

# Get coverage stats in bed entries
bedtools bamtobed -i *.bam | bedtools coverage -b - -a ref_genes.bed > default_bedtools_coverage.tsv
bedtools bamtobed -i *.bam | bedtools coverage -header -mean -b - -a ref_genes.bed > meandepth_bedtools_coverage.tsv

# Merge stats
echo -e "chrom\tstart\tend\tlocus_tag\tgene\tproduct\treads\tnon_zero_cov_bases\tfeature_length\tnon_zero_coverage\tmean_depth" > gene_coverage.tsv
join -j 4 -t $'\t' default_bedtools_coverage.tsv meandepth_bedtools_coverage.tsv | awk -v FS='\t' -v OFS='\t' '{ print $2,$3,$4,$1,$5,$6,$7,$8,$9,$10,$16 }' >> gene_coverage.tsv

# ---- Add possible_missing_feature variants to snippy results ----
# - If coverage (f10) is less than 0.95 or depth (f11) less than 5 print row
# - Format row to fit snippy result: CHROM  POS   TYPE REF   ALT     EVIDENCE        FTYPE   STRAND  NT_POS  AA_POS  EFFECT  LOCUS_TAG       GENE    PRODUCT

# Tab format 
echo -e "CHROM\tPOS\tTYPE\tREF\tALT\tEVIDENCE\tFTYPE\tSTRAND\tNT_POS\tAA_POS\tEFFECT\tLOCUS_TAG\tGENE\tPRODUCT" > possible_missing_features.tsv
cat gene_coverage.tsv | \
    awk -v FS='\t' -v OFS='\t' '{ if ($10 < 0.95 || $11 < 5) print $0 }' | \
    awk -v FS='\t' -v OFS='\t' '{ 
        printf "%s\t%s\tpossible_missing_feature\tfeature\t-\t\"PMF: %.2f%% %.0fx\"\t-\t-\t-\t-\tpossible_missing_feature\t%s\t\"%s\"\t\"%s\"\n", 
        $1,$2,100*$10,$11,$4,$5,$6
    }' | tee -a snps.tab snps.nofilt.tab >> possible_missing_features.tsv

# Also add rows to snippy's csv result
awk '{ FS="\t"; OFS="," } NR>1 {$1=$1; print}' possible_missing_features.tsv >> snps.csv

# Remove temp files
rm default_bedtools_coverage.tsv meandepth_bedtools_coverage.tsv
