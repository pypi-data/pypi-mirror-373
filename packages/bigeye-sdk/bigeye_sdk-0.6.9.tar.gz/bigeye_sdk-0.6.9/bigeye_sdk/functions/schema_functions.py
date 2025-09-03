from typing import List, Tuple, Dict, Union

from bigeye_sdk.generated.com.bigeye.models.generated import Schema


def get_database_from_bigeye_schema_name(bigeye_schema_name: str) -> Union[None, str]:
    """
    Bigeye concats database.schema as the schema name.  Sometimes a database exists and sometimes not.
    :param bigeye_schema_name: the bigeye_schema_name
    :return: the database name if included or else None
    """
    bigeye_schema_split = bigeye_schema_name.split('.')
    bigeye_schema_split.reverse()
    return bigeye_schema_split[1] if 1 < len(bigeye_schema_split) else None


def get_schema_from_bigeye_schema_name(bigeye_schema_name: str) -> str:
    """
    Bigeye concats database.schema as the schema name.  Sometimes a database exists and sometimes not.
    :param bigeye_schema_name: the bigeye_schema_name
    :return: the schema name with no database name included.
    """
    bigeye_schema_split = bigeye_schema_name.split('.')
    bigeye_schema_split.reverse()
    return bigeye_schema_split[0]


def create_schema_id_pairs(source_schema_dict: Dict[str, Schema], target_schema_dict: Dict[str, Schema],
                           schema_name_pairs: List[Tuple[str, str]]) -> List[Tuple[int, int]]:
    """
    Matches id pairs based on schema name pairs.
    :param source_schema_dict: Dict[schema_name:str, Schema]
    :param target_schema_dict: Dict[schema_name:str, Schema]
    :param schema_name_pairs: paired names of schemas (source_schema_name, target_schema_name)
    :return: List[source_schema_id, target_schema_id]
    """

    return [(source_schema_dict[pair[0]].id, target_schema_dict[pair[1]].id) for pair in schema_name_pairs]
