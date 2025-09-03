from colorama import Fore, Style
import pandas as pd
from subprocess import run, PIPE
import re
import glob
import os
from pathlib import Path
from snakemake.io import expand
from arvia.utils.console_log import (
    CONSOLE_STDOUT,
    CONSOLE_STDERR,
    rich_display_dataframe,
    display_progress,
    log_error_and_raise,
    get_log_tail_errors,
)
from multiprocessing import Process
from rich.syntax import Syntax
import yaml
from arvia.utils.local_paths import BASE_YAML_CONFIG, DB_INSTALL_YAML_CONFIG
from collections import OrderedDict, Counter


def replace_proxy_rule_output(wildcards, expandable_structure, wildcards_dict, zip_expansion="yes"):
    """
    Takes path structure (fakepath/{barcode}/{barcode}_assembly.fasta) and expands the ProxyRule
    Inputs:
        wildcards = snakemake wildcard object produced in rule (it is not used in the function)
        expandable_structure =  "fakepath/{wildcard1}/{wildcard2}_assembly.fasta"
        wildcards_dict = {'wildcard1':['A','B','C], 'wildcard2':['D','E','F']}
    """
    if zip_expansion == "yes":
        l = expand(expandable_structure, zip, **wildcards_dict)
    else:
        l = expand(expandable_structure, **wildcards_dict)

    if l:
        return l
    else:
        raise Exception(f"Error: Structure {expandable_structure} does not contain any known wildcards.")


# def run_snakemake(snakefile: str, parameters: dict, ppln_name: str):
#     snakemake.snakemake(
#         snakefile,
#         printshellcmds=False,
#         forceall=True,
#         force_incomplete=True,
#         # workdir=config[KEY_TEMPDIR],
#         config=config,
#         cores=parameters["cores"],
#         lock=False,
#         quiet=True,
#         # log_handler=logger.log_handler,
#     )


def params_to_yaml(params: dict, output_yaml_file: str) -> str:
    # Choose yaml based on command
    if params["command"] == "run":
        yaml_d = OrderedDict(BASE_YAML_CONFIG.copy())
    elif params["command"] == "dbs":
        yaml_d = OrderedDict(DB_INSTALL_YAML_CONFIG.copy())
    else:
        raise Exception("Not ready")

    repeated_entries = [
        k for k, v in Counter([j for i in BASE_YAML_CONFIG.values() for j in list(i.keys())]).items() if v != 1
    ]
    assert not repeated_entries, CONSOLE_STDERR.log(f"Repeated params in default YAML config: {repeated_entries}")

    # Modify base yaml
    for k, v in yaml_d.items():  # for every key (section tittle) and its contents
        for p_id, p_value in params.items():  # for every parameter
            if p_id in v.keys():  # if parameter is in section values then modify with value in parameter
                v[p_id] = p_value

    # Save dict as yaml
    with open(output_yaml_file, "w") as out_handle:
        for comment, values in yaml_d.items():
            out_handle.write(f"# ---- {comment.capitalize().replace('_',' ')} ----\n")  # section title
            yaml.dump(values, out_handle, default_flow_style=False, sort_keys=False)
            out_handle.write("\n")

    return yaml_d


