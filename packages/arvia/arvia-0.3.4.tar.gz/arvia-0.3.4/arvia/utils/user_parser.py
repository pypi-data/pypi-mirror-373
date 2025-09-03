from colorama import Fore, Style
import argparse, textwrap
import os

# import arvia
from arvia.arvia import VERSION
from rich_argparse import RichHelpFormatter, ArgumentDefaultsRichHelpFormatter
from arvia.utils.console_log import CONSOLE_STDOUT, CONSOLE_STDERR


ASCII =f"""
{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}           _______      _______          {Style.RESET_ALL}
{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}     /\   |  __ \ \    / /_   _|   /\    {Style.RESET_ALL}
{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}    /  \  | |__) \ \  / /  | |    /  \   {Style.RESET_ALL}
{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}   / /\ \ |  _  / \ \/ /   | |   / /\ \  {Style.RESET_ALL}
{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}  / ____ \| | \ \  \  /   _| |_ / ____ \ {Style.RESET_ALL}
{Style.BRIGHT}{Fore.LIGHTYELLOW_EX} /_/    \_\_|  \_\  \/   |_____/_/    \_\{Style.RESET_ALL}
{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}                                         {Style.RESET_ALL}
"""



RichHelpFormatter.styles["argparse.groups"] = "white bold"
RichHelpFormatter.styles["argparse.default"] = ""
# RichHelpFormatter._max_help_position = 52
# RichHelpFormatter._width = 200

class CustomFormatter(
    RichHelpFormatter,
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.MetavarTypeHelpFormatter,
    argparse.RawTextHelpFormatter,
):
    pass


# Top-level parser
parser = argparse.ArgumentParser(
    description=f"{Fore.YELLOW}{Style.BRIGHT}ARVIA:{Style.RESET_ALL} {Style.BRIGHT}A{Style.RESET_ALL}ntibiotic {Style.BRIGHT}R{Style.RESET_ALL}esistance {Style.BRIGHT}V{Style.RESET_ALL}ariant {Style.BRIGHT}I{Style.RESET_ALL}dentifier for Pseudomonas {Style.BRIGHT}a{Style.RESET_ALL}eruginosa",
    allow_abbrev=False,
    formatter_class=RichHelpFormatter,
    # usage=argparse.SUPPRESS,
    # add_help=False
)
parser.add_argument(
    "-v", "--version",
    action="version",
    version=f"ARVIA {VERSION}",
)
parser.set_defaults(func=lambda x: parser.print_usage())

subparsers = parser.add_subparsers(help="command", required=True, dest="command")

########################
# ---- Main ARVIA ---- #
########################
parser_run_arvia = subparsers.add_parser(
    "run",
    help=f"Run ARVIA",
    description=f"{Fore.YELLOW}{Style.BRIGHT}ARVIA:{Style.RESET_ALL} {Style.BRIGHT}A{Style.RESET_ALL}ntibiotic {Style.BRIGHT}R{Style.RESET_ALL}esistance {Style.BRIGHT}V{Style.RESET_ALL}ariant {Style.BRIGHT}I{Style.RESET_ALL}dentifier for Pseudomonas {Style.BRIGHT}a{Style.RESET_ALL}eruginosa",
    formatter_class=lambda prog: CustomFormatter(prog, max_help_position=60, width=140), 
    add_help=False
)
parser_run_arvia__in_out = parser_run_arvia.add_argument_group("Input/Output")
parser_run_arvia__req_params = parser_run_arvia.add_argument_group("Required arguments")
parser_run_arvia__opt_params = parser_run_arvia.add_argument_group("Additional arguments")

