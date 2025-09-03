from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

from pydomjudge.models.shared import StatementFile, ImageFile, ArchiveFile


class User(BaseModel):
    id: str
    username: str
    name: str
    email: Optional[str] = None
    team_id: Optional[str] = None
    roles: List[str]
    enabled: bool
    last_login_time: Optional[datetime] = None

class ContestState(BaseModel):
    started: Optional[datetime] = None
    ended: Optional[datetime] = None
    frozen: Optional[datetime] = None
    thawed: Optional[datetime] = None
    finalized: Optional[datetime] = None
    end_of_updates: Optional[datetime] = None

class ContestProblem(BaseModel):
    id: str
    label: str
    name: str
    time_limit: float
    statement: List[StatementFile] = Field(default_factory=list)

class Balloon(BaseModel):
    balloonid: int
    time: str
    problem: str
    contestproblem: ContestProblem
    team: str
    teamid: int
    location: Optional[str]
    affiliation: Optional[str]
    affiliationid: Optional[int]
    category: str
    total: List[ContestProblem]
    awards: str
    done: bool

class Award(BaseModel):
    id: str
    citation: str
    team_ids: List[str]

class Contest(BaseModel):
    id: str
    name: str
    shortname: str
    start_time: datetime
    end_time: datetime
    banner: List[ImageFile] = Field(default_factory=list)  # From "Banner" schema

class ContestStatus(BaseModel):
    num_submissions: int
    num_queued: int
    num_judging: int

class Event(BaseModel):
    id: str
    type: str
    op: str
    data: Dict
    time: str

class Team(BaseModel):
    id: str
    name: str
    display_name: Optional[str] = None
    group_ids: List[str] = Field(default_factory=list)
    photo: List[ImageFile] = Field(default_factory=list)  # From "Photo" schema

class Submission(BaseModel):
    id: str
    language_id: str
    problem_id: str
    team_id: str
    time: datetime
    files: List[ArchiveFile] = Field(default_factory=list)  # From "Files" schema

class TeamCategory(BaseModel):
    id: str
    name: str
    hidden: bool
    icpc_id: str
    sortorder: int
    color: str

class JudgementType(BaseModel):
    id: str
    name: str
    penalty: bool
    solved: bool

class Judgehost(BaseModel):
    id: str
    hostname: str
    enabled: bool
    polltime: str
    hidden: bool

class Language(BaseModel):
    id: str
    name: str
    extensions: List[str]
    compile_executable_hash: Optional[str]
    filter_compiler_files: bool
    allow_judge: bool
    time_factor: float
    entry_point_required: bool
    entry_point_name: Optional[str]

class Judging(BaseModel):
    id: str
    submission_id: str
    start_time: str
    start_contest_time: str
    end_time: str
    end_contest_time: str
    valid: bool

class Judgement(BaseModel):
    id: str
    submission_id: str
    judgement_type_id: Optional[str] = None
    valid: bool
    max_run_time: Optional[float] = None

class TeamAffiliation(BaseModel):
    id: str
    shortname: str
    icpc_id: Optional[str]
    name: str
    formal_name: str
    country: Optional[str]

class Clarification(BaseModel):
    id: str
    text: str
    problem_id: Optional[str] = None
    from_team_id: Optional[str] = None
    to_team_id: Optional[str] = None
    time: Optional[datetime] = None

class JudgingRun(BaseModel):
    id: str
    judgement_id: str
    run_time: float
    time: str
    contest_time: str
    ordinal: int
