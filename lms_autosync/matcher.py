from datetime import date, timedelta

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