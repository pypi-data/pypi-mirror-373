from textwrap import wrap
import pandas as pd
from arvia.utils.aeruginosa_snippy import AERUGINOSA_GENES
from pathlib import Path
import glob
from collections import Counter
import numpy as np

BLAST_OUTFMT = "6 qseqid sseqid stitle pident qcovs qcovhsp qcovus length mismatch gapopen qlen slen qstart qend sstart send evalue bitscore qseq sseq"
GENES = pd.DataFrame(AERUGINOSA_GENES.items())
GENES.columns = ["locus_tag", "gene"]


def check_truncations(
    input_file: str, genes_df: pd.DataFrame = GENES, blast_outfmt: str = BLAST_OUTFMT
) -> pd.DataFrame:
    df = pd.read_csv(input_file, sep="\t", header=None)
    df.columns = BLAST_OUTFMT.split(" ")[1:]

    df = df[(df["pident"] >= 90) & (df["qcovs"] >= 20)]

    df = pd.merge(genes_df, df, left_on="locus_tag", right_on="qseqid", how="left")

    # ---- Easy mutations ----
    df.loc[(df["qcovs"] == 100) & (df["pident"] == 100), "easy_muts"] = "perfect_match"
    df.loc[(df["qcovs"] == 100) & (df["pident"] < 100), "easy_muts"] = "mutated"
    df.loc[df["qcovs"] > 100, "easy_muts"] = "insertion"
    df.loc[df["qcovs"] < 100, "easy_muts"] = "deletion"
    df.loc[df["sseqid"].isna(), "easy_muts"] = "not_found (possible truncation/missassembly/low blast identity)"

    # ---- Truncations ----
    def get_frame(pos: int):
        pos = int(pos)
        current_pos = pos
        while True:
            if (
                pos == 1 or current_pos / 3 % 1 == 0
            ):  # if int # assumes all queries were proteins that started in frame 1
                moves = current_pos - pos
                moves = moves if moves == 0 else moves + 1
                return moves
            elif current_pos / 3 % 1 != 0:  # if float
                current_pos += 1
            else:
                raise "Unexpected"

    def get_codon_prop(s: str):
        return round(len(s) / 3, 2)

    def get_stop_codons(s: str):
        return [[idx + 1, 3 * (idx + 1), i] for idx, i in enumerate(wrap(s, 3)) if i in ["TAG", "TAA", "TGA"]]

    def check_big_changes(row):
        if type(row["qseq"]) == str:  # math.isnan(record["qseq"]):
            # Get gaps length
            sseq_gap_length = row["sseq"].count("-")
            qseq_gap_length = row["qseq"].count("-")
            # assert not (sseq_gap_length>0 and qseq_gap_length>0), f"Did not expect both sequences to have gaps. Code is not prepared: qseqid={row['qseqid']} sseqid={row['sseqid']}"

            # Remove gaps
            sseq = row["sseq"].replace("-", "")
            qseq = row["qseq"].replace("-", "")

            # Move frame so both sequences start in the start of a codon
            frame_move = get_frame(row["qstart"])
            sseq = sseq[frame_move:]
            qseq = qseq[frame_move:]

            # Get stop codons in each sequence according to the frame_move
            sstops = get_stop_codons(sseq)
            qstops = get_stop_codons(qseq)

            # Get number of codons in sequence
            sseq_codon_prop = get_codon_prop(sseq)
            qseq_codon_prop = get_codon_prop(qseq)
            if qseq_codon_prop % 1 != 0 and row["qcovs"] == 100 and row["length"] == row["qlen"]:
                print(row)
                print(qseq_codon_prop, sseq_codon_prop)
                raise Exception(f"Unexpected: Query's codons were not a multiple of 3\n{row}")

            sstops_is_larger = len(sstops) > len(qstops)
            sstops_and_qstops_is_equal = len(sstops) == len(qstops)
            codon_prop_is_equal = qseq_codon_prop == sseq_codon_prop
            sseq_codon_prop_is_ok = sseq_codon_prop % 1 == 0  # if subject number of codons is a multiple of 3
            sseq_codon_prop_is_larger = sseq_codon_prop > qseq_codon_prop

            if sstops_and_qstops_is_equal:
                if (
                    not sstops and not qstops
                ):  # if no stop codons it is broken piece or indel just at the last nucleotide so it does not appear on blast
                    return np.nan
                elif sseq_codon_prop_is_ok:
                    if codon_prop_is_equal:
                        return np.nan
                    elif sseq_codon_prop_is_larger:
                        return "in_frame_insertion"
                    elif not sseq_codon_prop_is_larger:
                        return "in_frame_deletion"
                    else:
                        print(input_file, "\n", row)
                        raise Exception("Unexpected condition 0")
                else:
                    # print(input_file, "\n", row)
                    # print(qstops)
                    # print(sstops)
                    # print(qseq_codon_prop)
                    # print(sseq_codon_prop)
                    # print(row["qseq"])
                    # print(row["sseq"])
                    if codon_prop_is_equal:
                        return np.nan
                    elif not codon_prop_is_equal:
                        if sseq_codon_prop_is_larger:
                            return "frame_shift (disruptive insertion)"
                        elif not sseq_codon_prop_is_larger:
                            return "frame_shift (disruptive deletion)"
                        else:
                            print(input_file, "\n", row)
                            raise Exception("Unexpected condition 2")
                    else:
                        print(input_file, "\n", row)
                        raise Exception("Unexpected condition 3")

                    raise Exception("Unexpected condition 3.1")

            elif sstops_is_larger:
                if codon_prop_is_equal:
                    return "truncated (additional stop(s) by substitution)"
                elif not codon_prop_is_equal:
                    if codon_prop_is_equal:
                        return np.nan
                    elif sseq_codon_prop_is_larger:
                        return "frame_shift (disruptive insertion)"
                    elif not sseq_codon_prop_is_larger:
                        return "frame_shift (disruptive deletion)"
                    else:
                        print(input_file, "\n", row)
                        raise Exception("Unexpected condition 2")
                else:
                    print(input_file, "\n", row)
                    raise Exception("Unexpected condition 3")

            elif not sstops_is_larger:
                if codon_prop_is_equal:
                    return "truncated (lost stop(s) by substitution)"
                elif not codon_prop_is_equal:
                    if sseq_codon_prop_is_larger:
                        return "frame_shift (disruptive insertion)"
                    elif not sseq_codon_prop_is_larger:
                        return "frame_shift (disruptive deletion)"
                    else:
                        print(input_file, "\n", row)
                        raise Exception("Unexpected condition 4")
                else:
                    print(input_file, "\n", row)
                    raise Exception("Unexpected condition 5")

            else:
                print(input_file, "\n", row)
                raise Exception("Unexpected condition 6")

            # # If subject has more stops
            # if len(sstops) > len(qstops):
            #     return "truncated (additional stop(s))"
            # # If subject has less stops
            # elif len(sstops) < len(qstops):
            #     return "truncated (lost stop(s))"
            # # If they have the same number of stops but different codon proportion
            # elif (len(sstops) == len(qstops)) and (qseq_codon_prop != sseq_codon_prop):
            #     # Check for disruptive insertions or deletions
            #     if sseq_codon_prop % 1 != 0:  # if subject number of codons is not a multiple of 3
            #         if sseq_codon_prop > qseq_codon_prop:
            #             return "frame_shift (disruptive insertion)"
            #         elif sseq_codon_prop < qseq_codon_prop:
            #             return "frame_shift (disruptive deletion)"
            #     # Check for in-frame insertions or deletions
            #     else:
            #         if sseq_codon_prop > qseq_codon_prop:
            #             return "in_frame_insertion"
            #         elif sseq_codon_prop < qseq_codon_prop:
            #             return "in_frame_deletion"
            # elif (len(sstops) == len(qstops)) and (qseq_codon_prop == sseq_codon_prop):
            #     return np.nan
            # else:
            #     raise Exception("Unexpected condition")

        return np.nan

    def check_splits(row):
        # Count contig occurences
        row["sseqid_count"] = [i for i in row["sseqid_count"] if i and i is not np.nan]
        row["sseqid_count"] = Counter(row["sseqid_count"])

        # Decide comment
        keys = row["sseqid_count"].keys()
        if len(keys) == 1:
            return "one_contig"
        elif len(keys) > 1:
            return "multiple_contigs"
        elif len(keys) == 0:
            return np.nan
        else:
            raise Exception("Unexpected")

    # Splits
    temp = df.copy().groupby(["locus_tag"], dropna=False)["sseqid"].apply(list).reset_index(name="sseqid_count")
    temp["contigs"] = temp.apply(check_splits, axis=1)
    df = pd.merge(df, temp, on="locus_tag")

    # Big mutations (frameshifts, stops, in-frame indels)
    df["big_mutations"] = df.apply(check_big_changes, axis=1)

    # Merge comments
    df["comment"] = df["big_mutations"].fillna(df["easy_muts"])
    df.loc[(df[["locus_tag", "gene"]].duplicated(keep=False)), "comment"] = "truncation or missassembly"
    df["comment"] = df.apply(
        lambda row: f"{row['comment']} ({row['contigs']})" if row["contigs"] is not np.nan else row["comment"], axis=1
    )

    # ---- Finalize -----
    df = df[
        [
            "locus_tag",
            "gene",
            "comment",
            "pident",
            "qcovs",
            "sseqid",
            "sstart",
            "send",
            "qstart",
            "qend",
            "qseq",
            "sseq",
        ]
    ]
    df.sort_values("comment")

    return df


# l = []
# for i in glob.glob("/home/usuario/Proyectos/Results/tests/truncation_test/blast/ARGA*/res.tsv"):
#     bc = Path(i).parent.name
#     df = check_truncations(i)
#     df["bc"] = bc
#     l.append(df)

# df = pd.concat(l)
# data = df[["bc", "locus_tag", "gene", "comment"]].drop_duplicates()
# data["locus_gene"] = data["locus_tag"].astype(str) + "\n" + data["gene"].astype(str)
# data.pivot(index="bc", columns="locus_gene", values="comment").to_excel("/home/usuario/Proyectos/Results/testX.xlsx")
