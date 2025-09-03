from Bio import SeqIO
import pandas as pd


def get_proteins_from_gbk(input_gbk, cds_output_file, output_aa=True):
    # Reset output file if it exists
    with open(cds_output_file, "wt") as handle:
        pass

    # For every contig
    for contig in SeqIO.parse(input_gbk, "genbank"):
        # Get contig features and for every feature extract relevant information
        source = contig.annotations["source"]
        if contig.features:
            for feature in contig.features:
                # Type of feature 1
                if feature.type in ["CDS"]:  # ,'rRNA','tRNA','tmRNA'
                    qualifiers = feature.qualifiers
                    locus_tag = qualifiers["locus_tag"][0]
                    product = qualifiers["product"][0]
                    ncl_sequence = feature.extract(contig.seq)
                    prot_sequence = None

                    if output_aa:
                        try:
                            prot_sequence = feature.qualifiers["translation"][0]
                        except Exception as e:
                            print(f"Unexpected problem in {locus_tag} ({product}): Could not extract protein")
                            prot_sequence = None

                    out_seq = prot_sequence if output_aa else ncl_sequence
                    if out_seq:
                        with open(cds_output_file, "at") as handle:
                            handle.write(f">{locus_tag} {product}\n{out_seq}\n")

                # Type of feature 2
                elif feature.type in ["misc_binding", "misc_feature", "regulatory"]:
                    qualifiers = feature.qualifiers
                    ncl_sequence = feature.extract(contig.seq)
                    out_seq = ncl_sequence
                    locus_tag = "no_locus_tag"
                    product = qualifiers["note"][0].split(";")[0]
                    # print(f'>{locus_tag} {product} [{source}]\n{out_seq}')

                # Type of feature 3
                elif feature.type in ["repeat_region"]:
                    qualifiers = feature.qualifiers
                    ncl_sequence = feature.extract(contig.seq)
                    out_seq = ncl_sequence
                    locus_tag = "no_locus_tag"
                    product = qualifiers["rpt_family"][0]
                    repeat = qualifiers["rpt_unit_seq"]

                    # print(f'>{locus_tag} {product} [{source}]\n{out_seq}')

                elif feature.type in ["ncRNA"]:
                    qualifiers = feature.qualifiers
                    ncl_sequence = feature.extract(contig.seq)
                    out_seq = ncl_sequence
                    locus_tag = qualifiers["locus_tag"][0]
                    product = qualifiers["product"][0]

                    # print(f'>{locus_tag} {product} [{source}]\n{out_seq}')

                else:
                    pass

    return cds_output_file


# input_gbk = '/home/usuario/Proyectos/Innova/output/IlluminaBacteria/ARGA001BACGEM101121/13_prokka/ARGA0002_L001_ds.359743fd49404ad39026f0de1b0d9f9b/ARGA0002_S2/ARGA0002_S2.gbk'
# output_faa = '/home/usuario/Proyectos/Innova/output/pruebas/diamond/input.faa'

# get_proteins_from_gbk(input_gbk, output_faa)
