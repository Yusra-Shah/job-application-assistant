import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from job_application_assistant.tools import (
    save_job_application,
    get_all_applications,
    get_user_profile,
    update_application_status,
    send_email_summary,
    get_application_stats
)
load_dotenv()
model = os.getenv("MODEL")
analyzer_agent = Agent(
    name="analyzer_agent",
    model=model,
    description="Analyzes job descriptions and extracts key requirements.",
    instruction="""You are an expert job analyst. When given a job description:
1. Extract the company name and role title
2. List the top 5 required technical skills
3. Identify the experience level required
4. Note any specific qualifications mentioned
Format: COMPANY: [name] ROLE: [title] REQUIRED_SKILLS: [list] EXPERIENCE_LEVEL: [level]""",
    output_key="job_analysis"
)
matcher_agent = Agent(
    name="matcher_agent",
    model=model,
    description="Matches user profile against job requirements.",
    instruction="""Using {job_analysis}: call get_user_profile, compare skills, calculate match score 0-100, recommend APPLY if score >= 40, call save_job_application.
Format: MATCH_SCORE: [n]/100 MATCHING_SKILLS: [list] MISSING_SKILLS: [list] RECOMMENDATION: [APPLY/DO NOT APPLY] APPLICATION_ID: [id]""",
    tools=[get_user_profile, save_job_application],
    output_key="match_result"
)
cover_letter_agent = Agent(
    name="cover_letter_agent",
    model=model,
    description="Writes personalized cover letter.",
    instruction="""Using {job_analysis} and {match_result}, write a 3-paragraph cover letter. Be specific, professional, confident. Sign off as Yusra Batool.""",
    output_key="cover_letter"
)
email_agent = Agent(
    name="email_agent",
    model=model,
    description="Sends application summary email.",
    instruction="""Using {job_analysis}, {match_result} and {cover_letter}: call send_email_summary with to_email=shahyusra05@gmail.com, subject=Job Application Summary - [ROLE] at [COMPANY], body=full summary.""",
    tools=[send_email_summary],
    output_key="email_result"
)
scheduler_agent = Agent(
    name="scheduler_agent",
    model=model,
    description="Creates follow-up reminder.",
    instruction="""Using {job_analysis} and {match_result}: if APPLY, create a follow-up note for 7 days from today. Include Application ID.""",
    output_key="schedule_result"
)
application_workflow = SequentialAgent(
    name="application_workflow",
    description="Full job application workflow.",
    sub_agents=[analyzer_agent, matcher_agent, cover_letter_agent, email_agent, scheduler_agent]
)
root_agent = Agent(
    name="job_assistant_manager",
    model=model,
    description="SmartApply - intelligent job application assistant.",
    instruction="""You are SmartApply, an intelligent job application assistant.
When user pastes a job description: transfer to application_workflow.
When user asks to see applications: call get_all_applications.
When user asks for stats: call get_application_stats.
When user says update application [ID] to [status]: call update_application_status.
Greet the user as SmartApply and list what you can do.""",
    tools=[get_all_applications, update_application_status, get_application_stats],
    sub_agents=[application_workflow]
)
