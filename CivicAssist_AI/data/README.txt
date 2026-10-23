CivicAssist AI - data folder
============================
When you click "Save to CivicPulse demo dashboard", the app creates data/reports.json here.

* It is prototype storage for a hackathon demo, NOT a real database.
* On free hosting (Streamlit Community Cloud) this file can be ERASED whenever the app
  restarts, sleeps, or is redeployed. Do not rely on it for permanent records.
* It can contain text typed by citizens, so it is listed in .gitignore and must NOT be
  uploaded to GitHub.
* If the file ever becomes unreadable, the app renames it to reports.corrupt-<number>.json
  and starts a fresh list instead of silently deleting your data.
* For reliable long-term storage, replace this with a managed database (future work).
