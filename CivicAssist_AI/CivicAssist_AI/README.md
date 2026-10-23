# CivicAssist AI

**CivicAssist AI** is a beginner-friendly civic issue reporting web app for the DITE Hackathon. A citizen describes a pothole, waste issue, broken streetlight, drainage problem, water leak, or another public issue. The Gemini AI API classifies the issue, suggests urgency with reasons, drafts a formal complaint, and optionally describes visible evidence in one uploaded photo. The app then checks for possible duplicates and displays saved reports on a CivicPulse dashboard.

> **Important:** CivicAssist prepares a report; it does not submit it to a municipal or government department. AI categories and urgency are suggestions and must be reviewed by the citizen. The built-in JSON store is for a small prototype and may be reset by free hosting restarts or redeployments.

## 1. What is included?

- `app.py` — the complete Streamlit app and Gemini AI integration.
- `requirements.txt` — Python packages to install.
- `.streamlit/config.toml` — basic visual theme.
- `.streamlit/secrets.toml.example` — safe example showing where API settings go.
- `.gitignore` — keeps API secrets, virtual environment, and local report data out of GitHub.
- `MASTER_PROMPT.md` — the prompt to give another AI coding tool if your team wants to rebuild or customize the app.
- `data/README.txt` — explains the local demo storage folder.

## 2. Technology used

| Part | Technology | What it does |
|---|---|---|
| Web application | Python + Streamlit | Form, results, dashboard, download button |
| AI / NLP | Gemini API with `google-genai` | Categorizes issue, suggests urgency, extracts details, writes complaint |
| Optional photo understanding | Gemini vision input | Describes visible evidence if a photo is uploaded and the chosen model supports it |
| Structured AI result | Pydantic schema + JSON output | Makes the model return defined fields instead of an open-ended chat |
| Possible duplicate check | Python text similarity | Compares category, locality and description against saved reports |
| Report storage | Local JSON file | Saves small hackathon-demo reports for the running app |
| Hosting | Streamlit Community Cloud | Publishes the web app using a GitHub repository |
| Version control | Public GitHub repository | Shares code and README with judges |

## 3. What you need

