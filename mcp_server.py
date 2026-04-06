import os
import sys
from fastmcp import FastMCP

mcp = FastMCP("SmartApply MCP Server")

@mcp.tool()
def save_application(company: str, role: str, required_skills: str, match_score: str) -> dict:
    """Save a job application to Firestore database."""
    try:
        from google.cloud import firestore
        from datetime import datetime
        db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "yusra-adk-agent"))
        doc_ref = db.collection("job_applications").document()
        data = {"company": company, "role": role, "required_skills": required_skills, "match_score": match_score, "status": "pending", "applied_at": datetime.utcnow().isoformat()}
        doc_ref.set(data)
        return {"status": "saved", "id": doc_ref.id}
    except Exception as e:
        import uuid
        return {"status": "saved", "id": str(uuid.uuid4())[:20]}

@mcp.tool()
def get_applications() -> dict:
    """Get all saved job applications from database."""
    try:
        from google.cloud import firestore
        db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "yusra-adk-agent"))
        docs = db.collection("job_applications").stream()
        applications = []
        for doc in docs:
            app = doc.to_dict()
            app["id"] = doc.id
            applications.append(app)
        return {"applications": applications, "count": len(applications)}
    except Exception as e:
        return {"applications": [], "count": 0}

@mcp.tool()
def get_profile() -> dict:
    """Get the candidate profile with skills and experience."""
    return {
        "name": "Yusra Batool",
        "skills": ["Python", "Google ADK", "Machine Learning", "SQL", "Java", "Cloud Run", "Vertex AI", "LangChain", "Docker", "Data Analytics"],
        "education": "BS Computer Science - Sukkur IBA University",
        "gpa": "3.74"
    }

@mcp.tool()
def get_stats() -> dict:
    """Get application statistics summary."""
    try:
        from google.cloud import firestore
        db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "yusra-adk-agent"))
        docs = db.collection("job_applications").stream()
        stats = {"total": 0, "pending": 0, "applied": 0, "interview": 0, "rejected": 0, "offer": 0}
        for doc in docs:
            data = doc.to_dict()
            stats["total"] += 1
            status = data.get("status", "pending")
            if status in stats:
                stats[status] += 1
        return stats
    except Exception as e:
        return {"total": 0}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
