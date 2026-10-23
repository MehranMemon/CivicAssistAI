"""
CivicAssist AI — Hackathon civic issue reporting prototype.
=============================================================
Stack: Python · Streamlit · Google Gemini API (google-genai) · Pydantic · local JSON.

IMPORTANT NOTICES (displayed in the UI):
- This app prepares a report; it does NOT submit anything to a government department.
- AI categories, urgency levels, and complaint drafts are suggestions for citizen review.
- Local JSON storage is prototype-only; free-hosting restarts may reset saved data.
- Never enter private, sensitive, or personally identifying information into a public demo.
"""

from __future__ import annotations

import json
import os
import re
import secrets
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
REPORTS_FILE = DATA_DIR / "reports.json"
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB
KARACHI_TZ = ZoneInfo("Asia/Karachi")

CATEGORIES = [
    "Road Damage",
    "Waste / Garbage",
    "Streetlight",
    "Drainage / Sewage",
    "Water Supply / Leak",
    "Public Safety",
    "Other",
]

URGENCY_COLORS = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}


# ---------------------------------------------------------------------------
# Pydantic schema for structured AI output
# ---------------------------------------------------------------------------
class ComplaintAnalysis(BaseModel):
    """Validated structured output returned by the Gemini API."""

    title: str = Field(description="Short and clear complaint title (max 12 words)")
    category: Literal[
        "Road Damage",
        "Waste / Garbage",
        "Streetlight",
        "Drainage / Sewage",
        "Water Supply / Leak",
        "Public Safety",
        "Other",
    ]
    urgency: Literal["Low", "Medium", "High"]
    urgency_reasons: list[str] = Field(
        description="One to three evidence-based reasons supporting the suggested priority level"
    )
    issue_summary: str = Field(
        description="One or two sentence neutral, factual summary of the reported issue"
    )
    complaint_draft: str = Field(
        description="Polite, clear, formal complaint text ready for a citizen to review, edit, and submit"
    )
    recommended_action: str = Field(
        description="Practical next step the citizen could take (do not name a specific government department number or invent contact details)"
    )
    safety_concerns: list[str] = Field(
        description="Only immediate safety concerns directly supported by the submitted information — empty list if none"
    )
    evidence_observations: list[str] = Field(
        description="Visible details observed in the uploaded photo — must be EMPTY LIST when no photo is provided"
    )
    missing_information: list[str] = Field(
        description="Important details not in the report that would meaningfully improve it"
    )


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def get_setting(name: str, default: str = "") -> str:
    """Read a setting from Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(name, "")
        if value:
            return str(value).strip()
    except Exception:
        # Local secrets file is optional; fall through to env vars.
        pass
    return os.getenv(name, default).strip()


def now_local() -> str:
    """Return the current PKT timestamp as an ISO 8601 string."""
    return datetime.now(KARACHI_TZ).isoformat(timespec="seconds")


def load_reports() -> list[dict]:
    """Load the report list from the JSON file, returning [] on any error."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not REPORTS_FILE.exists():
        return []
    try:
        loaded = json.loads(REPORTS_FILE.read_text(encoding="utf-8"))
        return loaded if isinstance(loaded, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_reports(reports: list[dict]) -> None:
    """Atomic-ish save: write to a temp file then rename to reduce corruption risk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = REPORTS_FILE.with_suffix(".tmp")
    temp_file.write_text(
        json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temp_file.replace(REPORTS_FILE)


def simplify(text: str) -> str:
    """Lowercase and collapse whitespace for comparison."""
    return re.sub(r"\s+", " ", (text or "").casefold()).strip()


def token_overlap(a: str, b: str) -> float:
    """Jaccard similarity over word tokens (Latin + Arabic-script words)."""
    words_a = set(re.findall(r"[a-zA-Z0-9\u0600-\u06FF]+", simplify(a)))
    words_b = set(re.findall(r"[a-zA-Z0-9\u0600-\u06FF]+", simplify(b)))
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def find_possible_duplicates(candidate: dict, reports: list[dict]) -> list[dict]:
    """
    Simple, transparent heuristic: same locality AND category AND text similarity.
    Flags POSSIBLE duplicates only — never confirmed duplicates.
    """
    matches: list[tuple[float, dict]] = []
    candidate_area = simplify(candidate.get("locality", ""))
    candidate_category = simplify(candidate.get("category", ""))
    candidate_text = candidate.get("description", "") + " " + candidate.get("issue_summary", "")

    if not candidate_area:
        return []  # Cannot compare without a locality

    for old in reports:
        if simplify(old.get("locality", "")) != candidate_area:
            continue
        if simplify(old.get("category", "")) != candidate_category:
            continue
        old_text = old.get("description", "") + " " + old.get("issue_summary", "")
        overlap = token_overlap(candidate_text, old_text)
        sequence_score = SequenceMatcher(
            None, simplify(candidate_text), simplify(old_text)
        ).ratio()
        combined = max(overlap, sequence_score * 0.75)
        if overlap >= 0.28 or sequence_score >= 0.67:
            matches.append((combined, old))

    matches.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in matches[:3]]


def make_report_id() -> str:
    """Generate a unique, human-readable reference ID."""
    return "CIV-" + datetime.now(KARACHI_TZ).strftime("%y%m%d") + "-" + secrets.token_hex(2).upper()


# ---------------------------------------------------------------------------
# Gemini API call
# ---------------------------------------------------------------------------
def analyze_complaint(
    description: str,
    city: str,
    locality: str,
    landmark: str,
    output_language: str,
    image_bytes: bytes | None = None,
    image_mime: str | None = None,
) -> ComplaintAnalysis:
    """
    Send the complaint to the Gemini API and return a validated ComplaintAnalysis.
    Raises RuntimeError with a clear message if the API key is missing or the call fails.
    Never returns a fake/mocked response.
    """
    api_key = get_setting("GEMINI_API_KEY")
    model_id = get_setting("GEMINI_MODEL", "gemini-3.5-flash-lite")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not found.\n\n"
            "Local users: create .streamlit/secrets.toml from the example file and add your key.\n"
            "Streamlit Cloud users: add the key in App Settings → Secrets.\n"
            "See README.md section 6 for step-by-step instructions."
        )

    client = genai.Client(api_key=api_key)

    system_prompt = f"""You are the analysis engine for CivicAssist AI, a citizen civic-issue reporting demo.
Analyze the citizen's report and return a single structured response that strictly matches the requested JSON schema.

Citizen description:
{description}

City / area: {city}
Locality / neighbourhood: {locality or 'Not provided'}
Nearby landmark: {landmark or 'Not provided'}
Required output language for title, summary, and complaint draft: {output_language}

STRICT RULES — follow every rule without exception:
1. Choose EXACTLY ONE category from the schema enum. Never invent a new category.
2. Suggest Low, Medium, or High urgency based only on what the citizen described.
   Always note clearly that this is a suggestion, NOT an official municipal decision.
3. Provide one to three urgency_reasons that are directly supported by the submitted information.
4. Do NOT invent precise street addresses, dates, injuries, causes, government phone numbers,
   repair deadlines, official statuses, legal requirements, or government department names.
5. Do NOT claim the complaint has been sent or will be sent to any government authority.
6. The complaint_draft must be polite, practical, and easy for the citizen to edit before using.
7. If critical information is missing, list it in missing_information instead of guessing.
8. If an image is attached, describe ONLY what is visually observable in evidence_observations.
   An image does not prove cause, severity, ownership, or exact location.
9. If NO image is attached, evidence_observations MUST be an empty list [].
10. If immediate danger is described, note that the citizen should contact a local emergency
    or utility service directly. Do NOT invent specific phone numbers.
11. Write the title, issue_summary, and complaint_draft in {output_language}.
    Other fields (category, urgency, urgency_reasons, etc.) may remain in English.
""".strip()

    # Build contents list: text prompt first, then optional image
    contents: list = [system_prompt]
    if image_bytes and image_mime:
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type=image_mime)
        )

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComplaintAnalysis,
                temperature=0.2,
                max_output_tokens=2048,
            ),
        )
    except Exception as api_exc:
        raise RuntimeError(
            f"The Gemini API call failed: {api_exc}\n\n"
            "Check your API key, model name, quota, and internet connection. "
            "See README.md section 11 for troubleshooting."
        ) from api_exc

    if not response.text:
        raise RuntimeError(
            "The AI returned an empty response. This can happen when the model "
            "cannot process the request. Please try again or check your quota."
        )

    return ComplaintAnalysis.model_validate_json(response.text)


# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CivicAssist AI | Civic Issue Reporting",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS — clean, accessible, mobile-friendly
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* max width and comfortable padding */
    .block-container {max-width: 1180px; padding-top: 1.6rem; padding-bottom: 2.5rem;}

    /* hero banner */
    .hero {
        padding: 1.4rem 1.6rem;
        border: 1px solid rgba(120,130,150,.25);
        border-radius: 18px;
        background: linear-gradient(120deg, rgba(14,116,144,.10), rgba(37,99,235,.06));
        margin-bottom: 0.5rem;
    }
    .hero h1 {margin: 0 0 .4rem 0; font-size: 2rem;}

    /* muted captions */
    .subtle {color: #64748b; font-size: .91rem;}

    /* metric card borders */
    div[data-testid="stMetric"] {
        border: 1px solid rgba(120,130,150,.24);
        padding: .8rem 1rem;
        border-radius: 12px;
        background: rgba(255,255,255,.5);
    }

    /* disclaimer banner */
    .disclaimer {
        background: rgba(234,179,8,.08);
        border-left: 4px solid #ca8a04;
        padding: .6rem 1rem;
        border-radius: 0 8px 8px 0;
        font-size: .9rem;
        margin-bottom: .8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏙️ CivicAssist AI")
    st.caption("Intelligent civic issue reporting · Hackathon prototype")
    st.divider()
    page = st.radio(
        "Navigate",
        ["📝 Report an issue", "📊 CivicPulse dashboard", "ℹ️ About this demo"],
        index=0,
    )
    st.divider()
    st.markdown(
        """
        <div class="subtle">
        ⚠️ AI recommendations require citizen review.<br>
        Reports are NOT sent to any authority.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Hero banner (shown on all pages)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <h1>CivicAssist AI</h1>
      <div style="font-size:1.08rem;">Report smarter. Identify patterns. Improve your neighbourhood.</div>
      <p class="subtle" style="margin:.5rem 0 0 0;">
        Describe a civic issue, get an AI-structured complaint report, and help spot repeated problems in your area.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load saved reports once at the top level (not inside each page block)
reports = load_reports()

# ===========================================================================
# PAGE 1 — Report an issue
# ===========================================================================
if page == "📝 Report an issue":
    st.subheader("Tell us about the problem")
    st.write(
        "Describe the issue in your own words. The AI will suggest a category, "
        "urgency level, and draft a formal complaint you can review and use."
    )

    # Disclaimer
    st.markdown(
        """
        <div class="disclaimer">
        ℹ️ <strong>Important:</strong> CivicAssist <em>prepares</em> a complaint report.
        It does <strong>not</strong> submit anything to a government department or authority.
        The suggested urgency is a recommendation only — not an official decision.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("complaint_form", clear_on_submit=False):
        description = st.text_area(
            "What happened? *",
            placeholder=(
                "Example: There is a deep pothole near the school gate on Main Road. "
                "Motorcycles and rickshaws are swerving to avoid it. It gets dangerous at night."
            ),
            height=130,
            help=(
                "Describe what you saw and why it matters. "
                "Do not include personal ID numbers, phone numbers, or private details."
            ),
        )
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input(
                "City / area *",
                value="Hyderabad, Sindh",
                help="Enter the city or town where this issue is located.",
            )
            locality = st.text_input(
                "Locality / neighbourhood",
                placeholder="e.g., Qasimabad, Latifabad, Hirabad",
                help="The specific neighbourhood helps with duplicate detection.",
            )
        with col2:
            landmark = st.text_input(
                "Nearby landmark (optional)",
                placeholder="e.g., near a school gate, bus stop, or mosque",
            )
            output_language = st.selectbox(
                "Complaint language",
                ["English", "Urdu", "Sindhi"],
                help="The AI will write the formal complaint in this language.",
            )
        photo = st.file_uploader(
            "Optional photo evidence (JPG, JPEG, PNG, WEBP — max 5 MB)",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=False,
            help=(
                "If uploaded and the model supports image input, the AI will describe "
                "visible evidence only. The app works without a photo."
            ),
        )
        submitted = st.form_submit_button(
            "✨ Analyze issue with AI", type="primary", use_container_width=True
        )

    # Validation and submission
    if submitted:
        errors = []
        if len(description.strip()) < 12:
            errors.append("Please describe the issue in at least a short sentence so the AI has enough context.")
        if not city.strip():
            errors.append("Please enter the city or area.")
        if photo is not None and len(photo.getvalue()) > MAX_IMAGE_BYTES:
            errors.append(
                f"The photo is {len(photo.getvalue()) / 1024 / 1024:.1f} MB, which exceeds the 5 MB limit. "
                "Choose a smaller image or continue without a photo."
            )

        if errors:
            for err in errors:
                st.warning(err)
        else:
            with st.spinner(
                "AI is analyzing the description"
                + (" and photo" if photo else "")
                + "… this usually takes 5–15 seconds."
            ):
                try:
                    analysis = analyze_complaint(
                        description=description.strip(),
                        city=city.strip(),
                        locality=locality.strip(),
                        landmark=landmark.strip(),
                        output_language=output_language,
                        image_bytes=photo.getvalue() if photo else None,
                        image_mime=photo.type if photo else None,
                    )

                    new_report = {
                        "report_id": make_report_id(),
                        "created_at": now_local(),
                        "city": city.strip(),
                        "locality": locality.strip(),
                        "landmark": landmark.strip(),
                        "description": description.strip(),
                        "output_language": output_language,
                        "category": analysis.category,
                        "urgency": analysis.urgency,
                        "urgency_reasons": analysis.urgency_reasons,
                        "title": analysis.title,
                        "issue_summary": analysis.issue_summary,
                        "complaint_draft": analysis.complaint_draft,
                        "recommended_action": analysis.recommended_action,
                        "safety_concerns": analysis.safety_concerns,
                        "evidence_observations": analysis.evidence_observations,
                        "missing_information": analysis.missing_information,
                        "photo_attached": photo is not None,
                        "status": "Prepared in CivicAssist — NOT submitted to any government authority",
                    }

                    # Duplicate detection runs against existing reports (before inserting new one)
                    duplicates = find_possible_duplicates(new_report, reports)
                    new_report["possible_duplicate_ids"] = [
                        d.get("report_id", "Unknown") for d in duplicates
                    ]

                    # Insert at front; save to file
                    reports.insert(0, new_report)
                    save_reports(reports)

                    # Stash in session state to display below (survives st.rerun)
                    st.session_state["latest_report"] = new_report
                    st.session_state["latest_duplicates"] = duplicates
                    st.rerun()

                except RuntimeError as exc:
                    st.error("❌ " + str(exc))
                except Exception as exc:
                    st.error(
                        "The report could not be analyzed. "
                        "Check your API key, model access, and internet connection."
                    )
                    with st.expander("🔧 Technical details (for debugging)"):
                        st.code(str(exc), language="text")

    # Display the most recently generated report
    latest_report = st.session_state.get("latest_report")
    if latest_report:
        st.divider()
        urgency_icon = URGENCY_COLORS.get(latest_report["urgency"], "⚪")
        st.subheader(f"Your AI-generated report — {latest_report['report_id']}")
        st.success(
            f"✅ Report prepared successfully. Reference ID: **{latest_report['report_id']}**"
        )
        st.caption(
            "Review the result below before using it. "
            "This is a suggested report, not an official submission or verified municipal priority."
        )

        # Summary metrics row
        m1, m2, m3 = st.columns(3)
        m1.metric("Suggested category", latest_report["category"])
        m2.metric("Suggested urgency", f"{urgency_icon} {latest_report['urgency']}")
        m3.metric("Reference ID", latest_report["report_id"])

        st.markdown(f"### {latest_report['title']}")
        st.write(latest_report["issue_summary"])

        # Two-column detail view
        left, right = st.columns(2)
        with left:
            st.markdown("**Why this urgency was suggested**")
            if latest_report.get("urgency_reasons"):
                for item in latest_report["urgency_reasons"]:
                    st.markdown(f"- {item}")
            else:
                st.write("No specific urgency reasons returned.")

            st.markdown("**Safety considerations**")
            if latest_report.get("safety_concerns"):
                for item in latest_report["safety_concerns"]:
                    st.markdown(f"- {item}")
            else:
                st.write("No specific safety concern was identified from the supplied information.")

        with right:
            st.markdown("**Photo observations**")
            if latest_report.get("evidence_observations"):
                for item in latest_report["evidence_observations"]:
                    st.markdown(f"- {item}")
            elif latest_report.get("photo_attached"):
                st.write("No clear visual observations were returned for the uploaded photo.")
            else:
                st.write("No photo was attached.")

            st.markdown("**Details you could add to strengthen the report**")
            if latest_report.get("missing_information"):
                for item in latest_report["missing_information"]:
                    st.markdown(f"- {item}")
            else:
                st.write("No important missing details were flagged.")

        # Complaint draft — copyable
        st.markdown("#### Formal complaint draft")
        st.text_area(
            "Review, edit, and copy this complaint before submitting it yourself:",
            value=latest_report["complaint_draft"],
            height=190,
            key="latest_complaint_copy",
        )
        st.info(
            "📋 **Next step:** Review the complaint above, then submit it yourself through "
            "the appropriate real-world channel (e.g., the local municipal helpline or app). "
            "CivicAssist has NOT sent this to anyone."
        )
        st.write("**Suggested next action:** " + latest_report.get("recommended_action", ""))

        # Download button
        json_bytes = json.dumps(latest_report, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            label="⬇️ Download full report (JSON)",
            data=json_bytes,
            file_name=f"{latest_report['report_id']}.json",
            mime="application/json",
            use_container_width=True,
        )

        # Duplicate warning
        st.divider()
        duplicates = st.session_state.get("latest_duplicates", [])
        if duplicates:
            st.warning(
                f"⚠️ **Possible duplicate(s) detected** — {len(duplicates)} existing report(s) "
                "in the same locality and category are similar to this one. "
                "Please review before treating these as separate issues."
            )
            for dup in duplicates:
                dup_id = dup.get("report_id", "Unknown")
                dup_title = dup.get("title", "Civic issue")
                dup_area = dup.get("locality", "")
                dup_date = dup.get("created_at", "")
                st.write(f"**{dup_id}** — {dup_title}  ·  {dup_area}  ·  {dup_date[:10] if dup_date else ''}")
        else:
            st.caption("✔️ No likely duplicate was found among the reports currently stored in this demo.")

# ===========================================================================
# PAGE 2 — CivicPulse dashboard
# ===========================================================================
elif page == "📊 CivicPulse dashboard":
    st.subheader("CivicPulse — Community issue dashboard")
    st.caption(
        "Shows reports saved in this CivicAssist demo instance. "
        "This is NOT an official or complete municipal database."
    )

    if not reports:
        st.info(
            "📭 No reports have been saved yet. "
            "Open **📝 Report an issue** and analyze a sample civic issue to populate this dashboard."
        )
    else:
        total = len(reports)
        high_urgency = sum(1 for r in reports if r.get("urgency") == "High")
        medium_urgency = sum(1 for r in reports if r.get("urgency") == "Medium")
        categories_seen = len(set(r.get("category", "Other") for r in reports))
        with_duplicates = sum(1 for r in reports if r.get("possible_duplicate_ids"))

        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total reports", total)
        m2.metric("🔴 Suggested high urgency", high_urgency)
        m3.metric("Issue categories", categories_seen)
        m4.metric("Reports with possible duplicates", with_duplicates)

        st.divider()

        # Filters
        fc1, fc2 = st.columns(2)
        with fc1:
            category_filter = st.selectbox("Filter by category", ["All"] + CATEGORIES)
        with fc2:
            urgency_filter = st.selectbox("Filter by suggested urgency", ["All", "High", "Medium", "Low"])

        filtered = [
            r for r in reports
            if (category_filter == "All" or r.get("category") == category_filter)
            and (urgency_filter == "All" or r.get("urgency") == urgency_filter)
        ]

        # Charts
        st.markdown("### Reports by category")
        count_by_category: dict[str, int] = {}
        for r in reports:
            cat = r.get("category", "Other")
            count_by_category[cat] = count_by_category.get(cat, 0) + 1
        st.bar_chart(count_by_category)

        st.markdown("### Reports by locality")
        area_counts: dict[str, int] = {}
        for r in reports:
            area = r.get("locality") or "Locality not provided"
            area_counts[area] = area_counts.get(area, 0) + 1
        st.bar_chart(area_counts)

        st.markdown("### Urgency breakdown")
        urgency_counts = {
            "🔴 High": sum(1 for r in reports if r.get("urgency") == "High"),
            "🟡 Medium": medium_urgency,
            "🟢 Low": sum(1 for r in reports if r.get("urgency") == "Low"),
        }
        st.bar_chart(urgency_counts)

        # Recent reports list
        st.markdown(f"### Recent reports ({len(filtered)} shown)")
        if not filtered:
            st.info("No reports match the selected filters.")
        else:
            for r in filtered[:50]:
                urgency_icon = URGENCY_COLORS.get(r.get("urgency", ""), "⚪")
                title_label = (
                    f"{r.get('report_id', 'CIV')} · "
                    f"{urgency_icon} {r.get('urgency', '')} · "
                    f"{r.get('title', 'Civic issue')}"
                )
                with st.expander(title_label):
                    st.write(
                        f"**Category:** {r.get('category', 'Other')}  |  "
                        f"**Suggested urgency:** {urgency_icon} {r.get('urgency', 'Unspecified')}"
                    )
                    st.write(
                        f"**Area:** {r.get('locality') or 'Not provided'}, {r.get('city', '')}"
                    )
                    st.write(f"**Created:** {r.get('created_at', 'Unknown time')}")
                    st.write(r.get("issue_summary", ""))
                    if r.get("possible_duplicate_ids"):
                        st.warning(
                            "⚠️ Possible duplicate of: "
                            + ", ".join(r["possible_duplicate_ids"])
                        )
                    st.caption(r.get("status", "Saved in demo"))

        st.caption(
            "Dashboard data is from reports stored by this running demo. "
            "Report counts are not evidence of real-world problem severity. "
            "Data may be reset if the hosting service restarts."
        )

# ===========================================================================
# PAGE 3 — About this demo
# ===========================================================================
elif page == "ℹ️ About this demo":
    st.subheader("What CivicAssist AI does")
    st.markdown(
        """
        **CivicAssist AI** is a beginner-friendly hackathon prototype showing how AI can help citizens
        write structured civic issue reports.

        ### Features
        - **AI classification & NLP** — classifies a free-text complaint into one of six categories,
          extracts details, suggests urgency with evidence-based reasons, and drafts a polite formal complaint.
        - **Multilingual output** — complaint drafts can be generated in English, Urdu, or Sindhi.
        - **Optional photo analysis** — if you upload a photo and the model supports image input,
          the AI describes what it can visually observe (not what it assumes).
        - **Possible duplicate detection** — compares category, locality, and text similarity against
          saved reports using a transparent Python heuristic (Jaccard token overlap + SequenceMatcher).
          Flags *possible* matches only — never confirmed duplicates.
        - **CivicPulse dashboard** — summarizes saved reports by category, locality, and suggested urgency.
        - **Citizen control** — you review and decide what to do with the generated report.
          There is no automatic submission.
        - **JSON download** — download the complete structured report as a JSON file.

        ### Technology stack
        | Part | Technology |
        |---|---|
        | Web UI | Python + Streamlit |
        | AI / NLP | Google Gemini API via `google-genai` SDK |
        | Structured output | Pydantic schema + JSON response mode |
        | Duplicate detection | `difflib.SequenceMatcher` + Jaccard token overlap |
        | Report storage | Local `data/reports.json` (hackathon prototype) |
        | Hosting | Streamlit Community Cloud (free tier) |
        | Version control | GitHub (public repository) |

        ### Known limitations
        - CivicAssist **does not** send reports to a government department or authority.
        - An AI urgency level is a **suggestion**, not an official priority or municipal decision.
        - Photo interpretation can be incorrect or incomplete.
        - The built-in JSON file store is a small prototype. Free hosting may reset local file data
          after restarts or redeployments. For reliable multi-user storage, a managed database is needed.
        - AI analysis quality depends on the amount of detail provided. Vague descriptions produce
          less useful results.
        - Do **not** enter private, sensitive, or personally identifying information into a public demo.
        - Sindhi and Urdu complaint drafts depend on model capability; quality may vary.
        """
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "CivicAssist AI · Hackathon prototype · "
    "AI-generated content must be reviewed before use · "
    "Reports are NOT submitted to any government authority."
)
