import pandas as pd
import pytest

from sqlalchemy import MetaData, Table, Column, String, Integer, UniqueConstraint

from database.database_engine import DatabaseEngine, get_db_engine, initialize_db_engine
from pancham.pancham_configuration import PanchamConfiguration
from pancham.reporter import PrintReporter


class MockConfig(PanchamConfiguration):

    @property
    def database_connection(self) -> str:
        return "sqlite:///:memory:"

class TestDatabaseEngine:

    def test_engine(self):
        config = MockConfig()
        db_engine = DatabaseEngine(config, PrintReporter())

        assert db_engine.engine is not None

    def test_engine_write_df(self):
        config = MockConfig()
        db_engine = DatabaseEngine(config, PrintReporter())
        meta = MetaData()
        customer = Table('customer', meta, Column("email", String))

        meta.create_all(db_engine.engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com']})

        db_engine.write_df(data, 'customer')

    def test_get_db_engine(self):
        with pytest.raises(ValueError):
            get_db_engine()

    def test_db_init(self):
        initialize_db_engine(MockConfig(), PrintReporter())

        assert get_db_engine() is not None

    def test_merge_data(self):
        config = MockConfig()
        db_engine = DatabaseEngine(config, PrintReporter())
        meta = MetaData()
        customer = Table('customer2', meta, Column("email", String), Column("customer_name", String))

        meta.create_all(db_engine.engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com']})

        db_engine.write_df(data, 'customer2')

        update = pd.Series(data={'email': 'b@example.com', 'customer_name': 'Bob'}, index=['email', 'customer_name'])

        db_engine.merge_row(update, 'customer2', 'email', on_missing='ignore')

        select = customer.select().where(customer.c.email == 'b@example.com')

        with db_engine.engine.connect() as conn:
            result = conn.execute(select).fetchall()

            assert len(result) == 1
            assert result[0][0] == 'b@example.com'
            assert result[0][1] == 'Bob'

    def test_merge_data_and_append(self):
        table_name = 'customer3'
        config = MockConfig()
        db_engine = DatabaseEngine(config, PrintReporter())
        meta = MetaData()
        customer = Table(table_name, meta, Column("email", String), Column("customer_name", String))

        meta.create_all(db_engine.engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com']})

        db_engine.write_df(data, table_name)

        update = pd.Series(data={'email': 'b@example.com', 'customer_name': 'Bob'}, index=['email', 'customer_name'])
        update2 = pd.Series(data={'email': 'c@example.com', 'customer_name': 'Chris'}, index=['email', 'customer_name'])

        db_engine.merge_row(update, table_name, 'email', on_missing='append')
        db_engine.merge_row(update2, table_name, 'email', on_missing='append')

        select = customer.select()

        with db_engine.engine.connect() as conn:
            result = conn.execute(select).fetchall()

            assert len(result) == 3
            assert result[1][0] == 'b@example.com'
            assert result[1][1] == 'Bob'
            assert result[2][0] == 'c@example.com'
            assert result[2][1] == 'Chris'

    def test_merge_data_without_append(self):
        table_name = 'customer4'
        config = MockConfig()
        db_engine = DatabaseEngine(config, PrintReporter())
        meta = MetaData()
        customer = Table(table_name, meta, Column("email", String), Column("customer_name", String))

        meta.create_all(db_engine.engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com']})

        db_engine.write_df(data, table_name)

        update = pd.Series(data={'email': 'b@example.com', 'customer_name': 'Bob'}, index=['email', 'customer_name'])
        update2 = pd.Series(data={'email': 'c@example.com', 'customer_name': 'Chris'}, index=['email', 'customer_name'])

        db_engine.merge_row(update, table_name, 'email', on_missing='ignore')
        db_engine.merge_row(update2, table_name, 'email', on_missing='ignore')

        select = customer.select()

        with db_engine.engine.connect() as conn:
            result = conn.execute(select).fetchall()

            assert len(result) == 2
            assert result[1][0] == 'b@example.com'
            assert result[1][1] == 'Bob'

    def test_merge_data_cast_without_append(self):
        table_name = 'customer5'
        config = MockConfig()
        db_engine = DatabaseEngine(config, PrintReporter())
        meta = MetaData()
        customer = Table(table_name, meta, Column("email", String), Column("customer_name", String))

        meta.create_all(db_engine.engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com']})

        db_engine.write_df(data, table_name)

        update = pd.Series(data={'email': 'b@example.com', 'customer_name': 'Bob'}, index=['email', 'customer_name'])
        update2 = pd.Series(data={'email': 'c@example.com', 'customer_name': 'Chris'}, index=['email', 'customer_name'])

        db_engine.merge_row(update, table_name, 'email', on_missing='ignore', merge_data_type='str')
        db_engine.merge_row(update2, table_name, 'email', on_missing='ignore', merge_data_type='str')

        select = customer.select()

        with db_engine.engine.connect() as conn:
            result = conn.execute(select).fetchall()

            assert len(result) == 2
            assert result[1][0] == 'b@example.com'
            assert result[1][1] == 'Bob'

    def test_merge_data_cast_int_without_append(self):
        table_name = 'customer7'
        config = MockConfig()
        db_engine = DatabaseEngine(config, PrintReporter())
        meta = MetaData()
        customer = Table(table_name, meta, Column("email", String), Column("customer_name", String), Column("customer_id", Integer))

        meta.create_all(db_engine.engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com'], 'customer_id': [1, 2]})

        db_engine.write_df(data, table_name)

        update = pd.Series(data={'email': 'b@example.com', 'customer_name': 'Bob', 'customer_id': 2}, index=['email', 'customer_name', 'customer_id'])
        update2 = pd.Series(data={'email': 'c@example.com', 'customer_name': 'Chris', 'customer_id': 3}, index=['email', 'customer_name', 'customer_id'])

        db_engine.merge_row(update, table_name, 'customer_id', on_missing='ignore', merge_data_type='int')
        db_engine.merge_row(update2, table_name, 'customer_id', on_missing='ignore', merge_data_type='int')

        select = customer.select()

        with db_engine.engine.connect() as conn:
            result = conn.execute(select).fetchall()

            assert len(result) == 2
            assert result[1][0] == 'b@example.com'
            assert result[1][1] == 'Bob'

    def test_merge_data_with_duplicate_key(self):
        table_name = 'customer6'
        config = MockConfig()
        db_engine = DatabaseEngine(config, PrintReporter())
        meta = MetaData()
        customer = Table(table_name, meta, Column("email", String), Column("customer_name", String))

        meta.create_all(db_engine.engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com', 'b@example.com']})

        db_engine.write_df(data, table_name)

        update = pd.Series(data={'email': 'b@example.com', 'customer_name': 'Bob'}, index=['email', 'customer_name'])

        with pytest.raises(ValueError):
            db_engine.merge_row(update, table_name, 'email', on_missing='ignore')


    def test_merge_data_with_sqlite(self):
        table_name = 'customer8'
        config = MockConfig()
        db_engine = DatabaseEngine(config, PrintReporter())
        meta = MetaData()
        customer = Table(table_name, meta, Column("email", String), Column("customer_name", String), UniqueConstraint('email', name='email_unique_constraint'))

        meta.create_all(db_engine.engine)

        data = pd.DataFrame({'email': ['a@example.com', 'b@example.com']})

        db_engine.write_df(data, table_name)

        update = pd.Series(data={'email': 'b@example.com', 'customer_name': 'Bob'}, index=['email', 'customer_name'])
        update2 = pd.Series(data={'email': 'c@example.com', 'customer_name': 'Chris'}, index=['email', 'customer_name'])

        db_engine.merge_row(update, table_name, 'email', on_missing='ignore', use_native='sqlite')
        db_engine.merge_row(update2, table_name, 'email', on_missing='ignore', use_native='sqlite')

        select = customer.select()

        with db_engine.engine.connect() as conn:
            result = conn.execute(select).fetchall()

            assert len(result) == 3
            assert result[1][0] == 'b@example.com'
            assert result[1][1] == 'Bob'


