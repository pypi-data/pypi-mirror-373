#!/usr/bin/env python3
"""
AutoClean EEG Pipeline - Command Line Interface

This module provides a flexible CLI for AutoClean that works both as a
standalone tool (via uv tool) and within development environments.
"""

import argparse
import csv
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from autoclean import __version__
from autoclean.utils.audit import verify_access_log_integrity
from autoclean.utils.auth import get_auth0_manager, is_compliance_mode_enabled
# Simple branding constants
PRODUCT_NAME = "AutoClean EEG"
TAGLINE = "Professional EEG Processing & Analysis Platform" 
LOGO_ICON = "🧠"
DIVIDER = "═════════════════════════════════════════════════"
from autoclean.utils.config import (
    disable_compliance_mode,
    enable_compliance_mode,
    get_compliance_status,
    load_user_config,
    save_user_config,
)
from autoclean.utils.database import DB_PATH
from autoclean.utils.logging import message
from autoclean.utils.task_discovery import (
    extract_config_from_task,
    get_task_by_name,
    get_task_overrides,
    safe_discover_tasks,
)
from autoclean.utils.user_config import UserConfigManager, user_config

# Try to import database functions (used conditionally in login)
try:
    from autoclean.utils.database import (
        manage_database_conditionally,
        set_database_path,
    )

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Try to import inquirer (used for interactive setup)
try:
    import inquirer

    INQUIRER_AVAILABLE = True
except ImportError:
    INQUIRER_AVAILABLE = False

# Try to import autoclean core components (may fail in some environments)
try:
    from autoclean.core.pipeline import Pipeline

    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser for AutoClean CLI."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Basic Usage:
  autocleaneeg-pipeline setup                          # First time setup
  autocleaneeg-pipeline process RestingEyesOpen data.raw   # Process single file
  autocleaneeg-pipeline list-tasks                     # Show available tasks
  autocleaneeg-pipeline review                         # Start review GUI

Custom Tasks:
  autocleaneeg-pipeline task add my_task.py            # Add custom task file
  autocleaneeg-pipeline task list                      # List all tasks


For detailed help on any command: autocleaneeg-pipeline <command> --help
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process EEG data")

    # Positional arguments for simple usage: autocleaneeg-pipeline process TaskName FilePath
    process_parser.add_argument(
        "task_name", nargs="?", type=str, help="Task name (e.g., RestingEyesOpen)"
    )
    process_parser.add_argument(
        "input_path", nargs="?", type=Path, help="EEG file or directory to process"
    )

    # Optional named arguments (for advanced usage)
    process_parser.add_argument(
        "--task", type=str, help="Task name (alternative to positional)"
    )
    process_parser.add_argument(
        "--task-file", type=Path, help="Python task file to use"
    )

    # Input options (for advanced usage)
    process_parser.add_argument(
        "--file",
        type=Path,
        help="Single EEG file to process (alternative to positional)",
    )
    process_parser.add_argument(
        "--dir",
        "--directory",
        type=Path,
        dest="directory",
        help="Directory containing EEG files to process (alternative to positional)",
    )

    process_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: workspace/output)",
    )
    process_parser.add_argument(
        "--format",
        type=str,
        default="*.set",
        help="File format glob pattern for directory processing (default: *.set). Examples: '*.raw', '*.edf', '*.set'. Note: '.raw' will be auto-corrected to '*.raw'",
    )
    process_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search subdirectories recursively",
    )
    process_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without running",
    )
    process_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose/debug output",
    )
    process_parser.add_argument(
        "--parallel",
        "-p",
        type=int,
        metavar="N",
        help="Process files in parallel (default: 3 concurrent files, max: 8)",
    )
    # List tasks command (alias for 'task list')
    list_tasks_parser = subparsers.add_parser(
        "list-tasks", help="List all available tasks"
    )
    list_tasks_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed information"
    )
    list_tasks_parser.add_argument(
        "--overrides",
        action="store_true",
        help="Show workspace tasks that override built-in tasks",
    )

    # Review command
    review_parser = subparsers.add_parser("review", help="Start review GUI")
    review_parser.add_argument(
        "--output",
        type=Path,
        required=False,  # Changed from required=True to required=False
        help="AutoClean output directory to review (default: workspace/output)",
    )

    # Task management commands
    task_parser = subparsers.add_parser("task", help="Manage custom tasks")
    task_subparsers = task_parser.add_subparsers(
        dest="task_action", help="Task actions"
    )

    # Add task
    add_task_parser = task_subparsers.add_parser("add", help="Add a custom task")
    add_task_parser.add_argument("task_file", type=Path, help="Python task file to add")
    add_task_parser.add_argument(
        "--name", type=str, help="Custom name for the task (default: filename)"
    )
    add_task_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing task with same name"
    )

    # Remove task
    remove_task_parser = task_subparsers.add_parser(
        "remove", help="Remove a custom task"
    )
    remove_task_parser.add_argument(
        "task_name", type=str, help="Name of the task to remove"
    )

    # List all tasks (replaces old list-tasks command)
    list_all_parser = task_subparsers.add_parser(
        "list", help="List all available tasks"
    )
    list_all_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed information"
    )
    list_all_parser.add_argument(
        "--overrides",
        action="store_true",
        help="Show workspace tasks that override built-in tasks",
    )

    # Show config location
    config_parser = subparsers.add_parser("config", help="Manage user configuration")
    config_subparsers = config_parser.add_subparsers(
        dest="config_action", help="Config actions"
    )

    # Show config location
    config_subparsers.add_parser("show", help="Show configuration directory location")

    # Setup/reconfigure workspace
    config_subparsers.add_parser("setup", help="Reconfigure workspace location")

    # Reset config
    reset_parser = config_subparsers.add_parser(
        "reset", help="Reset configuration to defaults"
    )
    reset_parser.add_argument(
        "--confirm", action="store_true", help="Confirm the reset action"
    )

    # Export/import config
    export_parser = config_subparsers.add_parser("export", help="Export configuration")
    export_parser.add_argument(
        "export_path", type=Path, help="Directory to export configuration to"
    )

    import_parser = config_subparsers.add_parser("import", help="Import configuration")
    import_parser.add_argument(
        "import_path", type=Path, help="Directory to import configuration from"
    )

    # Setup command (same as config setup for simplicity)
    setup_parser = subparsers.add_parser("setup", help="Setup or reconfigure workspace")
    setup_parser.add_argument(
        "--compliance-mode",
        action="store_true",
        help="Enable FDA 21 CFR Part 11 compliance mode with Auth0 authentication",
    )

    # Export access log command
    export_log_parser = subparsers.add_parser(
        "export-access-log",
        help="Export database access log with integrity verification",
    )
    export_log_parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: access-log-{timestamp}.json)",
    )
    export_log_parser.add_argument(
        "--format",
        choices=["json", "csv", "human"],
        default="json",
        help="Output format (default: json)",
    )
    export_log_parser.add_argument(
        "--start-date", type=str, help="Start date filter (YYYY-MM-DD format)"
    )
    export_log_parser.add_argument(
        "--end-date", type=str, help="End date filter (YYYY-MM-DD format)"
    )
    export_log_parser.add_argument(
        "--operation", type=str, help="Filter by operation type"
    )
    export_log_parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify integrity, don't export data",
    )
    export_log_parser.add_argument(
        "--database",
        type=Path,
        help="Path to database file (default: auto-detect from workspace)",
    )

    # Authentication commands (for compliance mode)
    subparsers.add_parser("login", help="Login to Auth0 for compliance mode")
    subparsers.add_parser("logout", help="Logout and clear authentication tokens")
    subparsers.add_parser("whoami", help="Show current authenticated user")
    auth_diag_parser = subparsers.add_parser(
        "auth0-diagnostics", help="Diagnose Auth0 configuration and connectivity issues"
    )
    auth_diag_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed diagnostic information",
    )

    # Clean task command
    clean_task_parser = subparsers.add_parser(
        "clean-task", help="Remove task output directory and database entries"
    )
    clean_task_parser.add_argument("task", help="Task name to clean")
    clean_task_parser.add_argument(
        "--output-dir", type=Path, help="Output directory (defaults to configured workspace)"
    )
    clean_task_parser.add_argument(
        "--force", action="store_true", help="Skip confirmation prompt"
    )
    clean_task_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be deleted without actually deleting"
    )

    # View command
    view_parser = subparsers.add_parser("view", help="View EEG files using MNE-QT Browser")
    view_parser.add_argument("file", type=Path, help="Path to EEG file")
    view_parser.add_argument("--no-view", action="store_true", help="Validate without viewing")

    # Version command
    subparsers.add_parser("version", help="Show version information")    # Help command (for consistency)
    subparsers.add_parser("help", help="Show detailed help information")

    # Tutorial command
    subparsers.add_parser(
        "tutorial", help="Show a helpful tutorial for first-time users"
    )

    return parser


