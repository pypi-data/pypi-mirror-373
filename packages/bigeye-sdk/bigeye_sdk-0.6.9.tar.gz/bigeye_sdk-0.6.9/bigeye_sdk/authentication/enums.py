from __future__ import annotations

import sys

from bigeye_sdk.class_ext.enum_ext import StrEnum
from bigeye_sdk.exceptions import BrowserAuthException


class OperatingSystem(StrEnum):
    LINUX = 'linux'
    MACOS = 'darwin'

    @classmethod
    def factory(cls) -> OperatingSystem:

        if sys.platform == 'darwin':
            return cls.MACOS
        elif sys.platform.startswith('linux'):
            return cls.LINUX
        else:
            raise BrowserAuthException("Invalid OS. Currently, only works on OSX or Linux.")


class BrowserType(StrEnum):
    CHROME = 'Chrome'
    CHROMIUM = 'Chromium'
    FIREFOX = 'Firefox'


class AuthConfType(StrEnum):
    BASIC_AUTH = 'BASIC_AUTH'
    BROWSER_AUTH = 'BROWSER_AUTH'
    API_KEY_AUTH = 'API_KEY_AUTH'
