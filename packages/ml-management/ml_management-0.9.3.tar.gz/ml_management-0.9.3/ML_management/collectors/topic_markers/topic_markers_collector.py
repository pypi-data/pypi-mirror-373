"""Collector for fetching texts marked with ceritain topic, as well as negative examples."""
import os
from typing import List

import pandas as pd
from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation

from ML_management.collectors.collector_pattern import CollectorPattern
from ML_management.collectors.topic_markers.api_schema import Query


class TopicMarkersCollector(CollectorPattern):
    """Collector class for fetching texts marked with ceritain topic, as well as negative examples."""

    def __init__(self):
        # can not import GRAPHQL_URL from server's env_variables file
        self.graphql_url = os.environ.get("GRAPHQL_URL", "http://localhost:9000/graphql")
        self.endpoint = HTTPEndpoint(self.graphql_url)
        # TODO for now, recreate csv file every time at a hardcoded location

    @staticmethod
    def get_json_schema():
        """Return json schema."""
        schema = {
            "type": "object",
            "properties": {
                "local_path": {"type": "string"},
                "marker": {"type": "string"},
                "start_date": {"type": "integer"},
                "end_date": {"type": "integer"},
            },
            "required": [
                "marker",
            ],
            "additionalProperties": False,
        }

        return schema

    def __save_texts(self, texts: List[str], labels: List[int], path: str):
        """Save texts and labels to csv by passed path."""
        # path is supposed to be a full path to file
        data_dict = {
            "text": texts,
            "label": labels,
        }
        dataframe = pd.DataFrame(data_dict)
        # shuffle everything
        dataframe = dataframe.sample(frac=1).reset_index(drop=True)
        # this should work correctly with commas and quotes in text...
        dataframe.to_csv(path, index=False)

    def __gql_query(self, form: dict) -> dict:
        """Make GraphQL query to fetch new data from IE module."""
        op = Operation(Query)

        query = op.list_text_from_document_with_marker(form=form)
        query.marker_text()
        query.not_marker_text()

        data = self.endpoint(op)
        return data

    def set_data(self, *_args, **kwargs):
        """Fetch texts with passed marker, serialize into given dir and return path."""
        local_path = kwargs.get("local_path", "topic_markers.csv")
        form = {
            "marker": kwargs["marker"],
        }
        if "start_date" in kwargs:
            form["startDate"] = kwargs["start_date"]
        if "end_date" in kwargs:
            form["endDate"] = kwargs["end_date"]

        raw_data = self.__gql_query(form)
        marker_texts = raw_data["data"]["listTextFromDocumentWithMarker"]["markerText"]
        not_marker_texts = raw_data["data"]["listTextFromDocumentWithMarker"]["notMarkerText"]
        # TODO do we raise if there are no examples whatsoever?
        all_labels = [1] * len(marker_texts) + [0] * len(not_marker_texts)
        all_texts = marker_texts + not_marker_texts
        self.__save_texts(texts=all_texts, labels=all_labels, path=local_path)

        return local_path
