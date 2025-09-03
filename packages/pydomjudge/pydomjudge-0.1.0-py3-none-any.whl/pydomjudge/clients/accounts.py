from typing import List, Union

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import User


class AccountsClient(_Client):
    def get_all_accounts(self, contest_id: Union[str, int], idlist: List[str] = None, team_id: str = None,
                         strict: bool = False) -> List[User]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/accounts"
        params = {
            "ids[]": idlist,
            "team_id": team_id,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [User.model_validate(account) for account in response.json()]

    def get_account(self, contest_id: Union[str, int], account_id: str, strict: bool = False) -> User:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/accounts/{account_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return User.model_validate(response.json())

    def get_current_account(self, contest_id: Union[str, int], strict: bool = False) -> User:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/account"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return User.model_validate(response.json())