import odp.tabular_v2.client as tab
from odp.new_client import Client


class Dataset:
    """
    Represents a dataset in the Ocean Data Platform.
    This class provides access to the dataset's storage (files, table)
    """

    def __init__(self, cli: Client, id: str):
        self.cli = cli
        self.id = id
        self.table = tab.Table(cli, id)
        self.files = self.table.raw
        self.name = ""  # do integration with catalog v2 when ready

        # shortcuts for common operations
        self.select = self.table.select

    def __str__(self):
        if self.name:
            return f"Dataset({self.id} - {self.name})"
        else:
            return f"Dataset({self.id})"

    def __enter__(self):
        return self.table.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.table.__exit__(exc_type, exc_val, exc_tb)

    @staticmethod
    def _from_catalog_v2(cli: Client, data: dict):
        ds = Dataset(cli, data["id"])
        ds.name = data["name"]
        return ds
