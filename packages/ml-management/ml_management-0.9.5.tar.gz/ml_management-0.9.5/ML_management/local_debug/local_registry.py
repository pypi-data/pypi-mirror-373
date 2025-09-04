import csv
import os
from typing import Dict

from ML_management.variables import DEBUG_REGISTRY_PATH


class LocalRegistry:
    def __init__(self, registry_path: str = DEBUG_REGISTRY_PATH):
        self.registry_path = registry_path

    def get_metrics(self, job_id: int) -> Dict[str, list]:
        job_dir = os.path.join(self.registry_path, "jobs", str(job_id))
        if not os.path.isdir(job_dir):
            raise Exception(f"Job: {job_id} not found in local debug registry.")
        metrics_dir = os.path.join(job_dir, "metrics")
        if not os.path.isdir(metrics_dir):
            return {}
        result = {}
        for filename in os.listdir(metrics_dir):
            with open(os.path.join(metrics_dir, filename)) as file:
                reader = csv.DictReader(file)
                result[os.path.splitext(filename)[0]] = list(reader)

        return result
