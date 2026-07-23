from playwright.sync_api import sync_playwright
from . import auth, scanner, parsers, matcher, excel_writer
from .logger import get_logger


def run(username=None, password=None, output_path="output/LMS_Schedule.xlsx",
        progress_cb=None):
    """LMS sync එක run කරනවා.

    username/password නොදුන්නොත් local keyring vault එකෙන් ගන්නවා (CLI mode).
    progress_cb(msg) දුන්නොත් web UI එකට status updates යවනවා.
    Return: dict — deadlines, resources, announcements, lab_quiz, courses.
    """
    log = get_logger()
    log.info("=== LMS Auto-Sync run started ===")

    def progress(msg):
        if progress_cb:
            progress_cb(msg)

    all_deadlines = []
    all_resources = []
    all_announcements = []
    all_lab_quiz = []

    with sync_playwright() as pw:
        progress("LMS එකට login වෙනවා...")
        browser, context, page = auth.login(pw, username, password)
        log.info("Login OK")
        progress("Login OK — courses හොයනවා...")

        courses, _ = scanner.scan_dashboard(page)
        log.info(f"Found {len(courses)} courses")

        progress(f"Courses {len(courses)}ක් හම්බුණා — calendar එක scan කරනවා...")
        events = scanner.get_calendar_events_multi_month(page, months_back=3, months_ahead=4)
        log.info(f"Found {len(events)} calendar events (multi-month)")

        # Safety-net: dashboard එකෙන් courses හම්බුණේ නැත්නම් (slow instance එකක
        # course cards render වෙන්නෙ නැති වෙන්න පුළුවන්), calendar events වලින්ම
        # deadlines හදනවා — user ට හිස් result එකක් යන්නේ නෑ.
        if not courses:
            log.warning("Found 0 courses — falling back to calendar events for deadlines")
            all_deadlines = matcher.deadlines_from_calendar(events)
            for d in all_deadlines:
                if parsers.is_lab_test_or_quiz(d):
                    d["category"] = parsers.categorize_lab_quiz(d)
                    d["due_at_full"] = d.get("due_date")
                    all_lab_quiz.append(d)
            progress(f"Courses හම්බුණේ නෑ — calendar එකෙන් deadlines {len(all_deadlines)}ක් හදනවා...")

        for idx, course in enumerate(courses, 1):
            progress(f"Course {idx}/{len(courses)}: {course['name']} scan කරනවා...")
            try:
                page.goto(course["url"], wait_until="domcontentloaded", timeout=60000)
                items = parsers.parse_course_page(page.content(), course["name"])
                items = matcher.attach_due_dates(items, events)

                deadlines = [i for i in items if i["is_deadline"]]
                for d in deadlines:
                    matcher.classify_deadline(d)
                resources = [i for i in items if i["is_resource"]]

                all_deadlines += deadlines
                all_resources += resources

                # Announcements
                ann_forum = parsers.find_announcements_forum(items)
                if ann_forum and ann_forum.get("url"):
                    page.goto(ann_forum["url"], wait_until="domcontentloaded", timeout=60000)
                    posts = parsers.parse_announcements(page.content(), course["name"])
                    all_announcements += posts

                # Lab Tests, TMA, Mini Project & Quizzes - exact Opened/Due date+time
                lab_quiz = [d for d in deadlines if parsers.is_lab_test_or_quiz(d)]
                for item in lab_quiz:
                    if not item.get("url"):
                        continue
                    page.goto(item["url"], wait_until="domcontentloaded", timeout=60000)
                    dates = parsers.parse_activity_dates(page.content()) or {}
                    item["opened_at"] = dates.get("Opened") or dates.get("Opens")
                    item["due_at_full"] = dates.get("Due") or dates.get("Closed") or dates.get("Closes")
                    item["category"] = parsers.categorize_lab_quiz(item)
                all_lab_quiz += lab_quiz

                log.info(f"  {course['name']}: {len(deadlines)} deadlines, "
                         f"{len(resources)} resources, {len(lab_quiz)} lab/quiz/tma items")
            except Exception as e:
                log.warning(f"  Skipped '{course['name']}' due to error: {e}")
                continue

        browser.close()

    progress("Excel file එක හදනවා...")
    excel_writer.write_workbook(all_deadlines, all_resources, all_announcements, all_lab_quiz,
                                output_path=output_path)
    log.info(f"Total: {len(all_deadlines)} deadlines, {len(all_resources)} resources, "
             f"{len(all_announcements)} announcements, {len(all_lab_quiz)} lab/quiz/tma items "
             f"across {len(courses)} courses")
    log.info("=== LMS Auto-Sync run finished ===")

    return {
        "deadlines": all_deadlines,
        "resources": all_resources,
        "announcements": all_announcements,
        "lab_quiz": all_lab_quiz,
        "courses": [c["name"] for c in courses],
        "output_path": output_path,
    }


if __name__ == "__main__":
    run()