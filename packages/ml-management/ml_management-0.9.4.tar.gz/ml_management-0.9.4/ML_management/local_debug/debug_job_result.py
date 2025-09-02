import pprint
from dataclasses import asdict, dataclass, field
from typing import List, Optional

from ML_management.singleton_pattern import Singleton


@dataclass(init=True)
class DebugJobResult:
    job_name: str
    job_id: int
    artifacts: Optional[str] = None
    metrics: Optional[str] = None
    params: Optional[str] = None
    models: List[dict] = field(default_factory=list)
    buckets: List[dict] = field(default_factory=list)

    def __repr__(self):
        printer = pprint.PrettyPrinter(width=80, indent=4)
        return "\nResult of the job: \n" + printer.pformat(asdict(self))


@dataclass(init=True, repr=True)
class DebugJobLogContext(DebugJobResult, metaclass=Singleton):
    job_name: Optional[str] = None
    job_id: Optional[int] = None
    old_python_path: list = None
    old_sys_modules: list = None
    extra_sys_path: List[str] = field(default_factory=list)

    def clear(self):
        self.__init__()

    def get_result(self) -> DebugJobResult:
        return DebugJobResult(
            job_id=self.job_id,
            job_name=self.job_name,
            artifacts=self.artifacts,
            metrics=self.metrics,
            params=self.params,
            models=self.models,
            buckets=self.buckets,
        )
