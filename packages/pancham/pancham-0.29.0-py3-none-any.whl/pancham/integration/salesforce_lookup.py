import pandas as pd

from pancham.reporter import get_reporter
from .salesforce_connection import get_connection


class SalesforceLookup:

    def __init__(self, query: str):
        self.query = query
        self.cache = None

    def get_mapped_id(self, search_column: str, value: str, value_column: str = 'Id') -> str | None:
        """
        Retrieve a mapped ID from a DataFrame based on a key-value pair.

        This function searches for rows in an internal DataFrame, matching
        a specified key-value pair. If matching rows are found, it retrieves
        the value from the specified output column (defaulting to 'Id')
        from the first matched row. If no matches are found, the function
        returns None.

        :param search_column: The column name to use as the key for filtering.
        :param value: The value to match in the specified key column.
        :param output_key: The column name from which to retrieve the mapped ID.
                           Defaults to 'Id'.
        :return: The mapped ID string from the first matching row if a match is
                 found; otherwise, None.
        :rtype: str | None
        """
        data = self.__get_data()

        filtered = data.loc[data[search_column] == value]

        if len(filtered) == 0:
            return None

        return filtered[value_column].iloc[0]

    def __get_data(self) -> pd.DataFrame:
        if self.cache is not None:
            return self.cache

        data = []

        sf = get_connection()
        query_result = sf.query_all_iter(self.query)
        for record in query_result:
            data.append(record)
        self.cache = pd.DataFrame(data)

        reporter = get_reporter()
        reporter.report_debug(
            f'Salesforce Lookup data {self.cache}'
        )

        return self.cache

