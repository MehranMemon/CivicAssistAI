# Master Prompt: Build CivicAssist AI (Beginner Hackathon Version)

Copy everything between the lines into the AI coding tool you are using (Antigravity, Replit Agent, or another coding agent). If you already have the CivicAssist_AI starter folder, tell the agent to inspect and improve that code instead of unnecessarily starting over.

---

You are my senior full-stack developer and patient beginner-friendly hackathon mentor. Build a complete working project named **CivicAssist AI**. I am a beginner and our team has very little time. Do not over-engineer, add unnecessary libraries, or give me just sample snippets. Create/edit the actual project files in the workspace, run checks where possible, fix errors, and finish with a clear file tree and exact terminal commands.

## Hackathon requirements
- A working web application.
- A real AI model/API that does useful work.
- A public GitHub repository with all project source code and a clear README.
- The web application deployed online to a public link.
- A 3–5 minute demo video uploaded to Google Drive.
- Keep all API keys and passwords out of code and GitHub.
- We must follow the event's five-hour build deadline. The code must be written during the official build window.

## Product idea
CivicAssist AI helps citizens report potholes, overflowing waste, broken streetlights, drainage/sewage problems, water leaks, and other public issues. A citizen describes the issue in their own words, enters the city and locality, and optionally uploads one photo. The app uses AI to create a structured complaint report, then checks existing local reports for possible duplicates and shows a simple community dashboard.

## Very simple tech stack (do not add more unless essential)
- Python
- Streamlit for the website UI
- Google Gemini API using the official `google-genai` Python SDK
- Pydantic for structured AI output validation
- JSON file for lightweight hackathon-demo report storage
- GitHub for source control
- Streamlit Community Cloud for deployment

Do not use React, Node.js, Docker, Supabase, login/authentication, complicated maps, video processing, or a custom-trained model for this MVP. The JSON storage is for a prototype only; explain honestly in the README that a hosted app may lose local file data after restarts. Do not promise durable storage.

## Required app features
1. **Report form:** issue description, city (default Hyderabad, Sindh), locality, optional landmark, desired complaint language (English, Urdu or Sindhi), and optional single photo upload.
2. **Real AI/NLP:** send the description and context to the Gemini API. If a photo is attached and the model supports image input, send it as well. Do not mock or fake an AI response. If the API key is missing or the call fails, show an honest error message and do not pretend the report was analyzed.
3. **Structured output:** validate and display the following fields: short title, one category from a fixed list, urgency recommendation (Low/Medium/High), one to three reasons for urgency, short summary, formal complaint draft, recommended next action, safety concerns, visible photo observations (empty if there is no photo), and missing details that may improve the report.
4. **Safe AI behavior:** do not invent addresses, evidence, injuries, legal requirements, exact repair dates, official government departments, or official priority. Clearly label urgency as a recommendation. Never claim the report was sent to government.
5. **Citizen review:** show the complaint so the citizen can review and copy it. Add a JSON download if easy.
6. **Unique differentiator — possible duplicate detection:** before or after saving, compare category, locality, and description against saved reports using a short, understandable Python text-similarity method (e.g. `difflib.SequenceMatcher` plus token overlap). Display possible duplicates for review. Do not label them confirmed duplicates and do not add complex vector databases.
7. **CivicPulse dashboard:** show saved reports, category counts, locality counts, suggested urgency totals, and a filterable recent-reports list. Label the dashboard as reports stored in this demo, not a complete official city dataset.
8. **Data storage:** create a local `data/reports.json` only as needed. Handle a missing or invalid JSON file. Do not commit the file because it may contain citizen text. Explain prototype limitations in README.
9. **Optional image:** accept JPG/JPEG/PNG/WEBP of maximum 5 MB. Analyze visible evidence only. Do not add video. The app must still work without a photo.
10. **Professional simple UI:** clean, accessible, responsive enough for a phone, with loading, error, empty, and success states. Avoid spending time on decorative animations.

## Required project files
Create these files at minimum:
- `app.py` — complete runnable Streamlit app
- `requirements.txt` — minimal runtime dependencies
- `README.md` — full beginner instructions detailed below
- `.gitignore` — ignores `.venv/`, `__pycache__/`, `.streamlit/secrets.toml`, `.env`, and `data/reports.json`
- `.streamlit/config.toml` — optional basic theme
- `.streamlit/secrets.toml.example` — placeholders only, never a real key
- `data/README.txt` — explain that the report JSON is created automatically and should not be committed
- `MASTER_PROMPT.md` — this prompt, so the project contains its build instructions

## API key handling
Read `GEMINI_API_KEY` from Streamlit secrets or an environment variable. Read `GEMINI_MODEL` the same way, defaulting to a supported, low-cost model such as `gemini-3.5-flash-lite` only if available to the account. If the model is unavailable, explain how to change it in README. Never hardcode the key. The local secrets file is `.streamlit/secrets.toml` and must be git-ignored. For Streamlit Cloud, use its Secrets settings.

## README must be written for a Windows beginner
Include exact, copy-paste commands and explain where to run them:
1. Install Python and Git and verify them in Windows Command Prompt.
2. Open the extracted folder and start CMD in that folder by typing `cmd` into File Explorer's address bar.
3. Create and activate `.venv`.
4. Install `requirements.txt`.
5. Create `.streamlit/secrets.toml` from the example file and use Notepad to add the Gemini API key. Explain where to get the key from Google AI Studio and never to share it.
6. Start the app with `streamlit run app.py` and explain how to open localhost and stop the server.
7. Give a sample complaint to test.
8. Explain every file in the project.
9. Show GitHub setup and exact `git init`, `git add`, `git status`, `git commit`, `git branch`, `git remote`, and `git push` commands with a placeholder repo URL. Warn the user to check that `.streamlit/secrets.toml` and `data/reports.json` are not staged.
10. Explain Streamlit Community Cloud deployment, selecting the GitHub repository and `app.py`, and adding secrets in Advanced settings.
11. Explain common fixes for a missing API key, unavailable model, quota error, package installation error, and deployment error.
12. Include demo script and final hackathon checklist.

## Execution plan
- First inspect the workspace and state what exists; do not overwrite user work without checking.
- Create the smallest working version first: text form -> real AI result -> save report -> dashboard.
- Run syntax/import checks and start the app where the environment allows.
- Fix errors rather than leaving TODOs or pseudocode.
- Add the photo feature only if text analysis works end-to-end.
- Verify `.gitignore` and secrets handling.
- Do not claim API, deployment, or file persistence was tested unless it really was.
- Do not create a fake government integration or fake report data. If adding sample records, label them Demo data.
- Do not ask me to choose extra features; make sensible defaults and keep moving.

## Final response required from you
When done, return:
1. A concise list of implemented features.
2. The exact project file tree.
3. All complete files in the workspace, not incomplete snippets.
4. A ZIP archive of the complete project if file tools are available.
5. The exact Windows CMD commands to install and run it.
6. The exact API key setup location and deployment-secret instructions.
7. A clear list of anything you could not test or complete.

Start building now. Prefer a simple working app over ambitious unfinished features.

---