def validate_args(args) -> bool:
    """Validate command line arguments."""
    if args.command == "process":
        # Normalize positional vs named arguments
        task_name = args.task_name or args.task
        input_path = args.input_path or args.file or args.directory

        # Check that either task or task-file is provided
        if not task_name and not args.task_file:
            message("error", "Either task name or --task-file must be specified")
            return False

        if task_name and args.task_file:
            message("error", "Cannot specify both task name and --task-file")
            return False

        # Check input exists - with fallback to task config
        if input_path and not input_path.exists():
            message("error", f"Input path does not exist: {input_path}")
            return False
        elif not input_path:
            # Try to get input_path from task config as fallback
            task_input_path = None
            if task_name:
                task_input_path = extract_config_from_task(task_name, "input_path")

            if task_input_path:
                input_path = Path(task_input_path)
                if not input_path.exists():
                    message(
                        "error",
                        f"Input path from task config does not exist: {input_path}",
                    )
                    return False
                message("info", f"Using input path from task config: {input_path}")
            else:
                message(
                    "error",
                    "Input file or directory must be specified (via CLI or task config)",
                )
                return False

        # Store normalized values back to args
        args.final_task = task_name
        args.final_input = input_path

        # Check task file exists if provided
        if args.task_file and not args.task_file.exists():
            message("error", f"Task file does not exist: {args.task_file}")
            return False

    elif args.command == "review":
        # Set default output directory if not provided
        if not args.output:
            args.output = user_config.get_default_output_dir()
            message("info", f"Using default workspace output directory: {args.output}")
        
        if not args.output.exists():
            message("error", f"Output directory does not exist: {args.output}")
            return False

    return True


def cmd_process(args) -> int:
    """Execute the process command."""
    try:
        # Check if Pipeline is available
        if not PIPELINE_AVAILABLE:
            message(
                "error",
                "Pipeline not available. Please ensure autoclean is properly installed.",
            )
            return 1

        # Initialize pipeline with verbose logging if requested
        pipeline_kwargs = {"output_dir": args.output}
        if args.verbose:
            pipeline_kwargs["verbose"] = "debug"

        pipeline = Pipeline(**pipeline_kwargs)

        # Add Python task file if provided
        if args.task_file:
            task_name = pipeline.add_task(args.task_file)
            message("info", f"Loaded Python task: {task_name}")
        else:
            task_name = args.final_task

            # Check if this is a custom task using the new discovery system
            task_class = get_task_by_name(task_name)
            if task_class:
                # Task found via discovery system
                message("info", f"Loaded task: {task_name}")
            else:
                # Fall back to old method for compatibility
                custom_task_path = user_config.get_custom_task_path(task_name)
                if custom_task_path:
                    task_name = pipeline.add_task(custom_task_path)
                    message(
                        "info",
                        f"Loaded custom task '{args.final_task}' from user configuration",
                    )

        if args.dry_run:
            message("info", "DRY RUN - No processing will be performed")
            message("info", f"Would process: {args.final_input}")
            message("info", f"Task: {task_name}")
            message("info", f"Output: {args.output}")
            if args.final_input.is_dir():
                message("info", f"File format: {args.format}")
                if args.recursive:
                    message("info", "Recursive search: enabled")
            return 0

        # Process files
        if args.final_input.is_file():
            message("info", f"Processing single file: {args.final_input}")
            pipeline.process_file(file_path=args.final_input, task=task_name)
        else:
            message("info", f"Processing directory: {args.final_input}")
            message("info", f"Using file format: {args.format}")
            if args.recursive:
                message("info", "Recursive search: enabled")
            
            # Use parallel processing if requested
            if hasattr(args, 'parallel') and args.parallel:
                import asyncio
                max_concurrent = min(max(1, args.parallel), 8)  # Clamp between 1-8
                message("info", f"Parallel processing: {max_concurrent} concurrent files")
                asyncio.run(pipeline.process_directory_async(
                    directory_path=args.final_input,
                    task=task_name,
                    pattern=args.format,
                    sub_directories=args.recursive,
                    max_concurrent=max_concurrent,
                ))
            else:
                pipeline.process_directory(
                    directory=args.final_input,
                    task=task_name,
                    pattern=args.format,
                    recursive=args.recursive,
                )
        message("info", "Processing completed successfully!")
        return 0

    except Exception as e:
        message("error", f"Processing failed: {str(e)}")
        return 1


def cmd_list_tasks(args) -> int:
    """Execute the list-tasks command."""
    try:
        console = Console()

        # If --overrides flag is specified, show override information
        if hasattr(args, "overrides") and args.overrides:
            overrides = get_task_overrides()

            if not overrides:
                console.print("\n[green]✓[/green] [bold]No Task Overrides[/bold]")
                console.print(
                    "[dim]All tasks are using their built-in package versions.[/dim]"
                )
                return 0

            console.print(
                f"\n[bold]Task Overrides[/bold] [dim]({len(overrides)} found)[/dim]\n"
            )

            override_table = Table(
                show_header=True, header_style="bold yellow", box=None, padding=(0, 1)
            )
            override_table.add_column("Task Name", style="cyan", no_wrap=True)
            override_table.add_column("Workspace Source", style="green")
            override_table.add_column("Built-in Source", style="dim")
            override_table.add_column("Description", style="dim", max_width=40)

            for override in sorted(overrides, key=lambda x: x.task_name):
                workspace_file = Path(override.workspace_source).name
                builtin_file = Path(override.builtin_source).name
                override_table.add_row(
                    override.task_name,
                    workspace_file,
                    builtin_file,
                    override.description or "No description",
                )

            override_panel = Panel(
                override_table,
                title="[bold]Workspace Tasks Overriding Built-in Tasks[/bold]",
                border_style="yellow",
                padding=(1, 1),
            )
            console.print(override_panel)

            console.print(
                "\n[dim]💡 Tip: Move workspace tasks to a different name to use built-in versions.[/dim]"
            )
            return 0

        valid_tasks, invalid_files, skipped_files = safe_discover_tasks()

        console.print("\n[bold]Available Processing Tasks[/bold]\n")

        # --- Built-in Tasks ---
        built_in_tasks = [
            task for task in valid_tasks if "autoclean/tasks" in task.source
        ]
        if built_in_tasks:
            built_in_table = Table(
                show_header=True, header_style="bold blue", box=None, padding=(0, 1)
            )
            built_in_table.add_column("Task Name", style="cyan", no_wrap=True)
            built_in_table.add_column("Module", style="dim")
            built_in_table.add_column("Description", style="dim", max_width=50)

            for task in sorted(built_in_tasks, key=lambda x: x.name):
                # Extract just the module name from the full path
                module_name = Path(task.source).stem
                built_in_table.add_row(
                    task.name, module_name + ".py", task.description or "No description"
                )

            built_in_panel = Panel(
                built_in_table,
                title="[bold]Built-in Tasks[/bold]",
                border_style="blue",
                padding=(1, 1),
            )
            console.print(built_in_panel)
        else:
            console.print(
                Panel(
                    "[dim]No built-in tasks found[/dim]",
                    title="[bold]Built-in Tasks[/bold]",
                    border_style="blue",
                    padding=(1, 1),
                )
            )

        # --- Custom Tasks ---
        custom_tasks = [
            task for task in valid_tasks if "autoclean/tasks" not in task.source
        ]
        if custom_tasks:
            custom_table = Table(
                show_header=True, header_style="bold magenta", box=None, padding=(0, 1)
            )
            custom_table.add_column("Task Name", style="magenta", no_wrap=True)
            custom_table.add_column("File", style="dim")
            custom_table.add_column("Description", style="dim", max_width=50)

            for task in sorted(custom_tasks, key=lambda x: x.name):
                # Show just the filename for custom tasks
                file_name = Path(task.source).name
                custom_table.add_row(
                    task.name, file_name, task.description or "No description"
                )

            custom_panel = Panel(
                custom_table,
                title="[bold]Custom Tasks[/bold]",
                border_style="magenta",
                padding=(1, 1),
            )
            console.print(custom_panel)
        else:
            console.print(
                Panel(
                    "[dim]No custom tasks found.\n"
                    "Use [yellow]autocleaneeg-pipeline task add <file.py>[/yellow] to add one.[/dim]",
                    title="[bold]Custom Tasks[/bold]",
                    border_style="magenta",
                    padding=(1, 1),
                )
            )

        # --- Skipped Task Files ---
        if skipped_files:
            skipped_table = Table(
                show_header=True, header_style="bold yellow", box=None, padding=(0, 1)
            )
            skipped_table.add_column("File", style="yellow", no_wrap=True)
            skipped_table.add_column("Reason", style="dim", max_width=70)

            for file in skipped_files:
                # Show just the filename for skipped files
                file_name = Path(file.source).name
                skipped_table.add_row(file_name, file.reason)

            skipped_panel = Panel(
                skipped_table,
                title="[bold]Skipped Task Files[/bold]",
                border_style="yellow",
                padding=(1, 1),
            )
            console.print(skipped_panel)

        # --- Invalid Task Files ---
        if invalid_files:
            invalid_table = Table(
                show_header=True, header_style="bold red", box=None, padding=(0, 1)
            )
            invalid_table.add_column("File", style="red", no_wrap=True)
            invalid_table.add_column("Error", style="yellow", max_width=70)

            for file in invalid_files:
                # Show relative path if in workspace, otherwise just filename
                file_path = Path(file.source)
                if file_path.is_absolute():
                    display_name = file_path.name
                else:
                    display_name = file.source

                invalid_table.add_row(display_name, file.error)

            invalid_panel = Panel(
                invalid_table,
                title="[bold]Invalid Task Files[/bold]",
                border_style="red",
                padding=(1, 1),
            )
            console.print(invalid_panel)

        # Summary statistics
        console.print(
            f"\n[dim]Found {len(valid_tasks)} valid tasks "
            f"({len(built_in_tasks)} built-in, {len(custom_tasks)} custom), "
            f"{len(skipped_files)} skipped files, and {len(invalid_files)} invalid files[/dim]"
        )

        return 0

    except Exception as e:
        message("error", f"Failed to list tasks: {str(e)}")
        return 1


