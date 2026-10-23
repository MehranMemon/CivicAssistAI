# Master Prompt - CivicAssist AI

This is the prompt used to build this project with an AI coding assistant.
Paste it into a coding assistant together with the project folder if you want to rebuild or extend the app.

---

You are my senior full-stack developer and beginner-friendly hackathon mentor. Build a complete working web app called CivicAssist AI for a five-hour public-service hackathon. I am a beginner, so keep everything simple. Create the actual files, run checks, fix errors, and explain exactly how to run, configure, deploy, and submit the app.

## Problem
Citizens need help writing and categorizing reports about potholes, overflowing waste, broken streetlights, drainage issues, water leaks, and similar civic problems.

## Simple technology stack
- Python
- Streamlit for the web interface
- Gemini API using the official "google-genai" Python SDK
- Pydantic for structured AI output
- Local JSON storage for the hackathon prototype
- GitHub for source code
- Streamlit Community Cloud for free-tier deployment

Do not use React, Node.js, Docker, complicated databases, authentication, video processing, or custom model training. We have very little time.

## Required functionality
1. Let the user enter the issue description, city, locality, optional landmark, and preferred complaint language: English, Urdu, or Sindhi.
2. Allow one optional JPG, JPEG, PNG, or WEBP photo of up to 5 MB.
3. Make a real Gemini API call to classify the complaint, suggest low/medium/high urgency, explain its reasoning, summarize the issue, draft a formal complaint, recommend a next action, identify supported safety concerns, and list missing details.
4. Return structured and validated JSON instead of a chatbot conversation.
5. If the API key is missing or AI fails, display an honest error. Never fake an AI response.
6. Show the report to the user for review and give it a unique reference ID. Let the user copy or download the report.
7. Compare new reports with existing reports using category, locality, and simple text similarity. Flag possible duplicates, never confirmed duplicates.
8. Build a CivicPulse dashboard showing report counts, categories, localities, suggested urgency, and recent reports.
9. Save reports to "data/reports.json" for the prototype. Explain that free-hosting restarts may reset the data.
10. Never claim a report has been submitted to a government department. Never present an AI urgency recommendation as an official decision.
11. Keep the interface clean, responsive, and accessible, with loading, error, empty, and success states.
12. Keep API keys in Streamlit secrets or environment variables. Never hardcode or commit secrets.

## Required files
Create "app.py", "requirements.txt", "README.md", ".gitignore", ".streamlit/config.toml", ".streamlit/secrets.toml.example", "data/README.txt", and "MASTER_PROMPT.md".

## README requirements
Write for a Windows beginner. Explain:
- Installing Python and Git.
- Opening Command Prompt in the extracted folder.
- Creating and activating a virtual environment.
- Installing the requirements.
- Getting a Gemini API key from Google AI Studio.
- Creating ".streamlit/secrets.toml" and adding the key with Notepad.
- Running "streamlit run app.py".
- Testing the app with an example complaint.
- Uploading the source to a public GitHub repository using exact commands.
- Deploying on Streamlit Community Cloud and adding secrets safely.
- Fixing missing-key, unavailable-model, quota, installation, and deployment errors.
- Recording a 3-5 minute demo and verifying all submission links.

## Development priorities
Build the working text-report workflow first, then the dashboard, then duplicate detection. Add photo analysis only if the core workflow already works. Do not add video support. Do not pretend features have been tested when they have not.

Inspect the existing project before changing files. Create complete files, run syntax and practical checks, fix errors, and finish by showing the file tree, setup commands, API-key location, deployment instructions, and any limitations honestly.

Start building now. Choose sensible defaults and prioritize a working submission over unnecessary complexity.
