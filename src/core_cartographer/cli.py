"""Interactive CLI for Core Cartographer."""

import logging
import sys

import questionary
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from . import __version__
from .config import Settings, get_settings
from .cost_estimator import estimate_cost, format_cost, format_tokens
from .exceptions import (
    CartographerError,
    ClientNotFoundError,
    ConfigurationError,
    ExtractionError,
)
from .extractor import (
    estimate_prompt_tokens,
    extract_rules_and_guidelines,
    extract_rules_and_guidelines_batch,
    save_results,
    scan_client_folder,
)
from .logging_config import get_logger, setup_logging
from .models import DocumentSet

console = Console()
logger = get_logger(__name__)


def main() -> None:
    """Main entry point for the CLI."""
    # Setup logging (quiet for CLI, shows warnings and above)
    setup_logging(level=logging.WARNING, console=True)

    console.print(
        Panel(
            f"[bold blue]Core Cartographer[/bold blue] v{__version__}\n"
            "[dim]Extract validation rules and localization guidelines from copy documents[/dim]",
            expand=False,
        )
    )

    try:
        settings = get_settings()
        logger.info("Settings loaded successfully")
    except ConfigurationError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        console.print("[dim]Make sure you have a .env file with ANTHROPIC_API_KEY set.[/dim]")
        sys.exit(1)

    # Ensure input directory exists
    if not settings.input_dir.exists():
        console.print(f"[red]Input directory not found:[/red] {settings.input_dir}")
        logger.error(f"Input directory not found: {settings.input_dir}")
        sys.exit(1)

    # Main menu loop
    while True:
        action = questionary.select(
            "What would you like to do?",
            choices=[
                "Extract rules & guidelines",
                "List clients",
                "Exit",
            ],
        ).ask()

        if action is None or action == "Exit":
            console.print("[dim]Goodbye![/dim]")
            break
        elif action == "List clients":
            _list_clients(settings)
        elif action == "Extract rules & guidelines":
            _process_documents(settings)


def _list_clients(settings: Settings) -> None:
    """List available client folders."""
    clients = [d.name for d in settings.input_dir.iterdir() if d.is_dir()]

    if not clients:
        console.print("[yellow]No client folders found in input directory.[/yellow]")
        return

    table = Table(title="Available Clients")
    table.add_column("Client", style="cyan")
    table.add_column("Subtypes", style="green")

    for client in sorted(clients):
        client_path = settings.input_dir / client
        subtypes = [d.name for d in client_path.iterdir() if d.is_dir()]
        table.add_row(client, ", ".join(subtypes) if subtypes else "(no subtypes)")

    console.print(table)


def _process_documents(settings: Settings) -> None:
    """Process documents for a selected client."""
    # Get available clients
    clients = [d.name for d in settings.input_dir.iterdir() if d.is_dir()]

    if not clients:
        console.print("[yellow]No client folders found. Add folders to input/[/yellow]")
        return

    # Select client
    client_name = questionary.select(
        "Select a client:",
        choices=sorted(clients),
    ).ask()

    if client_name is None:
        return

    # Scan for documents
    console.print(f"\n[dim]Scanning {client_name}...[/dim]")
    logger.info(f"Scanning client folder: {client_name}")

    try:
        document_sets = scan_client_folder(settings, client_name)
    except ClientNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        logger.error(f"Client not found: {e}")
        return
    except CartographerError as e:
        console.print(f"[red]Error scanning folder:[/red] {e}")
        logger.error(f"Error scanning folder: {e}")
        return

    if not document_sets:
        console.print("[yellow]No documents found in client folder.[/yellow]")
        return

    # Display summary
    _display_document_summary(document_sets)

    # Select subtypes to process
    subtype_choices = [ds.subtype for ds in document_sets]
    subtype_choices.insert(0, "[All subtypes]")

    selected = questionary.select(
        "Which subtypes to process?",
        choices=subtype_choices,
    ).ask()

    if selected is None:
        return

    if selected == "[All subtypes]":
        to_process = document_sets
    else:
        to_process = [ds for ds in document_sets if ds.subtype == selected]

    # Ask about debug mode
    debug_mode = questionary.confirm(
        "Enable debug mode? (Save prompts without calling API)",
        default=False
    ).ask()

    # Ask about batch processing (only if processing multiple subtypes)
    batch_processing = False
    if len(to_process) > 1:
        batch_processing = questionary.confirm(
            "Use batch processing? (Process all subtypes in one API call)",
            default=False
        ).ask()

    # Update settings with user choices
    settings.debug_mode = debug_mode
    settings.batch_processing = batch_processing

    # Estimate costs (skip if debug mode)
    if not debug_mode:
        _display_cost_estimate(settings, to_process, batch_processing)

        # Confirm
        if not questionary.confirm("Proceed with extraction?").ask():
            return
    else:
        console.print("[yellow]Debug mode enabled - no API calls will be made[/yellow]\n")

    # Process documents based on mode
    if batch_processing and len(to_process) > 1:
        _process_document_sets_batch(settings, to_process)
    else:
        # Process each document set individually
        for doc_set in to_process:
            _process_document_set(settings, doc_set)


