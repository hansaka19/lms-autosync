from playwright.sync_api import sync_playwright
from lms_autosync import auth, scanner, parsers, matcher

with sync_playwright() as pw:
    browser, context, page = auth.login(pw)

    courses, _ = scanner.scan_dashboard(page)
    events = scanner.get_calendar_events_multi_month(page, months_back=3, months_ahead=4)

    page.goto("https://oulms.ou.ac.lk/course/view.php?id=3436")  # EEI4360
    page.wait_for_load_state("networkidle")
    items = parsers.parse_course_page(page.content(), "EEI4360 Introduction to Artificial Intelligence")
    items = matcher.attach_due_dates(items, events)

    deadlines = [i for i in items if i["is_deadline"]]
    for i in deadlines:
        matcher.classify_deadline(i)

    for label in ["Overdue", "Due Soon", "Upcoming", "Unknown"]:
        group = [i for i in deadlines if i["urgency"] == label]
        if not group:
            continue
        print(f"\n=== {label} ({len(group)}) ===")
        for i in group:
            print(f" - {i['name']}  ->  {i['due_date']}")

    browser.close()