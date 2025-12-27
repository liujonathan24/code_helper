"""
This module defines the workflows, which are compositions of phases.
"""
from ..storage.persistence import JobStorage
from .phases import ReportPhase, SuggestPhase, ExecutePhase

storage = JobStorage()

class BaseWorkflow:
    def __init__(self, job_id: str):
        self.job_id = job_id

    async def run(self, params: dict):
        raise NotImplementedError

    def update_status(self, status: str):
        job_data = storage.load(self.job_id, "job.json")
        job_data["status"] = status
        storage.save(self.job_id, "job.json", job_data)


class ReportSuggestExecute(BaseWorkflow):
    """
    A workflow that chains the Report, Suggest, and Execute phases.
    """
    async def run(self, params: dict):
        self.update_status("running_report")
        print(f"[{self.job_id}] Running Report-Suggest-Execute workflow with params: {params}")
        
        query = params.get("query", "")
        if not query:
            print(f"[{self.job_id}] Error: 'query' parameter is required.")
            self.update_status("failed")
            return

        # 1. Run Report phase
        report_phase = ReportPhase(self.job_id)
        report = await report_phase.run(query)
        storage.save_report(self.job_id, report)
        
        # 2. Run Suggest phase
        self.update_status("running_suggest")
        suggest_phase = SuggestPhase(self.job_id)
        suggestions = await suggest_phase.run(report)
        storage.save(self.job_id, "suggestions.json", suggestions)

        # 3. Run Execute phase
        self.update_status("running_execute")
        execute_phase = ExecutePhase(self.job_id)
        execution_log = await execute_phase.run(suggestions)
        storage.save(self.job_id, "execution.log", {"log": execution_log})

        print(f"[{self.job_id}] Workflow finished.")
        self.update_status("completed")
        # Overwrite the initial report with the final execution log as the main result
        storage.save_report(self.job_id, execution_log)


WORKFLOWS = {
    "report_suggest_execute": ReportSuggestExecute,
}


