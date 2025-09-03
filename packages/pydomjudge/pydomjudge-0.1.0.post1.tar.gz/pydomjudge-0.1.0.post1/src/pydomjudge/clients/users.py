from typing import List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import User


class UsersClient(_Client):
    def get_all_users(self, idlist: List[str] = None, team_id: str = None) -> List[User]:
        url = f"{self.base_url}/api/v4/users"
        params = {
            "ids[]": idlist,
            "team_id": team_id
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [User.model_validate(user) for user in response.json()]

    def get_user(self, user_id: str) -> User:
        url = f"{self.base_url}/api/v4/users/{user_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return User.model_validate(response.json())

    def add_user(self, user_data: dict) -> User:
        url = f"{self.base_url}/api/v4/users"
        response = self.session.post(url, json=user_data)
        response.raise_for_status()
        return User.model_validate(response.json())

    def update_user(self, user_id: str, user_data: dict) -> User:
        url = f"{self.base_url}/api/v4/users/{user_id}"
        response = self.session.put(url, json=user_data)
        response.raise_for_status()
        return User.model_validate(response.json())

    def delete_user(self, user_id: str) -> None:
        url = f"{self.base_url}/api/v4/users/{user_id}"
        response = self.session.delete(url)
        response.raise_for_status()

    def add_groups(self, groups_data: dict) -> dict:
        url = f"{self.base_url}/api/v4/users/groups"
        response = self.session.post(url, files=groups_data)
        response.raise_for_status()
        return response.json()

    def add_organizations(self, organizations_data: dict) -> dict:
        url = f"{self.base_url}/api/v4/users/organizations"
        response = self.session.post(url, files=organizations_data)
        response.raise_for_status()
        return response.json()

    def add_teams(self, teams_data: dict) -> dict:
        url = f"{self.base_url}/api/v4/users/teams"
        response = self.session.post(url, files=teams_data)
        response.raise_for_status()
        return response.json()

    def add_accounts(self, accounts_data: dict) -> dict:
        url = f"{self.base_url}/api/v4/users/accounts"
        response = self.session.post(url, files=accounts_data)
        response.raise_for_status()
        return response.json()