def _display_document_summary(document_sets: list[DocumentSet]) -> None:
    """Display a summary of found documents."""
    table = Table(title="Documents Found")
    table.add_column("Subtype", style="cyan")
    table.add_column("Documents", justify="right")
    table.add_column("Tokens", justify="right", style="yellow")

    for ds in document_sets:
        table.add_row(
            ds.subtype,
            str(len(ds.documents)),
            format_tokens(ds.total_tokens),
        )

    console.print(table)


def _display_cost_estimate(
    settings: Settings,
    document_sets: list[DocumentSet],
    batch_processing: bool = False,
) -> None:
    """Display cost estimate for processing."""
    # Get client name from first document set
    client_name = document_sets[0].client_name if document_sets else "unknown"

    # Calculate estimated input tokens dynamically
    if batch_processing and len(document_sets) > 1:
        # Batch mode: one prompt for all subtypes
        total_input_tokens = estimate_prompt_tokens(client_name, document_sets, settings)
        console.print("\n[bold cyan]Batch Processing Mode:[/bold cyan]")
        console.print("  All subtypes will be processed in one API call")
    else:
        # Individual mode: separate prompts per subtype
        total_input_tokens = 0
        for doc_set in document_sets:
            total_input_tokens += estimate_prompt_tokens(client_name, [doc_set], settings)
        console.print("\n[bold cyan]Individual Processing Mode:[/bold cyan]")
        console.print(f"  {len(document_sets)} separate API call(s)")

    # Estimate output tokens (rules + guidelines are substantial)
    estimated_output_tokens = int(total_input_tokens * 0.5)

    cost = estimate_cost(
        total_input_tokens,
        estimated_output_tokens,
        settings.model,
    )

    console.print("\n[bold]Estimated Cost:[/bold]")
    console.print(f"  Input tokens:  {format_tokens(total_input_tokens)}")
    console.print(f"  Output tokens: ~{format_tokens(estimated_output_tokens)}")
    console.print(f"  [yellow]Estimated cost: {format_cost(cost)}[/yellow]\n")


