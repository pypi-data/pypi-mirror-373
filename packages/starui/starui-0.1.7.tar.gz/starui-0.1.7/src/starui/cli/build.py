from pathlib import Path

import typer
from rich.table import Table

from ..config import detect_project_config
from ..css.builder import BuildMode, CSSBuilder
from .utils import console, error, info, success


def format_size(bytes: int) -> str:
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f} KB"
    return f"{bytes / (1024 * 1024):.1f} MB"


def build_command(
    output: str | None = typer.Option(None, "--output", "-o", help="CSS output path"),
    minify: bool = typer.Option(True, "--minify/--no-minify", help="Minify CSS"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show details"),
) -> None:
    """Build production CSS."""

    try:
        config = detect_project_config()

        if output:
            path = Path(output)
            if not path.suffix:
                path = path.with_suffix(".css")
            config.css_output = path.absolute() if path.is_absolute() else path

        if verbose:
            info(f"Output: {config.css_output_absolute}")

        # Clean existing file
        if config.css_output_absolute.exists():
            config.css_output_absolute.unlink()
        config.css_output_absolute.parent.mkdir(parents=True, exist_ok=True)

        # Build
        builder = CSSBuilder(config)
        with console.status("[bold green]Building CSS..."):
            result = builder.build(
                mode=BuildMode.PRODUCTION if minify else BuildMode.DEVELOPMENT,
                watch=False,
                scan_content=True,
            )

        if result.success:
            success("Build completed!")

            # Show stats
            table = Table(show_header=False)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            if result.css_path:
                table.add_row("Output", str(result.css_path))
            if result.build_time:
                table.add_row("Time", f"{result.build_time:.1f}s")
            if result.css_size_bytes:
                table.add_row("Size", format_size(result.css_size_bytes))
            if result.classes_found:
                table.add_row("Classes", str(result.classes_found))

            console.print(table)
        else:
            error(f"Build failed: {result.error_message}")
            raise typer.Exit(1)

    except Exception as e:
        error(f"Build error: {e}")
        raise typer.Exit(1) from e
