from __future__ import annotations

import enum


class Method(str, enum.Enum):
    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    DELETE = 'DELETE'
    PATCH = 'PATCH'

    def __str__(self):
        return self.name
