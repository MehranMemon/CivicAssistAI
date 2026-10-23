# CivicAssist AI

A beginner-friendly web app that helps citizens write and categorize reports about civic problems
(potholes, overflowing waste, broken streetlights, drainage problems, water leaks and similar issues).

- A citizen describes the problem (optionally with one photo).
- **Gemini AI** returns a *structured, validated* report: category, suggested urgency with reasons, summary, formal complaint draft, next action, safety concerns and missing details.
- The citizen **reviews and edits** it, gets a **reference ID**, and can copy or download it.
- Saved reports are compared to find **possible duplicates**, and shown on the **CivicPulse** dashboard.

> **Honest limits.** CivicAssist **does not submit anything to any government department**. The urgency level is an **AI suggestion, not an official decision**. Reports are saved in a local JSON file that **free hosting can erase** when the app restarts.

---

## 1. Files in this project

| File | What it is for |
|---|---|
| `app.py` | The whole app (screen, Gemini call, duplicate check, dashboard) |
| `requirements.txt` | Python packages to install |
| `README.md` | This guide |
| `MASTER_PROMPT.md` | The prompt used to build the project |
| `.gitignore` | Tells Git to never upload secrets, your virtual environment, or saved reports |
| `.env.example` | Optional alternative way to set the key (you can ignore it) |
| `.streamlit/config.toml` | Colors/theme |
| `.streamlit/secrets.toml.example` | Template for your API key file |
| `data/README.txt` | Explains the demo storage folder |

You will create `.streamlit/secrets.toml` yourself (Step 5). It is never uploaded.

## 2. How it works (for your demo)

1. **Report an issue** tab: fill the form and click **Analyze issue with AI**.
2. A **real Gemini API call** returns JSON that must match a fixed schema (Pydantic). If it does not match, it is rejected, not shown.
3. Review the result, edit the complaint if you like, download it (.txt or .json), then click **Save to CivicPulse demo dashboard**.
4. If a saved report in the **same area and category** has **similar wording**, you see a *possible duplicate* warning (a simple text-similarity guess, never "confirmed").
5. **CivicPulse dashboard** tab: counts by category, locality and suggested urgency, filters, and recent reports.

If the API key is missing or Gemini fails, you see an honest error message. The app never invents an AI answer.

---

## 3. Install Python and Git (one time)

1. **Python:** download Python 3.12 from <https://www.python.org/downloads/>. Run the installer and **tick "Add python.exe to PATH"** on the first screen, then click *Install Now*.
2. **Git:** download from <https://git-scm.com/download/win> and click *Next* through the installer (defaults are fine).
3. Close any open Command Prompt windows.

## 4. Open Command Prompt in the project folder

1. Extract `CivicAssist_AI.zip` (right-click, **Extract All**).
2. Open the extracted `CivicAssist_AI` folder in File Explorer (you should see `app.py` inside).
3. Click the **address bar** at the top, type `cmd` and press **Enter**. A black Command Prompt window opens *in that folder*.
4. Check the installs:

```bat
py --version
git --version
```

Both should print a version number. If `py` is "not recognized", reinstall Python and tick *Add python.exe to PATH*.

### Create and activate a virtual environment, then install

Run these one at a time in that same window:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

You should now see `(.venv)` at the start of the line. Use **Command Prompt (cmd)**, not PowerShell, because PowerShell may block the activate script.
Every time you open a new Command Prompt later, run `.venv\Scripts\activate` again first.

## 5. Get a Gemini API key and add it

### A. Get the key

1. Open <https://aistudio.google.com/apikey> and sign in with a Google account.
2. Click **Create API key** and copy it.
3. Treat it like a password: do not paste it into chats, screenshots, GitHub or code.

### B. Put it in `.streamlit/secrets.toml` using Notepad

In Command Prompt (inside the project folder):

```bat
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
notepad .streamlit\secrets.toml
```

Notepad opens. Replace only `PASTE_YOUR_REAL_GEMINI_API_KEY_HERE` with your key, keep the quotation marks, then **File > Save** and close Notepad:

