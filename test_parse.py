from playwright.sync_api import sync_playwright
from lms_autosync import auth, scanner, parsers

with sync_playwright() as pw:
    browser, context, page = auth.login(pw)

    page.goto("https://oulms.ou.ac.lk/course/view.php?id=3436")  # EEI4360
    page.wait_for_load_state("networkidle")

    items = parsers.parse_course_page(page.content(), "EEI4360 Introduction to Artificial Intelligence")

    print(f"{len(items)} activities found:\n")
    for i in items:
        tag = "DEADLINE" if i["is_deadline"] else "RESOURCE" if i["is_resource"] else "ZOOM" if i["is_zoom"] else i["type"]
        print(f" [{tag:8}] {i['name']}")

    browser.close()