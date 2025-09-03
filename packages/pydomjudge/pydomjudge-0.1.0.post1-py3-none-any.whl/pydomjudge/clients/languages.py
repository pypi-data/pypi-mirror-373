from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Language


class LanguagesClient(_Client):
    def get_all_languages(self, contest_id: Union[str, int], idlist: List[str] = None, strict: bool = False) -> \
    List[Language]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/languages"
        params = {
            "ids[]": idlist,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Language.model_validate(language) for language in response.json()]

    def get_language(self, contest_id: Union[str, int], language_id: str, strict: bool = False) -> Language:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/languages/{language_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Language.model_validate(response.json())