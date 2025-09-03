from datetime import datetime


def has_either_ids_or_names(id: int = None, name: str = None) -> bool:
    return id is not None or name is not None


def str_to_bool(s) -> bool:
    if isinstance(s, str):
        if s.lower() == "true":
            return True
        elif s.lower() == "false":
            return False
        else:
            raise ValueError(f"Failed to convert string value {s} to boolean.")
    elif isinstance(s, bool):
        return s
    else:
        raise TypeError(f"{s} is not a valid bool or string and cannot be converted.")


def get_timestamp_from_epoch_seconds(epoch_seconds: int) -> str:
    return datetime.fromtimestamp(epoch_seconds).strftime("%Y-%m-%d %H:%M:%S")
