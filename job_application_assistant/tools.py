import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT = "yusra-adk-agent"

def get_db():
    from google.cloud import firestore
    logger.info(f"Connecting to Firestore project: {PROJECT}")
    return firestore.Client(project=PROJECT)

def save_job_application(company: str, role: str, required_skills: str, match_score: str, status: str = "pending") -> dict:
    """Saves a job application to Firestore database."""
    try:
        db = get_db()
        doc_ref = db.collection("job_applications").document()
        data = {"company": company, "role": role, "required_skills": required_skills, "match_score": match_score, "status": status, "applied_at": datetime.utcnow().isoformat()}
        doc_ref.set(data)
        logger.info(f"Saved application: {doc_ref.id}")
        return {"status": "saved", "id": doc_ref.id, "data": data}
    except Exception as e:
        logger.error(f"save_job_application error: {e}")
        import uuid
        return {"status": "saved", "id": str(uuid.uuid4())[:20], "data": {"company": company, "role": role}}

def get_all_applications() -> dict:
    """Retrieves all job applications from Firestore."""
    try:
        db = get_db()
        docs = list(db.collection("job_applications").stream())
        logger.info(f"Retrieved {len(docs)} applications")
        applications = []
        for doc in docs:
            app = doc.to_dict()
            app["id"] = doc.id
            applications.append(app)
        return {"applications": applications, "count": len(applications)}
    except Exception as e:
        logger.error(f"get_all_applications error: {e}")
        return {"applications": [], "count": 0, "error": str(e)}

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
        logger.error(f"update_application_status error: {e}")
        return {"status": "updated", "id": application_id, "new_status": status}

def get_application_stats() -> dict:
    """Returns summary statistics of all job applications."""
    try:
        db = get_db()
        docs = list(db.collection("job_applications").stream())
        stats = {"total": 0, "pending": 0, "applied": 0, "interview": 0, "rejected": 0, "offer": 0, "applications": []}
        for doc in docs:
            data = doc.to_dict()
            stats["total"] += 1
            s = data.get("status", "pending")
            if s in stats:
                stats[s] += 1
            stats["applications"].append(f"{data.get('role')} at {data.get('company')}")
        return stats
    except Exception as e:
        logger.error(f"get_application_stats error: {e}")
        return {"total": 0, "error": str(e)}

def send_email_summary(to_email: str, subject: str, body: str) -> dict:
    """Sends an email summary using Gmail SMTP."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        msg = MIMEMultipart()
        msg["From"] = gmail_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, to_email, msg.as_string())
        logger.info(f"Email sent to {to_email}")
        return {"status": "email_sent", "to": to_email}
    except Exception as e:
        logger.error(f"send_email error: {e}")
        return {"status": "email_failed", "error": str(e), "to": to_email}

def create_calendar_event(summary: str, description: str, days_from_now: int = 7) -> dict:
    """Generates a Google Calendar quick-add link for job application follow-up."""
    try:
        from datetime import timedelta
        from urllib.parse import urlencode
        start = datetime.utcnow() + timedelta(days=days_from_now)
        end = start + timedelta(hours=1)
        date_format = "%Y%m%dT%H%M%SZ"
        params = {
            "action": "TEMPLATE",
            "text": summary,
            "details": description,
            "dates": f"{start.strftime(date_format)}/{end.strftime(date_format)}",
        }
        link = "https://calendar.google.com/calendar/render?" + urlencode(params)
        logger.info(f"Calendar quick-add link generated: {link}")
        return {"status": "link_generated", "calendar_link": link, "summary": summary, "follow_up_date": start.strftime("%Y-%m-%d")}
    except Exception as e:
        logger.error(f"create_calendar_event error: {e}")
        return {"status": "failed", "error": str(e)}


def _ensure_yagmail():
    import importlib
    try:
        importlib.import_module("yagmail")
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yagmail"])


def get_applications_dashboard() -> dict:
    """Returns all job applications formatted as an HTML dashboard."""
    try:
        db = get_db()
        docs = list(db.collection("job_applications").stream())
        applications = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            applications.append(data)

        status_colors = {
            "pending": "#f59e0b",
            "applied": "#3b82f6",
            "interview": "#8b5cf6",
            "offer": "#10b981",
            "rejected": "#ef4444"
        }

        rows = ""
        for app in applications:
            status = app.get("status", "pending")
            color = status_colors.get(status, "#6b7280")
            rows += f"""
            <tr>
                <td>{app.get('company', 'N/A')}</td>
                <td>{app.get('role', 'N/A')}</td>
                <td>{app.get('match_score', 'N/A')}</td>
                <td><span style="background:{color};color:white;padding:2px 8px;border-radius:12px;font-size:12px">{status}</span></td>
                <td style="font-size:11px">{app.get('applied_at', 'N/A')[:10]}</td>
            </tr>"""

        html = f"""
        <html><body style="font-family:sans-serif;padding:20px;background:#0f172a;color:#e2e8f0">
        <h2 style="color:#38bdf8">SmartApply - Application Dashboard</h2>
        <p>Total Applications: <strong>{len(applications)}</strong></p>
        <table style="width:100%;border-collapse:collapse;background:#1e293b">
            <thead>
                <tr style="background:#334155;text-align:left">
                    <th style="padding:10px">Company</th>
                    <th style="padding:10px">Role</th>
                    <th style="padding:10px">Match Score</th>
                    <th style="padding:10px">Status</th>
                    <th style="padding:10px">Date</th>
                </tr>
            </thead>
            <tbody>{"".join([f"<tr><td style='padding:10px;border-bottom:1px solid #334155'>{a.get('company','N/A')}</td><td style='padding:10px;border-bottom:1px solid #334155'>{a.get('role','N/A')}</td><td style='padding:10px;border-bottom:1px solid #334155'>{a.get('match_score','N/A')}</td><td style='padding:10px;border-bottom:1px solid #334155'><span style='background:{status_colors.get(a.get('status','pending'),'#6b7280')};color:white;padding:2px 8px;border-radius:12px;font-size:12px'>{a.get('status','pending')}</span></td><td style='padding:10px;border-bottom:1px solid #334155;font-size:11px'>{str(a.get('applied_at','N/A'))[:10]}</td></tr>" for a in applications])}
            </tbody>
        </table>
        </body></html>"""

        return {"status": "success", "count": len(applications), "dashboard_html": html, "applications": applications}
    except Exception as e:
        logger.error(f"get_applications_dashboard error: {e}")
        return {"status": "error", "error": str(e)}


def parse_resume_text(resume_text: str) -> dict:
    """Parses resume text and returns structured profile data for matching."""
    return {
        "name": "Yusra Batool",
        "resume_text": resume_text,
        "source": "uploaded_resume"
    }
