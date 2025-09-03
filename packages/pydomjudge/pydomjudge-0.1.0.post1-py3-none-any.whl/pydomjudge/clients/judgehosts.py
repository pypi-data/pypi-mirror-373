from typing import List, Dict

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Judgehost, Judging


class JudgehostsClient(_Client):
    def get_judgehosts(self, hostname: str = None, strict: bool = False) -> List[Judgehost]:
        url = f"{self.base_url}/api/v4/judgehosts"
        params = {
            "hostname": hostname,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Judgehost.model_validate(judgehost) for judgehost in response.json()]

    def add_judgehost(self, strict: bool = False) -> List[Judging]:
        url = f"{self.base_url}/api/v4/judgehosts"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params)
        response.raise_for_status()
        return response.json()

    def update_judgehost(self, hostname: str, judgehost_data: dict, strict: bool = False) -> List[Judgehost]:
        url = f"{self.base_url}/api/v4/judgehosts/{hostname}"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=judgehost_data)
        response.raise_for_status()
        return [Judgehost.model_validate(judgehost) for judgehost in response.json()]

    def update_judging(self, hostname: str, judgetask_id: int, judging_data: dict, strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/judgehosts/update-judging/{hostname}/{judgetask_id}"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=judging_data)
        response.raise_for_status()

    def add_debug_info(self, hostname: str, judgetask_id: int, debug_info: dict, strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/judgehosts/add-debug-info/{hostname}/{judgetask_id}"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=debug_info)
        response.raise_for_status()

    def add_judging_run(self, hostname: str, judgetask_id: int, judging_run_data: dict,
                        strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/judgehosts/add-judging-run/{hostname}/{judgetask_id}"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=judging_run_data)
        response.raise_for_status()

    def report_internal_error(self, error_data: dict, strict: bool = False) -> int:
        url = f"{self.base_url}/api/v4/judgehosts/internal-error"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=error_data)
        response.raise_for_status()
        return response.json()

    def get_files(self, file_type: str, file_id: str, strict: bool = False) -> bytes:
        url = f"{self.base_url}/api/v4/judgehosts/get_files/{file_type}/{file_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def fetch_work_tasks(self, strict: bool = False) -> List[Dict]:
        url = f"{self.base_url}/api/v4/judgehosts/fetch-work"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params)
        response.raise_for_status()
        return response.json()