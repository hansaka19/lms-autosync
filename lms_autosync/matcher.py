from datetime import date, timedelta

_COMPONENT_TYPE = {
    "mod_assign": "assign",
    "mod_quiz": "quiz",
    "mod_choice": "choice",
}


def deadlines_from_calendar(events):
    """Course scan එක fail උනොත් (Found 0 courses), calendar events වලින්ම
    deadline list එකක් හදනවා — due/close events විතරක් අරගෙන. මේක safety-net
    එකක්: courses හම්බුණේ නැති උනත් අඩුම deadlines ටික user ට පේනවා."""
    deadlines = []
    seen = set()
    for ev in events:
        if ev.get("event_type") not in ("due", "close"):
            continue
        key = (ev.get("url"), ev.get("date"))
        if key in seen:
            continue
        seen.add(key)
        comp = ev.get("component") or ""
        item = {
            "course": "(from calendar)",
            "name": ev.get("title") or "Untitled",
            "type": _COMPONENT_TYPE.get(comp, comp.replace("mod_", "") or "event"),
            "url": ev.get("url"),
            "due_date": ev.get("date"),
            "is_deadline": True,
            "is_resource": False,
        }
        classify_deadline(item)
        deadlines.append(item)
    return deadlines


def attach_due_dates(course_items, calendar_events):
    """Calendar event URLs (mod/assign/view.php?id=... වගේ) course item
    URLs ටිකට match කරලා, deadline items වලට exact due date එක දානවා."""
    events_by_url = {}
    for ev in calendar_events:
        events_by_url.setdefault(ev["url"], []).append(ev)

    for item in course_items:
        if not item["is_deadline"]:
            continue
        matches = events_by_url.get(item["url"], [])
        due_ev = next((e for e in matches if e["event_type"] in ("due", "close")), None)
        item["due_date"] = due_ev["date"] if due_ev else None
        item["due_event_type"] = due_ev["event_type"] if due_ev else None

    return course_items


def classify_deadline(item, today=None, due_soon_days=7):
    """Due date එක අද දවසට compare කරලා urgency එක තීරණය කරනවා:
    Overdue (ඉවර වෙලා) / Due Soon (ළඟදීම) / Upcoming (ඉස්සරහට) / Unknown."""
    today = today or date.today()

    if not item.get("due_date"):
        item["urgency"] = "Unknown"
        return item

    due = date.fromisoformat(item["due_date"])
    if due < today:
        item["urgency"] = "Overdue"
    elif due <= today + timedelta(days=due_soon_days):
        item["urgency"] = "Due Soon"
    else:
        item["urgency"] = "Upcoming"
    return item