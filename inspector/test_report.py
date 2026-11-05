
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"


def sanitize_url(url):
    """Remove query parameters and fragments from a URL."""
    if not url:
        return ""

    parsed = urlsplit(url)

    return urlunsplit((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        "",
        ""
    ))


def write_login_report(
    initial_url,
    final_url,
    submission_attempted,
    session_assessment,
    click_timed_out=False
):
    """
    Save a login test summary without collecting credentials.
    """

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().astimezone()

    report = {
        "test_type": "authorized_login_test",
        "timestamp": timestamp.isoformat(),
        "portal": urlsplit(initial_url).hostname,
        "initial_url": sanitize_url(initial_url),
        "final_url": sanitize_url(final_url),
        "transport": urlsplit(initial_url).scheme.upper(),
        "submission_attempted": submission_attempted,
        "click_timed_out": click_timed_out,
        "session_assessment": session_assessment,
        "credentials_recorded": False
    }

    filename = (
        "login_test_"
        + timestamp.strftime("%Y%m%d_%H%M%S_%f")
        + ".json"
    )

    report_path = REPORTS_DIR / filename

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return report_path

def write_logout_report(
    initial_url,
    final_url,
    login_attempted,
    logout_attempted,
    logout_assessment
):
    """Write a JSON report for an authorized logout test."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().astimezone()

    report = {
        "test_type": "authorized_logout_test",
        "timestamp": timestamp.isoformat(),
        "portal": urlsplit(initial_url).hostname,
        "initial_url": sanitize_url(initial_url),
        "final_url": sanitize_url(final_url),
        "transport": urlsplit(initial_url).scheme.upper(),
        "login_attempted": login_attempted,
        "logout_attempted": logout_attempted,
        "logout_assessment": logout_assessment,
        "credentials_recorded": False
    }

    filename = (
        "logout_test_"
        + timestamp.strftime("%Y%m%d_%H%M%S_%f")
        + ".json"
    )

    report_path = REPORTS_DIR / filename

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return report_path
