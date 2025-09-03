import pandas as pd

from pancham.integration.salesforce_connection import get_connection
from pancham.file_loader import FileLoader
from pancham.reporter import get_reporter


class SalesforceQueryLoader(FileLoader):
    """
    Provides functionality to load data from Salesforce based on a given query.

    This class is designed to interact with Salesforce using a SOQL query provided through
    the `read_file` method. It uses an established connection to Salesforce and iterates
    through the result set to create a DataFrame containing the queried records.

    :ivar file_loader: Base file loader class to provide core file loading mechanisms.
    :type file_loader: FileLoader
    """

    def read_file(self, filename: str, **kwargs) -> pd.DataFrame:
        query = kwargs.get('query')

        sf = get_connection()
        data = []

        sf_data = sf.query_all(query)
        df = pd.DataFrame(sf_data['records'])

        reporter = get_reporter()
        reporter.report_debug(f'Salesforce Query data {df}')

        return df
