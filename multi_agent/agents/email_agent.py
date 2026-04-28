"""
Email monitoring agent.

Mock email tools are provided out of the box so the agent works immediately.
To connect a real inbox, replace the bodies of _fetch_mock() and _fetch_details_mock()
with calls to your email provider (Gmail API, IMAP via imaplib, Microsoft Graph, etc.).
"""

import json
from datetime import datetime, timedelta

import anthropic
from anthropic import beta_tool

# ---------------------------------------------------------------------------
# Mock data — swap in real API calls here
# ---------------------------------------------------------------------------

def _fetch_mock(max_emails: int) -> list[dict]:
    now = datetime.now()
    return [
        {
            "id": "e001",
            "from": "ceo@company.com",
            "subject": "URGENT: Board deck needs your slide by EOD",
            "date": (now - timedelta(hours=1)).isoformat(),
            "read": False,
            "preview": "Hi, I need your department slide for the board presentation. Please send by 5pm today.",
        },
        {
            "id": "e002",
            "from": "client@bigcorp.com",
            "subject": "Re: Proposal — still waiting for revised quote",
            "date": (now - timedelta(days=3)).isoformat(),
            "read": True,
            "preview": "Following up again on the revised pricing proposal we discussed last week...",
        },
        {
            "id": "e003",
            "from": "hr@company.com",
            "subject": "Action required: Complete annual compliance training",
            "date": (now - timedelta(days=5)).isoformat(),
            "read": False,
            "preview": "This is a reminder that the deadline for completing mandatory compliance training is Friday.",
        },
        {
            "id": "e004",
            "from": "noreply@github.com",
            "subject": "PR review requested: fix/auth-token-expiry",
            "date": (now - timedelta(hours=4)).isoformat(),
            "read": False,
            "preview": "alice requested your review on pull request #142.",
        },
        {
            "id": "e005",
            "from": "newsletter@techdigest.io",
            "subject": "This week in AI — April digest",
            "date": (now - timedelta(days=1)).isoformat(),
            "read": True,
            "preview": "Top stories: new model benchmarks, open-source releases, and regulatory updates...",
        },
    ][:max_emails]


def _fetch_details_mock(email_id: str) -> dict:
    bodies = {
        "e001": "Hi team, I need everyone's department slide for the Q2 board presentation. Format: 3 bullets max, include key metric. Please send to me directly by 5pm today. This is critical.",
        "e002": "Hi, I've sent two follow-up emails about the revised quote. Our procurement team needs this to proceed. Please respond ASAP or we'll have to look at other vendors.",
        "e003": "This is your third reminder. The compliance training deadline is this Friday. Non-completion will be escalated to your manager. Link: https://training.internal/compliance",
        "e004": "PR #142 fixes the auth token expiry bug causing user logouts. Alice needs your review before merging. CI is green.",
        "e005": "Newsletter content here...",
    }
    return {
        "id": email_id,
        "body": bodies.get(email_id, "Email body not found."),
        "attachments": [],
    }


# ---------------------------------------------------------------------------
# Tools (replace mock implementations above to connect a real inbox)
# ---------------------------------------------------------------------------

@beta_tool
def check_unread_emails(max_emails: int = 10) -> str:
    """Retrieve recent emails from the inbox.

    Args:
        max_emails: Maximum number of emails to retrieve (1–50, default 10).
    """
    emails = _fetch_mock(min(max(max_emails, 1), 50))
    return json.dumps(emails, indent=2)


@beta_tool
def get_email_details(email_id: str) -> str:
    """Get the full body of a specific email.

    Args:
        email_id: The unique ID of the email (from check_unread_emails).
    """
    return json.dumps(_fetch_details_mock(email_id), indent=2)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

_SYSTEM = (
    "You are an email assistant. Check the inbox, identify every email that needs "
    "action or is significantly overdue, and present a prioritised summary. "
    "For urgent items include what action is needed and by when. "
    "Be concise — the user is busy."
)


class EmailAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def run(self, request: str) -> str:
        runner = self.client.beta.messages.tool_runner(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=_SYSTEM,
            tools=[check_unread_emails, get_email_details],
            messages=[{"role": "user", "content": request}],
        )

        final_text = ""
        for message in runner:
            for block in message.content:
                if block.type == "text" and block.text:
                    print(block.text, end="", flush=True)
                    final_text = block.text

        print()
        return final_text
