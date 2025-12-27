"""
This module defines the tools available to the assistant.
"""
import arxiv
import smtplib
from email.mime.text import MIMEText

def academic_search(query: str, max_results: int = 3) -> str:
    """
    Performs a search on arXiv for academic papers.
    """
    print(f"Searching arXiv for: {query}")
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for result in search.results():
            results.append(f"Title: {result.title}\nAuthors: {', '.join(a.name for a in result.authors)}\nURL: {result.pdf_url}\nSummary: {result.summary[:500]}...")
        return "\n\n".join(results) if results else "No results found."
    except Exception as e:
        return f"An error occurred during search: {e}"


def send_email(to: str, subject: str, body: str) -> str:
    """
    Sends an email notification.
    
    NOTE: This function requires a configured SMTP server.
    The following are placeholders and need to be replaced with actual credentials.
    """
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_user = "user@example.com"
    smtp_password = "password"
    sender_email = "sender@example.com"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            return "Email sent successfully."
    except Exception as e:
        print(f"Failed to send email: {e}")
        return f"Failed to send email: {e}"

# A registry of available tools
AVAILABLE_TOOLS = {
    "academic_search": academic_search,
    "send_email": send_email,
}
