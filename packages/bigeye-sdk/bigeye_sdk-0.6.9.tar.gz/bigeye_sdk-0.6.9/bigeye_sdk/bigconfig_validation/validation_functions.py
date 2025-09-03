from typing import Any, List, Dict

import yaml

from bigeye_sdk.bigconfig_validation.yaml_validation_error_messages import FORMATTING_ERRMSG


def safe_dump_dict(value: dict):
    return yaml.safe_dump(value, indent=True, sort_keys=False).strip().split('\n')


def safe_split_dict_entry_lines(key: str, value: Any):
    return yaml.safe_dump({key: value}, indent=True, sort_keys=False).strip().split('\n')


def must_be_list_validator(clazz: Any, attribute_name: str, values: dict):
    """
    Will throw error if not a list.
    Args:
        clazz: the calling class to which the validation error will be attributed.
        attribute_name: the attribute name that is being validated
        values: the root validation values.

    """

    def register_invalid_type_validation_error(key: str, value: Any):
        # error_context_lines = yaml.safe_dump(values, indent=True).split('\n'),
        errlns = safe_split_dict_entry_lines(key, value)
        clazz.register_validation_error(
            error_lines=errlns,
            error_message=FORMATTING_ERRMSG.format(
                s=f'`{key}` attribute expects a list but type {values.get(key).__class__.__name__} was received')
        )

    if not values or not isinstance(values, Dict):
        return

    attribute_value = values.get(attribute_name)
    if attribute_value and not isinstance(attribute_value, List):
        register_invalid_type_validation_error(key=attribute_name, value=attribute_value)
        values[attribute_name] = [attribute_value]  # set it as a list to continue and not get thrown out.
