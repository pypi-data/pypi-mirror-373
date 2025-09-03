import time
from rich.progress import Progress
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    SpinnerColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
import re
from pathlib import Path
from multiprocessing import Process
import snakemake
from contextlib import redirect_stdout, redirect_stderr
from rich.console import Console
import contextlib
from rich.errors import NotRenderableError
from rich.table import Table
from rich.theme import Theme
import pandas as pd
import sys
from subprocess import run, PIPE
import re

CONSOLE_THEMES = Theme(
    {
        "info": "bold yellow",
        "warning": "bold magenta",
        "danger": "bold red",
        "muted": "#808080",
        "success": "bold green",
    }
)
CONSOLE_STDOUT = Console(log_time_format="[%Y-%m-%d %X] ", log_path=False, theme=CONSOLE_THEMES,)
CONSOLE_STDERR = Console(
    stderr=True, style="danger", log_time_format="[%Y-%m-%d %X] ", log_path=True, theme=CONSOLE_THEMES,
) 
CONSOLE_STDOUT._log_render.omit_repeated_times = False
CONSOLE_STDERR._log_render.omit_repeated_times = False
PROGRESS_BARS = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),  # pct
    TextColumn("•"),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    console=CONSOLE_STDOUT,
    # TimeRemainingColumn(),
    refresh_per_second=10,
)
# def log_error_and_raise(message, console=CONSOLE_STDERR):
#     console.log(message)
#     raise Exception(message)


def log_error_and_raise(message, console=CONSOLE_STDERR):
    try:
        raise Exception(message)
    except Exception as e:
        # console.print_exception(show_locals=False)
        console.log(message)
        sys.exit(1)


def get_log_tail_errors(log_file, lines=40):
    """
    Print last errors in snakemake log file
    """
    assert Path(log_file).exists()

    out = run(
        f"tail -n {lines} {log_file}",
        check=True,
        shell=True,
        encoding="utf-8",
        stdout=PIPE,
        stderr=PIPE,
    )

    # Split command stdout
    tail_stdout_l = out.stdout.split("\n")

    # For each line in the log check if it contains a signal of error or exception
    # if it does, mark that the error starts and store lines
    # finally print lines
    error_message_l = []
    error_starts = False
    for i in tail_stdout_l:
        if error_starts or re.search("exception|error", i.lower()):
            error_starts = True
            error_message_l.append(i)

    if error_starts:
        CONSOLE_STDERR.print(
            Panel("\n".join([f"Displaying last errors found in snakemake log ({log_file})\n"] + error_message_l))
        )
    else:
        CONSOLE_STDERR.log(f"Function get_log_tail_errors was called but no errors were found in snakemake log?")


def rich_display_dataframe(df, title="Dataframe") -> None:
    """Display dataframe as table using rich library.
    Args:
        df (pd.DataFrame): dataframe to display
        title (str, optional): title of the table. Defaults to "Dataframe".
    Raises:
        NotRenderableError: if dataframe cannot be rendered
    Returns:
        rich.table.Table: rich table
    """

    # ensure dataframe contains only string values
    df = df.astype(str)

    table = Table(title=title, header_style="bold #808080", row_styles=["#808080"], border_style="#808080")
    for col in df.columns:
        col_just = "center" if col != "rule_name" else "left"
        table.add_column(col, justify=col_just)
    for row in df.values:
        with contextlib.suppress(NotRenderableError):
            table.add_row(*row)
    CONSOLE_STDOUT.print(table)


