from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uuid
from ..storage.persistence import JobStorage
from ..orchestration.workflows import WORKFLOWS

router = APIRouter()

# Use JobStorage for persistence
storage = JobStorage()

class TaskRequest(BaseModel):
    workflow: str
    params: dict

class Job(BaseModel):
    job_id: str
    status: str

def run_workflow_background(job_id: str, workflow_name: str, params: dict):
    workflow_class = WORKFLOWS.get(workflow_name)
    if not workflow_class:
        # This should ideally be checked before starting the background task
        print(f"Workflow {workflow_name} not found.")
        return

    workflow = workflow_class(job_id)
    # Since this is running in the background, we need to handle exceptions
    # to prevent the server process from crashing.
    try:
        # The 'run' method in the workflow should be async
        import asyncio
        asyncio.run(workflow.run(params))
    except Exception as e:
        print(f"Error running workflow {workflow_name} for job {job_id}: {e}")
        # Optionally update job status to 'failed'
        workflow.update_status("failed")


@router.post("/submit", response_model=Job)
async def submit_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Submits a task to a workflow to be run in the background.
    """
    job_id = str(uuid.uuid4())
    
    if request.workflow not in WORKFLOWS:
        raise HTTPException(status_code=404, detail=f"Workflow '{request.workflow}' not found.")

    job_data = {"status": "pending", "workflow": request.workflow, "params": request.params}
    storage.save(job_id, "job.json", job_data)
    
    background_tasks.add_task(run_workflow_background, job_id, request.workflow, request.params)
    
    return {"job_id": job_id, "status": "pending"}

@router.get("/status/{job_id}", response_model=Job)
async def get_job_status(job_id: str):
    """
    Queries the status of a job.
    """
    try:
        job_data = storage.load(job_id, "job.json")
        return {"job_id": job_id, "status": job_data["status"]}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Job not found")

class JobResult(BaseModel):
    job_id: str
    status: str
    result: dict # Or a more specific model

@router.get("/results/{job_id}", response_model=JobResult)
async def get_job_result(job_id: str):
    """
    Fetches the results of a completed job.
    """
    try:
        job_data = storage.load(job_id, "job.json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Placeholder for result loading
    if job_data["status"] != "completed":
        return {"job_id": job_id, "status": job_data["status"], "result": {}}

    try:
        report = storage.load_report(job_id)
        return {"job_id": job_id, "status": "completed", "result": {"report": report}}
    except FileNotFoundError:
        return {"job_id": job_id, "status": "completed", "result": {"report": "Report not found."}}


