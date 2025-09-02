import psutil
import time
from rich.live import Live
from rich.table import Table
from rich.console import Console
import threading


class ProcessDashboard:
    def __init__(self):
        self.console = Console()
        self.running = True

    def generate_table(self):
        table = Table(title="Live Process Monitor")

        table.add_column("PID", style="cyan", width=8)
        table.add_column("Name", style="magenta", width=15)
        table.add_column("CPU%", justify="right", style="yellow", width=8)
        table.add_column("Memory%", justify="right", style="blue", width=8)
        table.add_column("Status", style="green", width=10)
        table.add_column("Command", style="white")

        # Get top processes by CPU
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status", "cmdline"]):
            try:
                info = proc.info
                if info["cpu_percent"] is not None:
                    processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage
        processes.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)

        for proc in processes[:15]:  # Top 15
            cmdline = proc.get("cmdline", [])
            command = " ".join(cmdline) if cmdline else proc["name"]

            table.add_row(
                str(proc["pid"]),
                proc["name"][:14],
                f"{proc.get('cpu_percent', 0):.1f}",
                f"{proc.get('memory_percent', 0):.1f}",
                proc.get("status", "unknown"),
                command[:80] + "..." if len(command) > 40 else command,
            )

        return table

    def run(self):
        with Live(self.generate_table(), refresh_per_second=2) as live:
            while self.running:
                time.sleep(0.5)
                live.update(self.generate_table())

    def stop(self):
        self.running = False


# Usage
dashboard = ProcessDashboard()
try:
    dashboard.run()
except KeyboardInterrupt:
    dashboard.stop()
