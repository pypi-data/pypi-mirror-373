import pytest
import responses
from pydomjudge.domjudge import DOMJudge
from pydomjudge.models.main import Contest


@pytest.fixture
def api_client():
    return DOMJudge("http://mock-server", "user", "pass")


@responses.activate
def test_get_contests_success(api_client):
    # Mock response
    mock_data = [{
        "id": "1",
        "name": "Test Contest",
        "shortname": "test",
        "start_time": "2023-01-01T00:00:00Z",
        "end_time": "2023-01-02T00:00:00Z"
    }]

    responses.add(
        responses.GET,
        "http://mock-server/api/v4/contests",
        json=mock_data,
        status=200
    )

    # Test
    result = api_client.get_contests()

    # Assertions
    assert len(result) == 1
    assert isinstance(result[0], Contest)
    assert result[0].name == "Test Contest"


@responses.activate
def test_get_contests_error(api_client):
    responses.add(
        responses.GET,
        "http://mock-server/api/v4/contests",
        json={"error": "Unauthorized"},
        status=401
    )

    with pytest.raises(Exception) as exc_info:
        api_client.get_all_contests()

    assert "401 Client Error" in str(exc_info.value)
