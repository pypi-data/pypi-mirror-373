import asyncio
import tempfile
import time
from pathlib import Path

import typer
from rich.panel import Panel
from rich.table import Table

from ..config import detect_project_config
from ..css.binary import TailwindBinaryManager
from ..dev.analyzer import resolve_port
from ..dev.process_manager import ProcessManager
from ..templates.css_input import generate_css_input
from .utils import console, error, success


def prepare_css_input(config) -> Path:
    if (project_input := config.project_root / "static" / "css" / "input.css").exists():
        return project_input

    css_dir = config.css_output_absolute.parent
    css_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".css", dir=css_dir, delete=False
    ) as f:
        f.write(generate_css_input(config))
        return Path(f.name)


def start_tailwind(
    manager: ProcessManager, input_css: Path, config, enable_css_hot_reload: bool = True
):
    binary = TailwindBinaryManager("latest").get_binary()

    def notify_css_update(css_path: Path):
        if not enable_css_hot_reload:
            return

        from ..dev.unified_reload import DevReloadHandler

        try:
            asyncio.run(DevReloadHandler.notify_css_update(css_path, time.time()))
        except Exception as e:
            console.print(f"[yellow]Warning: Could not notify CSS update: {e}[/yellow]")

    manager.start_tailwind_watcher(
        tailwind_binary=Path(binary),
        input_css=input_css,
        output_css=config.css_output_absolute,
        project_root=config.project_root,
        on_rebuild=notify_css_update if enable_css_hot_reload else None,
    )


def wait_for_css(config, timeout: int = 10) -> None:
    if config.css_output_absolute.exists():
        success("✓ CSS ready")
        return

    console.print("[yellow]Building CSS...[/yellow]")
    for _ in range(timeout * 2):
        if config.css_output_absolute.exists():
            success("✓ CSS built")
            return
        time.sleep(0.5)

    error("CSS build timed out")
    raise typer.Exit(1)


def cleanup_files(input_css: Path | None, config, app_path: Path) -> None:
    files_to_clean = [
        input_css if input_css and input_css.name.startswith("tmp") else None,
        *app_path.parent.glob(f"{app_path.stem}_dev_*.py"),
        *config.css_output_absolute.parent.glob("tmp*.css"),
    ]

    for file_path in filter(None, files_to_clean):
        file_path.unlink(missing_ok=True)


def show_status(config, port: int, css_hot: bool, app_file: str) -> None:
    table = Table(title="StarUI Development Server", show_header=False)
    table.add_column(style="cyan")
    table.add_column(style="green")

    for label, value in [
        ("App", f"http://localhost:{port}"),
        ("File", app_file),
        ("CSS", str(config.css_output)),
        ("Hot Reload", f"✓ (Unified WebSocket on port {port})" if css_hot else "✗"),
    ]:
        table.add_row(label, value)

    console.print(Panel(table, border_style="green"))


def dev_command(
    app_file: str | None = typer.Argument(None, help="StarHTML app file to run"),
    port: int = typer.Option(5000, "--port", "-p", help="Port for app server"),
    css_hot_reload: bool = typer.Option(
        True, "--css-hot/--no-css-hot", help="Enable CSS hot reload"
    ),
    strict: bool = typer.Option(
        False, "--strict", help="Fail if requested port is unavailable"
    ),
    debug: bool = typer.Option(
        True, "--debug/--no-debug", help="Enable debug mode (disables compression)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show details"),
) -> None:
    """Start development server with CSS hot reload and smart port detection."""
    if not app_file:
        error("App file is required")
        raise typer.Exit(1)

    app_path = Path(app_file)
    if not app_path.exists():
        error(f"App file not found: {app_file}")
        raise typer.Exit(1)

    config = detect_project_config()
    manager = ProcessManager()
    input_css = None

    try:
        app_port, port_message = resolve_port(port, strict, app_path)
        if port_message:
            console.print(f"[blue]{port_message}[/blue]")
    except RuntimeError as e:
        error(str(e))
        raise typer.Exit(1) from e

    try:
        input_css = prepare_css_input(config)
        start_tailwind(manager, input_css, config, css_hot_reload)
        wait_for_css(config)

        manager.start_uvicorn(
            app_file=app_path,
            port=app_port,
            watch_patterns=["*.py", "*.html"],
            enable_css_hot_reload=css_hot_reload,
            force_debug=debug,
        )

        success(f"✓ Server running at http://localhost:{app_port}")
        show_status(config, app_port, css_hot_reload, app_file)
        console.print("Press Ctrl+C to stop\n")

        try:
            manager.wait_for_any_exit()
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down...[/yellow]")

    except Exception as e:
        error(f"Dev server error: {e}")
        raise typer.Exit(1) from e
    finally:
        manager.stop_all()
        cleanup_files(input_css, config, app_path)
