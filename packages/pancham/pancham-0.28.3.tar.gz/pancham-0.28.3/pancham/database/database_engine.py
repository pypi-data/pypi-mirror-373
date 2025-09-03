import pandas as pd
from sqlalchemy import create_engine, Engine, MetaData, Table, cast, Integer, String
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from typing_extensions import Literal

from pancham.pancham_configuration import PanchamConfiguration
from pancham.reporter import Reporter

META = MetaData()

class DatabaseEngine:

    def __init__(self, config: PanchamConfiguration, reporter: Reporter):
        self.config = config
        self.reporter = reporter
        self.__engine: Engine|None = None

    @property
    def engine(self) -> Engine:
        """
        Provides a method to initialize and return a database engine instance. If the engine
        does not already exist, it is created using the provided configuration for the
        database connection.

        :return: Database engine instance

        :rtype: Engine
        """
        if self.__engine is None:
            self.__engine = create_engine(self.config.database_connection)

        return self.__engine

    def write_df(self, data: pd.DataFrame, table_name: str, exists: Literal["replace", "append"] = 'append'):
        """
        Writes a pandas DataFrame to a database table using SQLAlchemy engine.

        The method allows for specifying whether the existing table should be replaced
        or appended with new data. The operation uses a connection from the SQLAlchemy
        engine and supports various backends as determined by the engine configuration.

        :param data: A pandas DataFrame containing the data to be written to the table.
        :type data: pd.DataFrame
        :param table_name: The name of the target table in the database.
        :type table_name: str
        :param exists: Specifies the behavior if the table already exists.
                       Possible values are "replace" to overwrite the table or
                       "append" to add data to the existing table.
        :type exists: Literal["replace", "append"]
        :return: None
        """
        if self.reporter:
            self.reporter.report_output(data, table_name)

        with self.engine.connect() as conn:
            data.to_sql(table_name, conn, if_exists=exists, index=False)

    def merge_row(self,
                  row: pd.Series,
                  table_name: str,
                  merge_key: str,
                  on_missing: Literal['append', 'ignore'] = 'append',
                  merge_data_type: Literal['int', 'str'] | None = None,
                  use_native: Literal['sqlite'] | None = None
                  ):
        """
        Merges a given row into a database table. If an existing record with a matching
        merge key exists, it updates the record with non-null fields from the given row.
        If no match is found and `on_missing` is set to 'append', a new record is added.
        Raises an error if multiple records are found with the same merge key.

        :param row: A dictionary representing the row to merge into the table. The keys
            should correspond to the column names in the target table.
        :param table_name: The name of the database table to operate on.
        :param merge_key: The column name serving as the unique key for determining matches.
        :param on_missing: A flag indicating the behavior when no matching record
            exists in the table. Use 'append' to insert a new record or 'ignore'
            to skip the operation without any changes. Default is 'append'.
        :return: None
        """
        with self.engine.connect() as conn:
            table = Table(table_name, META, autoload_with=conn)

            if use_native == 'sqlite':
                query = sqlite_insert(table).values(**row)

                upsert_row = {}
                for k, v in row.items():
                    upsert_row[k] = query.excluded[k]

                query = query.on_conflict_do_update(index_elements=[merge_key], set_=upsert_row)
                conn.execute(query)
                conn.commit()
                return

            existing_record_query = table.select()

            if merge_data_type == 'int':
                existing_record_query = existing_record_query.where(cast(table.c[merge_key], Integer) == cast(row[merge_key], Integer))
            elif merge_data_type == 'str':
                existing_record_query = existing_record_query.where(cast(table.c[merge_key], String) == cast(row[merge_key], String))
            else:
                existing_record_query = existing_record_query.where(table.c[merge_key] == row[merge_key])

            existing_record = conn.execute(existing_record_query).fetchall()

            if len(existing_record) == 0 and on_missing == 'append' :
                insert_query = table.insert().values(**row)
                conn.execute(insert_query)
                conn.commit()

            if len(existing_record) == 1:
                non_null_row = dict(filter(lambda x: x[1] is not None, row.items()))
                update_query = table.update().where(table.c[merge_key] == row[merge_key]).values(**non_null_row)
                conn.execute(update_query)
                conn.commit()

            if len(existing_record) > 1:
                raise ValueError(f"Merge key {merge_key} is not a unique key.")


db_engine: DatabaseEngine|None = None

def initialize_db_engine(config: PanchamConfiguration, reporter: Reporter):
    """
    Initializes the database engine using the provided configuration and reporter.

    This function sets up the `db_engine` with the given `config` and `reporter`.
    It ensures the global database engine is initialized and ready to interact with
    the configured database.

    :param config: The configuration object used for database setup.
    :type config: PanchamConfiguration
    :param reporter: The reporter instance for logging or reporting database
        initialization details.
    :type reporter: Reporter
    :return: None
    :rtype: NoneType
    """
    global db_engine, META

    db_engine = DatabaseEngine(config, reporter)
    META = MetaData()

def get_db_engine() -> DatabaseEngine:
    """
    Retrieves the initialized database engine instance.

    This function returns a pre-initialized `DatabaseEngine` instance that
    is required for database operations. The function assumes that the
    database engine has already been configured and available; otherwise,
    it raises an error indicating the absence of the initialization.

    :raises ValueError: If the database engine has not been initialized.
    :return: The initialized database engine instance.
    :rtype: DatabaseEngine
    """
    global db_engine
    if db_engine is None:
        raise ValueError("Database engine not initialized")
    return db_engine
