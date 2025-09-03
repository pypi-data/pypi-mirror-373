from typing import List, Dict, Union
from pydantic import BaseModel

from pydomjudge.models.main import ContestState


class AccessInformation(BaseModel):
    capabilities: List[str]
    endpoints: List[Dict]  # Simplified for brevity

class ScoreboardRowProblem(BaseModel):
    label: str
    solved: bool
    time: int

class ScoreboardRow(BaseModel):
    rank: int
    team_id: str
    score: Dict[str, Union[int, float]]  # {"num_solved": 3, "total_time": 300}
    problems: List[ScoreboardRowProblem]

class Scoreboard(BaseModel):
    event_id: str
    state: ContestState
    rows: List[ScoreboardRow]
