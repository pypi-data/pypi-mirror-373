import yaml
import re
from pathlib import Path
import pandas as pd
import os
from arvia.utils.console_log import CONSOLE_STDOUT, CONSOLE_STDERR, log_error_and_raise, rich_display_dataframe

# Possible input file patterns so we can associate the sample name 
INPUT_FILE_PATTERNS = {
    "reads": [
        r"(.+)_S\d+_L\d+_R[12]_\d+.fastq.gz$",
        r"(.+)_R[12].fastq.gz$",
        r"(.+)_[12].fastq.gz$",
        r"(.+).fastq.gz$",
    ],
    "assembly": [
        r"(.+).fasta$",
        r"(.+).fna$",
        r"(.+).fas$",
        r"(.+).fa$",
    ],
    "gbk": [
        r"(.+).gbk$",
    ],
}


class UniqueKeyLoader(yaml.SafeLoader):
    """
    Special YAML loader with duplicate key checking
    # from https://stackoverflow.com/a/63215043
    """
    def construct_mapping(self, node, deep=False):
        mapping = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            assert key not in mapping, f"At least a key is repeated in --input_yaml file: {key}"
            mapping.append(key)
        return super().construct_mapping(node, deep)

def associate_user_input_files(config: dict) -> dict:
    """    
    Transform user input via command line (e.g. --reads) into expected dictionary associating sample ids in name file.
    Sample IDs are extracted from files through a set of possible patterns
    # Input:
    {
        "reads": ["f1","f2","f3"],
        "assemblies": ["f4"],
        "gbks": [] # optionañ
    }
    # Output:
    {
        "ARGA00461": { 
            "reads": ["ARGA00461.fastq.gz"],
            "assembly": ["ARGA00461.fasta"]
        },
        "ARGA00190": { 
            "reads": ["ARGA00190.fastq.gz"],
            "assembly": ["ARGA00190.fasta"],
            "gbk": ["ARGA00190.gbk"],
        },
    }
    """
    d = {
        # "ARGA00461": { 
        #     "reads": ["ARGA00461.fastq.gz"],
        #     "assembly": ["ARGA00461.fasta"]
        # },
    }
    for f in sorted(config["reads"]) + sorted(config["assemblies"]) + sorted(config["gbks"]):
        pattern_detected = False
        for pat_type, pats in INPUT_FILE_PATTERNS.items():
            for pat in pats:
                res = re.findall(pat, str(Path(f).name))
                if res:
                    assert len(res)==1 and type(res)==list, "Unexpected"
                    bc = res[0]
                    
                    if not d.get(bc):
                        d[bc] = {
                            "reads": [],
                            "assembly": [],
                            "gbk": [],
                        }
                    if pat_type=="reads":
                        d[bc]["reads"] += [f]
                    elif pat_type=="assembly":
                        d[bc]["assembly"] += [f]
                    elif pat_type=="gbk":
                        d[bc]["gbk"] += [f]
                    pattern_detected = True
                    break

        assert pattern_detected, f"Could not find expected file structure in {f}"
    return d


def input_file_dict_from_yaml(yaml_input):
    """
    Transform input files in YAML format into
    into expected dictionary doing some sanity checks.
    # Input
    sample_id:
        reads:
            - reads.fastq.gz
        assembly:
            - assembly.fasta
        gbk:
            - assembly.gbk
    # Output
    {
        "sample_id": {
            "reads": ["reads.fastq.gz"],
            "assembly": ["assembly.fasta"],
            "gbk": ["assembly.gbk"],
        }
    }

    """
    # Read user input files in yaml format
    with open(yaml_input, 'r') as f:
        d = yaml.load(f, Loader=UniqueKeyLoader)

    # Ensure the dict has the keys "reads" and "assembly" in each sample, each containning a list (can be empty)
    for k,v in d.items():
        # If main keys are not present initialize them with a list
        for i in ["reads", "assembly", "gbk"]:
            if not v.get(i):
                v[i] = []
            else:
                v[i] = sorted(v[i])
            if type(v.get(i))!=list:
                raise Exception(f"Input value is not in list format ({v[i]=}): {d}")
            v[i] = [os.path.abspath(file) for file in v[i]] # turn file paths into absolute paths

    return d


