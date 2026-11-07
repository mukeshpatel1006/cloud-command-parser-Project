import app as svc
import pytest
from fastapi.testclient import TestClient
from validation import validate_output

GOOD = '{"intent": "alarm_set", "date": "tomorrow", "time": "seven am", "place": null}'


def test_validate_output():
    assert validate_output(GOOD)["intent"] == "alarm_set"
    assert validate_output("not json") is None
    assert validate_output('{"intent": "alarm_set"}') is None
    assert validate_output(GOOD.replace("alarm_set", "nope")) is None
    assert validate_output(GOOD[:-5]) is None            # truncated JSON


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(svc, "load_model", lambda: None)
    monkeypatch.setattr(svc, "generate", lambda text: GOOD)
    svc.state["model"] = None
    return TestClient(svc.app)


def test_readyz_503_until_loaded_then_200(client):
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 503
    svc.state["model"] = object()
    assert client.get("/readyz").status_code == 200


def test_parse_ok_has_headers(client, monkeypatch):
    svc.state["model"] = object()
    monkeypatch.setattr(svc, "MODEL_VERSION", "v9")
    r = client.post("/parse", json={"text": "set alarm"})
    assert r.status_code == 200 and r.json()["time"] == "seven am"
    assert r.headers["X-Model-Version"] == "v9" and "X-Served-By" in r.headers


def test_fault_inject_returns_500_exact_body(client, monkeypatch):
    svc.state["model"] = object()
    monkeypatch.setenv("FAULT_INJECT", "1")
    r = client.post("/parse", json={"text": "x"})
    assert r.status_code == 500 and r.json() == {"error": "invalid_model_output"}
