import pandas as pd
from typing import Any

from pancham.output_configuration import OutputWriter, OutputConfiguration
from pancham.reporter import get_reporter
from .salesforce_connection import get_connection

SALESFORCE_REST_UPDATE = 'salesforce_rest_update'

class SalesforceRestUpdateOutputConfiguration(OutputConfiguration):

    def can_apply(self, configuration: dict):
        """
        Determines whether the Salesforce Bulk configuration can be applied
        based on the presence and validity of required keys.

        :param configuration: A dictionary containing the configuration details.
        :type configuration: dict
        :return: A boolean indicating whether the configuration is valid
                 and can be applied.
        :rtype: bool
        :raises ValueError: If the Salesforce Bulk configuration is present
                            but missing the 'object_name' key.
        """
        salesforce_configuration = self.extract_configuration_by_key(configuration, SALESFORCE_REST_UPDATE)

        if salesforce_configuration is None:
            return False

        if 'object_name' not in salesforce_configuration:
            raise ValueError('SalesforceBulkOutput requires an object_name')

        return True

    def to_output_writer(self, configuration: dict) -> OutputWriter:
        """
        Get output writer
        :param configuration:
        :return:
        """
        salesforce_configuration = self.extract_configuration_by_key(configuration, SALESFORCE_REST_UPDATE)

        return SalesforceRestUpdateWriter(salesforce_configuration)

class SalesforceRestUpdateWriter(OutputWriter):
    """
    Writes records to Salesforce using Simple Salesforce REST update calls.

    Configuration requirements:
    - object_name: API name of the Salesforce object (e.g., 'Account').
    - id_column: Column in the DataFrame containing the Salesforce record Id.
    Optional:
    - int_cols: list of column names to coerce to int (ignores NaN -> None)
    - bool_cols: list of column names to coerce to bool (ignores NaN -> None)
    - nullable_cols: list of column names for which NaN should be converted to None
    """

    def __init__(self, configuration: dict):
        super().__init__(configuration)
        self.object_name: str = configuration.get('object_name')
        self.id_column: str = configuration.get('id_column')
        self.int_cols: list[str] = configuration.get('int_cols', [])
        self.bool_cols: list[str] = configuration.get('bool_cols', [])
        self.nullable_cols: list[str] = configuration.get('nullable_cols', [])

        if not self.object_name:
            raise ValueError('SalesforceRestUpdateWriter requires object_name in configuration')
        if not self.id_column:
            raise ValueError('SalesforceRestUpdateWriter requires id_column in configuration')

    def _coerce_value(self, col: str, value: Any) -> Any:
        # Treat pandas NA/NaN as None by default
        if pd.isna(value):
            return None
        if col in self.int_cols:
            try:
                return int(value)
            except Exception:
                return None
        if col in self.bool_cols:
            # Accept various truthy/falsey representations
            if isinstance(value, str):
                v = value.strip().lower()
                if v in ('true', 't', '1', 'yes', 'y'): return True
                if v in ('false', 'f', '0', 'no', 'n'): return False
            return bool(value)
        if col in self.nullable_cols:
            # already handled NaN above; keep as-is
            return value
        return value

    def write(self, data: pd.DataFrame, *args, **kwargs):
        """
        Loop DataFrame rows and call Simple Salesforce REST update per record.
        The Id used for update comes from self.id_column; that field is not sent in the body.
        """
        sf = get_connection()
        reporter = get_reporter()

        if data is None or data.empty:
            reporter.report_debug('SalesforceRestUpdateWriter: no data to write', {})
            return

        sobject = getattr(sf, self.object_name)

        success_count = 0
        failure_count = 0
        failures: list[dict] = []

        # Ensure id column exists
        if self.id_column not in data.columns:
            raise ValueError(f"DataFrame does not contain id column '{self.id_column}'")

        for _, row in data.iterrows():
            record_id = row.get(self.id_column)
            if pd.isna(record_id) or record_id is None or str(record_id).strip() == '':
                failure_count += 1
                failures.append({'id': None, 'error': 'Missing id', 'row': row.to_dict()})
                continue

            # build fields dict excluding id column and null values
            payload: dict[str, Any] = {}
            for col, val in row.items():
                if col == self.id_column:
                    continue
                coerced = self._coerce_value(col, val)
                if coerced is None:
                    continue
                payload[col] = coerced

            try:
                # Simple Salesforce update: sobject.update(Id, fields)
                sobject.update(str(record_id), payload)
                success_count += 1
                reporter.report_info(f'Update {success_count} complete')
            except Exception as e:
                failure_count += 1
                failures.append({'id': record_id, 'error': str(e), 'fields': payload})

        reporter.report_debug('SalesforceRestUpdateWriter completed', {
            'object_name': self.object_name,
            'id_column': self.id_column,
            'success_count': success_count,
            'failure_count': failure_count,
            'failures': failures[:10]  # log only first 10 failures to avoid noise
        })
