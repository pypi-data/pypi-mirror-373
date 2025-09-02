import io
import json
import logging
import typing
from functools import partial
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Union

import pandas as pd
import pyarrow as pa
import requests

import odp.tabular_v2.client as old
from odp.tabular_v2.client.table_raw import Raw
from odp.tabular_v2.util import vars_to_json
from odp.util.cheapdantic import BaseModel

if TYPE_CHECKING:
    from odp.tabular_v2.client import Cursor


class TableStats(BaseModel):
    num_rows: int
    """number of rows in the table"""

    size: int
    """size of the table in bytes, including metadata and schema"""


# temporary: migrate old API to the new client
def _request_to_new_client(
    cli,  # new client instance
    path: str,
    data: Union[Dict, bytes, Iterator[bytes], io.IOBase, None] = None,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    retry: bool = True,  # if it is safe to retry the request on failure
) -> old.Client.Response:
    req = requests.Request(
        method="POST",
        url=cli.base_url + path,
        params=params,
        headers=headers,
        data=data,
    )
    res = cli._request(req, retry)
    return old.Client.Response(res)


class Table:
    def __init__(self, impl, table_id: str):
        self._id = table_id

        # unify new and old client _request() method
        import odp.new_client as new

        if isinstance(impl, new.Client):
            self._impl = partial(_request_to_new_client, impl)
        elif isinstance(impl, old.Client):
            self._impl = impl._request
        else:
            raise ValueError(f"Unexpected implementation type: {type(impl)}")

        self._tx = None

    @property
    def raw(self) -> "Raw":
        return Raw(self)

    def stats(self) -> TableStats:
        """
        Get the table statistics, such as the number of rows, size, etc.
        @return: a TableStats object containing the statistics, including:
                 - num_rows: the number of rows in the table
                 - size: the size of the table in bytes, including metadata and schema
        """
        res = self._impl(
            path="/api/table/v2/stats",
            params={
                "table_id": self._id,
            },
        )
        return TableStats(**res.json())

    def schema(self) -> typing.Optional[pa.Schema]:
        try:
            empty = list(self._select(inner_query='"fetch" == "schema"'))
        except FileNotFoundError:
            return None
        assert len(empty) == 1
        assert empty[0].num_rows == 0
        return empty[0].schema

    def alter(self, schema: pa.Schema, from_names: dict = {}):
        """
        perform a schema change, re-ingesting all the data in the table with the new schema
        from_names is a dictionary mapping new names to old names, used to rename fields or duplicate them
        """
        j = json.dumps(from_names).encode("utf-8")
        # create a stream with only the schema
        buf = io.BytesIO()
        w = pa.ipc.RecordBatchStreamWriter(buf, schema)
        w.write_batch(
            pa.RecordBatch.from_pylist([], schema),
            {"rename": j},
        )
        w.close()

        res = self._impl(
            path="/api/table/v2/sdk/alter",
            params={
                "table_id": self._id,
            },
            data=buf.getvalue(),  # send the schema using pa.ipc
            retry=False,
        )
        return res.json()

    def drop(self):
        """
        drop the table data and schema
        this operation is irreversible
        @return:
        """
        try:
            res = self._impl(
                path="/api/table/v2/drop",
                params={
                    "table_id": self._id,
                },
                retry=False,
            ).json()
            logging.debug("dropped %s: %s", self._id, res)
        except FileNotFoundError:
            logging.info("table %s does not exist", self._id)

    def _validate_parquet_schema(self, schema: pa.Schema):
        compatible_types = {
            pa.types.is_integer,
            pa.types.is_floating,
            pa.types.is_boolean,
            pa.types.is_string,
            pa.types.is_binary,
            pa.types.is_date,
            pa.types.is_timestamp,
            pa.types.is_decimal,
            pa.types.is_time,
        }
        for field in schema:
            if not any(check_function(field.type) for check_function in compatible_types):
                raise ValueError(f"Incompatible type for parquet detected: {field.name} ({field.type})")

    def create(self, schema: pa.Schema):
        """
        set the table schema using the given pyarrow schema
        fields might contains metadata which will be used internally:
        * index: the field should be used to partition the data
        * isGeometry: the field is a geometry (wkt for string, wkb for binary)
        @param schema: pyarrow.Schema
        @raise FileExistsError if the schema is already set
        @return:
        """
        self._validate_parquet_schema(schema)
        buf = io.BytesIO()
        w = pa.ipc.RecordBatchStreamWriter(buf, schema)
        w.write_batch(pa.RecordBatch.from_pylist([], schema=schema))
        w.close()

        self._impl(
            path="/api/table/v2/sdk/create",
            params={
                "table_id": self._id,
            },
            data=buf.getvalue(),
            retry=False,
        ).json()

    def aggregate(
        self,
        group_by: str = "",
        filter: str = "",
        aggr: Union[dict, None] = None,
        vars: Union[dict, list, None] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        aggregate the data after the optional `query` filter
        the paramater `by` is used to determine the key for the aggregation, and can be an expression.
        the optional `aggr` specify which fields need to be aggregated, and how
        If not specified, the fields with metadata "aggr" will be used
        a single DataFrame will be returned, with the index set to the key used for aggregation
        """
        schema = self.schema()
        if schema is None:
            raise FileNotFoundError(f"Table {self._id} does not exist")

        # backward compatibility
        filter = filter or kwargs.get("query", "")
        group_by = group_by or kwargs.get("by", "'TOTAL'")

        if aggr is None:
            aggr = {}
            for field in schema:
                if field.metadata and b"aggr" in field.metadata:
                    aggr[field.name] = field.metadata[b"aggr"].decode()

        tot_func = {
            "*": "sum",
        }
        for field, a_type in aggr.items():
            if a_type == "mean" or a_type == "avg":
                tot_func[field + "_sum"] = "sum"
                tot_func[field + "_count"] = "sum"
            elif a_type == "sum":
                tot_func[field + "_sum"] = "sum"
            elif a_type == "min":
                tot_func[field + "_min"] = "min"
            elif a_type == "max":
                tot_func[field + "_max"] = "max"
            elif a_type == "count":
                tot_func[field + "_count"] = "sum"
            else:
                raise ValueError(f"unknown aggregation type: {a_type}")

        total: Union[pd.DataFrame, None] = None
        for b in self._select(typ="aggregate", by=group_by or "'TOTAL'", inner_query=filter, aggr=aggr, vars=vars):
            df: pd.DataFrame = b.to_pandas()
            # logging.warning("PARTIAL:\n%s", df)
            if total is None:
                total = df
            else:
                total = pd.concat([total, df], ignore_index=True)
                total = total.groupby("").agg(tot_func).reset_index()
        if total is None:
            return pd.DataFrame()

        for field, a_type in aggr.items():
            logging.debug("field: %s, type: %s", field, a_type)
            if a_type == "mean" or a_type == "avg":
                total[field] = total[field + "_sum"] / total[field + "_count"]
                total.drop(columns=[field + "_sum", field + "_count"], inplace=True)
            elif a_type in "sum":
                total[field] = total[field + "_sum"]
                total.drop(columns=[field + "_sum"], inplace=True)
            elif a_type == "min":
                total[field] = total[field + "_min"]
                total.drop(columns=[field + "_min"], inplace=True)
            elif a_type == "max":
                total[field] = total[field + "_max"]
                total.drop(columns=[field + "_max"], inplace=True)
            elif a_type == "count":
                total[field] = total[field + "_count"]
                total.drop(columns=[field + "_count"], inplace=True)
            else:
                raise ValueError(f"unknown aggregation type: {a_type}")

        total = total.set_index("")
        # logging.debug("TOTAL:\n%s", total)
        return total

    def _query_cursor(
        self,
        filter: str = "",
        cols: Optional[List[str]] = None,
        vars: Union[dict, list, None] = None,
        stream_ttl: float = 30.0,
        typ: str = "select",
        tx_id: str = "",
    ) -> "Cursor":
        def scanner(scanner_cursor: str) -> Iterator[pa.RecordBatch]:
            logging.debug("selecting cursor=%s, filter=%s", scanner_cursor, filter)
            for b in self._select(
                tx=tx_id,
                typ=typ,
                inner_query=filter,
                cols=cols,
                vars=vars,
                cursor=scanner_cursor,
                timeout=stream_ttl,
            ):
                # logging.debug("got %d rows, decoding...", b.num_rows)
                yield b

        from odp.tabular_v2.client import Cursor

        schema = self.schema()
        if cols:
            invalid_cols = [col for col in cols if col not in schema.names]
            if invalid_cols:
                raise ValueError(f"Invalid columns: {invalid_cols}. Available columns: {schema.names}")
            schema = pa.schema([schema.field(col) for col in cols])
        return Cursor(scanner=scanner, schema=schema)

    def select(
        self,
        filter: str = "",
        columns: Optional[List[str]] = None,
        vars: Union[dict, list, None] = None,
        timeout: float = 30.0,
        **kwargs,  # for backward compatibility
    ) -> "Cursor":
        """
        fetch data from the underling table

        for row in tab.select("age > 18").rows():
            print(row)

        you can use bind variables, especially if you need to use date/time objects:

        for row in tab.select("age > $age", vars={"age": 18}).rows():
            print(row)

        and limits which columns you want to retrieve:

        for row in tab.select("age > 18", cols=["name", "age"]).rows():
            print(row)

        The object returned is a cursor, which can be scanned by rows, batches, pages, pandas dataframes, etc.

        you can check the documentation of the Cursor for more information
        """
        # backward compatibility
        filter = filter or kwargs.get("query", "")
        columns = columns or kwargs.get("cols", None)
        return self._query_cursor(filter, columns, vars, timeout, "select")

    def __enter__(self):
        if self._tx:
            raise ValueError("already in a transaction")

        res = self._impl(
            path="/api/table/v2/begin",
            params={
                "table_id": self._id,
            },
            retry=False,
        ).json()
        from odp.tabular_v2.client.table_tx import Transaction

        self._tx = Transaction(self, res["tx_id"])
        return self._tx

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logging.warning("aborting transaction %s", self._tx._id)
            # try:
            #    self._impl(
            #        path="/api/table/v2/rollback",
            #        params={
            #            "table_id": self._id,
            #            "tx_id": self._tx._id,
            #        },
            #    )
            # except Exception as e:
            #    logging.error("ignored: rollback failed: %s", e)
        else:
            self._tx.flush()
            self._impl(
                path="/api/table/v2/commit",
                params={
                    "table_id": self._id,
                    "tx_id": self._tx._id,
                },
                retry=False,
            )
        self._tx = None

    # used as a filter in Cursor, encode in tx
    def _select(
        self,
        tx: str = "",
        typ: str = "select",
        inner_query: str = "",
        aggr: Optional[dict] = None,
        cols: Optional[List[str]] = None,
        vars: Union[Dict, List, None] = None,
        by: Optional[str] = None,
        cursor: Union[str, None] = "",
        timeout: float = 30.0,
    ) -> Iterator[pa.RecordBatch]:
        # t0 = time.perf_counter()
        while cursor is not None:
            res = self._impl(
                path="/api/table/v2/sdk/" + typ,
                params={
                    "table_id": self._id,
                    "tx_id": tx,
                },
                data={
                    "query": str(inner_query) if inner_query else None,
                    "cols": cols,
                    "cursor": cursor,
                    "aggr": aggr,
                    "by": by,
                    "vars": vars_to_json(vars),
                    "timeout": timeout,
                },
                retry=typ in {"select", "aggregate"},
            )
            cursor = None
            reader = res.reader()
            r = pa.ipc.RecordBatchStreamReader(reader)
            for bm in r.iter_batches_with_custom_metadata():
                if bm.custom_metadata and b"error" in bm.custom_metadata:
                    raise ValueError("server error: %s" % bm.custom_metadata[b"error"].decode())

                if bm.custom_metadata:
                    if b"cursor" in bm.custom_metadata:
                        cursor = bm.custom_metadata[b"cursor"].decode()
                        logging.debug("response is partially processed with cursor %s", cursor)
                    if b"stats" in bm.custom_metadata:
                        logging.debug("stats: %s", bm.custom_metadata[b"stats"].decode())

                # logging.debug("got batch with %d rows", bm.batch.num_rows)
                yield bm.batch

    def _insert_batch(
        self,
        data: pa.RecordBatch,
        tx: str = "",
    ):
        schema = self.schema()
        buf = io.BytesIO()
        w = pa.ipc.RecordBatchStreamWriter(buf, schema)
        w.write_batch(data)
        w.close()

        self._impl(
            path="/api/table/v2/sdk/insert",
            params={
                "table_id": self._id,
                "tx_id": tx,
            },
            data=buf.getvalue(),
            retry=False,
        ).json()