def cmd_review(args) -> int:
    """Execute the review command."""
    try:
        # Check if Pipeline is available
        if not PIPELINE_AVAILABLE:
            message(
                "error",
                "Pipeline not available. Please ensure autoclean is properly installed.",
            )
            return 1

        pipeline = Pipeline(output_dir=args.output)

        message("info", f"Starting review GUI for: {args.output}")
        pipeline.start_autoclean_review()

        return 0

    except Exception as e:
        message("error", f"Failed to start review GUI: {str(e)}")
        return 1


def cmd_setup(args) -> int:
    """Run the interactive setup wizard."""
    try:
        # Check if compliance mode flag was passed
        if hasattr(args, "compliance_mode") and args.compliance_mode:
            return _setup_compliance_mode()
        else:
            return _run_interactive_setup()
    except KeyboardInterrupt:
        # User canceled - exit gracefully without error message
        return 0
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return 1


def _simple_header(console, title: str, subtitle: str = None):
    """Simple, consistent header for setup."""
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    
    console.print()
    
    # Create branding content
    branding_text = Text()
    branding_text.append(f"{LOGO_ICON} Welcome to AutoClean", style="bold bright_cyan")
    branding_text.append(f"\n{TAGLINE}", style="bright_blue")
    
    # Create panel with branding
    branding_panel = Panel(
        Align.center(branding_text),
        style="cyan",
        padding=(0, 1),
        title_align="center"
    )
    
    console.print(branding_panel)
    console.print()
    console.print(f"[bold green]{title}[/bold green]")
    if subtitle:
        console.print(f"[yellow]{subtitle}[/yellow]")
    console.print()


def _run_interactive_setup() -> int:
    """Run interactive setup wizard with arrow key navigation."""
    from rich.console import Console
    
    try:
        console = Console()
        _simple_header(console, "Setup Wizard", "Use arrow keys to navigate, Enter to select")
        
        if not INQUIRER_AVAILABLE:
            console.print("[yellow]⚠[/yellow] Interactive prompts not available. Running basic setup...")
            user_config.setup_workspace()
            return 0

        # Get current compliance status
        compliance_status = get_compliance_status()
        is_enabled = compliance_status["enabled"]
        is_permanent = compliance_status["permanent"]

        # Display compliance status - simple
        if is_permanent:
            console.print("[yellow]⚠[/yellow] FDA 21 CFR Part 11 compliance mode is permanently enabled")
            console.print("[blue]ℹ[/blue] You can only configure workspace location in compliance mode")
        elif is_enabled:
            console.print("[blue]ℹ[/blue] FDA 21 CFR Part 11 compliance mode is currently enabled")
        else:
            console.print("[dim]Current compliance mode: disabled[/dim]")

        # Check if compliance mode is permanently enabled
        if is_permanent:
            # Only allow workspace configuration
            questions = [
                inquirer.List(
                    "setup_type",
                    message="What would you like to configure?",
                    choices=[
                        ("Configure workspace location", "workspace_only"),
                        ("Exit setup", "exit"),
                    ],
                    default="workspace_only",
                )
            ]
        else:
            # Build setup options - simplified to 2 choices
            choices = [
                ("Basic setup (workspace + standard research use)", "basic"),
            ]

            if is_enabled:
                choices.append(
                    (
                        "Disable FDA 21 CFR Part 11 compliance mode",
                        "disable_compliance",
                    )
                )
            else:
                choices.append(
                    ("Enable FDA 21 CFR Part 11 compliance mode", "enable_compliance")
                )

            questions = [
                inquirer.List(
                    "setup_type",
                    message="What would you like to configure?",
                    choices=choices,
                    default="basic",
                )
            ]

        answers = inquirer.prompt(questions)
        if not answers:  # User canceled
            return 0

        setup_type = answers["setup_type"]

        if setup_type == "exit":
            return 0
        elif setup_type == "basic":
            # Basic setup always includes workspace configuration
            return _setup_basic_mode()
        elif setup_type == "enable_compliance":
            # Enable compliance mode
            return _enable_compliance_mode()
        elif setup_type == "disable_compliance":
            # Disable compliance mode
            return _disable_compliance_mode()
        elif setup_type == "compliance":
            # Legacy compliance setup (permanent)
            return _setup_compliance_mode()

    except KeyboardInterrupt:
        return 0
    except Exception as e:
        console.print(f"[red]❌[/red] Interactive setup failed: {str(e)}")
        return 1


def _setup_basic_mode() -> int:
    """Setup basic (non-compliance) mode."""
    from rich.console import Console
    
    try:
        console = Console()
        
        if not INQUIRER_AVAILABLE:
            user_config.setup_workspace()
            return 0

        console.print()
        console.print("[bold green]Basic Setup Configuration[/bold green]")
        console.print("[dim]Workspace + standard research use[/dim]")
        console.print()

        # Always run full workspace setup (includes prompting to change location if exists)
        # Don't show branding since we already showed it at the start of setup
        workspace_path = user_config.setup_workspace(show_branding=False)
        
        # Update user configuration - auto-backup enabled by default
        user_config_data = load_user_config()

        # Ensure compliance and workspace are dictionaries
        if not isinstance(user_config_data.get("compliance"), dict):
            user_config_data["compliance"] = {}
        if not isinstance(user_config_data.get("workspace"), dict):
            user_config_data["workspace"] = {}

        user_config_data["compliance"]["enabled"] = False
        user_config_data["workspace"]["auto_backup"] = True  # Always enabled for safety

        save_user_config(user_config_data)

        console.print("[green]✓[/green] Basic setup complete!")
        console.print("[blue]ℹ[/blue] You can now use AutoClean for standard EEG processing")
        console.print("[blue]ℹ[/blue] Run 'autocleaneeg-pipeline process TaskName file.raw' to get started")

        return 0

    except Exception as e:
        console.print(f"[red]❌[/red] Basic setup failed: {str(e)}")
        return 1


def _setup_compliance_mode() -> int:
    """Setup FDA 21 CFR Part 11 compliance mode with developer-managed Auth0."""
    from autoclean.utils.cli_display import setup_display
    
    try:
        if not INQUIRER_AVAILABLE:
            setup_display.error("Interactive setup requires 'inquirer' package")
            setup_display.info("Install with: pip install inquirer")
            return 1

        setup_display.blank_line()
        setup_display.header("FDA 21 CFR Part 11 Compliance Setup", "Regulatory compliance mode")
        setup_display.warning("Once enabled, compliance mode cannot be disabled")
        setup_display.blank_line()
        setup_display.console.print("[bold]This mode provides:[/bold]")
        setup_display.list_item("Mandatory user authentication")
        setup_display.list_item("Tamper-proof audit trails")
        setup_display.list_item("Encrypted data storage")
        setup_display.list_item("Electronic signature support")
        setup_display.blank_line()

        # Confirm user understands permanent nature
        confirm_question = [
            inquirer.Confirm(
                "confirm_permanent",
                message="Do you understand that compliance mode cannot be disabled once enabled?",
                default=False,
            )
        ]

        confirm_answer = inquirer.prompt(confirm_question)
        if not confirm_answer or not confirm_answer["confirm_permanent"]:
            setup_display.info("Compliance mode setup canceled")
            return 0

        # Setup Part-11 workspace with suffix
        user_config.setup_part11_workspace()

        # Ask about electronic signatures
        signature_question = [
            inquirer.Confirm(
                "require_signatures",
                message="Require electronic signatures for processing runs?",
                default=True,
            )
        ]

        signature_answer = inquirer.prompt(signature_question)
        if not signature_answer:
            return 0

        # Configure Auth0 manager with developer credentials
        auth_manager = get_auth0_manager()
        auth_manager.configure_developer_auth0()

        # Update user configuration
        user_config_data = load_user_config()

        # Ensure compliance and workspace are dictionaries
        if not isinstance(user_config_data.get("compliance"), dict):
            user_config_data["compliance"] = {}
        if not isinstance(user_config_data.get("workspace"), dict):
            user_config_data["workspace"] = {}

        user_config_data["compliance"]["enabled"] = True
        user_config_data["compliance"]["permanent"] = True  # Cannot be disabled
        user_config_data["compliance"]["auth_provider"] = "auth0"
        user_config_data["compliance"]["require_electronic_signatures"] = (
            signature_answer["require_signatures"]
        )
        user_config_data["workspace"][
            "auto_backup"
        ] = True  # Always enabled for compliance

        save_user_config(user_config_data)

        setup_display.success("Compliance mode setup complete!")
        setup_display.blank_line()
        setup_display.console.print("[bold]Next steps:[/bold]")
        setup_display.list_item("Run 'autocleaneeg-pipeline login' to authenticate", indent=0)
        setup_display.list_item("Use 'autocleaneeg-pipeline whoami' to check authentication status", indent=0)
        setup_display.list_item("All processing will now include audit trails and user authentication", indent=0)

        return 0

    except Exception as e:
        setup_display.error("Compliance setup failed", str(e))
        return 1


