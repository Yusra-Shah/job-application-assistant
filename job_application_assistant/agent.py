import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.tool_context import ToolContext
from job_application_assistant.tools import (
    save_job_application,
    get_all_applications,
    get_user_profile,
    update_application_status
)

load_dotenv()
model = os.getenv("MODEL")

# --- Agent 1: Job Analyzer ---
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

# --- Agent 2: Profile Matcher ---
matcher_agent = Agent(
    name="matcher_agent",
    model=model,
    description="Matches user profile against job requirements and scores the fit.",
    instruction="""
    You are a career counselor. Using the job analysis from {job_analysis}:
    1. Call get_user_profile to retrieve the candidate's profile
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

# --- Agent 3: Cover Letter Writer ---
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
    
    Store the complete cover letter in output.
    """,
    output_key="cover_letter"
)

# --- Agent 4: Email Sender ---
email_agent = Agent(
    name="email_agent",
    model=model,
    description="Sends the application summary email to the user.",
    instruction="""
    You are an email coordinator. Using {job_analysis}, {match_result} and {cover_letter}:
    
    Compose a clean summary email to shahyusra05@gmail.com with:
    
    Subject: Job Application Summary - [ROLE] at [COMPANY]
    
    Body:
    - Match Score and recommendation
    - Matching skills
    - Missing skills  
    - The full cover letter
    - Application ID for tracking
    
    Make it clean, professional and easy to read.
    End with: "This application has been saved to your database."
    
    Note: Email sending requires Gmail MCP integration.
    Confirm the summary has been prepared successfully.
    """,
    output_key="email_summary"
)

# --- Sequential Workflow ---
application_workflow = SequentialAgent(
    name="application_workflow",
    description="Full job application workflow: analyze, match, write, email.",
    sub_agents=[
        analyzer_agent,
        matcher_agent,
        cover_letter_agent,
        email_agent
    ]
)

# --- Root Manager Agent ---
root_agent = Agent(
    name="job_assistant_manager",
    model=model,
    description="Job Application Assistant - helps you manage and track job applications.",
    instruction="""
    You are SmartApply — an intelligent job application assistant.
    
    You help users with:
    1. Analyzing job descriptions and finding fit
    2. Writing personalized cover letters
    3. Tracking applications in database
    4. Viewing all past applications
    
    When user provides a job description:
    - Transfer to application_workflow immediately
    
    When user asks to see applications:
    - Call get_all_applications and present results clearly
    
    When user asks to update an application status:
    - Call update_application_status with the ID and new status
    
    Always be helpful, professional and encouraging.
    Start by greeting the user as SmartApply and asking what they need.
    """,
    tools=[get_all_applications, update_application_status],
    sub_agents=[application_workflow]
)