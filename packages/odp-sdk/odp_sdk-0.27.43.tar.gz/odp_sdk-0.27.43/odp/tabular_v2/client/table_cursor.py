import logging
import time
from typing import Callable, Iterator

import pandas as pd
import pyarrow as pa


class CursorException(Exception):
    """Raised when the client is required to connect again with the given cursor to fetch more data"""

    def __init__(self, cursor: str):
        self.cursor = cursor


class Cursor:
    """
    A Cursor, which reads data from a scanner and allow the user to iterate over in different flavors
    It internally uses a scanner to get the data, and perform multiple requests if a cursor is returned

    it's created by the Table.select() method
    """

    def __init__(
        self,
        scanner: Callable[[str], Iterator[pa.RecordBatch]],
        schema: pa.Schema,
    ):
        self.scanner = scanner
        self.schema = schema

    def dataframes(self) -> Iterator[pd.DataFrame]:
        """
        Allow the client to iterate over pyarrow Record Batches:

            for batch in tab.select().batches():
                print(batch.num_rows)
        """
        for b in self.batches():
            yield b.to_pandas()

    def all(self, max_rows: int = 1_000_000, max_time: float = 60.0):
        """
        attempt to fetch all the data from the server as a single table
        raises TimeoutError if it takes too long or too many rows
        """
        batches = []
        t0 = time.perf_counter()
        rows = 0
        for b in self.batches():
            rows += b.num_rows
            if rows > max_rows or time.perf_counter() - t0 > max_time:
                raise OverflowError("too many rows")
            if time.perf_counter() - t0 > max_time:
                raise TimeoutError("fetching all rows is taking too long")
            batches.append(b)

        class FlatList:
            def __init__(self, tab: pa.Table):
                self._tab = tab

            def table(self) -> pa.Table:
                return self._tab

            def dataframe(self) -> pd.DataFrame:
                return self._tab.to_pandas()

            def rows(self) -> list:
                return self._tab.to_pylist()

        if len(batches) == 0:
            return FlatList(pa.Table.from_pylist([], schema=self.schema))
        return FlatList(pa.Table.from_batches(batches))

    def batches(self) -> Iterator[pa.RecordBatch]:
        """
        Allow the client to iterate over pandas DataFrames:

            for batch in tab.select().dataframes():
                print(len(batch))
        """
        t0 = time.perf_counter()
        cursor = ""
        ct = 0
        rows = 0
        while True:
            try:
                for b in self.scanner(cursor):
                    ct += 1
                    rows += b.num_rows
                    if b.num_rows > 0:
                        yield b
            except CursorException as e:
                cursor = e.cursor
                continue
            break
        logging.debug("got %d batches with %d rows in %.2fs", ct, rows, time.perf_counter() - t0)

    def rows(self) -> Iterator[dict]:
        """
        Allow the client to iterate over each rows as a python dictionary:

            for row in tab.select().rows():
                print(row)
        """
        for b in self.batches():
            for row in b.to_pylist():
                yield row

    def pages(self, size: int = 0) -> Iterator[list[dict]]:
        """
        Allow the client to iterate over pages of data, where each page is a list of python dictionaries.

            for page in tab.select().pages(1_000):
                print(len(page))

        If no size is specified, it will make a page for each chunk of data retrieved from the server
        """
        if size < 1:  # page based on what we get
            for b in self.batches():
                yield b.to_pylist()
            return

        # page based on page_size
        buf: list[dict] = []
        for b in self.batches():
            buf.extend(b.to_pylist())
            while len(buf) >= size:
                yield buf[:size]
                buf = buf[size:]
        if len(buf) > 0:
            yield buf
