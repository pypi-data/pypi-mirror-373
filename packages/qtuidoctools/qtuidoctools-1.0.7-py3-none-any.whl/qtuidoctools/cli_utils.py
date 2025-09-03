#!/usr/bin/env python3
# this_file: src/qtuidoctools/cli_utils.py
"""
CLI utilities and logging/UX helpers for qtuidoctools.

Contains:
- Rich console instance and color theme
- Structured logging helpers
- User-facing progress/summary presenters
- Small CLI helpers (paths, YAML cleanup)

Keeping `__main__.py` thin by centralizing reusable logic here.
"""

from __future__ import annotations

import logging
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Single shared console for consistent output across modules
console = Console()

# Centralized color palette for consistent theming
COLORS = {
    "success": "bright_green",
    "error": "bright_red",
    "warning": "yellow",
    "info": "bright_blue",
    "progress": "cyan",
    "accent": "magenta",
    "muted": "dim white",
}


def setup_structured_logging(
    verbose: bool = False, debug: bool = False
) -> logging.Logger:
    """Configure structured logging with Rich handler and return module logger."""
    from rich.logging import RichHandler

    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )

    logging.basicConfig(
        level=log_level, format="%(message)s", datefmt="[%X]", handlers=[rich_handler]
    )

    logger = logging.getLogger("qtuidoctools")
    logger.setLevel(log_level)
    return logger


def log_processing_start(logger: logging.Logger, method: str, **params):
    param_str = ", ".join(f"{k}={v}" for k, v in params.items() if v is not None)
    logger.info(
        f"[{COLORS['info']}]🚀 Starting {method}[/] operation with params: {param_str}"
    )


def log_processing_step(
    logger: logging.Logger, step: str, details: str = "", level: str = "info"
):
    color = COLORS.get(level, COLORS["info"])
    if details:
        logger.log(getattr(logging, level.upper()), f"[{color}]▸ {step}[/]: {details}")
    else:
        logger.log(getattr(logging, level.upper()), f"[{color}]▸ {step}[/]")


def log_file_operation(
    logger: logging.Logger,
    operation: str,
    file_path: str,
    status: str = "success",
    details: str = "",
):
    status_color = COLORS["success"] if status == "success" else COLORS["error"]
    status_icon = "✅" if status == "success" else "❌"
    file_name = Path(file_path).name
    message = f"[{status_color}]{status_icon} {operation}[/] [{COLORS['accent']}]{file_name}[/]"
    if details:
        message += f" - {details}"
    (logger.info if status == "success" else logger.error)(message)


def log_performance_metrics(
    logger: logging.Logger,
    operation: str,
    files_count: int,
    elapsed_time: float,
    workers: int = 1,
    success_count: int | None = None,
    error_count: int | None = None,
):
    success_count = success_count or files_count
    error_count = error_count or 0
    avg_time = elapsed_time / files_count if files_count > 0 else 0
    files_per_sec = files_count / elapsed_time if elapsed_time > 0 else 0

    metrics = [
        f"[{COLORS['success']}]{success_count} successful[/]",
        f"[{COLORS['error']}]{error_count} failed[/]" if error_count > 0 else None,
        f"[{COLORS['info']}]{elapsed_time:.2f}s total[/]",
        f"[{COLORS['muted']}]{avg_time:.3f}s avg[/]",
        f"[{COLORS['muted']}]{files_per_sec:.1f} files/sec[/]",
    ]
    metrics_str = " | ".join(filter(None, metrics))
    if workers > 1:
        logger.info(
            f"[{COLORS['accent']}]📊 {operation} Performance[/] ({workers} workers): {metrics_str}"
        )
    else:
        logger.info(f"[{COLORS['accent']}]📊 {operation} Performance[/]: {metrics_str}")


def log_validation_error(
    logger: logging.Logger, error_type: str, message: str, suggestion: str | None = None
):
    logger.error(f"[{COLORS['error']}]❌ {error_type}[/]: {message}")
    if suggestion:
        logger.info(f"[{COLORS['info']}]💡 Suggestion[/]: {suggestion}")


def format_user_error(
    error: Exception, context: str = "", suggestions: list[str] | None = None
) -> str:
    error_msg = f"[{COLORS['error']}]{type(error).__name__}[/]: {str(error)}"
    if context:
        error_msg += f"\n[{COLORS['muted']}]Context[/]: {context}"
    if suggestions:
        error_msg += f"\n[{COLORS['info']}]Suggestions[/]:"
        for i, suggestion in enumerate(suggestions, 1):
            error_msg += f"\n  {i}. {suggestion}"
    return error_msg


def show_version(__version__: str):
    console.print(
        f"[{COLORS['accent']}]qtuidoctools[/], version [{COLORS['info']}]{__version__}[/]"
    )


