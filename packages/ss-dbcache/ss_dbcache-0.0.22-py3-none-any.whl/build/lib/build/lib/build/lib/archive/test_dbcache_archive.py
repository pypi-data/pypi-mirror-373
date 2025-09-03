"""
Created on 15 Jul 2025

@author: ph1jb
"""

from pandas import DataFrame
from unittest.mock import ANY, Mock
import pandas as pd
import pytest


class TestCacheManager:
    def test__read_sql(self, mock_cache_manager):
        # Arrange
        name = "name"
        table = "table"
        data = b"abc"
        row = [data]
        expected = DataFrame({"name": name, "data": row})
        mock_cache_manager.sqlahandler.read_sql = Mock(return_value=expected)
        # Act
        where_clause = " WHERE name = 'name'"
        result = mock_cache_manager._read_sql(table, columns="data", where_clause=where_clause)
        # Assert
        statement = "SELECT data FROM table WHERE name = 'name'"
        mock_cache_manager.sqlahandler.read_sql.assert_called_once_with(statement)
        pd.testing.assert_frame_equal(result, expected)

    def test__read_sql_no_row(self, mock_cache_manager):
        # Arrange
        name = "name"
        table = "table"
        df = DataFrame()
        mock_cache_manager.sqlahandler.read_sql = Mock(return_value=df)
        # Act
        with pytest.raises(ValueError):
            mock_cache_manager._read_sql(table, name)
