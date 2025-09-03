"""
Created on 8 Jul 2025

@author: ph1jb
"""

import io
import pandas as pd


def detect_compression(buffer: io.BytesIO) -> str:
    # Read the first few bytes to detect magic numbers
    magic = buffer.peek(4) if hasattr(buffer, "peek") else buffer.getbuffer()[:4]

    if magic.startswith(b"\x1f\x8b"):
        return "gzip"
    elif magic.startswith(b"BZh"):
        return "bz2"
    elif magic.startswith(b"\xfd7zXZ"):
        return "xz"
    elif magic.startswith(b"\x50\x4b\x03\x04"):  # Common zip magic
        return "zip"
    else:
        return None  # No compression or unknown


# Example usage
with open("example.pkl.gz", "rb") as f:
    buf = io.BytesIO(f.read())
    compression = detect_compression(buf)
    buf.seek(0)  # Reset buffer position
    df = pd.read_pickle(buf, compression=compression)

    def _read_sql(
        self, table: str, columns: List[str] | None = None, where_clause: str = ""
    ) -> DataFrame:
        """UNSAFE: vulnerable to SQL injection attack
        Read serialised, compressed data from cache table.
        table: cache table to select from
        columns: columns (PK) of data to select"""
        statement = f"SELECT {columns} FROM {table}{where_clause}"

        df = self.sqlahandler.read_sql(statement)
        if df.empty:
            raise ValueError("Data not found")
        return df
