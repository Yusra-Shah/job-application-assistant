from fastmcp import FastMCP
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_application_assistant.tools import (
    save_job_application,
    get_all_applications,
    get_user_profile,
    update_application_status,
    get_application_stats
)

mcp = FastMCP("SmartApply MCP Server")

@mcp.tool()
def save_application(company: str, role: str, required_skills: str, match_score: str) -> dict:
    """Save a job application to Firestore database."""
    return save_job_application(company, role, required_skills, match_score)

@mcp.tool()
def get_applications() -> dict:
    """Get all saved job applications."""
    return get_all_applications()

@mcp.tool()
def get_profile() -> dict:
    """Get the candidate profile."""
    return get_user_profile()

@mcp.tool()
def update_app_status(application_id: str, status: str) -> dict:
    """Update application status."""
    return update_application_status(application_id, status)

@mcp.tool()
def get_application_stats_mcp() -> dict:
    """Get application statistics."""
    return get_application_stats()

if __name__ == "__main__":
    mcp.run(transport="stdio")
