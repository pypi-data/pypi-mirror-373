import pandas as pd
import glob
import json
import re
import traceback
from pathlib import Path
import logging
from snakemake.logging import logger
import warnings
import datetime
from pprint import pprint

from arvia.arvia import ARVIA_DIR
from arvia.utils.console_log import CONSOLE_STDOUT, CONSOLE_STDERR, log_error_and_raise, rich_display_dataframe
from arvia.utils.local_paths import CONDA_ENVS
# from bactasys.utils.config.local_paths import MLST_DB, MLST_CONFIG
# from bactasys.utils.config.local_paths import CARD_JSON

warnings.simplefilter(action='ignore', category=FutureWarning) # remove warning from pandas
warnings.simplefilter(action='ignore', category=UserWarning) # remove warning from deprecated package in setuptools
# ARVIA_DIR = arvia.__file__.replace("/__init__.py", "")  # get install directory of bactasys
DATETIME_OF_CALL = datetime.datetime.now()


if config:
    snakemake_console_log = config.get("snakemake_console_log")

# ---- Send snakemake log to custom file to parse with custom log ----
if snakemake_console_log is not None:
    handler = logging.FileHandler(snakemake_console_log, mode='a')
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    try:
        # For old snakemake versions
        logger.set_stream_handler(handler)
    except Exception as e:
        # For new snakemake versions
        from arvia.utils.snakemake_logger import LogHandler

        logger.handlers = [LogHandler(None,None)] 


# ---- Input set-up ----

# ---- Output folders ----
PIPELINE_OUTPUT = config["output_folder"]
UPDATE_MLST_OUTPUT = f"{PIPELINE_OUTPUT}/mlst"
UPDATE_AMRFINDER_OUTPUT = f"{PIPELINE_OUTPUT}/amrfinder"




# ---- Params ----
skip_these_mlst_schemas = [
    "achromobacter",
    "abaumannii",
    "abaumannii_2",
    "aeromonas",
    "aactinomycetemcomitans",
    "aphagocytophilum",
    "arcobacter",
    "afumigatus",
    "bcereus",
    "blicheniformis",
    "bsubtilis",
    "bfragilis",
    "bbacilliformis",
    "bhenselae",
    "bwashoensis",
    "bordetella",
    "borrelia",
    "brachyspira",
    "brachyspira",
    "brachyspira",
    "brachyspira",
    "brachyspira",
    "brucella",
    "bcc",
    "bpseudomallei",
    "campylobacter_nonjejuni",
    "campylobacter_nonjejuni",
    "campylobacter_nonjejuni",
    "campylobacter_nonjejuni",
    "campylobacter_nonjejuni",
    "campylobacter",
    "campylobacter_nonjejuni",
    "campylobacter_nonjejuni",
    "campylobacter_nonjejuni",
    "campylobacter_nonjejuni",
    "calbicans",
    "cglabrata",
    "ckrusei",
    "ctropicalis",
    "liberibacter",
    "cmaltaromaticum",
    "chlamydiales",
    "cfreundii",
    "csinensis",
    "cdifficile",
    "cbotulinum",
    "cperfringens",
    "csepticum",
    "diphtheria",
    "cronobacter",
    "pacnes",
    "dnodosus",
    "edwardsiella",
    "ecloacae",
    "efaecalis",
    "efaecium",
    "escherichia",
    "ecoli",
    "fpsychrophilum",
    "gallibacterium",
    "geotrichum",
    "hparasuis",
    "hinfluenzae",
    "hcinaedi",
    "helicobacter",
    "hsuis",
    "kingella",
    "kaerogenes",
    "koxytoca",
    "klebsiella",
    "kseptempunctata",
    "lsalivarius",
    "llactis_phage",
    "leptospira",
    "leptospira",
    "leptospira",
    "listeria",
    "mcanis",
    "mcaseolyticus",
    "msciuri",
    "mhaemolytica",
    "mplutonius",
    "mcatarrhalis_achtman",
    "mycobacteria",
    "mabscessus",
    "magalactiae",
    "manserisalpingitidis",
    "mbovis",
    "mflocculare",
    "mgallisepticum",
    "mgallisepticum",
    "mhominis",
    "mhyopneumoniae",
    "mhyorhinis",
    "miowae",
    "mpneumoniae",
    "msynoviae",
    "neisseria",
    "otsutsugamushi",
    "orhinotracheale",
    "plarvae",
    "pmultocida",
    "pmultocida",
    "ppentosaceus",
    "pdamselae",
    "psalmonis",
    "pgingivalis",
    "rhodococcus",
    "ranatipestifer",
    "salmonella",
    "sparasitica",
    "shewanella",
    "sinorhizobium",
    "saureus",
    "schromogenes",
    "sepidermidis",
    "shaemolyticus",
    "shominis",
    "staphlugdunensis",
    "spseudintermedius",
    "smaltophilia",
    "sagalactiae",
    "sbsec",
    "scanis",
    "sdysgalactiae",
    "sgallolyticus",
    "oralstrep",
    "spneumoniae",
    "spyogenes",
    "ssuis",
    "streptothermophilus",
    "sthermophilus",
    "suberis",
    "szooepidemicus",
    "streptomyces",
    "taylorella",
    "tenacibaculum",
    "tpallidum",
    "tvaginalis",
    "ureaplasma",
    "vcholerae",
    "vcholerae",
    "vparahaemolyticus",
    "vibrio",
    "vtapetis",
    "vvulnificus",
    "wolbachia",
    "xfastidiosa",
    "ypseudotuberculosis_achtman",
    "yruckeri",
    "abaumannii_2",
    "blicheniformis_14",
    "bordetella_3",
    "brachyspira_2",
    "brachyspira_3",
    "brachyspira_4",
    "brachyspira_5",
    "campylobacter_nonjejuni_2",
    "campylobacter_nonjejuni_3",
    "campylobacter_nonjejuni_4",
    "campylobacter_nonjejuni_5",
    "campylobacter_nonjejuni_6",
    "campylobacter_nonjejuni_7",
    "campylobacter_nonjejuni_8",
    "campylobacter_nonjejuni_9",
    "diphtheria_3",
    "leptospira_2",
    "leptospira_3",
    "listeria_2",
    "mbovis_2",
    "mcatarrhalis_achtman_6",
    "mgallisepticum_2",
    "mhominis_3",
    "mycobacteria_2",
    "pacnes_3",
    "pmultocida_2",
    "salmonella_2",
    "vcholerae_2",
    "ypseudotuberculosis_achtman_3",
]


