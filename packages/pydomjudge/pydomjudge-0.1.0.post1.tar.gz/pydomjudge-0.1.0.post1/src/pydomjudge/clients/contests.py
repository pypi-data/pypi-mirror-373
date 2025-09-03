from typing import List, Union

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Contest, Event, ContestState, ContestStatus


class ContestsClient(_Client):
    def get_all_contests(self, idlist: List[str] = None, only_active: bool = False, strict: bool = False) -> List[Contest]:
        url = f"{self.base_url}/api/v4/contests"
        params = {
            "ids[]": idlist,
            "onlyActive": only_active,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Contest.model_validate(contest) for contest in response.json()]

    def get_contest(self, contest_id: Union[str, int], strict: bool = False) -> Contest:
        url = f"{self.base_url}/api/v4/contests/{contest_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Contest.model_validate(response.json())

    def add_contest(self, contest_data: dict, strict: bool = False) -> str:
        url = f"{self.base_url}/api/v4/contests"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, files=contest_data)
        response.raise_for_status()
        return response.json()

    def change_contest_start_time(self, contest_id: Union[str, int], start_time: str, force: bool = False, strict: bool = False) -> str:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/starttime"
        params = {
            "strict": strict
        }
        data = {
            "start_time": start_time,
            "force": force
        }
        response = self.session.patch(url, params=params, data=data)
        response.raise_for_status()
        return response.json()

    def get_contest_banner(self, contest_id: Union[str, int], strict: bool = False) -> bytes:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/banner"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def set_contest_banner(self, contest_id: Union[str, int], banner: bytes, strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/banner"
        params = {
            "strict": strict
        }
        files = {
            "banner": banner
        }
        response = self.session.put(url, params=params, files=files)
        response.raise_for_status()

    def delete_contest_banner(self, contest_id: Union[str, int], strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/banner"
        params = {
            "strict": strict
        }
        response = self.session.delete(url, params=params)
        response.raise_for_status()

    def get_contest_yaml(self, contest_id: Union[str, int], strict: bool = False) -> str:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/contest-yaml"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.text

    def get_contest_state(self, contest_id: Union[str, int], strict: bool = False) -> ContestState:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/state"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return ContestState.model_validate(response.json())

    def get_event_feed(self, contest_id: Union[str, int], since_id: str = None, types: List[str] = None,
                       stream: bool = True, strict: bool = False) -> List[Event]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/event-feed"
        params = {
            "since_id": since_id,
            "types": types,
            "stream": stream,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Event.model_validate(event) for event in response.json()]

    def get_contest_status(self, contest_id: Union[str, int], strict: bool = False) -> ContestStatus:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/status"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return ContestStatus.model_validate(response.json())

    def get_samples_zip(self, contest_id: Union[str, int], strict: bool = False) -> bytes:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/samples.zip"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content