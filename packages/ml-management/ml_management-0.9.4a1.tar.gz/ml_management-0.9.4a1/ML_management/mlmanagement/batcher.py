import time
import warnings
from collections import deque
from threading import Event, Thread

from sgqlc.operation import Operation

from ML_management import variables
from ML_management.graphql import schema
from ML_management.graphql.schema import MetricInput
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.singleton_pattern import Singleton
from ML_management.variables import (
    get_butch_polling_frequency,
    get_metric_accumulation_duration,
    get_timeout_log_metric_batch,
)


class Batcher(metaclass=Singleton):
    def __init__(self):
        self.batch = deque()
        self.thread = None
        self.stop_event = Event()

    def log_metrics(self, metrics: list[MetricInput]):
        self.batch.extend(metrics)
        self._start_thread()

    def _start_thread(self):
        if not self.thread:
            self.stop_event.clear()
            self.thread = Thread(target=self.log_batch_metric, args=(self.stop_event,), daemon=True)
            self.thread.start()

    def _stop_batching(self):
        self.batch = deque()
        if self.thread:
            self.stop_event.set()
            self.stop_event = Event()
            self.thread = None

    def log_batch_metric(self, stop_event):
        metric_accumulation_duration = get_metric_accumulation_duration()
        while not stop_event.is_set():
            time.sleep(metric_accumulation_duration)
            if len(self.batch) == 0:
                continue
            metrics_to_log = self.batch.copy()
            op = Operation(schema.Mutation)
            op.log_metrics(
                metrics=metrics_to_log,
                secret_uuid=variables.secret_uuid,
            )
            try:
                send_graphql_request(op, json_response=False)
                for _ in range(len(metrics_to_log)):
                    self.batch.popleft()
            except Exception as err:
                warnings.warn(str(err))

    def wait_log_metrics(self):
        stop_time = time.time()
        butch_polling_frequency = get_butch_polling_frequency()
        while self.batch and time.time() - stop_time < get_timeout_log_metric_batch():
            time.sleep(butch_polling_frequency)
        self._stop_batching()
