import pytest
import os
from dotenv import load_dotenv
from pydomjudge.domjudge import DOMJudge

# Cargar variables de entorno para el servidor de prueba
load_dotenv()


@pytest.fixture
def live_api():
    return DOMJudge(
        base_url=os.getenv("TEST_API_URL", "http://localhost/domjudge"),
        username=os.getenv("TEST_API_USER", "admin"),
        password=os.getenv("TEST_API_PASS", "adminpass")
    )
