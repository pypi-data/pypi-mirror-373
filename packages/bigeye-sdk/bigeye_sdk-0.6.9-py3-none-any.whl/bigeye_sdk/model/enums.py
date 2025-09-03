import enum


class MatchType(str, enum.Enum):
    STRICT = "strict"
    FUZZY = "fuzzy"


# Adding here because the protobuf enum only exists for documentation and could easily be changed.
class LineageDirection(str, enum.Enum):
    ALL = "ALL"
    UPSTREAM = "UPSTREAM"
    DOWNSTREAM = "DOWNSTREAM"
