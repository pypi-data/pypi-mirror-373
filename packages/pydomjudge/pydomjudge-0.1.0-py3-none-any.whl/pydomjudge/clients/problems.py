from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import ContestProblem


class ProblemsClient(_Client):
    def get_all_problems(self, contest_id: Union[str, int], idlist: List[str] = None, strict: bool = False) -> List[ContestProblem]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems"
        params = {
            "ids[]": idlist,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [ContestProblem.model_validate(problem) for problem in response.json()]

    def get_problem(self, contest_id: Union[str, int], problem_id: str, strict: bool = False) -> ContestProblem:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems/{problem_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return ContestProblem.model_validate(response.json())

    def add_problem(self, contest_id: Union[str, int], problem_data: dict, strict: bool = False) -> str:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, files=problem_data)
        response.raise_for_status()
        return response.json()

    def link_problem(self, contest_id: Union[str, int], problem_id: str, problem_data: dict, strict: bool = False) -> ContestProblem:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems/{problem_id}"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=problem_data)
        response.raise_for_status()
        return ContestProblem.model_validate(response.json())

    def unlink_problem(self, contest_id: Union[str, int], problem_id: str, strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems/{problem_id}"
        params = {
            "strict": strict
        }
        response = self.session.delete(url, params=params)
        response.raise_for_status()

    def get_problem_statement(self, contest_id: Union[str, int], problem_id: str, strict: bool = False) -> bytes:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems/{problem_id}/statement"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def add_problems(self, contest_id: Union[str, int], problems_data: dict, strict: bool = False) -> List[str]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/problems/add-data"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, files=problems_data)
        response.raise_for_status()
        return response.json()