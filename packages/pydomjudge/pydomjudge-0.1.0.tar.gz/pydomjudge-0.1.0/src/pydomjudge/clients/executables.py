from typing import Dict

from pydomjudge.clients.client import _Client


class ExecutablesClient(_Client):
    def get_executable(self, executable_id: str, strict: bool = False) -> Dict:
        url = f"{self.base_url}/api/v4/executables/{executable_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return self.model_validate(response.json())