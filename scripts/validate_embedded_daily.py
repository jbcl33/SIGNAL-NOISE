"""Validate the public Android lesson feed and its magazine links."""
import json
import re
import sys
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
FEED = ROOT / "data" / "embedded-daily.json"
FIELDS = ("title", "summary", "question", "expected", "debug")
TRACKS = {"hardware", "software", "lab"}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())

class AnchorIndex(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id":
                self.ids.add(value)

def link_url(item, context):
    require(isinstance(item, dict) and nonempty(item.get("title")) and nonempty(item.get("url")),
            f"{context}: link needs a title and URL")
    url = urlsplit(item["url"])
    require(url.scheme == "https" and url.netloc and not (url.username or url.password),
            f"{context}: link must use HTTPS")
    return url

def validate(feed_path=FEED):
    require(feed_path.stat().st_size <= 2_000_000, "Feed exceeds the Android download limit")
    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    require(feed.get("schemaVersion") == 1, "Unsupported lesson feed schema")
    revision = feed.get("updatedAt", "")
    require(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", revision), "Use a UTC revision in second precision")
    datetime.strptime(revision, "%Y-%m-%dT%H:%M:%SZ")

    registry = json.loads((ROOT / "data" / "publications.json").read_text(encoding="utf-8"))
    issue_paths = {entry["path"] for entry in registry["publications"]}
    records = feed.get("lessons")
    require(isinstance(records, list) and records, "Include at least one lesson")
    ids, dates = set(), set()
    for item in records:
        day, slug = item.get("date", ""), item.get("id", "")
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug), "Invalid lesson id")
        require(date.fromisoformat(day).isoformat() == day, f"{slug}: use YYYY-MM-DD")
        require(slug not in ids and day not in dates, f"{slug}: duplicate id or date")
        ids.add(slug)
        dates.add(day)
        require(item.get("track") in TRACKS, f"{slug}: invalid track")
        require(all(nonempty(item.get(field)) for field in FIELDS), f"{slug}: missing lesson text")
        for field in ("mechanism", "steps"):
            values = item.get(field)
            require(isinstance(values, list) and len(values) >= 2 and all(nonempty(v) for v in values),
                    f"{slug}: {field} needs at least two entries")
        sources = item.get("sources")
        require(isinstance(sources, list) and sources, f"{slug}: record a primary source")
        for source in sources:
            link_url(source, slug)
        require("calculation" not in item or isinstance(item["calculation"], str), f"{slug}: invalid calculation")
        require("demo" not in item or item["demo"] in {"adc", "pwm"}, f"{slug}: unknown model")
        if "magazine" in item:
            url = link_url(item["magazine"], slug)
            prefix = "/SIGNAL-NOISE/"
            rel = url.path[len(prefix):]
            require(url.netloc == "jbcl33.github.io" and url.path.startswith(prefix) and rel in issue_paths,
                    f"{slug}: magazine URL must point to a registered issue")
            page = ROOT / "static" / rel / "index.html"
            require(page.is_file(), f"{slug}: registered issue is missing")
            if url.fragment:
                index = AnchorIndex()
                index.feed(page.read_text(encoding="utf-8"))
                require(unquote(url.fragment) in index.ids, f"{slug}: missing magazine anchor")
    return len(records)

if __name__ == "__main__":
    try:
        size = validate()
    except (ValueError, TypeError, AttributeError, KeyError, OSError) as exc:
        print(f"Lesson feed validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Validated {size} embedded lessons.")
