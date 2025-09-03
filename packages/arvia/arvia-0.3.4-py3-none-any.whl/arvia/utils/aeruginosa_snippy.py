import pandas as pd
from subprocess import call, run

AERUGINOSA_GENES = {
    "PA0004": "gyrB",
    "PA0424": "mexR",
    "PA0425": "mexA",
    "PA2018": "mexY",
    "PA0426": "mexB",
    "PA0427": "oprM",
    "PA0807": "ampDh3",
    "PA0958": "oprD",
    "PA1798": "parS",
    "PA1799": "parR",
    "PA2019": "mexX",
    "PA2020": "mexZ",
    "PA2023": "galU",
    "PA2491": "mexS",
    "PA2492": "mexT",
    "PA2493": "mexE",
    "PA2494": "mexF",
    "PA2495": "oprN",
    "PA3047": "dacB",
    "PA3168": "gyrA",
    "PA3574": "nalD",
    "PA3721": "nalC",
    "PA3999": "dacC",
    "PA4003": "pbpA",
    "PA4020": "mpl",
    "PA4109": "ampR",
    "PA4110": "ampC",
    "PA4266": "fusA1",
    "PA4418": "ftsI",
    "PA4522": "ampD",
    "PA4597": "oprJ",
    "PA4598": "mexD",
    "PA4599": "mexC",
    "PA4600": "nfxB",
    "PA4776": "pmrA",
    "PA4777": "pmrB",
    "PA4964": "parC",
    "PA4967": "parE",
    # "PA5471.1": "-",
    "PA5471": "armZ",
    "PA5485": "ampDh2",
    "PA3271": "-",
    "PA1180": "phoQ",
    "PA4270": "rpoB",
    "PA3078": "cprS",
    "PA4381": "colR",
    "PA4380": "colS",
    "PA2047": "cmrA",
    "PA4315": "mvaT",
    "PA5199": "amgS",
    "PA5235": "glpT",
    "PA0929": "pirR",
    "PA0931": "pirA",
    "PA2392": "pvdP",
    "PA2426": "pvdS",
    "PA2688": "pfeA",
    "PA3899": "fecI",
    "PA4221": "fptA",
    "PA4226": "pchE",
    "PA4227": "pchR",
    "PA4514": "piuA",
    "PA4515": "piuC",
    "PA4228": "pchD",
    "PA4175": "piv",
    "PA2391": "opmQ",
    "PA2388": "fpvR",
    "PA2057": "sppR",
    "PA2385": "pvdQ",
    "PA2297": "-",
    "PA2394": "pvdN",
    "PA0434": "optJ",
    "PA4225": "pchF",
    "PA1922": "cirA",
    "PA4897": "optI",
    "PA4161": "fepG",
}
AERUGINOSA_GENES_DF = pd.DataFrame(list(AERUGINOSA_GENES.items()))
AERUGINOSA_GENES_DF.columns = ["LOCUS_TAG", "GENE"]


def filter_synonymous_variants(data: pd.DataFrame):
    if len(data) >= 1:
        return data[(~data["EFFECT"].isna()) & (data["EFFECT"].str.split(" ", expand=True)[0] != "synonymous_variant")]
    else:
        return data


def filter_snippy_result(
    snippy_res, filtered_snippy_res=None, aeruginosa_genes_df=AERUGINOSA_GENES_DF, input_sep="\t"
):
    # Read snippy result
    if type(snippy_res) == str:
        df = pd.read_csv(snippy_res, sep=input_sep)
    elif type(snippy_res) == pd.core.frame.DataFrame:
        df = snippy_res
    else:
        raise Exception("Dont know input type")

    # Keep non synonymous
    df = filter_synonymous_variants(df)

    # Keep genes of interest
    df = df[(df["LOCUS_TAG"].isin(aeruginosa_genes_df["LOCUS_TAG"])) | (df["GENE"].isin(aeruginosa_genes_df["GENE"]))]

    # Add gene names if gene column is NaN (dont know why snippy does this)
    def substitute_na_genes(row):
        if type(row["GENE"]) != str:
            row["GENE"] = aeruginosa_genes_df[aeruginosa_genes_df["LOCUS_TAG"] == row["LOCUS_TAG"]]["GENE"].tolist()[0]
        return row

    df = df.apply(substitute_na_genes, axis=1)

    # Save filtered df
    if filtered_snippy_res is not None:
        df.to_csv(filtered_snippy_res, sep="\t", index=None)

    return df