def _enable_compliance_mode() -> int:
    """Enable FDA 21 CFR Part 11 compliance mode (non-permanent)."""
    try:
        if not INQUIRER_AVAILABLE:
            message("error", "Interactive setup requires 'inquirer' package.")
            return 1

        message("info", "\n🔐 Enable FDA 21 CFR Part 11 Compliance Mode")
        message("info", "This mode provides:")
        message("info", "• User authentication (when processing)")
        message("info", "• Audit trails")
        message("info", "• Electronic signature support")
        message("info", "• Can be disabled later")

        # Confirm enabling
        confirm_question = [
            inquirer.Confirm(
                "confirm_enable", message="Enable compliance mode?", default=True
            )
        ]

        confirm_answer = inquirer.prompt(confirm_question)
        if not confirm_answer or not confirm_answer["confirm_enable"]:
            message("info", "Compliance mode not enabled.")
            return 0

        # Configure Auth0 manager with developer credentials
        try:
            auth_manager = get_auth0_manager()
            auth_manager.configure_developer_auth0()
            message("info", "✓ Auth0 configured")
        except Exception as e:
            message("warning", f"Auth0 configuration failed: {e}")
            message("info", "You can configure Auth0 later for authentication")

        # Enable compliance mode (non-permanent)
        if enable_compliance_mode(permanent=False):
            message("success", "✓ Compliance mode enabled!")
            message("info", "\nNext steps:")
            message(
                "info", "1. Run 'autocleaneeg-pipeline login' to authenticate (when needed)"
            )
            message("info", "2. Run 'autocleaneeg-pipeline setup' again to disable if needed")
            return 0
        else:
            message("error", "Failed to enable compliance mode")
            return 1

    except Exception as e:
        message("error", f"Failed to enable compliance mode: {e}")
        return 1


def _disable_compliance_mode() -> int:
    """Disable FDA 21 CFR Part 11 compliance mode."""
    try:
        if not INQUIRER_AVAILABLE:
            message("error", "Interactive setup requires 'inquirer' package.")
            return 1

        message("info", "\n🔓 Disable FDA 21 CFR Part 11 Compliance Mode")

        # Check if permanent
        compliance_status = get_compliance_status()
        if compliance_status["permanent"]:
            message("error", "Cannot disable permanently enabled compliance mode")
            return 1

        message("warning", "This will disable:")
        message("warning", "• Required authentication")
        message("warning", "• Audit trail logging")
        message("warning", "• Electronic signatures")

        # Confirm disabling
        confirm_question = [
            inquirer.Confirm(
                "confirm_disable",
                message="Are you sure you want to disable compliance mode?",
                default=False,
            )
        ]

        confirm_answer = inquirer.prompt(confirm_question)
        if not confirm_answer or not confirm_answer["confirm_disable"]:
            message("info", "Compliance mode remains enabled.")
            return 0

        # Disable compliance mode
        if disable_compliance_mode():
            message("success", "✓ Compliance mode disabled!")
            message("info", "AutoClean will now operate in standard mode")
            return 0
        else:
            message("error", "Failed to disable compliance mode")
            return 1

    except Exception as e:
        message("error", f"Failed to disable compliance mode: {e}")
        return 1


# FUTURE FEATURE: User-managed Auth0 setup (commented out for now)
# def _setup_compliance_mode_user_managed() -> int:
#     """Setup FDA 21 CFR Part 11 compliance mode with user-managed Auth0."""
#     try:
#         import inquirer
#         from autoclean.utils.config import load_user_config, save_user_config
#         from autoclean.utils.auth import get_auth0_manager, validate_auth0_config
#
#         message("info", "\n🔐 FDA 21 CFR Part 11 Compliance Setup")
#         message("warning", "This mode requires Auth0 account and application setup.")
#
#         # Setup workspace first
#         user_config.setup_workspace()
#
#         # Explain Auth0 requirements
#         message("info", "\nAuth0 Application Setup Instructions:")
#         message("info", "1. Create an Auth0 account at https://auth0.com")
#         message("info", "2. Go to Applications > Create Application")
#         message("info", "3. Choose 'Native' as the application type (for CLI apps)")
#         message("info", "4. In your application settings, configure:")
#         message("info", "   - Allowed Callback URLs: http://localhost:8080/callback")
#         message("info", "   - Allowed Logout URLs: http://localhost:8080/logout")
#         message("info", "   - Grant Types: Authorization Code, Refresh Token (default for Native)")
#         message("info", "5. Copy your Domain, Client ID, and Client Secret")
#         message("info", "6. Your domain will be something like: your-tenant.us.auth0.com\n")
#
#         # Confirm user is ready
#         ready_question = [
#             inquirer.Confirm(
#                 'auth0_ready',
#                 message="Do you have your Auth0 application configured and credentials ready?",
#                 default=False
#             )
#         ]
#
#         ready_answer = inquirer.prompt(ready_question)
#         if not ready_answer or not ready_answer['auth0_ready']:
#             message("info", "Please set up your Auth0 application first, then run:")
#             message("info", "autoclean setup --compliance-mode")
#             return 0
#
#         # Get Auth0 configuration
#         auth_questions = [
#             inquirer.Text(
#                 'domain',
#                 message="Auth0 Domain (e.g., your-tenant.auth0.com)",
#                 validate=lambda _, x: len(x) > 0 and '.auth0.com' in x
#             ),
#             inquirer.Text(
#                 'client_id',
#                 message="Auth0 Client ID",
#                 validate=lambda _, x: len(x) > 0
#             ),
#             inquirer.Password(
#                 'client_secret',
#                 message="Auth0 Client Secret",
#                 validate=lambda _, x: len(x) > 0
#             ),
#             inquirer.Confirm(
#                 'require_signatures',
#                 message="Require electronic signatures for processing runs?",
#                 default=True
#             )
#         ]
#
#         auth_answers = inquirer.prompt(auth_questions)
#         if not auth_answers:
#             return 0
#
#         # Validate Auth0 configuration
#         message("info", "Validating Auth0 configuration...")
#
#         is_valid, error_msg = validate_auth0_config(
#             auth_answers['domain'],
#             auth_answers['client_id'],
#             auth_answers['client_secret']
#         )
#
#         if not is_valid:
#             message("error", f"Auth0 configuration invalid: {error_msg}")
#             return 1
#
#         message("success", "✓ Auth0 configuration validated!")
#
#         # Configure Auth0 manager
#         auth_manager = get_auth0_manager()
#         auth_manager.configure_auth0(
#             auth_answers['domain'],
#             auth_answers['client_id'],
#             auth_answers['client_secret']
#         )
#
#         # Update user configuration
#         user_config_data = load_user_config()
#
#         # Ensure compliance and workspace are dictionaries
#         if not isinstance(user_config_data.get('compliance'), dict):
#             user_config_data['compliance'] = {}
#         if not isinstance(user_config_data.get('workspace'), dict):
#             user_config_data['workspace'] = {}
#
#         user_config_data['compliance']['enabled'] = True
#         user_config_data['compliance']['auth_provider'] = 'auth0'
#         user_config_data['compliance']['require_electronic_signatures'] = auth_answers['require_signatures']
#         user_config_data['workspace']['auto_backup'] = True  # Always enabled for compliance
#
#         save_user_config(user_config_data)
#
#         message("success", "✓ Compliance mode setup complete!")
#         message("info", "\nNext steps:")
#         message("info", "1. Run 'autoclean login' to authenticate")
#         message("info", "2. Use 'autoclean whoami' to check authentication status")
#         message("info", "3. All processing will now include audit trails and user authentication")
#
#         return 0
#
#     except ImportError:
#         message("error", "Interactive setup requires 'inquirer' package.")
#         message("info", "Install with: pip install inquirer")
#         return 1
#     except Exception as e:
#         message("error", f"Compliance setup failed: {e}")
#         return 1


def cmd_version(args) -> int:
    """Show version information."""
    try:
        console = Console()

        # Professional header consistent with setup
        console.print(f"[bold]{LOGO_ICON} Autoclean-EEG Version Information:[/bold]")
        console.print(f"  🏷️  [bold]{__version__}[/bold]")

        # GitHub and support info
        console.print("\n[bold]GitHub Repository:[/bold]")
        console.print(
            "  [blue]https://github.com/cincibrainlab/autoclean_pipeline[/blue]"
        )
        console.print("  [dim]Report issues, contribute, or get help[/dim]")

        return 0
    except ImportError:
        print("AutoClean EEG (version unknown)")
        return 0


def cmd_task(args) -> int:
    """Execute task management commands."""
    if args.task_action == "add":
        return cmd_task_add(args)
    elif args.task_action == "remove":
        return cmd_task_remove(args)
    elif args.task_action == "list":
        return cmd_list_tasks(args)
    else:
        message("error", "No task action specified")
        return 1


