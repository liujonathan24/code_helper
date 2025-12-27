import pytest
from src.hpc_assistant.orchestration.workflows import ReportSuggestExecute
from src.hpc_assistant.storage.persistence import JobStorage
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_model():
    model = MagicMock()
    model.generate.return_value = '{"recommendations": ["recommendation 1"]}'
    return model

@pytest.fixture
def mock_tools():
    tools = {
        "academic_search": MagicMock(return_value="Search results"),
        "send_email": MagicMock(),
    }
    return tools

@pytest.mark.asyncio
async def test_report_suggest_execute_workflow(tmp_path, mock_model, mock_tools):
    job_id = "test_job"
    storage = JobStorage(base_path=str(tmp_path))
    storage.save(job_id, "job.json", {"status": "pending"})

    with patch('src.hpc_assistant.orchestration.phases.get_model', return_value=mock_model), \
         patch('src.hpc_assistant.orchestration.phases.AVAILABLE_TOOLS', mock_tools):
        
        workflow = ReportSuggestExecute(job_id)
        # We need to patch the storage instance used by the workflow
        workflow.storage = storage

        await workflow.run(params={"query": "test query"})

    # Check that the status was updated
    job_data = storage.load(job_id, "job.json")
    assert job_data["status"] == "completed"

    # Check that the model and tools were called
    mock_model.generate.assert_called()
    mock_tools["academic_search"].assert_called_with("test query")
    mock_tools["send_email"].assert_called()

    # Check that a report was saved
    report = storage.load_report(job_id)
    assert "Execution summary" in report