def run_snakemake(snakefile: str, parameters: dict, ppln_name: str):
    CONSOLE_STDOUT.log(f"Ititializing {ppln_name} pipeline...\n", style="info")

    # Init command
    cmd = [f"snakemake -s {snakefile}"]

    # Add previz if required
    dry_run = False
    if parameters["previsualize"] == "yes" or parameters["previsualize"] is True:
        dry_run = True
        cmd.append("-n")  #  --quiet

    # Add cores
    cmd.append(f"-c{parameters['cores']}")

    # Use conda (can be optional)
    if parameters["use_conda"]:
        cmd.append("--use-conda")

    # Params to df
    config_df = pd.DataFrame.from_dict(parameters.items())
    config_df = config_df.set_index(0).T
    rich_display_dataframe(config_df, "User supplied params")
    CONSOLE_STDOUT.print()

    # Create folder and params file
    user_yaml_config_file = f"{parameters['output_folder']}/logs/config.yaml"
    snakemake_console_log = f"{parameters['output_folder']}/logs/snakemake.log"
    parameters["snakemake_console_log"] = snakemake_console_log
    _ = run(f"mkdir -p {parameters['output_folder']}/logs", check=True, shell=True)
    _ = params_to_yaml(parameters, user_yaml_config_file)
    # CONSOLE_STDOUT.print(Syntax.from_path(user_yaml_config_file, background_color="default"), end="")
    # config_df.to_csv(user_yaml_config_file, sep="\t", index=None)

    # TODO: make this optional
    cmd.append("--rerun-triggers input mtime")  # default: ['mtime', 'params', 'input', 'software-env', 'code']
    cmd.append("--keep-incomplete")
    cmd.append("--keep-going")

    # Add config file path to command
    cmd.append(f"--configfile {user_yaml_config_file}")

    # Create workflow image (HAS TO BE THE LAST ARGUMENT BECAUSE OF STDOUT)
    draw_wf = parameters.get("draw_wf")
    if draw_wf:
        draw_wf_file = draw_wf
        CONSOLE_STDOUT.log(f"Creating workflow image (rulegraph) in {draw_wf_file}...", style="info")
        CONSOLE_STDOUT.log(f"Note: If image is created then steps do not show in table", style="muted")
        cmd.append(f"--rulegraph | dot -Tpdf > {draw_wf_file}")

    # Execute
    cmd = " ".join(cmd)

    try:
        if Path(snakemake_console_log).exists():
            os.remove(snakemake_console_log)

        CONSOLE_STDOUT.log(f"Running pipeline...", style="info")
        smk_proc = Process(
            target=run,
            kwargs={
                "args": cmd,
                "check": True,
                "shell": True,
                # "stdout": PIPE,
                # "stderr": PIPE,
            },
        )
        _ = smk_proc.start()
        if (
            draw_wf is None
        ):  # if drawing workflow snakemake does not log any finishing info, so dont execute progress function

            # _ = display_progress(snakemake_console_log=snakemake_console_log, dry_run=dry_run)
            progress_proc = Process(
                target=display_progress,
                kwargs={
                    "snakemake_console_log": snakemake_console_log,
                    "dry_run": dry_run,
                },
            )
            _ = progress_proc.start()
            _ = progress_proc.join()

        _ = smk_proc.join()
        if smk_proc.exitcode == 0:
            CONSOLE_STDOUT.rule()
            CONSOLE_STDOUT.log(f"Finished running command.", style="success")
        else:
            CONSOLE_STDERR.rule(style="error")
            get_log_tail_errors(snakemake_console_log)
            CONSOLE_STDERR.log(f"Finished running command with error.")

    except Exception as e:
        log_error_and_raise(f"ERROR: {e}\nCheck log.\n")

    CONSOLE_STDOUT.log(f"Used command: {cmd}", style="warning")


