"""Fail-closed validation before an announcement can be emailed."""
from datetime import datetime
from urllib.parse import urlparse


def validate_notice(notice: dict) -> list[str]:
    errors = []
    for field in ("id", "title", "agency", "source_url", "start_date", "end_date"):
        if not isinstance(notice.get(field), str) or not notice[field].strip():
            errors.append(f"missing:{field}")
    url = notice.get("source_url", "")
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append("invalid:source_url")
    try:
        start = datetime.strptime(notice["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(notice["end_date"], "%Y-%m-%d").date()
        if start > end:
            errors.append("invalid:date_range")
    except (ValueError, KeyError, TypeError):
        errors.append("invalid:dates")
    if notice.get("source_verified") is not True:
        errors.append("unverified:source")
    if notice.get("dates_verified") is not True:
        errors.append("unverified:dates")
    return sorted(set(errors))


def ready_for_email(notice: dict) -> bool:
    return not validate_notice(notice)
