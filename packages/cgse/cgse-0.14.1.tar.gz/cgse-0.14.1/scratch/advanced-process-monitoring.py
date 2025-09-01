import psutil
import time
from dataclasses import dataclass
from typing import List, Dict
import json


@dataclass
class ProcessInfo:
    pid: int
    name: str
    username: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    create_time: float
    command: str

    def to_dict(self):
        return {
            "pid": self.pid,
            "name": self.name,
            "username": self.username,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_mb": self.memory_mb,
            "status": self.status,
            "create_time": self.create_time,
            "command": self.command,
        }


class ProcessMonitor:
    def __init__(self):
        self.previous_cpu = {}

    def get_processes(self, filter_func=None) -> List[ProcessInfo]:
        """Get current processes with optional filtering"""
        processes = []

        for proc in psutil.process_iter():
            try:
                with proc.oneshot():  # Efficient way to get multiple attributes
                    info = ProcessInfo(
                        pid=proc.pid,
                        name=proc.name(),
                        username=proc.username(),
                        cpu_percent=proc.cpu_percent(),
                        memory_percent=proc.memory_percent(),
                        memory_mb=proc.memory_info().rss / 1024 / 1024,
                        status=proc.status(),
                        create_time=proc.create_time(),
                        command=" ".join(proc.cmdline()) if proc.cmdline() else proc.name(),
                    )

                    if filter_func is None or filter_func(info):
                        processes.append(info)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes

    def find_by_name(self, name: str) -> List[ProcessInfo]:
        """Find processes by name"""
        return self.get_processes(lambda p: name.lower() in p.name.lower())

    def find_high_cpu(self, threshold: float = 5.0) -> List[ProcessInfo]:
        """Find processes using high CPU"""
        return self.get_processes(lambda p: p.cpu_percent > threshold)

    def find_high_memory(self, threshold_mb: float = 100.0) -> List[ProcessInfo]:
        """Find processes using high memory"""
        return self.get_processes(lambda p: p.memory_mb > threshold_mb)

    def kill_process(self, pid: int, force: bool = False):
        """Safely kill a process"""
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def export_to_json(self, filename: str):
        """Export current process list to JSON"""
        processes = [p.to_dict() for p in self.get_processes()]
        with open(filename, "w") as f:
            json.dump(processes, f, indent=2)


# Usage examples
monitor = ProcessMonitor()

# Find all Python processes
python_procs = monitor.find_by_name("python")
print(f"Found {len(python_procs)} Python processes")
for proc in python_procs:
    print(f"{proc.name} ({proc.pid} – {proc.cpu_percent}%)")

# Find high CPU usage
high_cpu = monitor.find_high_cpu(10.0)
for proc in high_cpu:
    print(f"High CPU: {proc.name} (PID: {proc.pid}) - {proc.cpu_percent}%")

# Export current state
monitor.export_to_json("processes.json")