def cmd_task_add(args) -> int:
    """Add a custom task by copying to workspace tasks folder."""
    try:
        if not args.task_file.exists():
            message("error", f"Task file not found: {args.task_file}")
            return 1

        # Ensure workspace exists
        if not user_config.tasks_dir.exists():
            user_config.tasks_dir.mkdir(parents=True, exist_ok=True)

        # Determine destination name
        if args.name:
            dest_name = f"{args.name}.py"
        else:
            dest_name = args.task_file.name

        dest_file = user_config.tasks_dir / dest_name

        # Check if task already exists
        if dest_file.exists() and not args.force:
            message(
                "error", f"Task '{dest_name}' already exists. Use --force to overwrite."
            )
            return 1

        # Copy the task file
        shutil.copy2(args.task_file, dest_file)

        # Extract class name for usage message
        try:
            class_name, _ = user_config._extract_task_info(dest_file)
            task_name = class_name
        except Exception:
            task_name = dest_file.stem

        message("info", f"Task '{task_name}' added to workspace!")
        print(f"📁 Copied to: {dest_file}")
        print("\nUse your custom task with:")
        print(f"  autocleaneeg-pipeline process {task_name} <data_file>")

        return 0

    except Exception as e:
        message("error", f"Failed to add custom task: {str(e)}")
        return 1


def cmd_task_remove(args) -> int:
    """Remove a custom task by deleting from workspace tasks folder."""
    try:
        # Find task file by class name or filename
        custom_tasks = user_config.list_custom_tasks()

        task_file = None
        if args.task_name in custom_tasks:
            # Found by class name
            task_file = Path(custom_tasks[args.task_name]["file_path"])
        else:
            # Try by filename
            potential_file = user_config.tasks_dir / f"{args.task_name}.py"
            if potential_file.exists():
                task_file = potential_file

        if not task_file or not task_file.exists():
            message("error", f"Task '{args.task_name}' not found")
            return 1

        # Remove the file
        task_file.unlink()
        message("info", f"Task '{args.task_name}' removed from workspace!")
        return 0

    except Exception as e:
        message("error", f"Failed to remove custom task: {str(e)}")
        return 1


def cmd_config(args) -> int:
    """Execute configuration management commands."""
    if args.config_action == "show":
        return cmd_config_show(args)
    elif args.config_action == "setup":
        return cmd_config_setup(args)
    elif args.config_action == "reset":
        return cmd_config_reset(args)
    elif args.config_action == "export":
        return cmd_config_export(args)
    elif args.config_action == "import":
        return cmd_config_import(args)
    else:
        message("error", "No config action specified")
        return 1


def cmd_config_show(_args) -> int:
    """Show user configuration directory."""
    config_dir = user_config.config_dir
    message("info", f"User configuration directory: {config_dir}")

    custom_tasks = user_config.list_custom_tasks()
    print(f"  • Custom tasks: {len(custom_tasks)}")
    print(f"  • Tasks directory: {config_dir / 'tasks'}")
    print(f"  • Config file: {config_dir / 'user_config.json'}")

    return 0


def cmd_config_setup(_args) -> int:
    """Reconfigure workspace location."""
    try:
        user_config.setup_workspace()
        return 0
    except Exception as e:
        message("error", f"Failed to reconfigure workspace: {str(e)}")
        return 1


def cmd_config_reset(args) -> int:
    """Reset user configuration to defaults."""
    if not args.confirm:
        message("error", "This will delete all custom tasks and reset configuration.")
        print("Use --confirm to proceed with reset.")
        return 1

    try:
        user_config.reset_config()
        message("info", "User configuration reset to defaults")
        return 0
    except Exception as e:
        message("error", f"Failed to reset configuration: {str(e)}")
        return 1


def cmd_config_export(args) -> int:
    """Export user configuration."""
    try:
        if user_config.export_config(args.export_path):
            return 0
        else:
            return 1
    except Exception as e:
        message("error", f"Failed to export configuration: {str(e)}")
        return 1


def cmd_config_import(args) -> int:
    """Import user configuration."""
    try:
        if user_config.import_config(args.import_path):
            return 0
        else:
            return 1
    except Exception as e:
        message("error", f"Failed to import configuration: {str(e)}")
        return 1


def cmd_clean_task(args) -> int:
    """Remove task output directory and database entries."""
    console = Console()
    
    # Determine output directory
    output_dir = args.output_dir or user_config._get_workspace_path()
    
    # Find matching task directories (could be task name or dataset name)
    potential_dirs = []
    
    # First try exact match
    exact_match = output_dir / args.task
    if exact_match.exists() and (exact_match / "bids").exists():
        potential_dirs.append(exact_match)
    
    # If no exact match, search for directories containing the task name
    if not potential_dirs:
        for item in output_dir.iterdir():
            if item.is_dir() and args.task.lower() in item.name.lower():
                if (item / "bids").exists():
                    potential_dirs.append(item)
    
    if not potential_dirs:
        message("warning", f"No task directories found matching: {args.task}")
        message("info", f"Searched in: {output_dir}")
        return 1
    
    if len(potential_dirs) > 1:
        console.print(f"\n[yellow]Multiple directories found matching '{args.task}':[/yellow]")
        for i, dir_path in enumerate(potential_dirs, 1):
            console.print(f"  {i}. {dir_path.name}")
        console.print("\nPlease be more specific or use the full directory name.")
        return 1
    
    # Use the single matching directory
    task_root_dir = potential_dirs[0]
    task_dir = task_root_dir / "bids"
    
    # Count files and calculate size
    total_files = 0
    total_size = 0
    for item in task_root_dir.rglob("*"):
        if item.is_file():
            total_files += 1
            total_size += item.stat().st_size
    
    # Format size for display
    size_mb = total_size / (1024 * 1024)
    size_str = f"{size_mb:.1f} MB" if size_mb < 1024 else f"{size_mb/1024:.1f} GB"
    
    # Database entries (if database exists) - search by both task name and directory name
    db_entries = 0
    if DB_PATH and Path(DB_PATH).exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Search for entries matching either the provided task name or the directory name
            cursor.execute(
                "SELECT COUNT(*) FROM runs WHERE task = ? OR task = ?", 
                (args.task, task_root_dir.name)
            )
            db_entries = cursor.fetchone()[0]
            conn.close()
        except Exception:
            pass
    
    # Display what will be deleted
    console.print("\n[bold]Task Cleanup Summary:[/bold]")
    console.print(f"Task: [cyan]{args.task}[/cyan]")
    console.print(f"Directory: [yellow]{task_root_dir}[/yellow]")
    console.print(f"Files: [red]{total_files:,}[/red]")
    console.print(f"Size: [red]{size_str}[/red]")
    if db_entries > 0:
        console.print(f"Database entries: [red]{db_entries}[/red]")
    
    if args.dry_run:
        console.print("\n[yellow]DRY RUN - No files will be deleted[/yellow]")
        return 0
    
    # Simple Y/N confirmation
    if not args.force:
        confirm = console.input("\n[bold red]Delete this task? (Y/N):[/bold red] ").strip().upper()
        if confirm != "Y":
            console.print("[yellow]Cancelled[/yellow]")
            return 1
    
    # Perform deletion
    try:
        # Delete filesystem
        console.print("\n[bold]Cleaning task files...[/bold]")
        shutil.rmtree(task_root_dir)
        console.print(f"✓ Removed directory: {task_root_dir}")
        
        # Delete database entries for both task name and directory name
        if db_entries > 0 and DB_PATH:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM runs WHERE task = ? OR task = ?", (args.task, task_root_dir.name))
            conn.commit()
            conn.close()
            console.print(f"✓ Removed {db_entries} database entries")
        
        console.print("\n[green]Task cleaned successfully![/green]")
        return 0
        
    except Exception as e:
        console.print(f"\n[red]Error during cleanup: {e}[/red]")
        return 1


def cmd_view(args) -> int:
    """View EEG files using autoclean-view."""
    # Check if file exists
    if not args.file.exists():
        message("error", f"File not found: {args.file}")
        return 1
    
    # Build command
    cmd = ["autoclean-view", str(args.file)]
    if args.no_view:
        cmd.append("--no-view")
    
    # Launch viewer
    message("info", f"Opening {args.file.name} in MNE-QT Browser...")
    
    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode == 0:
            message("success", "Viewer closed" if not args.no_view else "File validated")
            return 0
        else:
            message("error", f"Error: {process.stderr}")
            return 1
    except FileNotFoundError:
        message("error", "autoclean-view not installed. Run: pip install autoclean-view")
        return 1
    except Exception as e:
        message("error", f"Failed to launch viewer: {str(e)}")
        return 1


def cmd_help(args) -> int:
    """Show the same help as -h/--help."""
    parser = create_parser()
    parser.print_help()
    return 0


