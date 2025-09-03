from sqlalchemy import MetaData, Table, Column, String
import pandas as pd

from pancham.database.database_engine import get_db_engine, initialize_db_engine
from pancham.reporter import PrintReporter
from pancham.database.phone_database_search import PhoneDatabaseSearch
from pancham_configuration import PanchamConfiguration

class MockConfig(PanchamConfiguration):

    @property
    def database_connection(self) -> str:
        return "sqlite:///:memory:"

class TestPhoneDatabaseSearch:

    def test_match_phone_number(self):
        initialize_db_engine(MockConfig(), PrintReporter())
        database_name = 'tel1'

        meta = MetaData()
        Table(database_name, meta, Column("tel", String), Column("order_id", String), Column("region", String))

        meta.create_all(get_db_engine().engine)

        data = pd.DataFrame({'tel': ['+447781123456', '+447781111111'], 'order_id': ['1', '2'], 'region':['GB', 'GB']})

        get_db_engine().write_df(data, database_name)

        search = PhoneDatabaseSearch(database_name, 'tel', 'order_id', 'region')

        matched = search.get_mapped_phone_id('07781 111111', "GB")

        assert matched == '2'
        assert search.get_mapped_phone_id('0778222222', "GB") is None

    def test_match_invalid_phone_number(self):
        initialize_db_engine(MockConfig(), PrintReporter())
        database_name = 'tel2'

        meta = MetaData()
        Table(database_name, meta, Column("tel", String), Column("order_id", String), Column("region", String))

        meta.create_all(get_db_engine().engine)

        data = pd.DataFrame({'tel': [None, 'abc'], 'order_id': ['1', '2'], 'region':['GB', 'GB']})

        get_db_engine().write_df(data, database_name)

        search = PhoneDatabaseSearch(database_name, 'tel', 'order_id', 'region')

        matched = search.get_mapped_phone_id('07781 111111', "GB")

        assert matched is None
        assert search.get_mapped_phone_id('0778222222', "GB") is None
