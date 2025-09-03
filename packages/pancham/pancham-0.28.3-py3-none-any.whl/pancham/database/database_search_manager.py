import hashlib
import json
from typing import Literal

from pancham.reporter import get_reporter
from .caching_database_search import DatabaseSearch, FilteredCachingDatabaseSearch, CachingDatabaseSearch, \
    SQLFileCachingDatabaseSearch
from .populating_database_search import PopulatingDatabaseSearch
from .py_database_cache_search import PyDatabaseCacheSearch

__managed_db_cache: dict[str, DatabaseSearch] = {}

def get_database_search(
        table_name: str,
        search_col: str,
        value_col: str,
        filter: dict[str, str]|None = None,
        cast_search: None | str = None,
        cast_value: None | str = None,
        populate: bool = False,
        sql_file: str|None = None,
        cache_method: Literal['dict', 'pycache'] = 'dict'
) -> DatabaseSearch:
    """
    Creates or retrieves a `DatabaseSearch` object configured for a specific database query and caching
    strategy. This method determines the appropriate `DatabaseSearch` subclass based on the provided
    parameters such as the type of cache, whether to populate the search, SQL file, or filters applied.
    The function uses a managed cache to avoid re-instantiating equivalent database search objects.

    Arguments:
        table_name: The name of the database table to query.
        search_col: The column to be used for the search parameter.
        value_col: The column from where the values corresponding to the search parameters will be fetched.
        filter: Optional parameter specifying conditions in the form of a dictionary where keys are column
            names and values are filter values.
        cast_search: Optional parameter specifying the data type to cast the search value.
        cast_value: Optional parameter specifying the data type to cast the retrieved values.
        populate: A boolean indicating whether to use a populating search strategy.
        sql_file: The path to an optional SQL file that defines the structured query to be executed instead
            of generating it automatically.
        cache_method: Specifies the caching mechanism to use, either "dict" or "pycache". Defaults to "dict".

    Returns:
        An instance of a `DatabaseSearch`-like object, configured as per the provided parameters.

    Raises:
        ValueError: If an invalid argument is provided for `cache_method` or other parameters that lead
            to an undefined behavior for database caching/search configuration.

    """

    global __managed_db_cache

    reporter = get_reporter()
    reporter.report_debug(f'Database search cache {__managed_db_cache}')
    reporter.report_debug(f'Database search using populate - {populate}, filter - {filter}, Sql file - {sql_file}')

    filter_key = ''
    if filter is not None:
        filter_key = json.dumps(filter, sort_keys=True)

    db_key_str = f"{table_name}_{search_col}_{value_col}_{cast_search}_{cast_value}_{populate}_{filter_key}_{sql_file}"
    db_key = hashlib.md5(db_key_str.encode()).hexdigest()

    if db_key not in __managed_db_cache:
        if populate:
            __managed_db_cache[db_key] = PopulatingDatabaseSearch(table_name, search_col, value_col, cast_search, cast_value)
        elif filter is not None:
            __managed_db_cache[db_key] = FilteredCachingDatabaseSearch(table_name, search_col, value_col, filter, cast_search, cast_value)
        elif sql_file is not None:
            __managed_db_cache[db_key] = SQLFileCachingDatabaseSearch(sql_file, cast_search, cast_value)
        elif cache_method == 'pycache':
            __managed_db_cache[db_key] = PyDatabaseCacheSearch(table_name, search_col, value_col, cast_search)
        else:
            __managed_db_cache[db_key] = CachingDatabaseSearch(table_name, search_col, value_col, cast_search, cast_value)

    return __managed_db_cache[db_key]