def cmd_tutorial(_args) -> int:
    """Show a helpful tutorial for first-time users."""
    console = Console()

    # Use the tutorial header for consistent branding
    _simple_header(console, "Tutorial", "Interactive guide to AutoClean EEG")

    console.print(
        "\n[bold bright_green]🚀 Welcome to the AutoClean EEG Tutorial![/bold bright_green]"
    )
    console.print(
        "This tutorial will walk you through the basics of using AutoClean EEG."
    )
    console.print(
        "\n[bold bright_yellow]Step 1: Setup your workspace[/bold bright_yellow]"
    )
    console.print(
        "The first step is to set up your workspace. This is where AutoClean EEG will store its configuration and any custom tasks you create."
    )
    console.print("To do this, run the following command:")
    console.print("\n[green]autocleaneeg-pipeline setup[/green]\n")

    console.print(
        "\n[bold bright_yellow]Step 2: List available tasks[/bold bright_yellow]"
    )
    console.print(
        "Once your workspace is set up, you can see the built-in processing tasks that are available."
    )
    console.print("To do this, run the following command:")
    console.print("\n[green]autocleaneeg-pipeline task list[/green]\n")

    console.print("\n[bold bright_yellow]Step 3: Process a file[/bold bright_yellow]")
    console.print(
        "Now you are ready to process a file. You will need to specify the task you want to use and the path to the file you want to process."
    )
    console.print(
        "For example, to process a file called 'data.raw' with the 'RestingEyesOpen' task, you would run the following command:"
    )
    console.print("\n[green]autocleaneeg-pipeline process RestingEyesOpen data.raw[/green]\n")

    return 0


