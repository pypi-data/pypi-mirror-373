"""Collectors."""
from typing import Callable, Dict, Generic, ItemsView, Type, TypeVar

from ML_management.collectors.collector_pattern import CollectorPattern

_Value = TypeVar("_Value")


class ModelTypeFactory(Dict[str, _Value], Generic[_Value]):
    """Class for wrap call."""

    def __init__(self, items: Dict[str, Callable[[], _Value]]) -> None:
        """Init."""
        super().__init__(items)

    def __getitem__(self, k: str) -> _Value:
        """Get item."""
        return super().__getitem__(k)()

    def items(self) -> ItemsView[str, Callable[[], _Value]]:
        """Items."""
        return super().items()


def _get_s3() -> Type[CollectorPattern]:
    """Get s3."""
    from ML_management.collectors.s3.s3collector import S3Collector

    return S3Collector


def _get_topic_marker() -> Type[CollectorPattern]:
    """Get topic_marker."""
    from ML_management.collectors.topic_markers.topic_markers_collector import TopicMarkersCollector

    return TopicMarkersCollector


def _get_dummy() -> Type[CollectorPattern]:
    """Get dummy."""
    from ML_management.collectors.dummy.dummy_collector import DummyCollector

    return DummyCollector


def _get_local() -> Type[CollectorPattern]:
    """Get local."""
    from ML_management.collectors.local.local_collector import LocalCollector

    return LocalCollector


DATA_COLLECTORS = ModelTypeFactory(
    {
        "s3": _get_s3,
        "topic_marker": _get_topic_marker,
        "dummy": _get_dummy,
        "local": _get_local,
    }
)

DATA_REMOTE_COLLECTORS = ModelTypeFactory(
    {
        "s3": _get_s3,
        "topic_marker": _get_topic_marker,
        "dummy": _get_dummy,
    }
)
