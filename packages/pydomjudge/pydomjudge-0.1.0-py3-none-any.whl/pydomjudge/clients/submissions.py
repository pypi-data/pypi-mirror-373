from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Submission
from pydomjudge.models.shared import ArchiveFile, SourceCode


class SubmissionsClient(_Client):

    def get_submissions(self, contest_id: Union[str, int], idlist: List[Union[str, int]] = None, language_id: str = None,
                        strict: bool = False) -> List[Submission]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions"
        params = {
            "ids[]": idlist,
            "language_id": language_id,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Submission.model_validate(submission) for submission in response.json()]

    def get_submission(self, contest_id: Union[str, int], submission_id: Union[str, int], strict: bool = False) -> Submission:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions/{submission_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Submission.model_validate(response.json())

    def get_submission_files(self, contest_id: Union[str, int], submission_id: Union[str, int], strict: bool = False) -> List[ArchiveFile]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions/{submission_id}/files"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def get_submission_source_code(self, contest_id: Union[str, int], submission_id: Union[str, int], strict: bool = False) -> List[SourceCode]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions/{submission_id}/source-code"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [SourceCode.model_validate(source_code) for source_code in response.json()]

    def add_submission(self, contest_id: Union[str, int], submission_data: dict, strict: bool = False) -> str:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, files=submission_data)
        response.raise_for_status()
        return response.json()

    def update_submission(self, contest_id: Union[str, int], submission_id: str, submission_data: dict, strict: bool = False) -> str:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/submissions/{submission_id}"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=submission_data)
        response.raise_for_status()
        return response.json()