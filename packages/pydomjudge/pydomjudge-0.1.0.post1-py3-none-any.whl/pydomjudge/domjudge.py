from pydomjudge.clients.access import AccessClient
from pydomjudge.clients.accounts import AccountsClient
from pydomjudge.clients.awards import AwardsClient
from pydomjudge.clients.balloons import BalloonsClient
from pydomjudge.clients.clarifications import ClarificationsClient
from pydomjudge.clients.contests import ContestsClient
from pydomjudge.clients.executables import ExecutablesClient
from pydomjudge.clients.general import GeneralClient
from pydomjudge.clients.groups import GroupsClient
from pydomjudge.clients.judgehosts import JudgehostsClient
from pydomjudge.clients.judgements import JudgementsClient
from pydomjudge.clients.judgetypes import JudgeTypesClient
from pydomjudge.clients.languages import LanguagesClient
from pydomjudge.clients.metrics import MetricsClient
from pydomjudge.clients.organizations import OrganizationsClient
from pydomjudge.clients.problems import ProblemsClient
from pydomjudge.clients.runs import RunsClient
from pydomjudge.clients.scoreboards import ScoreboardsClient
from pydomjudge.clients.submissions import SubmissionsClient
from pydomjudge.clients.teams import TeamsClient
from pydomjudge.clients.users import UsersClient


class DOMJudge(AccessClient, AccountsClient, AwardsClient, BalloonsClient, ClarificationsClient, ContestsClient,
               ExecutablesClient, GeneralClient, GroupsClient, JudgehostsClient, JudgementsClient, JudgeTypesClient,
               LanguagesClient, MetricsClient, OrganizationsClient, ProblemsClient, RunsClient, ScoreboardsClient,
               SubmissionsClient, TeamsClient, UsersClient):
    pass