def discern_reads(reads: str, read_type: str, input_is_subfolders: bool = True) -> dict:
    """
    Given a file path for reads and read_type, discern the main ID of the sample and which type it is,
    it then replaces the ID of the sample with the string "{barcode}", preparing it for snakemake
    Input:
    - reads: file path to reads in fastq.gz
    - read_type: one of the following ["illumina_pe_reads","illumina_se_reads","ont_reads"]
    """
    structure_dict = {
        "illumina_pe_reads": {
            "pe_basespace": {  # Paired-end reads from basespace
                "re": r"/(.*)_.*ds\..*/\1_S\d+_L\d+_R[12]_\d+.fastq.gz$",
                "smk_format": "{folder_id}/{barcode}_S{trash1}_R{orientation}_{trash2}.fastq.gz",
                "re_file": r"/(.*)_S\d+_L\d+_R[12]_\d+.fastq.gz$",
                "smk_format_file": "{barcode}_S{trash1}_R{orientation}_{trash2}.fastq.gz",
            },
            "pe_any": {  # Paired-end reads from other place (takes whole id)
                "re": r"/(.*)/\1_R[12].fastq.gz$",
                "smk_format": "{folder_id}/{barcode}_R{orientation}.fastq.gz",
                "re_file": r"(.*)_R[12].fastq.gz$",
                "smk_format_file": "{barcode}_R{orientation}.fastq.gz",
            },
        },
        "illumina_se_reads": {
            "se_reads": {  # Single-end reads (?)
                "re": r"/(.*)/\1.fastq.gz$",
                "smk_format": "{folder_id}/{barcode}.fastq.gz",
                "re_file": r"/(.*).fastq.gz$",
                "smk_format_file": "{barcode}.fastq.gz",
            },
        },
        "ont_reads": {
            "ont_guppy": {  # Reads coming from Guppy
                "re": r"/(barcode\d+[A-Z]*)/\1.fastq.gz$",
                "smk_format": "{folder_id}/{barcode}.fastq.gz",
                "re_file": r"/(barcode\d+[A-Z]*).fastq.gz$",
                "smk_format_file": "{barcode}.fastq.gz",
            },
            "ont_porechop": {  # Reads coming from Porechop
                "re": r"/(bc\d+)[A-Z]*/\1.fastq.gz$",
                "smk_format": "{folder_id}/{barcode}.fastq.gz",
                "re_file": r"/(bc\d+)[A-Z]*.fastq.gz$",
                "smk_format_file": "{barcode}.fastq.gz",
            },
            "ont_any": {  # Reads from other place (takes the whole id)
                "re": r"/(.*)/\1.fastq.gz$",
                "smk_format": "{folder_id}/{barcode}.fastq.gz",
                "re_file": r"/(.*).fastq.gz$",
                "smk_format_file": "{barcode}.fastq.gz",
            },
        },
    }
    res_dict = {}
    for structure_name, structure in structure_dict[read_type].items():
        structure_re = structure["re"] if input_is_subfolders else structure["re_file"]
        res = re.search(structure_re, reads)
        if res:
            # print(f"FOUND | ID: {res.group(1)} | STR: {structure_name}")
            barcode = res.group(1)
            smk_format = structure["smk_format"] if input_is_subfolders else structure["smk_format_file"]
            res_dict = {
                "barcode": barcode,
                "found": True,
                "structure_name": structure_name,
                "smk_format": smk_format,
            }
            return res_dict
        else:
            pass
            # print(f"NOT FOUND | STR: {structure_name} | READS: {reads}")

    return {"barcode": None, "found": False}
    # raise Exception(f"Could not identify structure of file {reads}")


