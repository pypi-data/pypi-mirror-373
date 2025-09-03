

import pandas as pd
from pathlib import Path
import re

def process_mlst_result(input_file: Path, mlst_dbs_folder: Path, output_file: Path = None):
    # Extract sample name from parent folder 
    # (file is expected to belong to one sample)
    bc = Path(input_file).parent.name

    # Read table result
    mlst_df = pd.read_csv(input_file, header=None, sep="\t")
    mlst_df = mlst_df.rename(columns={0: "file", 1: "mlst_model", 2: "mlst"})
    mlst_df["bc"] = bc

    # For every row in table
    d = {}
    mlst_l = []
    for i in mlst_df.to_dict("records"):
        # Init variables
        # bc = i["bc"]
        mlst_model = i["mlst_model"]
        mlst = "ST" + str(i["mlst"]) 
        genes = []
        all_alleles = [] # n
        exact_alleles = [] # n
        missing_alleles = [] # -
        partial_match_alleles = [] # n?
        novel_alleles = [] # ~n
        mixed_alleles = [] # n,n
        
        # Init sample dictionary
        if not d.get(bc):
            d[bc] = {}

        # For every column_name:column_value
        # extract genes and alleles
        # acsA(15) -> gene="acsA" ; allele=15
        # If allele has a symbol (-,?~) append to specified list
        for k,v in i.items():
            finds = []
            if type(k)==int:
                finds = re.findall("^(.+)\((.+)\)$", v)
                assert finds, f"Unexpected: could not find allele pattern in {v=}"
                gene, allele = finds[0]
                try:
                    allele = int(allele)
                    d[bc][gene] = allele
                    exact_alleles.append(v)
                except ValueError:
                    allele = str(allele)
                    d[bc][gene] = allele
                    
                    if allele=="-":
                        missing_alleles.append(v)
                    elif "," in allele:
                        mixed_alleles.append(v)
                    elif "?" in allele:
                        partial_match_alleles.append(v)
                    elif "~" in allele:
                        novel_alleles.append(v)
                    else:
                        exact_alleles.append(v)

                all_alleles.append(v)
                genes.append(gene)

            elif type(k)==str:
                pass
                # d[bc][k] = v

            else:
                raise Exception(f"Unexpected type: {k=}")

        # Read database specified by mlst_model
        selected_db = pd.read_csv(f"{mlst_dbs_folder}/{mlst_model}/{mlst_model}.txt", sep="\t")
        selected_db = selected_db.rename(columns={"ST":"mlst"})

        # For every entry in database
        # check how many gene/alleles match
        # in result to the indicated mlst
        counter_l = []
        for db_row in selected_db.to_dict("records"):
            counter = 0
            for k,v in db_row.items():
                if k in genes and v == d[bc][k]:
                    counter += 1
            db_row["matched_alleles"] = counter
            counter_l.append(db_row)
            
        # Now get entries with the max matches (ideally the same number as the number of genes in model)
        mlst_counter_df = pd.DataFrame(counter_l)[["mlst","matched_alleles"]]
        mlst_allele_matches = mlst_counter_df["matched_alleles"].max()
        mlst_counter_df = mlst_counter_df[mlst_counter_df["matched_alleles"]==mlst_allele_matches]

        # If allele combination does not match (which means a gene is missing or mutated)
        # we will append "!" to each mlst, then we concat top 5 mlsts into a string separated by ;
        mlst_model_alleles_count = len(genes)
        suffix = "" if mlst_allele_matches == mlst_model_alleles_count else "!"
        closest_mlst = "; ".join([f"ST{i}{suffix}" for i in mlst_counter_df["mlst"].to_list()[:5]])

        # Our final result is the closest_mlst by default
        final_mlst = closest_mlst

        # Return dictionary of row results
        mlst_l.append(
            {
                "bc": bc,
                "mlst_model": mlst_model,
                "mlst_result": mlst,
                "closest_mlst": closest_mlst,
                "final_mlst": final_mlst,
                "mlst_model_alleles_count": mlst_model_alleles_count,
                "matches": f"{mlst_allele_matches}/{mlst_model_alleles_count}",
                "all_alleles": "; ".join(all_alleles),
                "new_alleles": "; ".join(novel_alleles),
                "partial_match_alleles": "; ".join(partial_match_alleles),
                "missing_alleles": "; ".join(missing_alleles),
                "mixed_alleles": "; ".join(mixed_alleles),
                # "new_alleles": f"{len(novel_alleles)}/{mlst_model_alleles_count}",
                # "partial_match_alleles": f"{len(partial_match_alleles)}/{mlst_model_alleles_count}",
                # "missing_alleles": f"{len(missing_alleles)}/{mlst_model_alleles_count}",
                # "mixed_alleles": f"{len(mixed_alleles)}/{mlst_model_alleles_count}",
            }
        )

    # Create dataframe, save and return
    mlst_df = pd.DataFrame(mlst_l)

    if output_file:
        mlst_df.to_csv(output_file, sep="\t", index=None)

    return mlst_df
