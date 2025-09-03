from typing import List, Union

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import TeamAffiliation


class OrganizationsClient(_Client):
    def get_all_organizations(self, contest_id: Union[str, int], idlist: List[str] = None, country: str = None,
                              strict: bool = False) -> List[TeamAffiliation]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations"
        params = {
            "ids[]": idlist,
            "country": country,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [TeamAffiliation.model_validate(org) for org in response.json()]

    def add_organization(self, contest_id: Union[str, int], organization_data: dict,
                         strict: bool = False) -> TeamAffiliation:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=organization_data)
        response.raise_for_status()
        return TeamAffiliation.model_validate(response.json())

    def get_organization(self, contest_id: Union[str, int], organization_id: str,
                         strict: bool = False) -> TeamAffiliation:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations/{organization_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return TeamAffiliation.model_validate(response.json())

    def get_organization_logo(self, contest_id: Union[str, int], organization_id: str,
                              strict: bool = False) -> bytes:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations/{organization_id}/logo"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def set_organization_logo(self, contest_id: Union[str, int], organization_id: str, logo: bytes,
                              strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations/{organization_id}/logo"
        params = {
            "strict": strict
        }
        files = {
            "logo": logo
        }
        response = self.session.put(url, params=params, files=files)
        response.raise_for_status()

    def delete_organization_logo(self, contest_id: Union[str, int], organization_id: str,
                                 strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/organizations/{organization_id}/logo"
        params = {
            "strict": strict
        }
        response = self.session.delete(url, params=params)
        response.raise_for_status()