import json
from pathlib import Path
from arvia.utils.console_log import CONSOLE_STDERR, CONSOLE_STDOUT
from arvia.arvia import ARVIA_DIR, VERSION
# import arvia
# ARVIA_DIR = arvia.__file__.replace("/__init__.py", "")  # get install directory of arvia

REPORT_LANGUAGE = "en"  # en|es # html reports language

###############################################
# ----------------- Tools ------------------- #
###############################################


################################################
# --------------- Conda envs ----------------- #
################################################

CONDA_ENVS = {
    # --------------------------------
    # If these strings finish in .yml/.yaml snakemake will install the environment
    # If they do not, they will be considered as names of already installed environments
    # --------------------------------
    "arvia": None, # f"{ARVIA_DIR}/envs/arvia.yaml
    # "arvia_mlst": "arvia_mlst", # f"{ARVIA_DIR}/envs/arvia_mlst.yaml
    # "arvia_rgi": "arvia_rgi", # f"{ARVIA_DIR}/envs/arvia_rgi.yaml
}


###############################################
# --------------- Databases ----------------- #
###############################################
# ---- Main reference ----
PAERUGINOSA_GENOME_GBK = f"{ARVIA_DIR}/data/genomes/Pseudomonas_aeruginosa_PAO1_107.gbk"
# PAERUGINOSA_GENOME_GFF = f"{ARVIA_DIR}/data/genomes/Pseudomonas_aeruginosa_PAO1_107.gff"
# PAERUGINOSA_GENOME_FNA = f"{ARVIA_DIR}/data/genomes/Pseudomonas_aeruginosa_PAO1_107.fna"

# ---- oprD P. aeruginosa ----
OPRD_FOLDER = f"{ARVIA_DIR}/data/genes/paeruginosa_oprd"
OPRD_NUCL = f"{OPRD_FOLDER}/oprD.ffn"
OPRD_CONFIG = {
    "oprD": {
        "PGD60817628": {
            "strain": "F23197_6110",
            "gbk": f"{OPRD_FOLDER}/Pseudomonas_aeruginosa_F23197_6110_oprD.gb",
        },
        "PGD23123403": {
            "strain": "FRD1_2621",
            "gbk": f"{OPRD_FOLDER}/Pseudomonas_aeruginosa_FRD1_2621_oprD.gb",
        },
        "PGD252821": {
            "strain": "LESB58_125",
            "gbk": f"{OPRD_FOLDER}/Pseudomonas_aeruginosa_LESB58_125_oprD.gb",
        },
        "PGD11780772": {
            "strain": "MTB-1_210",
            "gbk": f"{OPRD_FOLDER}/Pseudomonas_aeruginosa_MTB-1_210_oprD.gb",
        },
        "PA0958": {
            "strain": "PAO1",
            "gbk": f"{OPRD_FOLDER}/GCF_000006765.1_ASM676v1_genomic_oprD.gb",
        },
    }
}

# ---- Basic YAML config ----
BASE_YAML_CONFIG = {
    "input": {
        "command": "run",
        "input_yaml": None,
        "reads": [],
        "assemblies": [],
        "gbks": [],
    },
    "output": {"output_folder": None},
    "general_params": {
        "one_to_one": bool,
        "min_depth": int,
        "maxsoft": int,
        "previsualize": "yes",
        "barcodes": [],
        "cores": 60,
        "use_conda": True,
        "draw_wf": None,
        "snakemake_console_log": None,
    },
    "other": {
        "arvia_version": VERSION
    }
}
DB_INSTALL_YAML_CONFIG = {
    "input": {
        "command": "dbs",
    },
    "output": {
        "output_folder": None,
    },
    "general_params": {
        "previsualize": None,
        "cores": 60,
        "use_conda": True,
        "draw_wf": None,
        "snakemake_console_log": None,
    },
    "other": {
        "arvia_version": VERSION
    }
}
