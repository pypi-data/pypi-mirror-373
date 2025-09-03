from typing import Union

from pydomjudge.clients.client import _Client
from pydomjudge.models.response import AccessInformation


class AccessClient(_Client):
    def get_access_information(self, contest_id: Union[str, int], strict: bool = False) -> AccessInformation:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/access"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return AccessInformation.model_validate(response.json())