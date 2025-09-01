import datetime
from decimal import Decimal
from typing import Dict, List, Union

import pandas as pd
import pyarrow as pa
from pyarrow import Field


def validate_data_against_schema(data: Union[List[Dict], pa.RecordBatch, pd.DataFrame], schema: pa.Schema):
    """
    Validate data against schema
    Checks for required fields and data types
    """
    assert schema is not None
    assert data is not None

    if isinstance(data, list):
        for i, row in enumerate(data):
            if not isinstance(row, dict):
                raise ValueError(f"expected dict but got {type(row)}")
            _check_required_fields(list(row.keys()), schema)
            for k, v in row.items():
                try:
                    field = schema.field(k)
                    _validate_data_cell(i, field, v, k)
                except KeyError:
                    pass

    elif isinstance(data, pa.RecordBatch):
        _check_required_fields(data.schema.names, schema)
        for field in data.schema:
            column_data = data.column(field.name)
            for i in range(data.num_rows):
                py_val = column_data[i].as_py()
                _validate_data_cell(i, field, py_val, field.name)

    elif isinstance(data, pd.DataFrame):
        _check_required_fields(data.columns, schema)
        for column_name in data.columns:
            field = schema.field(column_name)
            data[column_name].apply(lambda cell: _validate_data_cell(0, field, cell, column_name))

    else:
        raise ValueError(f"unexpected type {type(data)}")


def _check_required_fields(input_field_names: List[str], schema: pa.Schema):
    for field_name in schema.names:
        field = schema.field(field_name)
        if field_name not in input_field_names and field.nullable is False:
            raise ValueError(f"missing required column: {field_name}")


def _validate_data_cell(row_index: int, field: Field, v: any, k: str):
    if v is None:
        if field.nullable is False:
            raise ValueError(f"missing required column value at row index {row_index}: {field.name}")
        else:
            return

    if pa.types.is_string(field.type):
        if not isinstance(v, str):
            raise ValueError(f"unexpected type {type(v)} for {k} at row index {row_index}")
    if pa.types.is_integer(field.type):
        if not isinstance(v, int):
            raise ValueError(f"unexpected type {type(v)} for {k} at row index {row_index}")
    if pa.types.is_floating(field.type):
        if not isinstance(v, (int, float)):
            raise ValueError(f"unexpected type {type(v)} for {k} at row index {row_index}")
    if pa.types.is_boolean(field.type):
        if not isinstance(v, bool):
            raise ValueError(f"unexpected type {type(v)} for {k} at row index {row_index}")
    if pa.types.is_date(field.type):
        if not isinstance(v, datetime.date):
            raise ValueError(f"unexpected type {type(v)} for {k} at row index {row_index}")
    if pa.types.is_timestamp(field.type):
        if not isinstance(v, datetime.datetime):
            raise ValueError(f"unexpected type {type(v)} for {k} at row index {row_index}")
    if pa.types.is_time(field.type):
        if not isinstance(v, datetime.time):
            raise ValueError(f"unexpected type {type(v)} for {k} at row index {row_index}")
    if pa.types.is_decimal(field.type):
        if not isinstance(v, int) and not isinstance(v, Decimal):
            raise ValueError(f"unexpected type {type(v)} for {k} at row index {row_index}")
    if pa.types.is_binary(field.type):
        if not isinstance(v, bytes):
            raise ValueError(f"unexpected type {type(v)} for {k} at row index {row_index}")