def display_progress(snakemake_console_log, dry_run: bool = False, step_selection: list = ["total"]):
    # ---- Get rule table summary ----
    rule_table = False
    CONSOLE_STDOUT.log("Generating rule table...")
    while not rule_table:
        if not Path(snakemake_console_log).exists():
            continue
        with open(snakemake_console_log, "rt") as read_handle:
            job_stats_part = False
            job_stats_l = []
            for line in read_handle:
                line = line.strip()
                if line.startswith("Job stats:") and not job_stats_part:
                    job_stats_part = True
                elif job_stats_part and not line:
                    job_stats_part = False
                    break
                elif (
                    job_stats_part
                    and not line.startswith("-")
                    and not re.search(r"job.+count.+min threads.+max threads", line)
                ):
                    job_stats_l.append(line.split())
                elif (
                    re.search(r"(Error|Exception|SystemExit) in line \d+.+", line)
                    or re.search(r"^Exiting because", line)
                    or re.search(r"^IncompleteFilesException|MissingInputException|SyntaxError|AssertionError", line)
                    # or re.search(r"^RuleException in rule", line)
                ):
                    log_error_and_raise(f"Error: {line}")
                elif re.search(r"^Nothing to be done \(all requested files are present and up to date\)", line):
                    CONSOLE_STDOUT.log("Nothing to be done (all requested files are present and up to date)")
                    return True

        if job_stats_l:
            table_lines = {
                i[0]: {
                    "rule_name": i[0],
                    "count": int(i[1]),
                    "min_threads": int(i[2]),
                    "max_threads": int(i[3]),
                }
                for i in job_stats_l
                if len(i) == 4
            }
            rule_table = True
        else:
            time.sleep(0.25)

    CONSOLE_STDOUT.print()
    rich_display_dataframe(pd.DataFrame(table_lines.values()), "To-do list\n(not in order of execution)")
    CONSOLE_STDOUT.print()

    if dry_run:
        CONSOLE_STDOUT.log("Dry run, progress bars not generated.")
        return True

    # ---- Get rule progress or errors ----
    with PROGRESS_BARS as progress:
        steps_are_selected = False
        if type(step_selection) == list and step_selection:
            steps_are_selected = True
            steps_not_present_in_smk_table = [i for i in step_selection if i not in list(table_lines.keys())]
            assert (
                len(steps_not_present_in_smk_table) == 0
            ), f"Selected rules for progress bar are not a possible job in pipeline: {steps_not_present_in_smk_table}"
        else:
            step_selection = list(table_lines.keys())

        jobs_status = {}
        # jobs_status = {
        #     k: {
        #         "rule_name": v["rule_name"],
        #         "expected_count": v["count"],
        #         "job_status": {
        #             # "1": "started",
        #             # "2": "finished",
        #             # "3": "error",
        #         },
        #         "job_wildcards": {
        #             # "1": ""
        #         },
        #         "progress_bar_id": progress.add_task(k, total=v["count"]),
        #     }
        #     for k, v in table_lines.items()
        # }
        for k, v in table_lines.items():
            jobs_status[k] = {
                "rule_name": v["rule_name"],
                "expected_count": v["count"],
                "job_status": {
                    # "1": "started",
                    # "2": "finished",
                    # "3": "error",
                },
                "job_wildcards": {
                    # "1": ""
                },
            }
            if v["rule_name"] in step_selection:
                jobs_status[k]["progress_bar_id"] = progress.add_task(k, total=v["count"])
            else:
                jobs_status[k]["progress_bar_id"] = None

        def finish():
            for k, v in jobs_status.items():
                if v["progress_bar_id"] is not None:
                    new_total = len(v["job_status"].values()) if v["expected_count"] is None else v["expected_count"]
                    progress.update(
                        v["progress_bar_id"],
                        completed=new_total,
                        total=new_total,
                    )
            return True

        n = 0
        while not progress.finished:
            with open(snakemake_console_log, "rt") as read_handle:
                rule_info_starts = False
                rule_name = None
                jobid = None
                job_wildcards = None
                finished_job_id = None
                failed_job = False
                smk_reported_completed_jobs = None
                smk_reported_total_jobs = None
                finished_pipeline = False
                for line in read_handle:
                    line = line.strip()

                    # Rule start and end info
                    if re.search(r"^(rule|checkpoint|localrule) .+:$", line) and not rule_info_starts:
                        rule_info_starts = True
                        rule_name = re.findall(r"^(rule|checkpoint|localrule) (.+):$", line)[0][1]

                    elif re.search(r"^Error in rule .+:$", line) and not rule_info_starts:
                        rule_info_starts = True
                        failed_job = True
                        rule_name = re.findall(r"^Error in rule (.+):$", line)[0]

                    elif rule_info_starts and re.search(r"^jobid: \d+$", line) and line:
                        jobid = re.findall(r"^jobid: (\d+)$", line)[0]

                    elif rule_info_starts and re.search(r"^wildcards: .+$", line) and line:
                        job_wildcards = re.findall(r"^wildcards: (.+)$", line)[0]

                    elif rule_info_starts and not line:
                        status = "started" if not failed_job else "error"
                        if jobs_status.get(rule_name):
                            jobs_status[rule_name]["job_status"][jobid] = status
                            jobs_status[rule_name]["job_wildcards"][jobid] = job_wildcards
                        else:  # new job name, probably triggered by checkpoint
                            jobs_status[rule_name] = {
                                "rule_name": rule_name,
                                "expected_count": None,  # FIXME
                                "job_status": {jobid: status},
                                "job_wildcards": {jobid: job_wildcards},
                                "progress_bar_id": progress.add_task(rule_name, total=1)
                                if not steps_are_selected
                                else None,
                                "is_additional_task": True,
                            }
                        rule_info_starts = False
                        rule_name = None

                    # Progress line
                    elif re.search(r"^\d+ of \d+ steps \(\d+%\) done$", line):
                        completed_steps, total_steps = re.findall(r"^(\d+) of (\d+) steps \(\d+%\) done$", line)[0]
                        jobs_status["total"]["expected_count"] = int(total_steps)
                        # smk_reported_completed_jobs, smk_reported_total_jobs = re.findall(
                        #     r"^(\d+) of (\d+) steps \(\d+%\) done$", line
                        # )[0]

                    # This line indicates snakemake finished
                    elif re.search(r"^Complete log: .+\.log$", line):
                        finished_pipeline = finish()

                    # Finished job line
                    elif re.search(r"^Finished job \d+\.$", line):
                        finished_job_id = re.findall(r"^Finished job (\d+)\.$", line)[0]

                        # IF rule id is 0 then initial calling rule is done and all jobs are finished
                        if int(finished_job_id) == 0:
                            finished_pipeline = finish()

                        rule_name = [
                            k
                            for k, v in jobs_status.items()
                            if k != "total" and finished_job_id in v["job_status"].keys()
                        ]
                        assert len(rule_name) == 1
                        rule_name = rule_name[0]
                        jobs_status[rule_name]["job_status"][finished_job_id] = "finished"
                        jobs_status["total"]["job_status"][finished_job_id] = "finished"
                        rule_name = None
                        finished_job_id = None

                    # Pipeline error
                    elif re.search(r"^Exiting because|^SyntaxError", line):
                        job_errors = "".join(
                            [
                                f"- {kk} (rule: {k} | wcs: {v['job_wildcards'][kk]})\n"
                                for k, v in jobs_status.items()
                                for kk, vv in v["job_status"].items()
                                if vv == "error"
                            ]
                        )
                        if job_errors:
                            log_error_and_raise(f"Pipeline error: {line}\nError in jobs IDs:\n{job_errors}")
                        else:
                            log_error_and_raise(f"Pipeline error: {line}")

                    # Other error
                    elif re.search(r"^(.+Error|Exception) in line \d+.+", line):
                        raise Exception(f"Error: {line}")

            # If finish() has not been called (finished_pipeline=False) then try to update progress bar
            # if it has been called and finished_pipeline=True, dont update again, finish() already marked everything as completed
            if not finished_pipeline:
                # CONSOLE_STDOUT.log("Updating job completion...", highlight=True)
                for k, v in jobs_status.items():
                    new_total = len(v["job_status"].values()) if v["expected_count"] is None else v["expected_count"]
                    completed = list(v["job_status"].values()).count("finished")
                    started = list(v["job_status"].values()).count("started")
                    advance = 0.5 * started

                    if v["progress_bar_id"] is not None:
                        progress.update(
                            v["progress_bar_id"],
                            advance=advance,
                            completed=completed + advance,
                            total=new_total,
                        )

                if n < 10:  # if in the first lopps sleep less to make it snappy if there are few rules
                    time.sleep(1)
                else:
                    time.sleep(3)
            n += 1

        # CONSOLE_STDOUT.log("All jobs finished!", highlight=True)

    return True