parser_run_arvia__in_out.add_argument(
    "-i", "--input_yaml", 
    required=False,
    metavar="path",
    type=os.path.abspath,
    help=f"Input files from a YAML. Each key is a sample_id containing two lists of paths with keys 'reads' and 'assembly'",
    dest="input_yaml",
)
parser_run_arvia__in_out.add_argument(
    "-r", "--reads", 
    required=False,
    metavar="path",
    type=os.path.abspath,
    nargs="+",
    help=f"Input reads files. Can be paired-end or single-end and must follow one of these structures: '{{sample_id}}.fastq.gz' / '{{sample_id}}_R[1,2].fastq.gz' / '{{sample_id}}_[1,2].fastq.gz' / '{{sample_id}}_S\\d+_L\\d+_R[1,2]_\\d+.fastq.gz'",
    dest="reads",
)
parser_run_arvia__in_out.add_argument(
    "-a", "--assemblies", 
    required=False,
    metavar="path",
    type=os.path.abspath,
    nargs="+",
    help=f"Input assembly files. Must follow one of these structures: '{{sample_id}}.{{fasta,fna,fa,fas}}'",
    dest="assemblies",
)
parser_run_arvia__in_out.add_argument(
    "-g", "--gbks", 
    required=False,
    metavar="path",
    type=os.path.abspath,
    nargs="+",
    help=f"Input annotated assembly files in GBK format. Only used in 1 vs 1 comparisons if given --one_to_one. Must follow one of these structures: '{{sample_id}}.{{gbk}}'",
    dest="gbks",
)
parser_run_arvia__in_out.add_argument(
    "-o", "--output_folder", 
    required=False,
    metavar="path",
    default="./arvia",
    type=os.path.abspath,
    help=f"Output folder",
    dest="output_folder",
)
parser_run_arvia__opt_params.add_argument(
    "--one_to_one", 
    required=False,
    action="store_true",
    help=f"Compare input samples between themselves using the assembly/annotated assembly of each one as reference. At least one assembly is neccessary.",
    dest="one_to_one",
)
parser_run_arvia__opt_params.add_argument(
    "-d", "--min_depth", 
    required=False,
    metavar="int",
    default=5,
    type=int,
    help=f"Minimum depth for mutation to pass (--mincov in snippy)",
    dest="min_depth",
)
parser_run_arvia__opt_params.add_argument(
    "-s", "--maxsoft", 
    required=False,
    metavar="int",
    default=1000,
    type=int,
    help=f"Maximum soft clipping allowed (--maxsoft in snippy)",
    dest="maxsoft",
)
parser_run_arvia__opt_params.add_argument(
    "-c", "--cores", 
    required=False,
    metavar="int",
    default=max(1, os.cpu_count()-1),
    type=int,
    help=f"Number of cores (default is available cores - 1)",
    dest="cores",
)
parser_run_arvia__opt_params.add_argument(
    "-p", "--previsualize", 
    required=False,
    action="store_true",
    help=f"Previsualize pipeline to see if everything is as expected",
    dest="previsualize",
)
parser_run_arvia__opt_params.add_argument(
    "--use_conda",
    required=False,
    action="store_true",
    help=f"If True, use conda environment specified by snakefile",
    dest="use_conda",
)
parser_run_arvia__opt_params.add_argument(
    "--barcodes",
    required=False,
    metavar="str",
    type=str,
    nargs="+",
    help=f"Space separated list of sample IDs. Only these samples will be processed",
    dest="barcodes",
)
parser_run_arvia__opt_params.add_argument(
    "--draw_wf",
    required=False,
    default=None,
    metavar="str",
    type=str,
    help=f"Draw pipeline to this path (PDF)",
    dest="draw_wf",
)
parser_run_arvia__opt_params.add_argument("-h", "--help", action="help", help="show this help message and exit")

########################
# ---- Test ARVIA ---- #
########################
parser_test_arvia = subparsers.add_parser(
    "test",
    help=f"Test ARVIA with a set of test files from SRA to ensure it is working properly (needs internet).",
    description=f"Test ARVIA with a set of test files from SRA to ensure it is working properly (needs internet).",
    formatter_class=lambda prog: CustomFormatter(prog, max_help_position=60, width=140),
    add_help=False
)

parser_test_arvia__in_out = parser_test_arvia.add_argument_group("Input/Output")
parser_test_arvia__req_params = parser_test_arvia.add_argument_group("Required parameters")
parser_test_arvia__opt_params = parser_test_arvia.add_argument_group("Optional parameters")

parser_test_arvia__in_out.add_argument(
    "-o", "--output_folder", 
    required=False,
    metavar="path",
    default="./arvia_test",
    type=os.path.abspath,
    help=f"Output folder",
    dest="output_folder",
)
parser_test_arvia__in_out.add_argument(
    "-f", "--full_run", 
    required=False,
    action="store_true",
    help=f"Fully run `arvia run` instead of --previsualize mode.",
    dest="full_run",
)

parser_test_arvia__opt_params.add_argument("-h", "--help", action="help", help="show this help message and exit")


########################
# ---- Install DB ---- #
########################
parser_installdb_arvia = subparsers.add_parser(
    "dbs",
    help=f"Install/update databases like amrfinderplus and mlst in current environment (needs internet).",
    description=f"Install/update databases like amrfinderplus and mlst in current environment (needs internet).",
    formatter_class=lambda prog: CustomFormatter(prog, max_help_position=60, width=140),
    add_help=False
)

parser_installdb_arvia__in_out = parser_installdb_arvia.add_argument_group("Input/Output")
parser_installdb_arvia__req_params = parser_installdb_arvia.add_argument_group("Required parameters")
parser_installdb_arvia__opt_params = parser_installdb_arvia.add_argument_group("Optional parameters")

parser_installdb_arvia__in_out.add_argument(
    "-o", "--output_folder", 
    required=False,
    metavar="path",
    default="./arvia_dbs",
    type=os.path.abspath,
    help=f"Output folder",
    dest="output_folder",
)
parser_installdb_arvia__opt_params.add_argument(
    "-c", "--cores", 
    required=False,
    metavar="int",
    default=max(1, os.cpu_count()-1),
    type=int,
    help=f"Number of cores (default is available cores - 1)",
    dest="cores",
)
parser_installdb_arvia__opt_params.add_argument(
    "-p", "--previsualize", 
    required=False,
    action="store_true",
    help=f"Previsualize pipeline to see if everything is as expected",
    dest="previsualize",
)
parser_installdb_arvia__opt_params.add_argument(
    "--use_conda",
    required=False,
    action="store_true",
    help=f"If True, use conda environment specified by snakefile",
    dest="use_conda",
)
parser_installdb_arvia__opt_params.add_argument(
    "--barcodes",
    required=False,
    metavar="str",
    type=str,
    nargs="+",
    help=f"Space separated list of sample IDs. Only these samples will be processed",
    dest="barcodes",
)
parser_installdb_arvia__opt_params.add_argument(
    "--draw_wf",
    required=False,
    default=None,
    metavar="str",
    type=str,
    help=f"Draw pipeline to this path (PDF",
    dest="draw_wf",
)
parser_installdb_arvia__opt_params.add_argument("-h", "--help", action="help", help="show this help message and exit")



def get_parser(parser=parser, subparsers=subparsers):
    print(ASCII)
    return parser
