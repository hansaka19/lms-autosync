from playwright.sync_api import sync_playwright
from lms_autosync import auth, scanner

with sync_playwright() as pw:
    browser, context, page = auth.login(pw)
    courses, events = scanner.scan_dashboard(page)

    print(f"{len(courses)} courses found:")
    for c in courses:
        print(" -", c["name"], "->", c["url"])

    print(f"\n{len(events)} calendar events found:")
    for e in events:
        print(" -", e["date"], e["title"], f"({e['event_type']})")

    browser.close()