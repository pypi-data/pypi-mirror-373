"""Development process coordination."""

import os
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rich.console import Console


class ProcessManager:
    def __init__(self):
        self.processes: dict[str, subprocess.Popen] = {}
        self.threads: dict[str, threading.Thread] = {}
        self.shutdown_event = threading.Event()
        self.console = Console()

    def start_process(
        self,
        name: str,
        cmd: list[str],
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.Popen:
        if existing := self.processes.get(name):
            self.console.print(f"[yellow]{name} already running[/yellow]")
            return existing

        self.console.print(f"[green]Starting {name}...[/green]")
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self.processes[name] = process
        self._start_monitor(name, process)
        return process

    def _start_monitor(self, name: str, process: subprocess.Popen) -> None:
        def monitor():
            try:
                while process.poll() is None and not self.shutdown_event.is_set():
                    if (line := process.stdout.readline()) and (clean := line.strip()):
                        self.console.print(f"[dim cyan][{name}][/dim cyan] {clean}")
                    else:
                        time.sleep(0.1)
            except Exception as e:
                self.console.print(f"[red]Error monitoring {name}: {e}[/red]")

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        self.threads[f"{name}_monitor"] = thread

    def start_uvicorn(
        self,
        app_file: Path,
        port: int,
        watch_patterns: list[str] | None = None,
        enable_css_hot_reload: bool = True,
        force_debug: bool = True,
    ) -> subprocess.Popen:
        app_module = self._create_app_module(
            app_file, enable_css_hot_reload, force_debug
        )
        cmd = self._build_uvicorn_cmd(app_module, port, watch_patterns)
        return self.start_process(
            "uvicorn", cmd, app_file.parent, env=os.environ.copy()
        )

    def _create_app_module(
        self, app_file: Path, enable_hot_reload: bool, force_debug: bool = True
    ) -> str:
        if not enable_hot_reload:
            return f"{app_file.stem}:app"

        wrapper_file = app_file.parent / f"{app_file.stem}_dev.py"
        wrapper_file.write_text(f"""from {app_file.stem} import app as original_app
from starui.dev.unified_reload import create_dev_reload_route, DevReloadJs

# Force debug mode to disable compression
if hasattr(original_app, 'debug'):
    original_app.debug = {force_debug}

# Replace StarHTML's live reload with StarUI's enhanced system
try:
    # Remove existing live reload routes
    if hasattr(original_app, 'routes'):
        original_app.routes = [
            route for route in original_app.routes
            if not (hasattr(route, 'path') and route.path == '/live-reload')
        ]

    # Remove existing live reload JS from headers
    if hasattr(original_app, 'hdrs') and original_app.hdrs:
        original_app.hdrs = [
            hdr for hdr in original_app.hdrs
            if 'live-reload' not in str(hdr).lower()
        ]
    elif not hasattr(original_app, 'hdrs'):
        original_app.hdrs = []

    # Add StarUI's unified dev reload
    original_app.hdrs.append(DevReloadJs())

    dev_route = create_dev_reload_route()
    if hasattr(original_app, 'routes'):
        original_app.routes.append(dev_route)
    elif hasattr(original_app, 'router') and hasattr(original_app.router, 'routes'):
        original_app.router.routes.append(dev_route)

    print("[StarUI] Replaced StarHTML live reload with unified dev reload system")

except Exception as e:
    print(f"Warning: Could not replace dev reload system: {{e}}")

app = original_app""")
        return f"{wrapper_file.stem}:app"

    def _build_uvicorn_cmd(
        self, app_module: str, port: int, watch_patterns: list[str] | None
    ) -> list[str]:
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            app_module,
            "--reload",
            "--port",
            str(port),
            "--host",
            "localhost",
            "--reload-delay",
            "0.1",
        ]

        for pattern in watch_patterns or ["*.py", "*.html"]:
            cmd.extend(["--reload-include", pattern])

        for exclude in [
            "*.css",
            "static/**",
            "**/tmp*",
            "**/__pycache__/**",
            "*_dev.py",
        ]:
            cmd.extend(["--reload-exclude", exclude])

        return cmd

    def start_tailwind_watcher(
        self,
        tailwind_binary: Path,
        input_css: Path,
        output_css: Path,
        project_root: Path,
        on_rebuild: Callable[[Path], Any] | None = None,
    ) -> subprocess.Popen:
        cmd = [
            str(tailwind_binary),
            "--input",
            str(input_css),
            "--output",
            str(output_css),
            "--watch=always",
            "--cwd",
            str(project_root),
        ]
        process = self.start_process("tailwind", cmd, project_root)

        if on_rebuild:
            self._start_file_watcher(output_css, on_rebuild)
        return process

    def _start_file_watcher(
        self, file_path: Path, callback: Callable[[Path], Any]
    ) -> None:
        def monitor():
            last_mtime = file_path.stat().st_mtime if file_path.exists() else 0
            if last_mtime:
                callback(file_path)  # Initial callback

            while not self.shutdown_event.is_set():
                try:
                    if (
                        file_path.exists()
                        and (mtime := file_path.stat().st_mtime) > last_mtime
                    ):
                        last_mtime = mtime
                        callback(file_path)
                except Exception:
                    pass
                time.sleep(0.5)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        self.threads["tailwind_monitor"] = thread

    def is_running(self, name: str) -> bool:
        return (
            process := self.processes.get(name)
        ) is not None and process.poll() is None

    def stop_process(self, name: str, timeout: int = 2) -> bool:
        if not (process := self.processes.get(name)):
            return True

        try:
            process.terminate()
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=1)
        except Exception:
            pass

        self.processes.pop(name, None)
        return True

    def stop_all(self, timeout: int = 2) -> None:
        if self.shutdown_event.is_set():
            return

        self.shutdown_event.set()
        for name in list(self.processes):
            self.stop_process(name, timeout)

        self.processes.clear()
        self.threads.clear()

    def wait_for_any_exit(self) -> None:
        while not self.shutdown_event.is_set():
            dead_processes = [
                name
                for name, proc in self.processes.items()
                if proc.poll() is not None
                and not (name == "tailwind" and proc.returncode == 0)
            ]

            if dead_processes:
                for name in dead_processes:
                    self.console.print(f"[red]{name} died unexpectedly[/red]")
                    del self.processes[name]

                if "uvicorn" in dead_processes:
                    break

            time.sleep(0.5)