def _process_document_set(settings: Settings, doc_set: DocumentSet) -> None:
    """Process a single document set and save results."""
    console.print(f"\n[bold]Processing {doc_set.subtype}...[/bold]")
    logger.info(f"Processing document set: {doc_set.subtype}")

    try:
        result = extract_rules_and_guidelines(settings, doc_set)
    except ExtractionError as e:
        console.print(f"[red]Extraction failed:[/red] {e}")
        logger.error(f"Extraction failed: {e}")
        return
    except CartographerError as e:
        console.print(f"[red]Error:[/red] {e}")
        logger.error(f"Error during extraction: {e}")
        return

    # Display preview of client_rules.js
    console.print("\n[bold green]Client Rules Preview:[/bold green]")
    rules_preview = (
        result.client_rules[:1500] + "\n// ... (truncated)"
        if len(result.client_rules) > 1500
        else result.client_rules
    )
    syntax = Syntax(rules_preview, "javascript", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="client_rules.js"))

    # Display preview of guidelines.md
    console.print("\n[bold green]Guidelines Preview:[/bold green]")
    guidelines_preview = (
        result.guidelines[:1500] + "\n\n... (truncated)"
        if len(result.guidelines) > 1500
        else result.guidelines
    )
    console.print(Panel(Markdown(guidelines_preview), title="guidelines.md"))

    # Show token usage
    console.print(
        f"\n[dim]Tokens used: {result.input_tokens:,} input, "
        f"{result.output_tokens:,} output[/dim]"
    )

    # Skip save in debug mode
    if settings.debug_mode:
        console.print("\n[yellow]Debug mode - prompt saved, skipping result save[/yellow]")
        return

    # Confirm save
    if not questionary.confirm("Save these results?").ask():
        console.print("[yellow]Results discarded.[/yellow]")
        return

    # Save
    rules_path, guidelines_path = save_results(settings, doc_set, result)
    console.print(f"[green]✓[/green] Saved: {rules_path}")
    console.print(f"[green]✓[/green] Saved: {guidelines_path}")
    logger.info(f"Results saved to {rules_path.parent}")


def _process_document_sets_batch(settings: Settings, doc_sets: list[DocumentSet]) -> None:
    """Process multiple document sets in batch mode (one API call)."""
    console.print(f"\n[bold]Processing {len(doc_sets)} subtypes in batch mode...[/bold]")
    logger.info(f"Processing {len(doc_sets)} document sets in batch")

    try:
        results = extract_rules_and_guidelines_batch(settings, doc_sets)
    except ExtractionError as e:
        console.print(f"[red]Batch extraction failed:[/red] {e}")
        logger.error(f"Batch extraction failed: {e}")
        return
    except CartographerError as e:
        console.print(f"[red]Error:[/red] {e}")
        logger.error(f"Error during batch extraction: {e}")
        return

    # Process and display results for each subtype
    for doc_set in doc_sets:
        subtype = doc_set.subtype
        if subtype not in results:
            console.print(f"[yellow]No results for {subtype}[/yellow]")
            continue

        result = results[subtype]

        console.print(f"\n[bold green]Results for {subtype}:[/bold green]")

        # Display preview of client_rules.js
        console.print("\n[bold green]Client Rules Preview:[/bold green]")
        rules_preview = (
            result.client_rules[:1500] + "\n// ... (truncated)"
            if len(result.client_rules) > 1500
            else result.client_rules
        )
        syntax = Syntax(rules_preview, "javascript", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"{subtype}/client_rules.js"))

        # Display preview of guidelines.md
        console.print("\n[bold green]Guidelines Preview:[/bold green]")
        guidelines_preview = (
            result.guidelines[:1500] + "\n\n... (truncated)"
            if len(result.guidelines) > 1500
            else result.guidelines
        )
        console.print(Panel(Markdown(guidelines_preview), title=f"{subtype}/guidelines.md"))

        # Show token usage
        console.print(
            f"\n[dim]Tokens used: {result.input_tokens:,} input, "
            f"{result.output_tokens:,} output[/dim]"
        )

    # Confirm save for all
    if settings.debug_mode:
        console.print("\n[yellow]Debug mode - prompts saved, skipping result save[/yellow]")
        return

    if not questionary.confirm("Save all results?").ask():
        console.print("[yellow]Results discarded.[/yellow]")
        return

    # Save all results
    for doc_set in doc_sets:
        subtype = doc_set.subtype
        if subtype in results:
            rules_path, guidelines_path = save_results(settings, doc_set, results[subtype])
            console.print(f"[green]✓[/green] Saved {subtype}: {rules_path}")
            console.print(f"[green]✓[/green] Saved {subtype}: {guidelines_path}")
            logger.info(f"Results saved to {rules_path.parent}")


if __name__ == "__main__":
    main()
