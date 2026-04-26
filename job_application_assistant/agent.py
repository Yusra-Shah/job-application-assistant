import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from job_application_assistant.tools import (
    save_job_application,
    get_all_applications,
    get_user_profile,
    update_application_status,
    send_email_summary,
    get_application_stats,
    create_calendar_event
)

load_dotenv()
model = os.getenv("MODEL")

analyzer_agent = Agent(
    name="analyzer_agent",
    model=model,
    description="Analyzes job descriptions.",
    instruction="""You are an expert job analyst. Extract:
COMPANY: [name]
ROLE: [title]
REQUIRED_SKILLS: [list]
EXPERIENCE_LEVEL: [level]""",
    output_key="job_analysis"
)

matcher_agent = Agent(
    name="matcher_agent",
    model=model,
    description="Matches profile against job.",
    instruction="""Using {job_analysis}: call get_user_profile, compare skills, calculate match score 0-100, recommend APPLY if score >= 40, call save_job_application.
Format:
MATCH_SCORE: [n]/100
MATCHING_SKILLS: [list]
MISSING_SKILLS: [list]
RECOMMENDATION: [APPLY/DO NOT APPLY]
APPLICATION_ID: [id]""",
    tools=[get_user_profile, save_job_application],
    output_key="match_result"
)

cover_letter_agent = Agent(
    name="cover_letter_agent",
    model=model,
    description="Writes cover letter.",
    instruction="""Using {job_analysis} and {match_result}, write a 3-paragraph cover letter. Sign off as Yusra Batool.""",
    output_key="cover_letter"
)

email_agent = Agent(
    name="email_agent",
    model=model,
    description="Sends email summary.",
    instruction="""Using {job_analysis}, {match_result} and {cover_letter}: call send_email_summary with to_email=shahyusra05@gmail.com, subject=Job Application Summary - [ROLE] at [COMPANY], body=full summary.""",
    tools=[send_email_summary],
    output_key="email_result"
)

scheduler_agent = Agent(
    name="scheduler_agent",
    model=model,
    description="Generates a Google Calendar quick-add link for follow-up.",
    instruction="""Using {job_analysis} and {match_result}: if RECOMMENDATION is APPLY, call create_calendar_event with summary='Follow up: [ROLE] at [COMPANY]', description='Application ID: [APPLICATION_ID]. Follow up on your job application.', days_from_now=7.
Return the calendar_link from the result so the user can click it to add the reminder to their Google Calendar.""",
    tools=[create_calendar_event],
    output_key="schedule_result"
)

interview_prep_agent = Agent(
    name="interview_prep_agent",
    model=model,
    description="Generates interview preparation guidance.",
    instruction="""Using {job_analysis} and {match_result}:
1. List 5 likely technical interview questions based on REQUIRED_SKILLS.
2. List 3 behavioral questions relevant to the role.
3. For each skill in MISSING_SKILLS, suggest one resource or topic to study before the interview.
4. Give a 2-sentence tip on how to frame Yusra's background for this specific role.
Keep it concise and practical.""",
    output_key="interview_prep"
)

application_workflow = SequentialAgent(
    name="application_workflow",
    description="Full job application workflow.",
    sub_agents=[analyzer_agent, matcher_agent, cover_letter_agent, email_agent, scheduler_agent, interview_prep_agent]
)

root_agent = Agent(
    name="job_assistant_manager",
    model=model,
    description="SmartApply - intelligent job application assistant.",
    instruction="""You are SmartApply, an intelligent job application assistant built by Yusra Batool.
When the user pastes a job description: transfer to application_workflow.
When the user asks to see applications: call get_all_applications.
When the user asks for stats: call get_application_stats.
When the user says update application [ID] to [status]: call update_application_status.
Greet the user as SmartApply and list what you can do.""",
    tools=[get_all_applications, update_application_status, get_application_stats],
    sub_agents=[application_workflow]
)
