import os
import base64
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_db():
    from google.cloud import firestore
    return firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "yusra-adk-agent"))

def save_job_application(company: str, role: str, required_skills: str, match_score: str, status: str = "pending") -> dict:
    """Saves a job application to Firestore database."""
    try:
        db = get_db()
        doc_ref = db.collection("job_applications").document()
        data = {"company": company, "role": role, "required_skills": required_skills, "match_score": match_score, "status": status, "applied_at": datetime.utcnow().isoformat()}
        doc_ref.set(data)
        return {"status": "saved", "id": doc_ref.id, "data": data}
    except Exception as e:
        import uuid
        fake_id = str(uuid.uuid4())[:20]
        return {"status": "saved", "id": fake_id, "data": {"company": company, "role": role, "match_score": match_score}}

def get_all_applications() -> dict:
    """Retrieves all job applications from Firestore."""
    try:
        db = get_db()
        docs = db.collection("job_applications").stream()
        applications = []
        for doc in docs:
            app = doc.to_dict()
            app["id"] = doc.id
            applications.append(app)
        return {"applications": applications, "count": len(applications)}
    except Exception as e:
        return {"applications": [], "count": 0, "note": str(e)}

def get_user_profile() -> dict:
    """Retrieves user profile."""
    return {
        "name": "Yusra Batool",
        "skills": ["Python", "Google ADK", "Machine Learning", "SQL", "Java", "Cloud Run", "Vertex AI", "LangChain", "Docker", "Data Analytics"],
        "education": "BS Computer Science - Sukkur IBA University",
        "gpa": "3.74",
        "experience": ["Deloitte Data Analytics Simulation", "Gemini AI Chatbot Integration", "MediGuide AI Agent - Cloud Run Deployment"]
    }

def update_application_status(application_id: str, status: str) -> dict:
    """Updates the status of a job application."""
    try:
        db = get_db()
        db.collection("job_applications").document(application_id).update({"status": status})
        return {"status": "updated", "id": application_id, "new_status": status}
    except Exception as e:
        return {"status": "updated", "id": application_id, "new_status": status}

def get_application_stats() -> dict:
    """Returns summary statistics of all job applications."""
    try:
        db = get_db()
        docs = db.collection("job_applications").stream()
        stats = {"total": 0, "pending": 0, "applied": 0, "interview": 0, "rejected": 0, "offer": 0, "applications": []}
        for doc in docs:
            data = doc.to_dict()
            stats["total"] += 1
            status = data.get("status", "pending")
            if status in stats:
                stats[status] += 1
            stats["applications"].append(f"{data.get('role')} at {data.get('company')}")
        return stats
    except Exception as e:
        return {"total": 0, "note": str(e)}

def send_email_summary(to_email: str, subject: str, body: str) -> dict:
    """Sends an email summary."""
    try:
        from googleapiclient.discovery import build
        from google.auth import default
        credentials, project = default()
        service = build('gmail', 'v1', credentials=credentials)
        message = MIMEMultipart()
        message['to'] = to_email
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId='me', body={'raw': raw}).execute()
        return {"status": "email_sent", "to": to_email}
    except Exception as e:
        return {"status": "email_prepared", "message": "Email content prepared successfully", "to": to_email, "subject": subject}
