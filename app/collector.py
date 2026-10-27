"""Opt-in RSS collection. Each feed must be an explicitly approved official source."""
from urllib.parse import urlparse
import feedparser
import requests


def collect_rss(url, max_items=30):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("HTTPS RSS 주소만 허용합니다.")
    response = requests.get(url, timeout=15, headers={"User-Agent": "AIBizScout/0.1"})
    response.raise_for_status()
    if len(response.content) > 3_000_000:
        raise ValueError("RSS 파일이 너무 큽니다.")
    feed = feedparser.parse(response.content)
    if feed.bozo and not feed.entries:
        raise ValueError("RSS 형식을 해석할 수 없습니다.")
    notices = []
    for entry in feed.entries[:max_items]:
        link = entry.get("link", "")
        if urlparse(link).scheme != "https":
            continue
        notices.append({
            "title": entry.get("title", "제목 없음"),
            "agency": feed.feed.get("title", parsed.netloc),
            "source_url": link,
            "description": entry.get("summary", ""),
            "start_date": "",
            "end_date": "",
            "source_verified": False,
            "dates_verified": False,
            "attachments_reviewed": False,
        })
    return notices
