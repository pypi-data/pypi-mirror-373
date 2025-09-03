from enum import Enum


class CollectionsTablesGetFormattedTableDataExportFormat(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    PARQUET = "parquet"
    TSV = "tsv"

    def __str__(self) -> str:
        return str(self.value)