def show_processing_summary(total_files: int, workers: int, mode: str = "parallel"):
    if mode == "parallel" and workers > 1:
        console.print(
            f"\n[{COLORS['info']}]🚀 Processing {total_files} UI files with {workers} parallel workers...[/]"
        )
    elif mode == "sequential":
        console.print(
            f"\n[{COLORS['info']}]📄 Processing {total_files} UI files sequentially...[/]"
        )
    else:
        console.print(
            f"\n[{COLORS['info']}]📄 Processing {total_files} UI file(s)...[/]"
        )


def show_parallel_results(
    successful_files: list[str],
    failed_files: list[dict[str, Any]],
    elapsed_time: float,
    verbose: bool = False,
):
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("Status", style=COLORS["accent"])
    table.add_column("Count", justify="right", style=COLORS["info"])
    table.add_column("Details", style=COLORS["muted"])
    table.add_row(
        "✅ Successful",
        str(len(successful_files)),
        f"{len(successful_files)} files processed",
    )
    if failed_files:
        table.add_row(
            "❌ Failed", str(len(failed_files)), f"{len(failed_files)} files had errors"
        )

    summary_text = f"Completed in [{COLORS['success']}]{elapsed_time:.2f} seconds[/]"
    if len(successful_files) > 1:
        avg_time = elapsed_time / len(successful_files)
        summary_text += f" ([{COLORS['muted']}]~{avg_time:.2f}s per file[/])"

    console.print(
        Panel(
            table,
            title=f"[{COLORS['success']}]Parallel Processing Results[/]",
            subtitle=summary_text,
            border_style=COLORS["success"],
        )
    )

    if failed_files:
        console.print(f"\n[{COLORS['error']}]Failed files:[/]")
        for failed_result in failed_files:
            file_name = (
                Path(failed_result["file_path"]).name
                if isinstance(failed_result, dict)
                else Path(failed_result).name
            )
            if isinstance(failed_result, dict) and "error_message" in failed_result:
                error_msg = failed_result["error_message"]
                error_type = failed_result.get("error_type", "Unknown")
                console.print(
                    f"  [dim red]• {file_name}[/] - [{COLORS['error']}]{error_type}[/]: {error_msg}"
                )
                if verbose and "error_traceback" in failed_result:
                    console.print("    [dim red]Traceback:[/]")
                    for line in failed_result["error_traceback"].split("\n"):
                        if line.strip():
                            console.print(f"    [dim red]{line}[/]")
            else:
                console.print(f"  [dim red]• {file_name}[/]")


def show_worker_progress(results: list[dict[str, Any]], quiet: bool = False):
    if quiet:
        return
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    for result in successful:
        file_name = Path(result["file_path"]).name
        widgets = result["widgets_found"]
        time_taken = result["processing_time"]
        status_text = f"[{COLORS['success']}]✓[/] {file_name}"
        if widgets > 0:
            status_text += (
                f" [{COLORS['muted']}]({widgets} widgets, {time_taken:.2f}s)[/]"
            )
        else:
            status_text += f" [{COLORS['muted']}]({time_taken:.2f}s)[/]"
        console.print(status_text)
    for result in failed:
        file_name = Path(result["file_path"]).name
        error = result["error_message"]
        console.print(
            f"[{COLORS['error']}]✗[/] {file_name} - [{COLORS['error']}]{error}[/]"
        )


def clipaths(uidir: str | None, uipath: str | None) -> list[str]:
    """Compute UI paths from a directory or a single path; exit with guidance when missing."""
    from .qtui import getUiPaths

    if uidir:
        uipaths = getUiPaths(dir=uidir)
    elif uipath:
        uipaths = getUiPaths(path=uipath)
    else:
        error_msg = (
            "Missing required input: UI directory or file not specified\n\n"
            "You must specify either a UI directory or a single UI file to process.\n\n"
            "Options:\n  --uidir=PATH     Process all .ui files in directory (recursive)\n  --uixml=PATH     Process a single .ui file\n\n"
            "Examples:\n  qtuidoctools update --uidir=./ui_files --outyamldir=./docs\n  qtuidoctools update --uixml=mainwindow.ui --outyamldir=./docs\n\n"
            "Use --help for complete usage information."
        )
        console.print(f"[{COLORS['error']}]❌ {error_msg}[/]")
        sys.exit(2)
    return uipaths


def cleanUpYamlData(
    data: dict[str, OrderedDict[str, str]], allowEmpty: bool = True
) -> dict[str, OrderedDict[str, str]]:
    """Clean up YAML data structure by sorting keys and optionally pruning empty values."""
    for ctr in data:
        od = data[ctr]
        nd: OrderedDict[str, str] = OrderedDict()
        for k, v in sorted(od.items(), key=lambda t: t[0]):
            if allowEmpty:
                nd[k] = v
            else:
                if isinstance(v, str) and v.lstrip().rstrip():
                    nd[k] = v
        data[ctr] = nd
    return data
