import csv
import json
import os
import shutil
from collections import defaultdict
from typing import Dict, Optional

from ML_management import variables
from ML_management.local_debug.debug_job_result import DebugJobLogContext
from ML_management.types.metainfo import ObjectMetaInfo
from ML_management.types.model_type import ModelType
from ML_management.variables import CACHED_LIST_FILENAME, DEBUG_REGISTRY_PATH


class LocalLogger:
    metric_field_order = ["key", "value", "step", "timestamp", "autostep"]

    entity_key_pattern: str = "{model_type}:{name}:{version}"

    def __init__(self, registry_path: str = DEBUG_REGISTRY_PATH):
        self.registry_path = registry_path
        os.makedirs(registry_path, exist_ok=True)

    def get_job_id(self) -> int:
        job_dir = os.path.join(self.registry_path, "jobs")
        if not os.path.exists(job_dir):
            return 1
        job_dirs = os.listdir(job_dir)

        job_id = int(max(job_dirs, key=lambda x: 0 if not x.isdigit() else int(x))) + 1

        return job_id

    def log_metrics(self, metrics: list[dict]):
        job_id = str(variables.secret_uuid)
        metrics_dir = os.path.join(self.registry_path, "jobs", job_id, "metrics")
        os.makedirs(metrics_dir, exist_ok=True)
        DebugJobLogContext().metrics = os.path.abspath(metrics_dir)
        metrics_key_map = defaultdict(list)

        for metric in metrics:
            metrics_key_map[metric["key"]].append(metric[key] for key in self.metric_field_order)

        for key, metrics in metrics_key_map.items():
            metric_file = os.path.join(metrics_dir, f"{key}.csv")
            if os.path.exists(metric_file):
                with open(metric_file, "a") as file:
                    csv_writer = csv.writer(file)
                    csv_writer.writerows(metrics)
            else:
                metrics.insert(0, self.metric_field_order)
                with open(metric_file, "w") as file:
                    csv_writer = csv.writer(file)
                    csv_writer.writerows(metrics)

    def log_params(self, params: Dict[str, str]):
        params = list(params.items())
        job_id = str(variables.secret_uuid)
        params_dir = os.path.join(self.registry_path, "jobs", job_id, "params")
        os.makedirs(params_dir, exist_ok=True)
        params_file = os.path.join(params_dir, "params.csv")
        DebugJobLogContext().params = os.path.abspath(params_dir)

        if os.path.exists(params_file):
            with open(params_file, "a") as file:
                csv_writer = csv.writer(file)
                csv_writer.writerows(params)
        else:
            params.insert(0, ["key", "value"])
            with open(params_file, "w") as file:
                csv_writer = csv.writer(file)
                csv_writer.writerows(params)

    @staticmethod
    def _copy_artifact(local_path: str, artifact_dir: str, dir_with_name: bool = True):
        os.makedirs(artifact_dir, exist_ok=True)

        name = os.path.basename(local_path)
        if os.path.isfile(local_path):
            shutil.copy2(local_path, os.path.join(artifact_dir, name))
        else:
            if dir_with_name:
                artifact_dir = os.path.join(artifact_dir, name)
            shutil.copytree(local_path, artifact_dir, dirs_exist_ok=True)

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        job_id = str(variables.secret_uuid)
        artifact_dir = os.path.join(self.registry_path, "jobs", job_id, "artifacts")
        DebugJobLogContext().artifacts = os.path.abspath(artifact_dir)
        if artifact_path is not None:
            artifact_dir = os.path.join(artifact_dir, artifact_path)
        self._copy_artifact(local_path, artifact_dir)

    def upload_bucket(self, local_path: str, bucket: str, prefix: str = ""):
        s3_dir = os.path.join(self.registry_path, "row_data")
        bucket_path = os.path.abspath(os.path.join(s3_dir, bucket))
        os.makedirs(bucket_path, exist_ok=True)

        artifact_dir = os.path.join(bucket_path, prefix)
        self._copy_artifact(local_path, artifact_dir, False)
        DebugJobLogContext().buckets.append({"bucket": bucket, "local_path": bucket_path})

    def log_model(
        self,
        register_name: str,
        model_type: ModelType,
        model_path: str,
        hash_artifacts: str,
    ) -> ObjectMetaInfo:
        version = 1

        os.makedirs(os.path.join(self.registry_path, model_type.value), exist_ok=True)

        list_path = os.path.join(self.registry_path, model_type.value, CACHED_LIST_FILENAME)
        models = {}
        if os.path.exists(list_path):
            with open(list_path) as file:
                models = json.load(file)
            if register_name in models:
                version = max(map(int, models[register_name].keys())) + 1

        dst_path = os.path.join(self.registry_path, model_type.value, register_name, str(version))
        os.makedirs(dst_path, exist_ok=True)

        self._copy_artifact(model_path, dst_path, False)

        if register_name not in models:
            models[register_name] = {}

        models[register_name][version] = dst_path

        with open(list_path, "w") as file:
            json.dump(models, file)

        DebugJobLogContext().models.append(
            {"name": register_name, "version": version, "local_path": os.path.abspath(dst_path)}
        )

        return ObjectMetaInfo(register_name, version, hash_artifacts, model_type)