def cmd_export_access_log(args) -> int:
    """Export database access log with integrity verification."""
    try:
        # Get workspace directory for database discovery and default output location
        workspace_dir = user_config._get_workspace_path()

        # Determine database path
        if args.database:
            db_path = Path(args.database)
        elif DB_PATH:
            db_path = DB_PATH / "pipeline.db"
        else:
            # Try to find database in workspace
            if workspace_dir:
                # Check for database directly in workspace directory
                workspace_db = workspace_dir / "pipeline.db"
                if workspace_db.exists():
                    db_path = workspace_db
                else:
                    # Fall back to checking workspace/output/ directory (most common location)
                    output_db = workspace_dir / "output" / "pipeline.db"
                    if output_db.exists():
                        db_path = output_db
                    else:
                        # Finally, look in output subdirectories (for multiple runs)
                        potential_outputs = workspace_dir / "output"
                        if potential_outputs.exists():
                            # Look for most recent output directory with database
                            for output_dir in sorted(
                                potential_outputs.iterdir(), reverse=True
                            ):
                                if output_dir.is_dir():
                                    potential_db = output_dir / "pipeline.db"
                                    if potential_db.exists():
                                        db_path = potential_db
                                        break
                            else:
                                message(
                                    "error",
                                    "No database found in workspace directory, output directory, or output subdirectories",
                                )
                                return 1
                        else:
                            message(
                                "error",
                                "No database found in workspace directory and no output directory exists",
                            )
                            return 1
            else:
                message(
                    "error", "No workspace configured and no database path provided"
                )
                return 1

        if not db_path.exists():
            message("error", f"Database file not found: {db_path}")
            return 1

        message("info", f"Using database: {db_path}")

        # Verify integrity first (need to temporarily set DB_PATH for verification)
        from autoclean.utils import database

        original_db_path = database.DB_PATH
        database.DB_PATH = db_path.parent

        try:
            integrity_result = verify_access_log_integrity()
        finally:
            database.DB_PATH = original_db_path

        if args.verify_only:
            if integrity_result["status"] == "valid":
                message("success", f"✓ {integrity_result['message']}")
                return 0
            elif integrity_result["status"] == "compromised":
                message("error", f"✗ {integrity_result['message']}")
                if "issues" in integrity_result:
                    for issue in integrity_result["issues"]:
                        message("error", f"  - {issue}")
                return 1
            else:
                message("error", f"✗ {integrity_result['message']}")
                return 1

        # Report integrity status
        if integrity_result["status"] == "valid":
            message("success", f"✓ {integrity_result['message']}")
        elif integrity_result["status"] == "compromised":
            message("warning", f"⚠ {integrity_result['message']}")
            if "issues" in integrity_result:
                for issue in integrity_result["issues"]:
                    message("warning", f"  - {issue}")
        else:
            message("warning", f"⚠ {integrity_result['message']}")

        # Query access log with filters
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM database_access_log WHERE 1=1"
        params = []

        # Apply date filters
        if args.start_date:
            query += " AND date(timestamp) >= ?"
            params.append(args.start_date)

        if args.end_date:
            query += " AND date(timestamp) <= ?"
            params.append(args.end_date)

        # Apply operation filter
        if args.operation:
            query += " AND operation LIKE ?"
            params.append(f"%{args.operation}%")

        query += " ORDER BY log_id ASC"

        cursor.execute(query, params)
        entries = cursor.fetchall()
        conn.close()

        if not entries:
            message("warning", "No access log entries found matching filters")
            return 0

        # Determine output file
        if args.output:
            output_file = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Use .jsonl extension for JSON Lines format
            if args.format == "json":
                extension = "jsonl"
            else:
                extension = args.format
            filename = f"access-log-{timestamp}.{extension}"
            # Default to workspace directory, not current working directory
            output_file = workspace_dir / filename if workspace_dir else Path(filename)

        # Export data
        export_data = []
        for entry in entries:
            entry_dict = dict(entry)
            # Parse JSON fields for export
            if entry_dict.get("user_context"):
                try:
                    entry_dict["user_context"] = json.loads(entry_dict["user_context"])
                except json.JSONDecodeError:
                    pass
            if entry_dict.get("details"):
                try:
                    entry_dict["details"] = json.loads(entry_dict["details"])
                except json.JSONDecodeError:
                    pass
            export_data.append(entry_dict)

        # Write export file
        if args.format == "json":
            # Write as JSONL (JSON Lines) format - more compact and easier to process
            with open(output_file, "w") as f:
                # First line: metadata
                metadata = {
                    "type": "metadata",
                    "export_timestamp": datetime.now().isoformat(),
                    "database_path": str(db_path),
                    "total_entries": len(export_data),
                    "integrity_status": integrity_result["status"],
                    "integrity_message": integrity_result["message"],
                    "filters_applied": {
                        "start_date": args.start_date,
                        "end_date": args.end_date,
                        "operation": args.operation,
                    },
                }
                f.write(json.dumps(metadata) + "\n")

                # Subsequent lines: one JSON object per access log entry
                for entry in export_data:
                    entry["type"] = "access_log"
                    f.write(json.dumps(entry) + "\n")

        elif args.format == "csv":
            with open(output_file, "w", newline="") as f:
                if export_data:
                    fieldnames = export_data[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for entry in export_data:
                        # Flatten JSON fields for CSV
                        csv_entry = {}
                        for key, value in entry.items():
                            if isinstance(value, (dict, list)):
                                csv_entry[key] = json.dumps(value)
                            else:
                                csv_entry[key] = value
                        writer.writerow(csv_entry)

        elif args.format == "human":
            with open(output_file, "w") as f:
                f.write("AutoClean Database Access Log Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Export Date: {datetime.now().isoformat()}\n")
                f.write(f"Database: {db_path}\n")
                f.write(f"Total Entries: {len(export_data)}\n")
                f.write(f"Integrity Status: {integrity_result['status']}\n")
                f.write(f"Integrity Message: {integrity_result['message']}\n\n")

                if args.start_date or args.end_date or args.operation:
                    f.write("Filters Applied:\n")
                    if args.start_date:
                        f.write(f"  Start Date: {args.start_date}\n")
                    if args.end_date:
                        f.write(f"  End Date: {args.end_date}\n")
                    if args.operation:
                        f.write(f"  Operation: {args.operation}\n")
                    f.write("\n")

                f.write("Access Log Entries:\n")
                f.write("-" * 30 + "\n\n")

                for i, entry in enumerate(export_data, 1):
                    f.write(f"Entry {i} (ID: {entry['log_id']})\n")
                    f.write(f"  Timestamp: {entry['timestamp']}\n")
                    f.write(f"  Operation: {entry['operation']}\n")

                    if entry.get("user_context"):
                        user_ctx = entry["user_context"]
                        if isinstance(user_ctx, dict):
                            # Handle both old and new format
                            user = user_ctx.get(
                                "user", user_ctx.get("username", "unknown")
                            )
                            host = user_ctx.get(
                                "host", user_ctx.get("hostname", "unknown")
                            )
                            f.write(f"  User: {user}\n")
                            f.write(f"  Host: {host}\n")

                    if entry.get("details") and entry["details"]:
                        f.write(
                            f"  Details: {json.dumps(entry['details'], indent=4)}\n"
                        )

                    f.write(f"  Hash: {entry['log_hash'][:16]}...\n")
                    f.write("\n")

        message("success", f"✓ Access log exported to: {output_file}")
        message("info", f"Format: {args.format}, Entries: {len(export_data)}")

        return 0

    except Exception as e:
        message("error", f"Failed to export access log: {e}")
        return 1


def cmd_login(args) -> int:
    """Execute the login command."""
    try:
        if not is_compliance_mode_enabled():
            message("error", "Compliance mode is not enabled.")
            message(
                "info",
                "Run 'autocleaneeg-pipeline setup --compliance-mode' to enable compliance mode and configure Auth0.",
            )
            return 1

        auth_manager = get_auth0_manager()

        # Always refresh configuration with latest credentials from environment/.env
        try:
            message("debug", "Loading Auth0 credentials from environment/.env files...")
            auth_manager.configure_developer_auth0()
        except Exception as e:
            message("error", f"Failed to configure Auth0: {e}")
            message(
                "info",
                "Check your .env file or environment variables for Auth0 credentials.",
            )
            return 1

        # Double-check configuration after loading
        if not auth_manager.is_configured():
            message("error", "Auth0 not configured.")
            message(
                "info",
                "Check your .env file or environment variables for Auth0 credentials.",
            )
            return 1

        if auth_manager.is_authenticated():
            user_info = auth_manager.get_current_user()
            user_email = user_info.get("email", "Unknown") if user_info else "Unknown"
            message("info", f"Already logged in as: {user_email}")
            return 0

        message("info", "Starting Auth0 login process...")

        if auth_manager.login():
            user_info = auth_manager.get_current_user()
            user_email = user_info.get("email", "Unknown") if user_info else "Unknown"
            message("success", f"✓ Login successful! Welcome, {user_email}")

            # Store user in database
            if user_info and DATABASE_AVAILABLE:
                # Set database path for the operation
                output_dir = user_config.get_default_output_dir()
                output_dir.mkdir(parents=True, exist_ok=True)
                set_database_path(output_dir)

                # Initialize database with all tables (including new auth tables)
                manage_database_conditionally("create_collection")

                user_record = {
                    "auth0_user_id": user_info.get("sub"),
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "user_metadata": user_info,
                }
                manage_database_conditionally("store_authenticated_user", user_record)

            return 0
        else:
            message("error", "Login failed. Please try again.")
            return 1

    except Exception as e:
        message("error", f"Login error: {e}")
        return 1


def cmd_logout(args) -> int:
    """Execute the logout command."""
    try:
        if not is_compliance_mode_enabled():
            message(
                "info", "Compliance mode is not enabled. No authentication to clear."
            )
            return 0

        auth_manager = get_auth0_manager()

        if not auth_manager.is_authenticated():
            message("info", "Not currently logged in.")
            return 0

        user_info = auth_manager.get_current_user()
        user_email = user_info.get("email", "Unknown") if user_info else "Unknown"

        auth_manager.logout()
        message("success", f"✓ Logged out successfully. Goodbye, {user_email}!")

        return 0

    except Exception as e:
        message("error", f"Logout error: {e}")
        return 1


def cmd_whoami(args) -> int:
    """Execute the whoami command."""
    try:
        if not is_compliance_mode_enabled():
            message("info", "Compliance mode: Disabled")
            message("info", "Authentication: Not required")
            return 0

        auth_manager = get_auth0_manager()

        if not auth_manager.is_configured():
            message("info", "Compliance mode: Enabled")
            message("info", "Authentication: Not configured")
            message(
                "info",
                "Run 'autocleaneeg-pipeline setup --compliance-mode' to configure Auth0.",
            )
            return 0

        if not auth_manager.is_authenticated():
            message("info", "Compliance mode: Enabled")
            message("info", "Authentication: Not logged in")
            message("info", "Run 'autocleaneeg-pipeline login' to authenticate.")
            return 0

        user_info = auth_manager.get_current_user()
        if user_info:
            message("info", "Compliance mode: Enabled")
            message("info", "Authentication: Logged in")
            message("info", f"Email: {user_info.get('email', 'Unknown')}")
            message("info", f"Name: {user_info.get('name', 'Unknown')}")
            message("info", f"User ID: {user_info.get('sub', 'Unknown')}")

            # Check token expiration
            if (
                hasattr(auth_manager, "token_expires_at")
                and auth_manager.token_expires_at
            ):

                expires_str = auth_manager.token_expires_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                message("info", f"Token expires: {expires_str}")
        else:
            message("warning", "User information unavailable")

        return 0

    except Exception as e:
        message("error", f"Error checking authentication status: {e}")
        return 1


def cmd_auth0_diagnostics(args) -> int:
    """Execute the auth0-diagnostics command."""
    try:
        console = Console()

        # Header
        console.print("\n🔍 [bold]Auth0 Configuration Diagnostics[/bold]", style="blue")
        console.print("[dim]Checking Auth0 setup and connectivity...[/dim]\n")

        # 1. Check compliance mode
        compliance_enabled = is_compliance_mode_enabled()
        console.print(
            f"✓ Compliance mode: {'[green]Enabled[/green]' if compliance_enabled else '[yellow]Disabled[/yellow]'}"
        )

        if not compliance_enabled:
            console.print(
                "[yellow]ℹ[/yellow] Auth0 is only used in compliance mode. Run 'autocleaneeg-pipeline setup --compliance-mode' to enable."
            )
            return 0

        # 2. Check environment variables
        console.print("\n📋 [bold]Environment Variables[/bold]")
        env_table = Table(show_header=True, header_style="bold blue")
        env_table.add_column("Variable", style="cyan", no_wrap=True)
        env_table.add_column("Status", style="green")
        env_table.add_column("Value Preview", style="dim")

        env_vars = [
            ("AUTOCLEAN_AUTH0_DOMAIN", os.getenv("AUTOCLEAN_AUTH0_DOMAIN")),
            ("AUTOCLEAN_AUTH0_CLIENT_ID", os.getenv("AUTOCLEAN_AUTH0_CLIENT_ID")),
            (
                "AUTOCLEAN_AUTH0_CLIENT_SECRET",
                os.getenv("AUTOCLEAN_AUTH0_CLIENT_SECRET"),
            ),
            ("AUTOCLEAN_AUTH0_AUDIENCE", os.getenv("AUTOCLEAN_AUTH0_AUDIENCE")),
            ("AUTOCLEAN_DEVELOPMENT_MODE", os.getenv("AUTOCLEAN_DEVELOPMENT_MODE")),
        ]

        for var_name, var_value in env_vars:
            if var_value:
                if "SECRET" in var_name:
                    preview = f"{var_value[:8]}..." if len(var_value) > 8 else "***"
                elif len(var_value) > 30:
                    preview = f"{var_value[:30]}..."
                else:
                    preview = var_value
                env_table.add_row(var_name, "✓ Set", preview)
            else:
                env_table.add_row(var_name, "[red]✗ Not Set[/red]", "")

        console.print(env_table)

        # 3. Check .env file
        console.print("\n📄 [bold].env File Detection[/bold]")
        env_paths = [
            Path(".env"),
            Path(".env.local"),
            Path("../.env"),
            Path("../../.env"),
        ]
        env_found = False
        for env_path in env_paths:
            if env_path.exists():
                console.print(f"✓ Found .env file: [cyan]{env_path.absolute()}[/cyan]")
                env_found = True
                if args.verbose:
                    try:
                        with open(env_path, "r") as f:
                            content = f.read()
                            auth_lines = [
                                line
                                for line in content.split("\n")
                                if "AUTOCLEAN_AUTH0" in line
                                and not line.strip().startswith("#")
                            ]
                            if auth_lines:
                                console.print("[dim]  Auth0 variables in file:[/dim]")
                                for line in auth_lines:
                                    # Mask secrets
                                    if "SECRET" in line and "=" in line:
                                        key, value = line.split("=", 1)
                                        masked_value = (
                                            f"{value[:8]}..."
                                            if len(value) > 8
                                            else "***"
                                        )
                                        console.print(
                                            f"[dim]    {key}={masked_value}[/dim]"
                                        )
                                    else:
                                        console.print(f"[dim]    {line}[/dim]")
                    except Exception as e:
                        console.print(f"[red]  Error reading file: {e}[/red]")
                break

        if not env_found:
            console.print(
                "[yellow]⚠[/yellow] No .env file found in current or parent directories"
            )

        # 4. Test credential loading
        console.print("\n🔧 [bold]Credential Loading Test[/bold]")
        try:
            auth_manager = get_auth0_manager()
            credentials = auth_manager._load_developer_credentials()

            if credentials:
                console.print("✓ Credentials loaded successfully")
                console.print(
                    f"  Source: [cyan]{credentials.get('source', 'unknown')}[/cyan]"
                )
                console.print(
                    f"  Domain: [cyan]{credentials.get('domain', 'NOT FOUND')}[/cyan]"
                )
                client_id = credentials.get("client_id", "NOT FOUND")
                if client_id != "NOT FOUND":
                    console.print(f"  Client ID: [cyan]{client_id[:8]}...[/cyan]")
                else:
                    console.print(f"  Client ID: [red]{client_id}[/red]")
            else:
                console.print("[red]✗ Failed to load credentials[/red]")
                console.print(
                    "[yellow]  Try setting environment variables or checking .env file[/yellow]"
                )
        except Exception as e:
            console.print(f"[red]✗ Error loading credentials: {e}[/red]")

        # 5. Test Auth0 domain connectivity
        console.print("\n🌐 [bold]Domain Connectivity Test[/bold]")
        openid_accessible = False
        connectivity_error = None

        try:
            # Get fresh credentials to ensure we test the correct domain
            auth_manager = get_auth0_manager()
            credentials = auth_manager._load_developer_credentials()

            if credentials and credentials.get("domain"):
                domain = credentials["domain"]
                console.print(f"Testing connection to: [cyan]{domain}[/cyan]")

                # Test basic connectivity
                try:
                    response = requests.get(f"https://{domain}", timeout=10)
                    if response.status_code in [
                        200,
                        404,
                        403,
                    ]:  # Any of these indicates domain exists
                        console.print("✓ Domain is reachable")
                        if args.verbose:
                            console.print(f"  HTTP Status: {response.status_code}")
                            console.print(
                                f"  Response time: {response.elapsed.total_seconds():.2f}s"
                            )
                    else:
                        connectivity_error = (
                            f"Unexpected status code: {response.status_code}"
                        )
                        console.print(f"[yellow]⚠[/yellow] {connectivity_error}")
                except requests.Timeout:
                    connectivity_error = "Connection timeout"
                    console.print(f"[red]✗ {connectivity_error}[/red]")
                except requests.ConnectionError:
                    connectivity_error = "Connection failed - check domain name"
                    console.print(f"[red]✗ {connectivity_error}[/red]")
                except Exception as e:
                    connectivity_error = f"Connection error: {e}"
                    console.print(f"[red]✗ {connectivity_error}[/red]")

                # Test Auth0 authorization endpoint (what login actually uses)
                try:
                    auth_url = f"https://{domain}/authorize"
                    response = requests.get(auth_url, timeout=10, allow_redirects=False)
                    # Auth0 authorize endpoint should return 400 (missing parameters) or redirect, not 404
                    if response.status_code in [400, 302, 301]:
                        openid_accessible = True
                        console.print("✓ Auth0 authorization endpoint accessible")
                        if args.verbose:
                            console.print(f"  Authorization URL: {auth_url}")
                            console.print(f"  Response status: {response.status_code}")
                    else:
                        console.print(
                            f"[yellow]⚠[/yellow] Auth0 authorization endpoint unexpected status: {response.status_code}"
                        )

                    # Also test the well-known endpoint (optional)
                    well_known_url = (
                        f"https://{domain}/.well-known/openid_configuration"
                    )
                    response = requests.get(well_known_url, timeout=5)
                    if response.status_code == 200:
                        console.print("✓ OpenID configuration also accessible")
                        if args.verbose:
                            config = response.json()
                            console.print(
                                f"  Issuer: {config.get('issuer', 'unknown')}"
                            )
                    else:
                        console.print(
                            f"[dim]ℹ OpenID config not available (status: {response.status_code}) - this is optional[/dim]"
                        )

                except Exception as e:
                    console.print(
                        f"[yellow]⚠[/yellow] Could not test Auth0 endpoints: {e}"
                    )
            else:
                connectivity_error = "No domain configured"
                console.print("[red]✗ No domain configured[/red]")
        except Exception as e:
            connectivity_error = f"Error testing connectivity: {e}"
            console.print(f"[red]✗ {connectivity_error}[/red]")

        # 6. Configuration summary
        console.print("\n📊 [bold]Configuration Summary[/bold]")
        try:
            auth_manager = get_auth0_manager()
            # Ensure configuration is loaded from environment/credentials
            credentials = auth_manager._load_developer_credentials()
            if credentials and not auth_manager.is_configured():
                auth_manager.configure_developer_auth0()

            summary_table = Table(show_header=True, header_style="bold blue")
            summary_table.add_column("Component", style="cyan")
            summary_table.add_column("Status", style="green")
            summary_table.add_column("Details", style="dim")

            # Check if configured
            is_configured = auth_manager.is_configured()
            summary_table.add_row(
                "Auth0 Configuration",
                "✓ Valid" if is_configured else "[red]✗ Invalid[/red]",
                "Ready for login" if is_configured else "Missing required credentials",
            )

            # Check authentication status
            is_authenticated = auth_manager.is_authenticated()
            summary_table.add_row(
                "Authentication",
                "✓ Logged in" if is_authenticated else "[yellow]Not logged in[/yellow]",
                "Valid session" if is_authenticated else "Run 'autocleaneeg-pipeline login'",
            )

            # Check config file
            config_file = auth_manager.config_file
            config_exists = config_file.exists()
            summary_table.add_row(
                "Config File",
                "✓ Exists" if config_exists else "[yellow]Not found[/yellow]",
                str(config_file) if config_exists else "Will be created on first setup",
            )

            console.print(summary_table)

        except Exception as e:
            console.print(f"[red]Error generating summary: {e}[/red]")

        # 7. Recommendations
        console.print("\n💡 [bold]Recommendations[/bold]")
        try:
            auth_manager = get_auth0_manager()
            credentials = auth_manager._load_developer_credentials()

            if not credentials:
                console.print("1. Set Auth0 environment variables:")
                console.print(
                    '   [cyan]export AUTOCLEAN_AUTH0_DOMAIN="your-tenant.us.auth0.com"[/cyan]'
                )
                console.print(
                    '   [cyan]export AUTOCLEAN_AUTH0_CLIENT_ID="your_client_id"[/cyan]'
                )
                console.print(
                    '   [cyan]export AUTOCLEAN_AUTH0_CLIENT_SECRET="your_client_secret"[/cyan]'
                )
                console.print("2. Or create a .env file with these variables")
                console.print(
                    "3. Install python-dotenv if using .env: [cyan]pip install python-dotenv[/cyan]"
                )
            elif connectivity_error:
                # Don't recommend login if there are connectivity issues
                console.print(
                    f"[red]⚠ Auth0 connectivity issue detected:[/red] {connectivity_error}"
                )
                console.print("")
                console.print("Please check:")
                console.print("1. Verify your Auth0 domain is correct in .env file")
                console.print("2. Ensure your Auth0 application is properly configured")
                console.print(
                    "3. Check that your Auth0 application type is 'Native' (for CLI apps)"
                )
                console.print("4. Verify your Auth0 tenant is active and accessible")
                console.print("")
                console.print(
                    "Once connectivity is fixed, run [cyan]autocleaneeg-pipeline login[/cyan] to authenticate"
                )
            elif not openid_accessible:
                console.print(
                    "[yellow]⚠ Auth0 OpenID configuration not accessible[/yellow]"
                )
                console.print("")
                console.print("This may indicate:")
                console.print("1. Auth0 domain is incorrect")
                console.print("2. Auth0 application is not properly configured")
                console.print("3. Network or firewall issues")
                console.print("")
                console.print(
                    "You can try [cyan]autocleaneeg-pipeline login[/cyan] but it may fail"
                )
            elif not auth_manager.is_authenticated():
                console.print("✓ Configuration looks good!")
                console.print("1. Run [cyan]autocleaneeg-pipeline login[/cyan] to authenticate")
            else:
                console.print(
                    "✓ Configuration looks good! You're ready to use Auth0 authentication."
                )

        except Exception as e:
            console.print(f"[red]Error generating recommendations: {e}[/red]")

        return 0

    except Exception as e:
        message("error", f"Diagnostics error: {e}")
        return 1


def main(argv: Optional[list] = None) -> int:
    """Main entry point for the AutoClean CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # ------------------------------------------------------------------
    # Always inform the user where the AutoClean workspace is (or will be)
    # so they can easily locate their configuration and results.  This runs
    # for *every* CLI invocation, including the bare `autocleaneeg-pipeline` call.
    # ------------------------------------------------------------------
    workspace_dir = user_config.config_dir

    # For real sub-commands, log the workspace path via the existing logger.
    if args.command and args.command != "setup":
        # Compact branding header for consistency across all commands (except setup which has its own branding)
        console = Console()

        if workspace_dir.exists() and (workspace_dir / "tasks").exists():
            console.print(f"[green]Autoclean Workspace Directory:[/green] {workspace_dir}")
        else:
            message(
                "warning",
                f"Workspace directory not configured yet: {workspace_dir} (run 'autocleaneeg-pipeline setup' to configure)",
            )

    if not args.command:
        # Show our custom 80s-style main interface instead of default help
        console = Console()
        _simple_header(console, "Welcome", "Professional EEG Processing & Analysis Platform")

        # Show workspace info elegantly beneath the banner
        if workspace_dir.exists() and (workspace_dir / "tasks").exists():
            console.print(f"\n[dim]Workspace:[/dim] {workspace_dir}")
        else:
            console.print(
                f"[yellow]⚠ Workspace not configured:[/yellow] {workspace_dir}\n"
                "Run [cyan]autocleaneeg-pipeline setup[/cyan] to configure."
            )

        return 0

    # Validate arguments
    if not validate_args(args):
        return 1

    # Execute command
    if args.command == "process":
        return cmd_process(args)
    elif args.command == "list-tasks":
        return cmd_list_tasks(args)
    elif args.command == "review":
        return cmd_review(args)
    elif args.command == "task":
        return cmd_task(args)
    elif args.command == "config":
        return cmd_config(args)
    elif args.command == "setup":
        return cmd_setup(args)
    elif args.command == "export-access-log":
        return cmd_export_access_log(args)
    elif args.command == "login":
        return cmd_login(args)
    elif args.command == "logout":
        return cmd_logout(args)
    elif args.command == "whoami":
        return cmd_whoami(args)
    elif args.command == "auth0-diagnostics":
        return cmd_auth0_diagnostics(args)
    elif args.command == "clean-task":
        return cmd_clean_task(args)
    elif args.command == "view":
        return cmd_view(args)
    elif args.command == "version":
        return cmd_version(args)
    elif args.command == "help":
        return cmd_help(args)
    elif args.command == "tutorial":
        return cmd_tutorial(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