def check_input_file_dict_and_decide_pipeline(d):
    for k,v in d.items():
        reads = v["reads"]
        assembly = v["assembly"]
        gbk = v["gbk"]

        assert type(reads)==list, "Reads are not in list format"
        assert type(assembly)==list, "Assembly is not in list format"
        assert type(gbk)==list, "Annotated assembly (.gbk) is not in list format"
        assert len(reads)<=2, "Only 0-2 reads files per sample is supported"
        assert len(assembly)<=1, "Only 0-1 assembly file per sample is supported"
        assert len(gbk)<=1, "Only 0-1 annotated assembly file per sample is supported"
        check_reads_exists = [i for i in reads if not Path(i).exists()]
        check_assembly_exists = [i for i in assembly if not Path(i).exists()]
        check_gbk_exists = [i for i in gbk if not Path(i).exists()]

        # If reads are supplied
        if (len(reads) in [1,2]):
            assert len(check_reads_exists)==0, f"At least a file path does not exist: {check_reads_exists}"
            v["reads_type"] = "single_end" if len(reads)==1 else "paired_end"

            # If assembly is supplied
            if assembly:
                assert len(check_assembly_exists)==0, f"At least a file path does not exist: {assembly}"
                v["pipeline"] = "full_pipeline"
            else:
                v["pipeline"] = "only_reads"
        
        elif assembly:
            assert len(check_assembly_exists)==0, f"At least a file path does not exist: {assembly}"
            v["pipeline"] = "only_assembly"
            v["reads_type"] = None
        
        else:
            raise Exception(f"Unexpected input -> {k}: {v}")
    return d

def expand_input_file_dict_into_multiple_cols(row):
    """
    Takes column "temp" and expands it into columns reads_1, reads_2 and assembly
    depending on the number of files and their presence
    """
    read_file_count: int = len(row["temp"]["reads"])
    assembly_file_count: int = len(row["temp"]["assembly"])
    gbk_file_count: int = len(row["temp"]["gbk"])
    pipeline = row["temp"]["pipeline"]

    if read_file_count==2:
        row["reads_1"] = row["temp"]["reads"][0]
        row["reads_2"] = row["temp"]["reads"][1]
    elif read_file_count==1:
        row["reads_1"] = row["temp"]["reads"][0]
    elif read_file_count>2:
        raise Exception(f"Unexpected number of reads: {row}")        

    if assembly_file_count == 1:
        row["assembly"] = row["temp"]["assembly"][0]

    if gbk_file_count == 1:
        row["gbk"] = row["temp"]["gbk"][0]

    if pipeline:
        row["pipeline"] = pipeline

    return row

def input_files_dict_to_df(d: dict) -> pd.DataFrame:
    file_manifest_df = pd.DataFrame(d.items())
    file_manifest_df.columns = ["sample", "temp"]
    file_manifest_df = file_manifest_df.apply(expand_input_file_dict_into_multiple_cols, axis=1)
    file_manifest_df = file_manifest_df.drop(columns=["temp"])
    file_manifest_df = file_manifest_df.fillna("-")
    file_manifest_df = file_manifest_df[["sample", "pipeline"]+ [i for i in file_manifest_df.columns if i not in ["sample", "pipeline"]]]
    return file_manifest_df

# # Read config (user input)
# yaml_config = "/home/usuario/Proyectos/Results/tests/arvia/config.yaml"
# with open(yaml_config, 'r') as f:
#     config = yaml.load(f, Loader=yaml.SafeLoader)

# input_files_dict_to_df(associate_user_input_files(config))


# INPUT_FILES = { # expected structure
#     # Single reads with or without assembly
#     "ARGA00461": { # full pipeline
#         "reads": [f"{temp_input_longreads_folder}/ARGA00461/ARGA00461.fastq.gz"],
#         "assembly": [f"{temp_input_assembly_folder}/ARGA00461/ARGA00461_assembly.fasta"]
#     },
#     "ARGA00190": { # truncation cant be done
#         "reads": [f"{temp_input_longreads_folder}/ARGA00190/ARGA00190.fastq.gz"],
#         "assembly": []
#     },
#     # Paired reads with or without assembly
#     "ARGA00024": { # full pipeline
#         "reads": [f"{temp_input_shortreads_folder}/ARGA00024/ARGA00024_R1.fastq.gz", f"{temp_input_shortreads_folder}/ARGA00024/ARGA00024_R2.fastq.gz"],
#         "assembly": [f"{temp_input_assembly_folder}/ARGA00024/ARGA00024_assembly.fasta"]
#     },
#     "ARGA00025": { # truncation cant be done
#         "reads": [f"{temp_input_shortreads_folder}/ARGA00025/ARGA00025_R1.fastq.gz", f"{temp_input_shortreads_folder}/ARGA00025/ARGA00025_R2.fastq.gz"],
#         "assembly": [f"{temp_input_assembly_folder}/ARGA00025/ARGA00025_assembly.fasta"]
#     },
#     # Assembly without reads
#     "ARGA00031": { # everything with assembly
#         "reads": [],
#         "assembly": [f"{temp_input_assembly_folder}/ARGA00031/ARGA00031_assembly.fasta"]
#     },
# }