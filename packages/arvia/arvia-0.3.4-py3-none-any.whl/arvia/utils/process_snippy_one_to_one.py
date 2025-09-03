import pandas as pd
import itertools
import numpy as np

def process_snippy_one_to_one(input_path, output_file, ref_barcodes, query_barcodes):
    # Ej: process_snippy_one_to_one('output/KlebsiellaMedular/snippy_one_to_one', 'output/test.tsv')

    snippy_one_to_one_path = input_path
    res_list = []
    reads_cols = list(query_barcodes)
    refs_cols = list(ref_barcodes)

    for ref_barcode, query_barcode in itertools.product(*[ref_barcodes, query_barcodes]):
        try:
            # Get files
            res_folder = f"{snippy_one_to_one_path}/ref_{ref_barcode}__vs__{query_barcode}"
            res = f"{res_folder}/snps.txt"

            # Create df
            df = pd.read_csv(res, sep="\t", header=None)
            changes = df[df[0] == "VariantTotal"][1].iloc[0]

            # Store df
            tmp = {"ref_id": ref_barcode, "count": changes, "reads": query_barcode}
            res_list.append(tmp)

        except Exception as e:
            print(f"Warning in {res_folder}: {e}")

    # Create df to store each result
    try:
        cols = ["ref_id"] + reads_cols
        # main_df = pd.DataFrame(columns=cols, data=[[np.nan] * len(cols) for l in range(len(cols) - 1)])
        main_df = pd.DataFrame(np.nan, index=np.arange(len(refs_cols)), columns=cols)
        main_df["ref_id"] = refs_cols
        main_df = pd.DataFrame(index=refs_cols, columns=reads_cols)
        main_df = main_df.rename_axis("ref_id").reset_index()
    except Exception as e:
        print(f"Warning in {res_folder}: {e}")

    # Insert each snippy result into the main dataframe
    for i in res_list:
        count = int(i["count"])
        reads = i["reads"]
        ref = i["ref_id"]

        r = main_df.index[main_df["ref_id"] == ref].tolist()
        c = main_df.columns.get_loc(reads)

        main_df.iloc[r, c] = count

    main_df = main_df.set_index("ref_id")
    # Transform each column to numeric
    main_df[reads_cols] = pd.to_numeric(main_df[reads_cols].stack(), errors="coerce").unstack()

    if output_file:
        main_df.to_csv(output_file, sep="\t")

    # Color the df
    # main_df.style.background_gradient(cmap='RdYlGn_r', axis=None)

    return main_df
