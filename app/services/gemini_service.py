import google.generativeai as genai
import json
import re
from typing import Optional
from datetime import datetime
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

def _safe_json_parse(text: str) -> Optional[dict]:
    """Strip markdown fences and parse JSON safely."""
    cleaned = re.sub(r"```(?:json)?|```", "", text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None

def enrich_task(title: str, description: Optional[str] = None) -> dict:
    """
    Given a task title (and optional description), ask Gemini to:
    1. Generate a clear, actionable task description
    2. Suggest a priority level with reasoning
    3. Recommend a deadline (relative days from today)

    Returns a dict with keys: description, priority, priority_reason, deadline_days, summary
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    user_desc = f"\nUser description: {description}" if description else ""

    user_prompt = f"""You are a smart task management assistant. A user created a task titled: "{title}"{user_desc}

Today's date: {today}

Respond ONLY with a valid JSON object (no markdown, no extra text) with these exact keys:
{{
  "description": "A clear, actionable 2-3 sentence task description expanding on the title",
  "priority": "low|medium|high|critical",
  "priority_reason": "One sentence explaining why this priority level is appropriate",
  "deadline_days": <integer: recommended days from today to complete this task>,
  "summary": "One crisp sentence summarising what this task involves and its importance"
}}"""

    try:
        response = gemini_model.generate_content(user_prompt)
        result = _safe_json_parse(response.text)
        if result:
            return result
    except Exception as e:
        print(f"Gemini enrich error: {e}")

    # Fallback defaults
    return {
        "description": description or title,
        "priority": "medium",
        "priority_reason": "Default priority assigned (AI unavailable)",
        "deadline_days": 7,
        "summary": title
    }

def score_task_priority(title: str, description: str, current_priority: str) -> dict:
    """
    Re-evaluate the priority of an existing task.
    Returns: { score: 1-10, suggested_priority, reasoning, risk_if_delayed }
    """
    user_prompt = f"""You are a senior project manager. Evaluate the urgency and importance of this task:

Title: "{title}"
Description: "{description}"
Current Priority: {current_priority}

Respond ONLY with a valid JSON object (no markdown, no extra text):
{{
  "score": <integer 1-10, where 10 is most critical>,
  "suggested_priority": "low|medium|high|critical",
  "reasoning": "2-3 sentences on urgency, impact, and effort",
  "risk_if_delayed": "One sentence on consequence of postponing this task"
}}"""

    try:
        response = gemini_model.generate_content(user_prompt)
        result = _safe_json_parse(response.text)
        if result:
            return result
    except Exception as e:
        print(f"Gemini scoring error: {e}")

    return {
        "score": 5,
        "suggested_priority": current_priority,
        "reasoning": "Could not evaluate (AI unavailable). Keeping current priority.",
        "risk_if_delayed": "Unknown"
    }

def summarize_task_list(tasks: list[dict]) -> str:
    """
    Given a list of task dicts, return an AI-generated daily briefing summary.
    """
    if not tasks:
        return "No tasks to summarise."

    task_lines = "\n".join(
        [f"- [{t['priority'].upper()}] {t['title']} (Status: {t['status']})" for t in tasks[:20]]
    )

    prompt = f"""You are a productivity assistant. Here are a user's current tasks:

{task_lines}

Write a concise daily briefing (3-5 sentences) that:
1. Highlights the most critical items
2. Flags any overdue or high-risk tasks
3. Suggests a focus order for the day

Respond with plain text only, no markdown."""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini summary error: {e}")
        return "Could not generate summary (AI unavailable)."