```toml
GEMINI_API_KEY = "your-real-key-here"
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

> If Notepad saves it as `secrets.toml.txt`, the app cannot find it. In File Explorer, turn on *View > Show > File name extensions* and rename it to exactly `secrets.toml`.

**Model note:** `gemini-3.5-flash-lite` is a low-cost model listed in Google's current Gemini API docs, and it accepts photos. Whether your key's free tier includes it can change, so check your limits in Google AI Studio. If you get a model or quota error, see Section 11.

## 6. Run the app on your computer

```bat
streamlit run app.py
```

Your browser opens the app (usually <http://localhost:8501>). If it does not, copy that address into your browser. To stop the app, click the Command Prompt window and press **Ctrl+C**.

## 7. Test it with an example complaint

On the **Report an issue** tab, enter:

- **What happened?** `There is a deep pothole on the road near a school gate. Motorcycles are swerving to avoid it and children cross here every morning.`
- **City:** `Hyderabad, Sindh`
- **Locality:** `Qasimabad`
- **Landmark:** `Near a primary school`
- **Language:** `English`

Click **Analyze issue with AI**. You should see a category, suggested urgency with reasons, a complaint draft and a reference ID.

Then test the other features:

1. Click **Save to CivicPulse demo dashboard**.
2. Start a new report in the **same locality** with similar wording (for example: `Big pothole near the school gate in Qasimabad, bikes swerve around it`). You should see a **possible duplicate** warning.
3. Open the **CivicPulse dashboard** tab to see counts and recent reports.
4. Try a different issue (for example a broken streetlight) and the **Urdu** or **Sindhi** language option.
5. Last, try a small JPG/PNG photo. If photo analysis fails, the app still works without a photo.
6. To test the error state: temporarily put a wrong key in `secrets.toml`, restart, and confirm you see a clear error and no fake report.

## 8. Upload to a public GitHub repository

### A. Create the repository

1. Sign in at <https://github.com/> and click **New repository**.
2. Name it `civicassist-ai`, choose **Public**.
3. Do **not** add a README, `.gitignore` or license (the project already has them). Click **Create repository** and copy the HTTPS address (`https://github.com/YOUR_USERNAME/civicassist-ai.git`).

### B. Check that secrets are protected (important)

In Command Prompt, inside the project folder:

```bat
git init
git add .
git status
```

The list **must NOT contain** `.streamlit/secrets.toml` or `data/reports.json`. It *should* contain `app.py`, `requirements.txt`, `README.md`, `.gitignore`, `.streamlit/secrets.toml.example` and the other project files. If a secret file is listed, stop and ask for help before continuing.

### C. Commit and push

First tell Git who you are (once per computer):

```bat
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Then (replace `YOUR_USERNAME`):

```bat
git commit -m "CivicAssist AI hackathon prototype"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/civicassist-ai.git
git push -u origin main
```

A browser window may ask you to sign in to GitHub. Afterwards refresh your GitHub page and confirm the files are there and **`secrets.toml` is not**. Open the repository link in a private/incognito window to confirm it is public.

**If you ever pushed a real key by mistake:** delete that key in Google AI Studio and create a new one. Removing it from GitHub is not enough.

To upload later changes: `git add .`, `git commit -m "describe change"`, `git push`.

## 9. Deploy on Streamlit Community Cloud (free)

1. Go to <https://share.streamlit.io/> and sign in with GitHub (allow access to your repositories if asked).
2. Click **Create app** and choose to deploy from a GitHub repository.
3. Select repository `YOUR_USERNAME/civicassist-ai`, branch `main`, main file path `app.py`.
4. Open **Advanced settings**. Choose Python **3.12** if a version picker is shown. In the **Secrets** box paste:

```toml
GEMINI_API_KEY = "your-real-key-here"
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

5. Click **Deploy** and wait for the build. Copy the final `https://....streamlit.app` link.
6. Open the link in a private/incognito window and run one real report to prove the cloud app works.

