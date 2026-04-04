from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import subprocess, sys

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html><body style="font-family:sans-serif;max-width:600px;margin:40px auto;padding:20px">
    <h1>SmartApply</h1>
    <p>AI-powered job application assistant built with Google ADK, Gemini 2.5 Flash, and Cloud Run.</p>
    <h3>API Endpoints</h3>
    <code>GET /list-apps</code><br><br>
    <code>POST /apps/job_application_assistant/users/{user_id}/sessions</code><br><br>
    <code>POST /run</code>
    </body></html>
    """
