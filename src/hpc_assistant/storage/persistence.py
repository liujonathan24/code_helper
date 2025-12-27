"""
This module handles the persistence of job artifacts.
"""
import json
from pathlib import Path

class JobStorage:
    def __init__(self, base_path: str = "./jobs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

    def create_job_dir(self, job_id: str):
        (self.base_path / job_id).mkdir(exist_ok=True)

    def save(self, job_id: str, filename: str, data: dict):
        self.create_job_dir(job_id)
        with open(self.base_path / job_id / filename, "w") as f:
            json.dump(data, f, indent=4)

    def load(self, job_id: str, filename: str) -> dict:
        with open(self.base_path / job_id / filename, "r") as f:
            return json.load(f)

    def save_report(self, job_id: str, report_content: str):
        self.create_job_dir(job_id)
        with open(self.base_path / job_id / "report.md", "w") as f:
            f.write(report_content)

    def load_report(self, job_id: str) -> str:
        with open(self.base_path / job_id / "report.md", "r") as f:
            return f.read()

