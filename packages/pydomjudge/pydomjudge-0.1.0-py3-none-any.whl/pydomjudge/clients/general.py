from typing import Dict, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import User


class GeneralClient(_Client):
    def get_api_version(self, strict: bool = False) -> Dict:
        url = f"{self.base_url}/api/v4/version"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_api_info(self, strict: bool = False) -> Dict:
        url = f"{self.base_url}/api/v4/info"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_api_root(self, strict: bool = False) -> Dict:
        url = f"{self.base_url}/api/v4/"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_general_status(self, strict: bool = False) -> List[Dict]:
        url = f"{self.base_url}/api/v4/status"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_user_info(self, strict: bool = False) -> User:
        url = f"{self.base_url}/api/v4/user"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return User.model_validate(response.json())

    def get_config(self, name: str = None, strict: bool = False) -> Dict:
        url = f"{self.base_url}/api/v4/config"
        params = {
            "name": name,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def update_config(self, config_data: Dict, strict: bool = False) -> Dict:
        url = f"{self.base_url}/api/v4/config"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=config_data)
        response.raise_for_status()
        return response.json()

    def check_config(self, strict: bool = False) -> Dict:
        url = f"{self.base_url}/api/v4/config/check"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_country_flag(self, country_code: str, size: str, strict: bool = False) -> bytes:
        url = f"{self.base_url}/api/v4/country-flags/{country_code}/{size}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content