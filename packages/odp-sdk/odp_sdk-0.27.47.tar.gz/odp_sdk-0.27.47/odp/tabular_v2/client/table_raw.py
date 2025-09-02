import io
import json
from typing import TYPE_CHECKING, Iterator, Optional, Union

import pyarrow as pa

if TYPE_CHECKING:
    from odp.tabular_v2.client import Table


class Raw:
    def __init__(self, table: "Table"):
        self.table = table

    def list(self, query: Optional[str] = None, vars: Optional[dict] = None) -> list:
        res = self.table._impl(
            "/api/table/v2/raw/list",
            params={"table_id": self.table._id, "query": query, "vars": vars},
            data={},
        )
        body = res.json()
        return body["files"]

    def list_batches(self, query: Optional[str] = None, vars: Optional[dict] = None) -> pa.Table:
        res = self.table._impl(
            "/api/table/v2/raw/batch-list",
            params={"table_id": self.table._id},
            data={"query": query, "vars": vars},
        )
        reader = pa.ipc.open_stream(res.reader())
        batches = [batch for batch in reader]
        return pa.Table.from_batches(batches, schema=reader.schema)

    def upload(self, name: str, data: Union[bytes, io.IOBase]) -> str:
        res = self.table._impl(
            "/api/table/v2/raw/upload",
            params={"table_id": self.table._id, "name": name},
            data=data,
            retry=False,
        )
        body = res.json()
        return body["raw_id"]

    def update_meta(self, identifier: str, data: dict) -> dict:
        res = self.table._impl(
            "/api/table/v2/raw/update_meta",
            params={"table_id": self.table._id, "id": identifier},
            data=json.dumps(data).encode("utf-8"),
            retry=False,
        )
        return res.json()

    def download(self, id: str) -> Iterator[bytes]:
        res = self.table._impl(
            "/api/table/v2/raw/download",
            params={"table_id": self.table._id, "id": id},
        )
        return res.iter()

    def delete(self, id: str) -> None:
        self.table._impl(
            "/api/table/v2/raw/delete",
            params={"table_id": self.table._id, "id": id},
            retry=False,
        )

    def ingest(self, id: str) -> None:
        self.table._impl(
            "/api/table/v2/raw/ingest",
            params={"table_id": self.table._id, "id": id},
            data={},
            retry=False,
        )
