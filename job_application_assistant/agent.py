import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
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

gmail_toolset = MCPToolset(
    connection_params=SseServerParams(url="https://gmail.mcp.claude.com/mcp")
)

calendar_toolset = MCPToolset(
    connection_params=SseServerParams(url="https://gcal.mcp.claude.com/mcp")
)

analyzer_agent = Agent(
    name="analyzer_agent",
    model=model,
    description="Analyzes job descriptions and extracts key requirements.",
    instruction="""
    You are an expert job analyst. When given a job description:
    1. Extract the company name and role title
    2. List the top 5 required technical skills
    3. Identify the experience level required
    4. Note any specific qualifications mentioned
    5. Store your findings clearly for the next agent

    Format your output as:
    COMPANY: [name]
    ROLE: [title]
    REQUIRED_SKILLS: [comma separated list]
    EXPERIENCE_LEVEL: [junior/mid/senior]
    KEY_QUALIFICATIONS: [list]
    """,
    output_key="job_analysis"
)

matcher_agent = Agent(
    name="matcher_agent",
    model=model,
    description="Matches user profile against job requirements and scores the fit.",
    instruction="""
    You are a career counselor. Using the job analysis from {job_analysis}:
    1. Call get_user_profile to retrieve the candidate profile
    2. Compare candidate skills against required skills
    3. Calculate a match score from 0-100
    4. List matching skills and missing skills
    5. Decide if we should apply: apply if score >= 40
    6. Call save_job_application to store this in the database

    Format your output as:
    MATCH_SCORE: [score]/100
    MATCHING_SKILLS: [list]
    MISSING_SKILLS: [list]
    RECOMMENDATION: [APPLY/DO NOT APPLY]
    REASON: [brief explanation]
    APPLICATION_ID: [id from save_job_application]
    """,
    tools=[get_user_profile, save_job_application],
    output_key="match_result"
)

cover_letter_agent = Agent(
    name="cover_letter_agent",
    model=model,
    description="Writes a personalized cover letter based on job analysis and profile match.",
    instruction="""
    You are an expert cover letter writer. Using {job_analysis} and {match_result}:
    1. Write a compelling 3-paragraph cover letter
    2. First paragraph: express interest and mention the role
    3. Second paragraph: highlight matching skills with specific examples
    4. Third paragraph: show enthusiasm and call to action

    Keep it professional, confident and concise.
    Do NOT write generic letters — be specific to the job.
    Sign off as Yusra Batool.
    """,
    output_key="cover_letter"
)

email_agent = Agent(
    name="email_agent",
    model=model,
    description="Sends application summary email via Gmail MCP.",
    instruction="""
    You are an email coordinator. Using {job_analysis}, {match_result} and {cover_letter}:

    Use Gmail MCP tool to send an email:
    - To: shahyusra05@gmail.com
    - Subject: Job Application Summary - [ROLE] at [COMPANY]
    - Body: Full summary with match score, skills analysis, cover letter, and application ID

    If Gmail MCP is unavailable, fall back to send_email_summary tool.
    Confirm the email was sent.
    """,
    tools=[gmail_toolset, send_email_summary],
    output_key="email_result"
)

scheduler_agent = Agent(
    name="scheduler_agent",
    model=model,
    description="Schedules a follow-up reminder in Google Calendar after job application.",
    instruction="""
    You are a scheduling assistant. Using {job_analysis} and {match_result}:

    If recommendation is APPLY:
    1. Use Google Calendar MCP to create a follow-up reminder
    2. Set it for 7 days from today
    3. Title: "Follow up: [ROLE] at [COMPANY]"
    4. Description: Application ID from match_result, note to check application status
    5. Duration: 30 minutes

    If Calendar MCP is unavailable, note the follow-up date in your response.
    Confirm the reminder was created.
    """,
    tools=[calendar_toolset],
    output_key="schedule_result"
)

application_workflow = SequentialAgent(
    name="application_workflow",
    description="Full job application workflow: analyze, match, write cover letter, send email via Gmail MCP, schedule follow-up via Calendar MCP.",
    sub_agents=[
        analyzer_agent,
        matcher_agent,
        cover_letter_agent,
        email_agent,
        scheduler_agent
    ]
)

root_agent = Agent(
    name="job_assistant_manager",
    model=model,
    description="SmartApply - intelligent job application assistant with Gmail and Calendar MCP integrations.",
    instruction="""
    You are SmartApply — an intelligent job application assistant powered by Google ADK and MCP.

    You can help with:

    1. PROCESS A JOB APPLICATION
       When user pastes a job description, transfer to application_workflow.
       This will: analyze the job, match their profile, write a cover letter,
       send an email via Gmail MCP, and schedule a follow-up in Google Calendar MCP.

    2. VIEW ALL APPLICATIONS
       When user asks to see applications: call get_all_applications.

    3. VIEW STATS
       When user asks for a summary or stats: call get_application_stats.

    4. UPDATE STATUS
       When user says update application [ID] to [status]:
       Call update_application_status. Valid: pending, applied, interview, rejected, offer

    5. CHECK EMAILS
       When user asks about emails or interview invites:
       Use Gmail MCP to search their inbox.

    6. CHECK CALENDAR
       When user asks about upcoming follow-ups or interviews:
       Use Google Calendar MCP to list upcoming events.

    Always be helpful, professional and encouraging.
    Start by greeting the user as SmartApply and listing what you can do.
    """,
    tools=[
        get_all_applications,
        update_application_status,
        get_application_stats,
        gmail_toolset,
        calendar_toolset
    ],
    sub_agents=[application_workflow]
)
