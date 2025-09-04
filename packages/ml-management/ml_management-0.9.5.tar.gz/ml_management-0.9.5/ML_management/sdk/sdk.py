"""SDK for client library."""
import json
from typing import Dict, List

import pandas as pd


def _to_datetime(df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:
    """
    Convert df's columns to datetime.

    Parameters
    ----------
    df: pd.DataFrame
        pd.DataFrame in which the columns will be converted.
    column_names: List[str]
        Column names to be converted.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with converted columns.
    """
    for column_name in column_names:
        df[column_name] = pd.to_datetime(df[column_name], unit="s")

    return df


def _print_params_by_schema(json_schema: Dict, schema_type: str) -> None:
    """Print entity JSON Schema with required params."""
    properties_and_required_dict = {key: json_schema[key] for key in ("properties", "required") if key in json_schema}

    json_formatted_str = json.dumps(properties_and_required_dict, indent=2)

    print(f"{schema_type} json-schema:")

    print(json_formatted_str)


def _entity(base):
    base.name()
    base.description()
    base.creation_timestamp()
    base.last_updated_timestamp()
    base.tags()
    base.visibility()
