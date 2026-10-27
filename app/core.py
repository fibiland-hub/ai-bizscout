"""Deterministic announcement processing. Never fabricate official facts."""
import csv
import hashlib
import io
import re
from datetime import date, datetime
from urllib.parse import urlparse

FIELDS = ("id", "title", "agency", "source_url", "start_date", "end_date")
KEYWORDS = ("해양", "수산", "선박", "항만", "해운", "AI", "인공지능", "데이터", "R&D", "연구개발")


def validate_notice(n):
    issues = []
    for key in FIELDS:
        if not str(n.get(key) or "").strip():
            issues.append("필수값 누락: " + key)
    url = str(n.get("source_url") or "")
    p = urlparse(url)
    if p.scheme != "https" or not p.netloc or p.username or p.password:
        issues.append("공식 HTTPS 링크 확인 필요")
    try:
        start = date.fromisoformat(str(n["start_date"]))
        end = date.fromisoformat(str(n["end_date"]))
        if start > end:
            issues.append("접수 시작일이 마감일보다 늦음")
    except (KeyError, ValueError, TypeError):
        issues.append("날짜 형식 오류 (YYYY-MM-DD)")
    if n.get("source_verified") is not True:
        issues.append("공식 출처 미검증")
    if n.get("dates_verified") is not True:
        issues.append("접수기간 미검증")
    if n.get("attachments_reviewed") is not True:
        issues.append("첨부파일 미검토")
    return issues


def ready_to_send(n):
    return not validate_notice(n)


def relevance(n, interests):
    text = (str(n.get("title") or "") + " " + str(n.get("description") or "")).lower()
    tokens = [x.strip().lower() for x in interests.split(",") if x.strip()]
    if not tokens:
        return 0
    return round(100 * sum(token in text for token in tokens) / len(tokens))


def normalized_id(n):
    raw = (str(n.get("agency", "")) + "|" + str(n.get("source_url", ""))).strip()
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def parse_csv(data):
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV 헤더가 없습니다.")
    required = {"title", "agency", "source_url", "start_date", "end_date"}
    missing = required - set(reader.fieldnames)
    if missing:
        raise ValueError("필수 열 누락: " + ", ".join(sorted(missing)))
    rows = []
    for row in reader:
        row["id"] = row.get("id") or normalized_id(row)
        for field in ("source_verified", "dates_verified", "attachments_reviewed"):
            row[field] = str(row.get(field, "")).strip().lower() in ("true", "1", "yes")
        rows.append(row)
    return rows


def make_email(n):
    if not ready_to_send(n):
        raise ValueError("검증되지 않은 공고는 이메일 초안을 만들 수 없습니다.")
    fields = [
        ("공고명", n["title"]), ("기관", n["agency"]),
        ("접수 시작", n["start_date"]), ("접수 마감", n["end_date"]),
        ("지원금", n.get("funding") or "원문 확인"),
        ("지원 대상", n.get("eligibility") or "원문 확인"),
        ("제출 서류", n.get("documents") or "원문 확인"),
        ("공고 원문", n["source_url"]),
    ]
    return "[AI BizScout] " + n["title"], "\n".join(f"{k}: {v}" for k, v in fields) + "\n\n※ 신청 자격은 최종적으로 공고 원문과 대조하세요."