Secrets are entered only in this box (or later via the app's **Settings > Secrets**). Your local `secrets.toml` is never uploaded. After you push code changes to GitHub, the app usually redeploys by itself.

**Remember:** on free hosting the app may sleep and the saved reports in `data/reports.json` may be erased. Do your final demo test shortly before recording.

## 10. What was and was not tested

Be honest with the judges too.

- **Tested by the author of this code (in a sandbox without internet):** Python syntax check, and automated checks of the non-screen logic using stand-ins for the libraries: duplicate detection, JSON storage (including a damaged file), report IDs, image-type checking, error messages, key redaction, API-key handling, and rejection of malformed AI output.
- **NOT tested there:** the actual Streamlit screens, a real Gemini API call, photo analysis, the browser on phones, GitHub, and Streamlit Cloud deployment. **You must run Section 7 yourself** before relying on the app. If something fails, use Section 11.

## 11. Fixing common problems

**`streamlit` is not recognized / package errors**
Make sure `(.venv)` shows in the prompt (run `.venv\Scripts\activate`), then `pip install -r requirements.txt`. Start with `python -m streamlit run app.py`. If installation fails, run `python -m pip install --upgrade pip` and try again; check you are using Python 3.11 or 3.12.

**"Gemini API key not found" (missing key)**
Check that `.streamlit\secrets.toml` exists (not only `.example`, and not `.txt`), has your real key inside quotes, and that you restarted the app after saving. On Streamlit Cloud, paste the key into **Settings > Secrets**. A key that still contains `PASTE_YOUR` counts as missing.

**"Google did not accept the API key"**
Create a new key in Google AI Studio and copy the whole key with no spaces.

**Model unavailable / "model not found"**
Change `GEMINI_MODEL` in `secrets.toml` (and in Streamlit Cloud Secrets). Look up current model names at <https://ai.google.dev/gemini-api/docs/models>. Models seen in Google's docs at the time of writing include `gemini-3.5-flash-lite`, `gemini-3.6-flash` and `gemini-3.1-flash-lite`; availability depends on your account. Then restart the app. If the error mentions the SDK, run `pip install --upgrade google-genai`.

**Quota / rate limit / 429**
Wait a minute, test less often, and check your usage and limits in Google AI Studio. Free quotas differ by model and account and can change. Do not add billing details unless the account owner decides to.

**"The AI answer did not match the required format"**
Click Analyze again. The app rejects malformed output on purpose instead of showing it.

**Photo problems**
Use a real JPG, PNG or WEBP under 5 MB. Renaming another file type to `.jpg` will be rejected.

**Works locally but not online**
Open *Manage app* on Streamlit Cloud and read the logs. Check that `requirements.txt` and `app.py` are in the repository root, the main file path is `app.py`, the repository is public, and the Secrets box contains the key.

**Dashboard is empty after a while**
Expected on free hosting. The JSON file can be reset by restarts or redeploys. Save a fresh sample report before your demo.

## 12. Record the demo (3-5 minutes) and submit

Suggested order of events:

1. Record on Windows with **Win + G** (Xbox Game Bar, then Record) or free OBS Studio. Close notifications first.
2. Script (about 4 min): problem (20 s) > enter an example report (40 s) > show the real AI result, urgency reasons and the "not submitted / AI suggestion" labels (50 s) > save it > enter a similar report and show the possible-duplicate warning (50 s) > CivicPulse dashboard (40 s) > photo, only if it worked for you (20 s) > honest limits: suggestion not official, nothing sent to government, JSON storage can reset (20 s).
3. Upload the video to Google Drive, click **Share > General access > Anyone with the link > Viewer**, and copy the link.
4. **Verify every link in a private/incognito window:** GitHub repo (public, no secrets), live Streamlit URL (runs a report), and the Drive video (plays without login).
5. Follow the organizer's rules for the exact submission form and deadline, and submit early.

## Official references

- Gemini API models: <https://ai.google.dev/gemini-api/docs/models>
- Gemini API keys: <https://ai.google.dev/gemini-api/docs/api-key>
- Streamlit Community Cloud: <https://docs.streamlit.io/deploy/streamlit-community-cloud>
- Streamlit secrets: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management>
