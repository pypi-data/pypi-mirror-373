from __future__ import annotations

from typing import List, Union, Tuple

from bigeye_sdk.exceptions import InvalidConfigurationException


def build_fq_name(source_pattern: str, schema_pattern: str, table_pattern: str, column_pattern: str = None):
    fq_name = f'{source_pattern}.{schema_pattern}.{table_pattern}'
    if column_pattern:
        fq_name = f'{fq_name}.{column_pattern}'
    return fq_name


def explode_fq_name(fq_name: str, is_regex: bool = False) -> List[str]:
    """
    Explodes a fully qualifeid name into a list of names.  Supports wild cards as *. Supports single and double-quoted
    names containing periods.  Will force concatenation of database and schema names per Bigeye standard.
        Example: wh."my.database".table.column resolves to ['wh', 'my.database', 'table', 'column']
        Example wh.my_database.my_schema.table.colum resolves to ['wh', 'my_database.myschema', 'table', 'column']
    Args:
        fq_name: fully qualified asset name.
        is_regex: bool to determine how fq_name should be split.

    Returns: list of names from the fully qualified name.
    """
    import re

    remove_quotes_pattern = re.compile(r"\"|'")

    if is_regex:
        r = [remove_quotes_pattern.sub('', i) for i in fq_name.split(r"\.")]
    else:
        split_unquoted_period_pattern = re.compile(r'''((?:[^."']|"[^"]*"|'[^']*')+)''')
        r = [remove_quotes_pattern.sub('', i) for i in split_unquoted_period_pattern.split(fq_name)[1::2]]

    return r


def explode_fq_table_name(fq_table_name: str) -> List[str]:
    names = explode_fq_name(fq_table_name)

    if len(names) == 4:
        """Accommodates source types that have a source/instance, database, and schema in the fully 
        qualified name"""
        names[1:3] = ['.'.join(names[1:3])]
        return names
    elif len(names) == 3:
        """Accommodates source types that have a source/instance/database and schema in the fully qualified
        name"""
        return names
    else:
        """Other patterns not currently supported."""
        raise InvalidConfigurationException(f"Fully qualified table names must have 3 elements or 4 elements.  For"
                                            f"example: source.schema.table OR source.database.schema.table.  "
                                            f"Wild cards are accepted.  The fully qualified name given "
                                            f"is {fq_table_name}")
