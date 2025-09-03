
from pathlib import Path
import glob
from subprocess import run, PIPE
from pprint import pprint
from arvia.utils.console_log import CONSOLE_STDOUT, CONSOLE_STDERR, log_error_and_raise, rich_display_dataframe
import yaml
from colorama import Fore, Style
import traceback

def test_arvia_pipeline_input(main_output_folder: Path, full_run: bool = False):
    # Variables
    # main_output_folder = "/home/usuario/Proyectos/Results/tests/arvia/test_pipeline"
    sratoolkit_url = "https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.2.1/sratoolkit.3.2.1-ubuntu64.tar.gz"
    sratoolkit_targz = f"{main_output_folder}/sratoolkit.tar.gz"
    sratoolkit_folder = f"{main_output_folder}/sratoolkit"
    arvia_folder = f"{main_output_folder}/arvia"
    fasterq_dump = f"{main_output_folder}/sratoolkit/sratoolkit*/bin/fasterq-dump"
    input_yaml_file = f"{main_output_folder}/arvia_test_input.yaml"
    TEST_SAMPLES = {
        "SAMN44420630": {
            "SRR32735229": {
                "file_type": "reads",
                "notes": "pacbio"
            },
            "SRR31104317": {
                "file_type": "reads",
                "notes": "illumina"
            },
            "GCA_043962715.1": {
                "url": "https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/GCA_043962715.1/download?include_annotation_type=GENOME_FASTA&hydrated=FULLY_HYDRATED",
                "file_type": "assembly",
            },
            "GCA_043962715.1_gbk": {
                "url": "https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/GCA_043962715.1/download?include_annotation_type=GENOME_GBFF&hydrated=FULLY_HYDRATED",
                "file_type": "gbk"
            }
        }
    }


    CONSOLE_STDOUT.log(f"Running ARVIA input test..", style="info")

    # Assert folder does not exist
    try:
        assert not Path(main_output_folder).exists(), f"Output folder exists, will not overwrite. Please delete or select non-existent folder and try again. ({main_output_folder})"
    except Exception as e:
        log_error_and_raise(f"{e}")

    # Create main directory
    CONSOLE_STDOUT.log(f"Creating output folder... ({main_output_folder})", style="muted")
    _ = run(f"mkdir -p {main_output_folder} {sratoolkit_folder} {arvia_folder}", check=True, shell=True)

    # Test ARVIA help menus
    try:
        CONSOLE_STDOUT.log("Testing ARVIA's help menus...", style="info")
        _ = run(f"arvia --version > {arvia_folder}/help.log", check=True, shell=True)
        _ = run(f"arvia --help > {arvia_folder}/help.log", check=True, shell=True)
        _ = run(f"arvia run --help > {arvia_folder}/help.log", check=True, shell=True)
        _ = run(f"arvia test --help > {arvia_folder}/help.log", check=True, shell=True)

    except Exception as e:
        log_error_and_raise(f"{traceback.format_exc()}\nFailed running ARVIA's help messages: {e}")

    # Download sratoolkit and decompress
    if not glob.glob(fasterq_dump):
        try:
            CONSOLE_STDOUT.log("Installing SRA Toolkit...", style="info")
            CONSOLE_STDOUT.log("Downloading SRA Toolkit...", style="muted")
            _ = run(f"wget -O {sratoolkit_targz} --quiet {sratoolkit_url} ", check=True, shell=True)
            CONSOLE_STDOUT.log("Decompressing SRA Toolkit...", style="muted")
            _ = run(f"tar -xf {sratoolkit_targz} -C {sratoolkit_folder}", check=True, shell=True)
        except Exception as e:
            log_error_and_raise(f"{traceback.format_exc()}\nCould not download/decompress SRA Toolkit: {e}")
    else:
        CONSOLE_STDOUT.log("fasterqdump present, skipping download of SRA Toolkit...", style="info")

    # ---- Download files ----
    FILES_DICT = {key: {"paired-end": [], "single-end": [], "assembly": [], "gbk": []} for key in TEST_SAMPLES.keys()}
    
    CONSOLE_STDOUT.log("Downloading files...", style="info")
    try:
        for biosample_id, v in TEST_SAMPLES.items():
            for accession_id, vv in v.items():
                CONSOLE_STDOUT.log(f"Downloading {accession_id} from {biosample_id}", style="muted")
                dw_folder = f"{main_output_folder}/dw/{biosample_id}/{accession_id}"
                assert not Path(dw_folder).exists(), ""
                _ = run(f"mkdir -p {dw_folder}", check=True, shell=True)

                # Download reads from SRA
                if vv["file_type"]=="reads":
                    _ = run(
                        f"{fasterq_dump} --split-3 --temp {main_output_folder} --outdir {dw_folder} {accession_id} > {dw_folder}/download.log", 
                        check=True, shell=True, 
                        capture_output = True,
                        text = True
                    )
                    _ = run(f"pigz {dw_folder}/*.fastq", check=True, shell=True)
                    
                    fs = glob.glob(f"{dw_folder}/*.fastq.gz")
                    if len(fs) not in [1,2]:
                        raise Exception(f"Unexpected. Number of files downloaded from {accession_id} ({biosample_id}) were not 1 or 2: {fs}")

                    if len(fs) == 1:
                        FILES_DICT[biosample_id]["single-end"] = fs
                    if len(fs) == 2:
                        FILES_DICT[biosample_id]["paired-end"] = fs
                
                # Download assembblies using links
                elif vv["file_type"] in ["assembly", "gbk"]:
                    file_suffix = ".fna" if vv["file_type"] == "assembly" else ".gbff"
                    _ = run(
                        f"wget --quiet -O {dw_folder}/ncbi_download.zip '{vv['url']}' > {dw_folder}/download.log", 
                        check=True, shell=True
                    )
                    _ = run(
                        f"unzip -qq -j {dw_folder}/ncbi_download.zip 'ncbi_dataset/data/*/*{file_suffix}' -d '{dw_folder}' > {dw_folder}/decompress.log", 
                        check=True, shell=True
                    )
                    _ = run(f"rm {dw_folder}/ncbi_download.zip", check=True, shell=True)
                    fs = glob.glob(f"{dw_folder}/*{file_suffix}")
                    if len(fs) == 1:
                        FILES_DICT[biosample_id][vv["file_type"]] = fs
                    else:
                        raise Exception(f"Expected only one assembly/gbk: {fs=}")
                    
                else:
                    raise Exception(f"Unexpected file_type: {vv['file_type']}")
                
                CONSOLE_STDOUT.log(f"Finished download {accession_id} from {biosample_id}", style="muted")

    except Exception as e:
        log_error_and_raise(f"{traceback.format_exc()}\nError downloading file: {e}")


    # Generate input YAML for ARVIA
    CONSOLE_STDOUT.log("Generating input YAML...", style="info")
    with open(input_yaml_file, "w") as out_handle:
        for biosample_id, values in FILES_DICT.items():
            out_handle.write(f"# ---- {biosample_id} ----\n")  # section title

            # Full with short reads, assembly and gbk
            yaml.dump(
                {
                    f"{biosample_id}_full_pe_with_gbk": {
                        "reads": values["paired-end"],
                        "assembly": values["assembly"],
                        "gbk": values["gbk"],
                    },
                }, 
                out_handle, default_flow_style=False, sort_keys=False
            )
            # Full with long reads, assembly and gbk
            yaml.dump(
                {
                    f"{biosample_id}_full_se_with_gbk": {
                        "reads": values["single-end"],
                        "assembly": values["assembly"],
                        "gbk": values["gbk"],
                    },
                }, 
                out_handle, default_flow_style=False, sort_keys=False
            )
            # Full with short reads and assembly
            yaml.dump(
                {
                    f"{biosample_id}_full_pe": {
                        "reads": values["paired-end"],
                        "assembly": values["assembly"],
                    },
                }, 
                out_handle, default_flow_style=False, sort_keys=False
            )
            # Full with long reads and assembly
            yaml.dump(
                {
                    f"{biosample_id}_full_se": {
                        "reads": values["single-end"],
                        "assembly": values["assembly"],
                    },
                }, 
                out_handle, default_flow_style=False, sort_keys=False
            )
            # Only assembly
            yaml.dump(
                {
                    f"{biosample_id}_only_assembly": {
                        "assembly": values["assembly"],
                    },
                }, 
                out_handle, default_flow_style=False, sort_keys=False
            )
            # Only short reads
            yaml.dump(
                {
                    f"{biosample_id}_only_pe": {
                        "reads": values["paired-end"],
                    },
                }, 
                out_handle, default_flow_style=False, sort_keys=False
            )
            # Only long reads
            yaml.dump(
                {
                    f"{biosample_id}_only_se": {
                        "reads": values["single-end"],
                    },
                }, 
                out_handle, default_flow_style=False, sort_keys=False
            )
            out_handle.write("\n")

    # Test running ARVIA
    try:
        _ = run(f"mkdir -p {arvia_folder}", check=True, shell=True)
        if full_run:
            CONSOLE_STDOUT.log("Running ARVIA with input YAML and without --previsualize...", style="info")
            _ = run(f"arvia run --input_yaml {input_yaml_file} --output_folder {arvia_folder} --one_to_one > {arvia_folder}/arvia.log", check=True, shell=True)
        else:
            CONSOLE_STDOUT.log("Running ARVIA with input YAML and --previsualize...", style="info")
            _ = run(f"arvia run --input_yaml {input_yaml_file} --output_folder {arvia_folder} --one_to_one --previsualize > {arvia_folder}/arvia.log", check=True, shell=True)

        # CONSOLE_STDOUT.log("Running ARVIA with input YAML...")
        # _ = run(f"arvia run --input_yaml {input_yaml_file} --output_folder {arvia_folder}", check=True, shell=True)

        CONSOLE_STDOUT.log("Test finished succesfully!", style="success")

    except Exception as e:
        log_error_and_raise(f"{traceback.format_exc()}\nFailed running ARVIA pipeline: {e}\nCheck log in {arvia_folder}/arvia.log")

    return True