# --- Other ----


##########################################
# --------------- Rules ---------------- #
##########################################

rule update_amrfinder:
    output:
        folder=directory(UPDATE_AMRFINDER_OUTPUT),
    threads: 4
    conda:
        CONDA_ENVS["arvia"]
    log:
        Path(UPDATE_AMRFINDER_OUTPUT, "arvia.log")
    shell:
        """
        (
        amrfinder -u
        downloaded_db_dir="$(grep 'Database directory: ' {log} | awk '{{ print $3 }}')"
        db_dir="$(dirname "$downloaded_db_dir")"

        cd ${{db_dir}}/latest
        wget https://ftp.ncbi.nlm.nih.gov/pathogen/Antimicrobial_resistance/AMRFinderPlus/database/latest/ReferenceGeneCatalog.txt
        ) &> {log}
        """

rule update_mlst:
    output:
        folder=directory(UPDATE_MLST_OUTPUT),
    params:
        skip_these_mlst_schemas_csv = ",".join(skip_these_mlst_schemas)
    threads: 1 # HAS TO BE "1" OR NGINX WILL PUSH BACK AND SEND HTMLs instead of FASTAs
    conda:
        CONDA_ENVS["arvia"]
    log:
        Path(UPDATE_MLST_OUTPUT, "arvia.log")
    shell:
        """
        (
        # Figure out where mlst is installed
        mlst_path="$(which mlst)"
        env_bin_path="$(dirname "$mlst_path")"
        env_path="$(dirname "$env_bin_path")"
        db_parent_path="${{env_path}}/db"
        org_db_path="${{db_parent_path}}/pubmlst"
        updated_db_path="${{db_parent_path}}/pubmlst-update"
        timestamp="$(date +%s)"

        # Log some things
        echo ""
        echo "mlst tool is installed in ${{mlst_path}}"
        echo "will download updated database to ${{updated_db_path}}"
        echo "will then replace previous database (${{org_db_path}}) with the new one"
        echo "previous database will be kept as ${{org_db_path}}.old.${{timestamp}}"
        echo ""
        
        # Go into the scripts folder (you need to have write access!)
        cd ${{env_bin_path}}
        
        # Run the downloader script (you need 'wget' installed)
        ./mlst-download_pub_mlst -d ${{updated_db_path}} -x {params.skip_these_mlst_schemas_csv} -j {threads} | bash 

        # Save the old database folder
        mv ${{org_db_path}} ${{org_db_path}}.old.${{timestamp}}
        mv ${{updated_db_path}} ${{org_db_path}}
        
        # Regenerate the BLAST database
        ./mlst-make_blast_db
        
        # Check schemes are installed
        mlst --longlist

        ) &> {log}
        """

        ### I dont know why this does not work
        # # Check that files are actually fastas or whatever and not a nginx error message
        # errors="$("Too Many Requests" $updated_db_path/*/* | wc -l)"
        # echo $errors
        # if [ $errors -gt 0 ]; then
        #     echo "FATAL ERROR: 'too many requests error' found at least ${{errors}} time(s) on downloaded files in ${{updated_db_path}}."
        #     echo "This means at least one file is corrupted. Try again wih less threads."
        #     exit 1 
        # fi


rule all:
    input:
        rules.update_amrfinder.output.folder,
        rules.update_mlst.output.folder,
    default_target: True


