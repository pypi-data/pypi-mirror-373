import os
import sys
from colorama import Fore, Style
from arvia.utils.console_log import CONSOLE_STDOUT, CONSOLE_STDERR, log_error_and_raise
from pathlib import Path

ARVIA_DIR = os.path.abspath(os.path.dirname(__file__))
WORKING_DIR = os.getcwd()
VERSION = "v0.3.4"

from arvia.utils.user_parser import get_parser
from arvia.utils.snakemake_common import run_snakemake
from arvia.utils.test_pipeline import test_arvia_pipeline_input

def main():
    if __name__ == "arvia.arvia":
        def print_help_if_empty_arguments():
            # If there are arguments
            if len(sys.argv)>1:
                # And the first argument is one of these commands (subparsers) and has additional arguments
                if (sys.argv[1] in ["run", "test"] and len(sys.argv)>2) or sys.argv[1] in ["dbs", "test", "--version"]: # ATTENTION: possible commands have to be stated here
                    # keep going
                    return None
            # Elseif no real arguments are given then print help
            # This way calling the tool with no arguments will automatically do --help
            return ['--help']

        parser = get_parser()
        # args = parser.parse_args() 
        args = parser.parse_args(args=print_help_if_empty_arguments()) # if no arguments print help
        command = vars(args)["command"]
        parameters = vars(args)
        del parameters['func']

        CONSOLE_STDOUT.log(f"Starting ARVIA {VERSION}...", style="info", highlight=False)
        # if Path(parameters["output_folder"]).exists() and parameters.get("force") is not True:
        #     log_error_and_raise(f"Output folder already exists and --force is not used. Rerun with --force or choose another directory")

        if command == "run":
            if not parameters["input_yaml"] and (not parameters["reads"] and not parameters["assemblies"]):
                log_error_and_raise("Provide files with --input_yaml or, if files follow specified format, use --reads and/or --assemblies, please.")
            elif parameters["input_yaml"] and (parameters["reads"] or parameters["assemblies"] or parameters["gbks"]):
                log_error_and_raise("You can only provide [--input_yaml] OR [--reads and/or --assemblies and/or --gbks]")
            elif parameters["gbks"] and not parameters["one_to_one"]:
                CONSOLE_STDOUT.log(f"You specified --gbks but not --one_to_one. Comparison between samples will not be performed.", style="info", highlight=False)

            # Run
            run_snakemake(
                f"{ARVIA_DIR}/workflows/arvia.smk",
                parameters,
                f"ARVIA",
            )
        
        elif command == "test":
            _ = test_arvia_pipeline_input(main_output_folder=parameters["output_folder"], full_run=parameters["full_run"])

        elif command == "dbs":
            # Run
            run_snakemake(
                f"{ARVIA_DIR}/workflows/dbs.smk",
                parameters,
                "ARVIA",
            )
            CONSOLE_STDOUT.log(f"If you want to install/update the databases again, please delete the selected --output_folder, which indicates snakemake which steps to run (does not contain the DBs itself): {parameters['output_folder']}", style="info")


        # elif command == "db_install":
        #     run_snakemake(
        #         f"{ARVIA_DIR}/workflows/db_installation/db_installation.smk",
        #         parameters,
        #         "Modular database installation",
        #     )