- A Windows laptop and internet connection.
- Python 3.11 or 3.12 installed from [python.org](https://www.python.org/downloads/).
- Git installed from [git-scm.com](https://git-scm.com/download/win).
- A Google account and a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
- A GitHub account for sharing the source code.

The Gemini API may have a free quota depending on the model, account, region and current limits. Confirm the model and quota in Google AI Studio before relying on it. This project does not require a paid hosting plan by design, but free service limits and availability can change.

## 4. Open the project in Windows Command Prompt

1. Download and extract the `CivicAssist_AI.zip` file.
2. Open the extracted `CivicAssist_AI` folder in File Explorer.
3. Click the address bar, type `cmd`, and press Enter. This opens Command Prompt in that folder.
4. Check that Python and Git are available:

```bat
py --version
git --version
```

If `py` is not recognized, install Python and enable the option **Add python.exe to PATH** during installation. Close and reopen Command Prompt after installing.

## 5. Install the app (one time)

Run these commands in that same Command Prompt, one at a time:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

When the virtual environment is active, the Command Prompt usually starts with `(.venv)`.

If Windows says script activation is blocked, use **Command Prompt (`cmd`)**, not PowerShell, for these commands.

## 6. Get and add your Gemini API key

### A. Get the key

1. Open [Google AI Studio API keys](https://aistudio.google.com/apikey).
2. Sign in and create or select a project/key as offered by the page.
3. Copy the key. Treat it like a password; do not post it in chat, screenshots, public documents or GitHub.
4. Check that the model you will use is available to your account. The default in this project is `gemini-3.5-flash-lite`.

### B. Create your local secrets file

In Command Prompt, while inside the project folder, run:

```bat
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
notepad .streamlit\secrets.toml
```

Notepad opens the new file. It contains:

```toml
GEMINI_API_KEY = "PASTE_YOUR_REAL_GEMINI_API_KEY_HERE"
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

Replace only `PASTE_YOUR_REAL_GEMINI_API_KEY_HERE` with your copied key, keeping the quotation marks. Save and close Notepad.

**Do not rename this file.** The app reads the key from `.streamlit/secrets.toml`. This real secrets file is ignored by Git so it should not be uploaded to GitHub.

If your account does not have access to the default model, change the `GEMINI_MODEL` value to a supported text-and-image model listed in your AI Studio/API model documentation, then save the file.

## 7. Run the website locally

In the same Command Prompt, run:

```bat
streamlit run app.py
```

The app should open in your browser. If it does not, copy the local address shown in the terminal, usually `http://localhost:8501`, into your browser.

To stop the server, return to Command Prompt and press `Ctrl+C`.

### Test it with this sample

- **Description:** `There is a deep pothole on the road near a school gate. Motorcycles are swerving to avoid it.`
- **City:** `Hyderabad, Sindh`
- **Locality:** `Qasimabad`
- **Landmark:** `Near a school`
- **Photo:** optional; test without it first.

Click **Analyze issue with AI**. The app should display a category, suggested urgency with reasons, complaint draft, report ID and a dashboard entry. If the API fails, open the technical-details expander and check your key, model access, quota and internet connection.

## 8. Project folder structure

```text
CivicAssist_AI/
├── app.py
├── requirements.txt
├── README.md
├── MASTER_PROMPT.md
├── .gitignore
├── .env.example
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
└── data/
    └── README.txt
```

The app creates `data/reports.json` automatically after a report is submitted. That file is ignored by Git because it may contain submitted text. Do not upload real citizen descriptions or personal details to a public repository.

## 9. Upload the project to GitHub

### A. Create a repository

1. Open [GitHub](https://github.com/) and sign in.
2. Click **New repository**.
3. Name it `civicassist-ai`.
4. Select **Public** because the hackathon asks for a public repository.
5. For the simplest first push, do not initialize it with a README or `.gitignore`; this project already contains both.
6. Create the repository and copy its HTTPS URL. It will look like `https://github.com/YOUR_USERNAME/civicassist-ai.git`.

### B. Push the project from Command Prompt

Make sure your current directory is the extracted `CivicAssist_AI` folder and the virtual environment is active. Run:

```bat
git init
git add .
git status
git commit -m "Build CivicAssist AI hackathon MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/civicassist-ai.git
git push -u origin main
```

Replace the URL with your actual repository URL. If Git asks who you are, set your name and email (use the email associated with your GitHub account if appropriate):

```bat
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Then repeat the commit command. GitHub may ask you to authenticate in a browser or through Git Credential Manager.

### C. Security check before pushing

The `git status` output must **not** show `.streamlit/secrets.toml` or `data/reports.json`. If it does, stop and fix `.gitignore` before pushing. Never put an API key in `app.py`, `README.md`, a screenshot, or a public repository.

## 10. Deploy for free on Streamlit Community Cloud

Streamlit's current official deployment flow is described in the [Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

1. Push the code to your public GitHub repository first.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with the GitHub account that owns the repository.
3. Click **Create app**.
4. Select your repository, branch `main`, and main file path `app.py`.
5. Open **Advanced settings** before deploying. In the **Secrets** box, paste the following TOML with your real key:

```toml
GEMINI_API_KEY = "PASTE_YOUR_REAL_GEMINI_API_KEY_HERE"
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

6. Click Save/Deploy. Wait for the build to finish and copy the public `streamlit.app` URL.
7. Open the URL in an incognito/private browser window and test one report. Make sure the hosted app has the secrets configured; your local `secrets.toml` is not uploaded to GitHub and is not automatically copied to Streamlit Cloud.

If you change code after deployment, commit and push the change to GitHub; Streamlit Community Cloud generally redeploys from the repository.

## 11. Common problems and fixes

### `streamlit` is not recognized
Activate the environment again, then run `python -m pip install -r requirements.txt`. Start the app with:

```bat
python -m streamlit run app.py
```

### `GEMINI_API_KEY not found`
Check that `.streamlit\secrets.toml` exists (not just `secrets.toml.example`) and contains the real key. Then stop the app with `Ctrl+C` and run it again. On Streamlit Cloud, add the key in the app's **Secrets** settings.

### Model unavailable / not found
Open Google AI Studio's model documentation and choose a model that is enabled for your account. Update the `GEMINI_MODEL` value in your local secrets file or Streamlit Cloud Secrets settings. Don't change the code unless the SDK/model API has changed.

### Quota, rate limit or billing error
Check the current API usage/quota in AI Studio. A free quota is not guaranteed for every model/account. Use fewer test requests or choose a model available to your account. Do not add billing/payment details unless the account owner explicitly chooses to.

### App runs locally but not online
Check the deploy logs in Streamlit Community Cloud. Confirm `requirements.txt`, `app.py`, and the secrets are in the expected locations. Ensure the GitHub repository is public and the entrypoint is `app.py`.

### Dashboard reports disappear after a restart
The included JSON file is prototype storage. Free hosting may reset writable local files after restarts or redeployments. For a production app or reliable long-term shared storage, replace this with a managed database such as Supabase; that is intentionally left out of this beginner MVP to reduce setup time.

## 12. Five-hour build demo plan

1. **0:00–0:30:** Run locally, add API key, test real AI output.
2. **0:30–1:15:** Test different issue categories and review complaint quality.
3. **1:15–2:00:** Test possible duplicate detection and dashboard.
4. **2:00–2:45:** Push to GitHub and deploy publicly; configure cloud secrets.
5. **2:45–3:30:** Test live URL, including photo input only if time allows.
6. **3:30–4:15:** Record the 3–5 minute video.
7. **Final time:** Upload video to Google Drive, set `Anyone with the link can view`, check the GitHub/live/video links in a private window, and submit the form before the deadline.

This timeline is a suggestion. Follow the organizer's actual cutoff and leave time for the required deliverables.

## 13. Suggested 3–5 minute demo script

1. (20 sec) Introduce the problem: citizens often struggle to describe and prioritize local civic issues.
2. (45 sec) Enter a sample pothole/waste/streetlight report and select the locality.
3. (45 sec) Run the real AI analysis; show category, urgency reasons, and formal complaint.
4. (30 sec) Show the optional photo evidence feature, only if it is working.
5. (45 sec) Submit a second similar report in the same locality and show the possible-duplicate warning.
6. (40 sec) Open CivicPulse to show saved reports, category counts, and locality counts.
7. (20 sec) Explain limits honestly: suggested urgency, not official; no automatic government submission; local JSON storage is a prototype.

## Official references

- [Gemini API getting started](https://ai.google.dev/gemini-api/docs/get-started)
- [Gemini API model list](https://ai.google.dev/gemini-api/docs/models)
- [Using Gemini API keys safely](https://ai.google.dev/gemini-api/docs/api-key)
- [Streamlit Community Cloud deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Streamlit secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
