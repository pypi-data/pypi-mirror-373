from rich.progress import Progress
from rich import print
from rich.prompt import Prompt
import subprocess
import time
import importlib
import sys

def start():
    print("[bold yellow]========================================[/bold yellow]")
    print("[bold yellow]=========[/bold yellow] [bold blue]Welcome to ImportPyP[/bold blue] [bold yellow]=========[/bold yellow]")
    print("[bold yellow]========[/bold yellow] [bold blue]Import your py libs here[/bold blue] [bold yellow]======[/bold yellow]")
    print("[bold yellow]========================================[/bold yellow]")

    start_ask = Prompt.ask("[green]Enter 'install', 'uninstall' or 'exit':[/green] ").lower()

    if start_ask in ["install", "uninstall"]:
        lib_name = Prompt.ask("[cyan]Enter the lib name:[/cyan]").strip()
        
        if start_ask == "install":
            try:
                importlib.import_module(lib_name)
                print(f"[green]Library '{lib_name}' is already installed![/green]")
            except ModuleNotFoundError:
                print(f"[yellow]Library '{lib_name}' not found. Downloading assets to install...[/yellow]")

                # Barra de progresso fake
                with Progress() as progress:
                    task = progress.add_task(f"[cyan]Installing {lib_name}...[/cyan]", total=100)
                    for _ in range(100):
                        time.sleep(0.05)
                        progress.update(task, advance=1)

                # Instala a lib
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", lib_name])
                    print(f"[green]Library '{lib_name}' successfully installed![/green]")
                except subprocess.CalledProcessError:
                    print(f"[red]Error installing the library '{lib_name}'.[/red]")

        elif start_ask == "uninstall":
            try:
                importlib.import_module(lib_name)
                print(f"[yellow]Library '{lib_name}' found. Preparing to uninstall...[/yellow]")

                with Progress() as progress:
                    task = progress.add_task(f"[cyan]Uninstalling {lib_name}...[/cyan]", total=100)
                    for _ in range(100):
                        time.sleep(0.05)
                        progress.update(task, advance=1)

                # Desinstala a lib
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", lib_name])
                    print(f"[green]Library '{lib_name}' successfully uninstalled![/green]")
                except subprocess.CalledProcessError:
                    print(f"[red]Error uninstalling the library '{lib_name}'.[/red]")
            except ModuleNotFoundError:
                print(f"[red]Library '{lib_name}' is not installed.[/red]")

    elif start_ask == "exit":
        print("[red]Leaving...[/red]")
    else:
        print("[red]Invalid command![/red]")