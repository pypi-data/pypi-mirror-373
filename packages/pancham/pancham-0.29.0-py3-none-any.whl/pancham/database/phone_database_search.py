import phonenumbers
from sqlalchemy import Table, select, Connection, Select

from pancham.reporter import get_reporter
from .database_engine import get_db_engine, META
from .caching_database_search import DatabaseSearch

class PhoneDatabaseSearch(DatabaseSearch):

    def __init__(self, table_name: str, search_col: str, value_col: str, region_col: str, cast_search: None|str = None):
        self.table_name = table_name
        self.search_col = search_col
        self.value_col = value_col
        self.cast_search = cast_search
        self.region_col = region_col
        self.cached_data = {}

    def get_mapped_phone_id(self, search_value: str | int, region: str) -> str | int | None:
        """
        Retrieves the mapped value corresponding to the provided search key.

        This method looks up the given `search_value` in the data dictionary. If the
        search key exists in the dictionary, the corresponding value is returned.
        If the search key is not found, the method returns `None`.

        :param search_value: The key for which the mapped value needs to be retrieved,
            which can be of type `str` or `int`.
        :return: Mapped value associated with the provided search key if found,
            which can be of type `str` or `int`. Returns `None` if the key is not found.
        """
        data = self.__load_data()
        phone = self.__parse_and_format(search_value, region)

        if phone is None:
            return None

        return data.get(phone, None)

    def __load_data(self) -> dict[phonenumbers, str|int]:
        """
        Loads data from the database table and caches it for future access. The
        method retrieves rows from the table based on the provided column names
        and performs type casting as per configuration. If data has been cached
        previously, it simply returns the cached data to optimize performance
        by avoiding redundant queries to the database.

        :return: A dictionary mapping search column values to value column values.
        :rtype: dict[str | int, str | int]
        :raises sqlalchemy.exc.SQLAlchemyError: If an error occurs during database
            connection or query execution.
        """
        if len(self.cached_data) > 0:
            return self.cached_data

        with get_db_engine().engine.connect() as conn:
            data_table = Table(self.table_name, META, autoload_with=conn)
            query = select(data_table.c[self.search_col, self.value_col, self.region_col]).where(data_table.c[self.search_col].is_not(None))

            res = conn.execute(query).fetchall()

            for row in res:
                id_value = self.cast_value(row[1], self.value_col)
                value = row[0]
                phone = self.__parse_and_format(value, row[2])
                if phone is None:
                    continue

                self.cached_data[phone] = id_value

        return self.cached_data

    def __parse_and_format(self, input: str, region: str) -> str|None:
        """
        Parses and formats a phone number input into the E.164 format.

        This method takes a string input representing a phone number, parses it
        using the phonenumbers library, and formats it into the standardized
        E.164 format. This is useful for ensuring consistency in phone number
        representation across different systems or outputs.

        :param input: A string representation of the input phone number.
        :return: A formatted phone number string in E.164 format.
        """
        try:
            phone = phonenumbers.parse(input, region)
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            return None
