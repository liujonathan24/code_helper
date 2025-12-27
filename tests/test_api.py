from fastapi.testclient import TestClient
from src.hpc_assistant.main import app
import pytest

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "HPC Assistant Server is running."}

def test_submit_task():
    # We are not testing the background task itself, just the submission
    response = client.post(
        "/submit",
        json={"workflow": "report_suggest_execute", "params": {"query": "test"}},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert "job_id" in json_response
    assert json_response["status"] == "pending"

def test_submit_invalid_workflow():
    response = client.post(
        "/submit",
        json={"workflow": "invalid_workflow", "params": {"query": "test"}},
    )
    assert response.status_code == 404

def test_get_status_not_found():
    response = client.get("/status/invalid_job_id")
    assert response.status_code == 404

# A more advanced test would involve mocking the storage and background tasks
# to check the status and results of a job.
# For now, this provides a basic check of the API endpoints.
