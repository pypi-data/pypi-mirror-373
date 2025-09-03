from rich.console import Console

console = Console()

def success(msg):
    console.print(f"[bold green]✔ {msg}[/bold green]")

def error(msg):
    console.print(f"[bold red]✖ {msg}[/bold red]")

def warn(msg):
    console.print(f"[bold yellow]! {msg}[/bold yellow]")
