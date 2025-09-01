import psutil
from rich.table import Table
from rich.console import Console
from datetime import datetime


def get_process_info():
    """Get detailed process information using psutil"""
    processes = []

    for proc in psutil.process_iter(
        ["pid", "name", "username", "cpu_percent", "memory_percent", "create_time", "cmdline"]
    ):
        try:
            # Get process info safely
            info = proc.info
            info["memory_mb"] = proc.memory_info().rss / 1024 / 1024
            info["cpu_times"] = proc.cpu_times()
            info["status"] = proc.status()

            # Handle command line
            cmdline = info.get("cmdline", [])
            info["command"] = " ".join(cmdline) if cmdline else info["name"]

            if "_cs" not in info["command"]:
                continue

            processes.append(info)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Process disappeared or no access
            continue

    return processes


def create_rich_table():
    """Create a beautiful table with rich"""
    console = Console()
    table = Table(title="Process Information")

    table.add_column("PID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("User", style="green")
    table.add_column("CPU%", justify="right", style="yellow")
    table.add_column("Memory%", justify="right", style="blue")
    table.add_column("Memory MB", justify="right", style="blue")
    table.add_column("Status", style="red")
    table.add_column("Command", style="white")

    processes = get_process_info()

    # Sort by CPU usage
    processes.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)

    for proc in processes[:20]:  # Top 20 processes
        table.add_row(
            str(proc["pid"]),
            proc["name"],
            proc.get("username", "N/A"),
            f"{proc.get('cpu_percent', 0):.1f}",
            f"{proc.get('memory_percent', 0):.1f}",
            f"{proc.get('memory_mb', 0):.1f}",
            proc.get("status", "unknown"),
            proc["command"][:80] + "..." if len(proc["command"]) > 50 else proc["command"],
        )

    console.print(table)


if __name__ == "__main__":
    create_rich_table()
