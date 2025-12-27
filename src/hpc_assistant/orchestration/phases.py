"""
This module defines the orchestration phases.
"""
from ..models.inference import get_model
from ..tools.available_tools import AVAILABLE_TOOLS

class BasePhase:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.model = get_model()

    async def run(self, *args, **kwargs):
        raise NotImplementedError

class ReportPhase(BasePhase):
    """
    Generates a detailed written report.
    Tools: Search tools are allowed.
    Output: Long-form text (Markdown or plain text).
    """
    async def run(self, query: str) -> str:
        print(f"[{self.job_id}] Running Report Phase with query: {query}")
        
        prompt = f"Please write a detailed report about: {query}. You can use the academic_search tool."
        
        # In a real implementation, this would be a loop of model calls and tool executions.
        # For now, we'll just call the model once.
        # response = self.model.generate(prompt)

        # Let's simulate a tool call
        tool_result = AVAILABLE_TOOLS["academic_search"](query)
        
        prompt_with_tool_results = f"Based on the following information, write a report about {query}:\n\n{tool_result}"
        
        report = self.model.generate(prompt_with_tool_results) if self.model else "This is a placeholder report because the model is not loaded."
        
        print(f"[{self.job_id}] Report generated.")
        return report


class SuggestPhase(BasePhase):
    """
    Converts a report into actionable recommendations.
    Tools: None.
    Output: Structured checklist or suggestions (e.g., JSON).
    """
    async def run(self, report: str) -> dict:
        print(f"[{self.job_id}] Running Suggest Phase.")
        
        prompt = f"Based on the following report, please provide a structured list of actionable recommendations in JSON format:\n\n{report}"
        
        suggestions_json = self.model.generate(prompt) if self.model else '{"recommendations": ["Placeholder recommendation 1", "Placeholder recommendation 2"]}'

        # In a real implementation, we would parse and validate the JSON.
        import json
        try:
            suggestions = json.loads(suggestions_json)
        except json.JSONDecodeError:
            print(f"[{self.job_id}] Error: Could not decode JSON from model output.")
            suggestions = {"error": "Failed to generate suggestions."}

        print(f"[{self.job_id}] Suggestions generated.")
        return suggestions


class ExecutePhase(BasePhase):
    """
    Acts on suggestions or verifies them.
    Tools: Execution tools, notification.
    Output: Execution log or status summary.
    """
    async def run(self, suggestions: dict) -> str:
        print(f"[{self.job_id}] Running Execute Phase.")
        
        execution_log = []
        recommendations = suggestions.get("recommendations", [])
        
        for rec in recommendations:
            # Here we could have tools to execute tasks. For now, we'll just log.
            log_entry = f"Executing: {rec}"
            print(f"[{self.job_id}] {log_entry}")
            execution_log.append(log_entry)
            
        summary = f"Execution summary for job {self.job_id}:\n" + "\n".join(execution_log)
        
        # Notify on completion
        try:
            # A real implementation would get user's email from somewhere
            user_email = "user@localhost" 
            AVAILABLE_TOOLS["send_email"](user_email, f"Job {self.job_id} completed", summary)
        except Exception as e:
            print(f"[{self.job_id}] Failed to send notification email: {e}")
            
        print(f"[{self.job_id}] Execution finished.")
        return summary
