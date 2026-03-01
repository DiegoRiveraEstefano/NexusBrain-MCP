import asyncio
import sys
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt

# Ensure the src import works when executing the tool as a local script
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.logging import setup_logging
from src.core.services.ingestion_service import IngestionService
from src.core.services.graph_service import GraphRAGService

setup_logging()
console = Console()

click.rich_click.THEME = "magenta2-modern"
click.rich_click.COMMAND_GROUPS = {
    "cli_tool.py": [
        {
            "name": "Main Commands",
            "commands": ["ingest", "view-graph", "simulate"],
        }
    ]
}

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option("1.0.0", prog_name="NexusBrain")
def cli():
    """
    NexusBrain MCP CLI.
    Unified tool for knowledge management and ingestion in SurrealDB.
    """
    pass

@cli.command()
@click.argument("repo_path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def ingest(repo_path: str):
    """Ingests a repository into the database and builds the Knowledge Graph."""
    console.print(Panel.fit(f"[bold magenta] Starting NexusBrain MCP Ingestion[/bold magenta]\n[dim]Target: {repo_path}[/dim]"))

    service = IngestionService()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task1 = progress.add_task("[cyan]Phase 1: Scanning files...", total=None)
        task2 = None
        task3 = None
        task4 = None

        def progress_callback(event: str, count: int, total: int):
            nonlocal task1, task2, task3, task4
            if event == "scan_done":
                progress.update(task1, description=f"[green]✔ Phase 1 completed: {count} files found.")
                task2 = progress.add_task("[cyan]Phase 2: Processing AST and extracting dependencies...", total=None)
            elif event == "process_done":
                progress.update(task2, description=f"[green]✔ Phase 2 completed: {count} logical chunks extracted.")
                task3 = progress.add_task("[cyan]Phase 3: Generating embeddings and inserting into SurrealDB...", total=None)
            elif event == "index_done":
                progress.update(task3, description=f"[green]✔ Phase 3 completed: Nodes saved in database.")
                task4 = progress.add_task("[cyan]Phase 4: Weaving the Relations Graph...", total=None)
            elif event == "graph_done":
                progress.update(task4, description=f"[green]✔ Phase 4 completed: {count} edges created.")

        try:
            result = asyncio.run(service.run_ingestion(repo_path, progress_callback))
            if result.get("status") == "empty":
                console.print("[yellow]No valid files found to process.[/yellow]")
            else:
                console.print(f"\n[bold green]✅ Ingestion completed successfully. The Central Brain is updated.[/bold green]")
                console.print(f"[dim]Total time: {result['time']:.2f} seconds[/dim]")
        except Exception as e:
            console.print(f"\n[bold red]❌ The process failed: {e}[/bold red]")


@cli.command(name="view-graph")
def view_graph():
    """Shows a view of the Graph (Nodes and Edges) in the database."""
    service = GraphRAGService()
    console.print("\n[bold blue]🔍 Connecting to SurrealDB...[/bold blue]")

    try:
        data = asyncio.run(service.get_graph_stats())
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])

        if not nodes:
            console.print(Panel("[yellow]The database is empty. Ingest code first.[/yellow]"))
            return

        table_nodes = Table(title="📦 Created Nodes (Code Chunks)", show_lines=True)
        table_nodes.add_column("ID (Node)", style="cyan", no_wrap=True)
        table_nodes.add_column("File", style="magenta")
        table_nodes.add_column("Content (Extract)", style="green")
        table_nodes.add_column("Dimensions", justify="right", style="yellow")

        for chunk in nodes:
            node_id = str(chunk.get("id", ""))
            file_path = chunk.get("file_path", "")
            content = chunk.get("content", "").replace("\n", " ").strip()
            vector_size = str(chunk.get("vector_size", 0))
            snippet = f"{content[:60]}..." if len(content) > 60 else content
            table_nodes.add_row(node_id, file_path, snippet, vector_size)

        console.print("\n", table_nodes)

        table_edges = Table(title="🕸️ Dependency Graph (DEPENDS_ON Relations)")
        table_edges.add_column("ID (Edge)", style="dim")
        table_edges.add_column("Source Node", style="cyan")
        table_edges.add_column("->", style="bold red")
        table_edges.add_column("Target Node", style="cyan")

        if edges:
            for edge in edges:
                table_edges.add_row(str(edge.get("id", "")), str(edge.get("source_node", "")), "->", str(edge.get("target_node", "")))
            console.print("\n", table_edges)
        else:
            console.print("\n[yellow]No DEPENDS_ON relations found.[/yellow]")
    except Exception as e:
         console.print(f"[bold red]Error getting graph:[/bold red] {e}")


@cli.command()
def simulate():
    """Interactive simulator for MCP reasoning flow."""
    console.print(Panel.fit("[bold magenta]🧠 NexusBrain MCP Simulator 🧠[/bold magenta]"))
    query = Prompt.ask("\n[bold cyan]🗣️ User[/bold cyan]: What do you want to search in the code?",
                       default="How do I connect to SurrealDB?")

    service = GraphRAGService()

    console.print(f"\n[dim]🤖 MCP reasoning: I need to find code related to '{query}'. Calling search_similar_code tool...[/dim]")
    try:
        result = asyncio.run(service.simulate_query(query))
        best_match = result.get("best_match")

        if not best_match:
            console.print("[red]No similar code found. Make sure you have ingested the project.[/red]")
            return

        file_path = best_match.get("file_path")
        console.print(Panel(
            f"[bold green]🎯 Best match found (Similarity: {best_match.get('score', 0):.2f})[/bold green]\n"
            f"[yellow]File:[/yellow] {file_path}\n"
            f"[yellow]Node ID:[/yellow] {best_match.get('id')}\n\n"
            f"[dim]{best_match.get('content')[:200]}...[/dim]",
            title="🛠️ Tool: search_similar_code", border_style="green"
        ))

        console.print(f"\n[dim]🤖 MCP reasoning: If the user modifies {file_path}, what else would break? Calling analyze_blast_radius...[/dim]")
        impacted_files = result.get("impacted_files", [])

        console.print(f"\n[dim]🤖 MCP reasoning: What does {file_path} depend on to work? Calling get_dependencies...[/dim]")
        dependencies = result.get("dependencies", [])

        table = Table(title=f"🕸️ Graph Analysis for: {file_path}", show_lines=True)
        table.add_column("💥 Blast Radius (Depend on me)", style="red")
        table.add_column("🎯 Central Node", style="cyan", justify="center")
        table.add_column("📦 Dependencies (I need this)", style="green")

        impact_str = "\n".join(set(impacted_files)) if impacted_files else "[dim]None detected[/dim]"
        deps_str = "\n".join(set(dependencies)) if dependencies else "[dim]None detected[/dim]"

        table.add_row(impact_str, f"[bold]{file_path}[/bold]", deps_str)
        console.print("\n", table)

        console.print("\n[bold magenta]🤖 Final AI response to the user:[/bold magenta]")
        console.print(f"The code you are looking for is in `{file_path}`. Be careful when modifying it, because it will affect: {', '.join(set(impacted_files)) if impacted_files else 'no known critical file'} and requires {', '.join(set(dependencies)) if dependencies else 'no internal dependency'} to work.")
    except Exception as e:
         console.print(f"[bold red]Simulation error:[/bold red] {e}")


if __name__ == "__main__":
    cli()
