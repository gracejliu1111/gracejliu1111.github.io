#!/usr/bin/env python3
"""Turn a Google Calendar iCal feed into projects/caderno/data/classes.json.

Reads the feed URL from the CALENDAR_ICS_URL environment variable (a repo
secret).  Expands recurring events, honours cancellations and one-off
reschedules, and keeps a rolling window: yesterday through +180 days.

Only the fields the app needs are written out, so the committed file never
contains descriptions, attendees or anything else from the calendar.
"""

import json
import os
import pathlib
import sys
from datetime import date, datetime, time, timedelta

import icalendar
import recurring_ical_events
import requests

OUT = pathlib.Path("projects/caderno/data/classes.json")
WINDOW_BACK = 1
WINDOW_FORWARD = 180
# Only keep events whose title matches one of these, case-insensitively.
# Empty list = keep everything on the calendar.
KEYWORDS = [k.strip().lower() for k in os.environ.get("CLASS_KEYWORDS", "").split(",") if k.strip()]


def fail(msg):
    print(f"::error::{msg}", file=sys.stderr)
    sys.exit(1)


def local_parts(value):
    """An ical date-time (or all-day date) -> ('YYYY-MM-DD', 'HH:MM')."""
    if isinstance(value, datetime):
        return value.date().isoformat(), value.strftime("%H:%M")
    if isinstance(value, date):
        return value.isoformat(), ""
    return None, None


def main():
    url = os.environ.get("CALENDAR_ICS_URL", "").strip()
    if not url:
        fail("CALENDAR_ICS_URL is not set. Add it under Settings -> Secrets and variables -> Actions.")
    if not url.startswith(("http://", "https://")):
        fail("CALENDAR_ICS_URL is not a URL. Use the calendar's 'Secret address in iCal format'.")
    if not url.endswith(".ics"):
        print("::warning::That URL does not end in .ics. If this fails to parse, you may have "
              "copied the calendar's public web link instead of its secret iCal address.")

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as exc:
        fail(f"Could not fetch the calendar feed: {exc}")

    try:
        cal = icalendar.Calendar.from_ical(resp.text)
    except Exception as exc:
        fail(f"The feed downloaded but would not parse as iCal: {exc}")

    start = date.today() - timedelta(days=WINDOW_BACK)
    end = date.today() + timedelta(days=WINDOW_FORWARD)
    events = recurring_ical_events.of(cal).between(start, end)

    rows = []
    for ev in events:
        title = str(ev.get("SUMMARY", "") or "").strip()
        if KEYWORDS and not any(k in title.lower() for k in KEYWORDS):
            continue
        if str(ev.get("STATUS", "") or "").upper() == "CANCELLED":
            continue

        d, t0 = local_parts(ev.get("DTSTART").dt)
        if not d:
            continue
        t1 = ""
        if ev.get("DTEND") is not None:
            _, t1 = local_parts(ev.get("DTEND").dt)

        rows.append({
            "uid": f"{str(ev.get('UID', '') or '')[:60]}-{d}-{t0}",
            "date": d,
            "start": t0,
            "end": t1 or "",
            "title": title,
            "where": str(ev.get("LOCATION", "") or "").strip()[:80],
        })

    rows.sort(key=lambda r: (r["date"], r["start"]))

    payload = {
        "updated": date.today().isoformat(),
        "count": len(rows),
        "classes": rows,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    new = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"

    # Rewrite only when the class list itself changed, so an unchanged
    # calendar does not produce a daily commit that only bumps the date.
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
            if old.get("classes") == rows:
                print(f"No change — {len(rows)} classes, already current.")
                return
        except Exception:
            pass

    OUT.write_text(new, encoding="utf-8")
    print(f"Wrote {len(rows)} classes to {OUT}.")


if __name__ == "__main__":
    main()
