class BaseApiClient:
    _base_url: str

    def __init__(self, base_url: str):
        self._base_url = self._cleanse_base_url(base_url)

    @classmethod
    def _cleanse_base_url(cls, base_url: str) -> str:
        if base_url[-1] == '/':
            return base_url[:-1]

        return base_url

    def get_base_url(self) -> str:
        return self._cleanse_base_url(self._base_url)