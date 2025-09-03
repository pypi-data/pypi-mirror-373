import re

def remove_and_split(value: str, split_char: str|list[str], remove_pattern: str|None=None) -> list[str|int|float]:
    """
    Splits a string based on a specified character or list of characters after
    removing a specific pattern. Handles various input types gracefully by
    returning appropriate output. Returns a list of split components, including
    the input value itself if it is already a numeric type (int or float).

    :param value:
        The input value to be processed and split. Can be a string, integer, or
        float.
    :param split_char:
        A single character or list of characters to use for splitting the string.
    :param remove_pattern:
        An optional regular expression pattern to remove certain parts of the
        string before splitting. Defaults to None, meaning no removal will occur.
    :return:
        A list containing the split components of the input string, or the input
        value itself if it is of type int or float. Returns an empty list if the
        input value is not a string, int, or float.
    """
    if remove_pattern is not None and type(value) is str:
        value = re.sub(remove_pattern, "", value)

    if type(value) is int or type(value) is float:
        return [value]

    if type(value) is not str:
        return []

    if isinstance(split_char, str):
        splits = value.split(split_char)
    else:
        split_values = "|".join(split_char)
        splits = re.split(split_values, value)

    return [x.strip() for x in splits if len(x.strip()) > 0]