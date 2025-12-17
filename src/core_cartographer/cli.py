"""Interactive CLI for Core Cartographer."""

import sys

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown

from . import __version__
from .config import get_settings, Settings
from .extractor import (
    scan_client_folder,
    extract_rules_and_guidelines,
    save_results,
    DocumentSet,
)
from .cost_estimator import estimate_cost, format_cost, format_tokens

console = Console()


def main() -> None:
    """Main entry point for the CLI."""
    console.print(
        Panel(
            f"[bold blue]Core Cartographer[/bold blue] v{__version__}\n"
            "[dim]Extract validation rules and localization guidelines from copy documents[/dim]",
            expand=False,
        )
    )

    try:
        settings = get_settings()
    except Exception as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        console.print("[dim]Make sure you have a .env file with ANTHROPIC_API_KEY set.[/dim]")
        sys.exit(1)

    # Ensure input directory exists
    if not settings.input_dir.exists():
        console.print(f"[red]Input directory not found:[/red] {settings.input_dir}")
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

    try:
        document_sets = scan_client_folder(settings, client_name)
    except Exception as e:
        console.print(f"[red]Error scanning folder:[/red] {e}")
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

    # Estimate costs
    _display_cost_estimate(settings, to_process)

    # Confirm
    if not questionary.confirm("Proceed with extraction?").ask():
        return

    # Process each document set
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


def _display_cost_estimate(settings: Settings, document_sets: list[DocumentSet]) -> None:
    """Display cost estimate for processing."""
    total_input_tokens = sum(ds.total_tokens for ds in document_sets)

    # Add estimated tokens for examples and instructions
    # These are larger now due to comprehensive examples
    example_tokens = 5000  # Rough estimate for examples + instructions
    total_input_tokens += example_tokens * len(document_sets)

    # Estimate output tokens (rules + guidelines are substantial)
    estimated_output_tokens = int(total_input_tokens * 0.5)

    cost = estimate_cost(
        total_input_tokens,
        estimated_output_tokens,
        settings.model,
    )

    console.print(f"\n[bold]Estimated Cost:[/bold]")
    console.print(f"  Input tokens:  {format_tokens(total_input_tokens)}")
    console.print(f"  Output tokens: ~{format_tokens(estimated_output_tokens)}")
    console.print(f"  [yellow]Estimated cost: {format_cost(cost)}[/yellow]\n")


def _process_document_set(settings: Settings, doc_set: DocumentSet) -> None:
    """Process a single document set and save results."""
    console.print(f"\n[bold]Processing {doc_set.subtype}...[/bold]")

    try:
        result = extract_rules_and_guidelines(settings, doc_set)
    except Exception as e:
        console.print(f"[red]Extraction failed:[/red] {e}")
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

    # Confirm save
    if not questionary.confirm("Save these results?").ask():
        console.print("[yellow]Results discarded.[/yellow]")
        return

    # Save
    rules_path, guidelines_path = save_results(settings, doc_set, result)
    console.print(f"[green]✓[/green] Saved: {rules_path}")
    console.print(f"[green]✓[/green] Saved: {guidelines_path}")


if __name__ == "__main__":
    main()