def check_reads_substitution_structure(parent_folder: str, read_type: str) -> str:
    """
    Find substitution structure for reads
    The input is the parent_folder, which contains multiple folders or files, and
    each folder can have 1 or 2 files with reads ending in ".fastq.gz".
    These files can be from illumina or ONT, so this is discerned in discern_reads()
    For each file, a structure is returned (if it follows any)
    If all structures are the same, the function passes and returns the final common structure,
    if not it raises an error
    The final common structure can then be used in snakemake.io.glob_wildcards()

    Input:
    - parent_folder: path to folder containing reads or folders with reads
    - read_type: "ont_reads" | "illumina_pe_reads" | "illumina_se_reads"
    Output:
    - common_structure: "{folder_id}/{barcode}.fastq.gz"
    - common_structure_name: ['ont_guppy']
    Possible exceptions:
    - No reads in subfolder
    - Could not find matching structure
    - Not all files follow same substitution structure
    - No available files
    """
    # ---- Check if input has files or subfolders ----
    folders = []
    files = []
    assert Path(parent_folder).exists(), f"Input folder does not exist: {parent_folder}"
    for i in glob.glob(f"{parent_folder}/*"):
        i = Path(i)
        if i.is_dir():
            folders.append(i)
        elif i.is_file() and str(i).endswith(".fastq.gz"):
            files.append(i)

    input_is_subfolders = None
    reads_folders = []
    if folders and files:
        raise Exception(
            f"Expected either all reads files (.fastq.gz) or all folders containing reads (.fastq.gz) inside {parent_folder}"
        )
    elif folders and not files:
        reads_folders = glob.glob(f"{parent_folder}/*/")
        input_is_subfolders = True
    elif not folders and files:
        reads_folders = glob.glob(f"{parent_folder}/")
        input_is_subfolders = False
    else:
        raise Exception(f"No reads found in {parent_folder}")

    # ---- Find structure ----
    smk_formats_found = []
    structure_names_found = []
    for folder in reads_folders:
        reads_files = glob.glob(f"{folder}/*.fastq.gz")
        if len(reads_files) == 0:
            raise Exception(f"ERROR: No files in folder: {folder}")
        else:
            for reads in reads_files:
                res = discern_reads(reads, read_type, input_is_subfolders)
                if res["found"]:
                    # print(f"{reads} | {res['barcode']} | {res['smk_format']}")
                    # print(res)
                    smk_formats_found.append(res["smk_format"])
                    structure_names_found.append(res["structure_name"])
                else:
                    raise Exception(f"ERROR: Could not find structure using {read_type} preset: {reads}")

    smk_formats_found = set(smk_formats_found)
    structure_names_found = set(structure_names_found)
    if len(smk_formats_found) > 1:
        raise Exception(
            f"ERROR: Not all files follow the same substitution structure. Not ready to handle it, rename all reads to have the same name structure. Detected structures: {smk_formats_found}"
        )
    elif len(smk_formats_found) == 0:
        raise Exception(f"ERROR: No input files available in {parent_folder}")
    else:
        common_structure = list(smk_formats_found)[0]
        common_structure_name = list(structure_names_found)
        # print(
        #     f"All files in {parent_folder} follow same structure: Structure='{common_structure}' | Structure names={common_structure_name}"
        # )
        return common_structure, common_structure_name


def get_snakemake_threads(recommended: int, samples: int, available: int, regulator: float = 1):
    """
    Returns an appropiate number of threads to use in a snakemake rule based on
    - recommended: recommended threads for rule
    - samples: number of input samples
    - regulator: total number of threads available

    Examples:
    - get_snakemake_threads(recommended=20, samples=len(wildcards_dict["barcode"]), available=workflow.cores) # typical use
    - get_snakemake_threads(recommended=20, samples=2, available=60) -> 30
    - get_snakemake_threads(recommended=20, samples=1, available=60) -> 60
    - get_snakemake_threads(recommended=20, samples=3, available=60) -> 20
    - get_snakemake_threads(recommended=20, samples=12, available=60) -> 20
    - get_snakemake_threads(recommended=20, samples=2, available=10) -> 20 # snakemake will conform this to the maximum number of cores available (10)
    """
    return int(max(min(available, regulator * available / samples), recommended))


POSSIBLE_FASTA_TERMINATIONS = ["_genomic.fna", "_genomic.fasta", ".fna", ".fasta", ".fas"]
POSSIBLE_GENBANK_TERMINATIONS = [".gbk", ".gbff", ".gb"]


def get_genome_ids(input_files: set, patts=POSSIBLE_FASTA_TERMINATIONS + POSSIBLE_GENBANK_TERMINATIONS) -> dict:
    """
    Input is a list or set of genome files, whose termination is detected and stripped obtainning their ID
    Output is a dict with {ID: path} structure
    """
    assert type(input_files) == list or type(input_files) == set, "Expected set or list"
    input_files = set(input_files)
    d = {}
    for i in input_files:
        id = Path(i).name
        change_n = 0
        for p in patts:
            if re.search(f"{p}$", id):
                id = re.sub(f"{p}$", "", id)
                change_n += 1
        assert change_n > 0, f"File did not end in one of the possible terminations: {i}"
        assert (
            d.get(id) is None
        ), f"Error: While stripping input terminations ({patts}) a repeated ID was found ({id}). Rename files and try again.\n\tPrevious: {d.get(id)}\n\tCurrent {i}"
        d[id] = i

    assert len(set(d.keys())) == len(
        set(input_files)
    ), f"Unexpected error: While stripping input terminations ({patts}) a different number of unique IDs in comparison to input files was obtained"
    return d

