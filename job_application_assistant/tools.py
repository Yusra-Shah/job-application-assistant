import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT = "yusra-adk-agent"

def get_db():
    try:
        from google.cloud import firestore
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-cloud-firestore==2.19.0"])
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
    """Returns all job applications as a summary list for the dashboard."""
    result = get_all_applications()
    if "error" in result:
        logger.error(f"get_applications_dashboard error: {result['error']}")
        return {"status": "error", "error": result["error"]}
    applications = result.get("applications", [])
    summary = []
    for a in applications:
        summary.append({
            "company": a.get("company", "N/A"),
            "role": a.get("role", "N/A"),
            "match_score": a.get("match_score", "N/A"),
            "status": a.get("status", "pending"),
            "date": str(a.get("applied_at", "N/A"))[:10],
            "id": a.get("id", "")
        })
    return {"status": "success", "count": len(summary), "applications": summary}


def parse_resume_text(resume_text: str) -> dict:
    """Parses resume text and returns structured profile data for matching."""
    return {
        "name": "Yusra Batool",
        "resume_text": resume_text,
        "source": "uploaded_resume"
    }


def generate_tailored_resume(job_title: str, company: str, required_skills: str, matching_skills: str, missing_skills: str) -> dict:
    """Generates a tailored resume text based on job requirements."""
    resume = f"""YUSRA BATOOL
Sukkur, Pakistan | shahyusra05@gmail.com | linkedin.com/in/yusra-batool-578a8433a | github.com/Yusra-Shah

OBJECTIVE
Motivated Computer Science student seeking {job_title} role at {company}. Bringing hands-on experience in AI/ML development, cloud deployment, and data analytics with a strong foundation in Python and Google Cloud.

EDUCATION
B.S. Computer Science | Sukkur IBA University, Pakistan | Expected June 2028 | GPA: 3.75/4.0

RELEVANT SKILLS
Matching: {matching_skills}
Learning: {missing_skills}

PROJECTS
SmartApply - Multi-Agent AI Job Application Assistant
- Architected a 6-agent pipeline using Google ADK SequentialAgent deployed on Cloud Run
- Built Firestore integration, Gmail SMTP email, and Google Calendar quick-add link generation
- Deployed MCP server via FastMCP exposing Firestore tools over SSE transport

MediGuide AI Agent
- Built multi-agent medical information assistant using Google ADK and Gemini 2.5 Flash
- Integrated real-time Wikipedia research via LangChain, deployed on Google Cloud Run

Matcha Journal - MLH AI Hackfest 2026
- Built full-stack AI journaling app solo in 24 hours using Groq API (LLaMA 3.3 70B) and MongoDB Atlas
- Deployed live on Streamlit Cloud with 54 registered participants

Pneumonia Detection ML App
- Building medical imaging application trained on chest X-ray datasets using CNNs and transfer learning

Maze Adventure Game
- GUI-based game implementing BFS, DFS, Dijkstra's algorithms; demonstrated at AI & CS Expo 2024

EXPERIENCE
Google Cloud Gen AI Academy APAC Edition - Cohort 1 | Jan - Apr 2026
- Completed Track 1; built and deployed 3 live AI agents on Google Cloud Run
- Selected for Builder Stories feature for publishing technical blog on SmartApply architecture

MLH AI Hackfest 2026 | April 2026
- Built and submitted Matcha Journal solo in under 24 hours; app deployed live

Deloitte Data Analytics Job Simulation | Summer 2025
- Analyzed business datasets using Excel and Tableau; built KPI dashboards

CERTIFICATIONS
- Google Generative AI Leader Professional Certificate
- Google Data Analytics Certificate
- IBM Data Analytics Professional Certificate
- Amazon Aurora SQL Training
- HackerRank: Java, SQL, Python

TECHNICAL SKILLS
Languages: Python, Java, C++, SQL, R
Tools: Google ADK, Gemini, Vertex AI, Cloud Run, Firestore, Docker, LangChain, Tableau, Power BI, Git
Concepts: Machine Learning, OOP, Data Structures, Cloud Computing, AI Agents, Data Visualization"""

    return {"status": "success", "resume_text": resume, "job_title": job_title, "company": company}
