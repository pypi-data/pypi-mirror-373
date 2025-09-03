

import pandas as pd
import glob
from pathlib import Path
import numpy as np
from arvia.utils.combine_snippy_results import concat_files




def get_formatted_amrfinder_genes(data: pd.DataFrame, db: pd.DataFrame):
    """
    For each gene in a amrfinder result, depending on identity and coverage of the reference gene,
    add a suffix to the end of the string. 
    Additionally, use closest reference name (by default if a blaPDC-1 is mutated amrfinder will only indicate blaPDC)
    """

    def assign_suffix(row, db=db):
        closest_ref_name = db.loc[db["refseq_protein_accession"]==row["closest_reference_accession"], "allele"].to_list()
        assert len(closest_ref_name)==1, f"Unexpected number of references (expected one): {closest_ref_name=}"
        closest_ref_name = closest_ref_name[0]


        # Perfect
        if row["pct_coverage_of_reference"] >= 100 and row["pct_identity_to_reference"] >= 100:
            return row["element_symbol"]
        # Mutated
        elif (
            (row["pct_identity_to_reference"] >= 90)
            & (row["pct_identity_to_reference"] < 100)
            & (row["pct_coverage_of_reference"] >= 70)
        ):
            return f"{closest_ref_name}*" # row["element_symbol"] + "*"
        # Unprobable or cut
        elif (row["pct_identity_to_reference"] >= 80) & (row["pct_coverage_of_reference"] < 70):
            return f"{closest_ref_name}?" # row["element_symbol"] + "?"
        # Other
        elif row["pct_coverage_of_reference"] > 90:
            return f"{closest_ref_name}?" # row["element_symbol"] + "?"
        else:
            return f"{closest_ref_name}?" # row["element_symbol"] + "?"
            # raise Exception("Unexpected, gene did not fit in any suffix category.")

    db["allele"] = db["allele"].fillna(db["gene_family"])

    if len(data) >= 1:  # apply fails if dataframe is empty
        data["mod_element_symbol"] = data.apply(assign_suffix, axis=1)
        genes = "; ".join(sorted(data["element_symbol"].to_list()))
    else:
        genes = ""

    return data, genes


def process_amrfinder_result(input_file: Path, amrfinder_catalog_file: Path, output_file: Path = None):
    """
    Basically format columns from a amrfinder result and apply func get_formatted_amrfinder_genes
    amrfinder_catalog_file: It is a file named ReferenceGeneCatalog.txt that should be in amrfinderplus db directory after running "arvia dbs"
                            Should be in /home/user/.../environments/miniconda3/envs/arvia/share/amrfinderplus/data/latest/ReferenceGeneCatalog.txt
    """
    amrfinder_df = pd.read_csv(input_file, sep="\t")
    amrfinder_catalog_df = pd.read_csv(amrfinder_catalog_file, sep="\t")

    amrfinder_df.columns = [i.lower().replace(" ", "_").replace("%", "pct") for i in amrfinder_df.columns]
    amrfinder_df, _ = get_formatted_amrfinder_genes(amrfinder_df, amrfinder_catalog_df)
    amrfinder_df["bc"] = Path(input_file).parent.name
    amrfinder_df = amrfinder_df[["bc", "contig_id", "element_symbol", "mod_element_symbol", "element_name", "scope", "type", "subtype", 'class', 'subclass', "pct_coverage_of_reference", "pct_identity_to_reference", "start", "stop"]]
    
    if output_file:
        amrfinder_df.to_csv(output_file, sep="\t", index=None)

    return amrfinder_df





