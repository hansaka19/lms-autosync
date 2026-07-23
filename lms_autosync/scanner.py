from bs4 import BeautifulSoup
from datetime import datetime
from . import config

def scan_dashboard(page):
    """FR-2: courses ටිකයි calendar events ටිකයි දෙකම /my/ page එකෙන්ම
    extract කරනවා - වෙනම navigation එකක් ඕන නෑ."""
    page.goto(config.LMS_BASE_URL + config.LMS_DASHBOARD_PATH)
    courses = _load_courses(page)
    events = _parse_calendar_events(BeautifulSoup(page.content(), "html.parser"))
    return courses, events


def _load_courses(page):
    """Course overview block එකේ cards ටික JavaScript/AJAX වලින් load වෙනවා.
    Render වගේ slow (0.1 CPU) instance එකක networkidle එක මදි වෙන නිසා —
    අඩුම එක card එකක් render වෙනකම් explicit-a wait කරලා, scroll කරලා,
    ඊට පස්සේ parse කරනවා."""
    page.wait_for_load_state("networkidle")
    _wait_and_scroll(page)
    courses = _parse_courses(BeautifulSoup(page.content(), "html.parser"))

    # තවමත් 0 නම්, Moodle 4.x dedicated "My courses" page එකෙනුත් try කරනවා.
    if not courses:
        try:
            page.goto(config.LMS_BASE_URL + "/my/courses.php")
            page.wait_for_load_state("networkidle")
            _wait_and_scroll(page)
            courses = _parse_courses(BeautifulSoup(page.content(), "html.parser"))
        except Exception:
            pass
    return courses


def _wait_and_scroll(page):
    """Course cards render වෙනකම් 30s දක්වා wait කරලා, lazy-load trigger
    කරන්න page එක ටික ටික scroll කරනවා."""
    try:
        page.wait_for_selector(
            "div.course-summaryitem[data-region='course-content'], [data-region='course-content']",
            timeout=30000,
        )
    except Exception:
        pass
    for _ in range(4):
        try:
            page.mouse.wheel(0, 4000)
        except Exception:
            pass
        page.wait_for_timeout(700)


def _parse_courses(soup):
    courses = []
    seen = set()
    cards = soup.select("div.course-summaryitem[data-region='course-content']")
    if not cards:
        # layout/version වෙනස් උනොත් fallback selector එක
        cards = soup.select("[data-region='course-content']")

    for card in cards:
        link_el = (card.select_one("a.aalink.coursename")
                   or card.select_one("a.coursename")
                   or card.select_one("a[href*='/course/view.php']"))
        if not link_el:
            continue

        name_el = (card.select_one(".summary-image .sr-only")
                   or card.select_one(".sr-only")
                   or card.select_one(".coursename .multiline")
                   or card.select_one(".coursename"))
        name = name_el.get_text(strip=True) if name_el else ""
        if not name:
            name = link_el.get_text(strip=True) or link_el.get("aria-label") or "Course"

        url = link_el.get("href")
        if isinstance(url, list):
            url = "".join(url)
        if not url or url in seen:
            continue
        seen.add(url)

        courses.append({
            "id": card.get("data-course-id"),
            "name": name,
            "url": url,
        })
    return courses

def _parse_calendar_events(soup):
    events = []
    for day_cell in soup.select("td.day.hasevent"):
        timestamp = day_cell.get("data-day-timestamp")
        date_str = (datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
                    if timestamp else None)
        for ev in day_cell.select("li[data-region='event-item']"):
            link = ev.select_one("a[data-action='view-event']")
            name_el = ev.select_one(".eventname")
            if not link or not name_el:
                continue
            events.append({
                "title": name_el.get_text(strip=True),
                "event_type": ev.get("data-event-eventtype"),   # due / close / open
                "component": ev.get("data-event-component"),     # mod_assign / mod_quiz / mod_choice
                "url": link["href"],
                "date": date_str,
            })
    return events

def get_calendar_events_multi_month(page, months_back=0, months_ahead=4):
    """Current month + ඉදිරි 'months_ahead' මාස ටිකේම සහ පසුගිය 'months_back' මාස ටිකේම calendar events ටික
    scan කරනවා - assignment due dates බොහෝවිට එක month එකකට වඩා ඈතට
    හෝ පසුගිය කාලයට තියෙන නිසා."""
    page.goto(config.LMS_BASE_URL + config.LMS_DASHBOARD_PATH)
    page.wait_for_load_state("networkidle")
    soup = BeautifulSoup(page.content(), "html.parser")

    # months_back ප්‍රමාණයට ආපස්සට යනවා
    for _ in range(months_back):
        prev_link = soup.select_one("a.arrow_link.previous")
        if not prev_link or not prev_link.get("href"):
            break
        page.goto(prev_link["href"])
        page.wait_for_load_state("networkidle")
        soup = BeautifulSoup(page.content(), "html.parser")

    # දැන් ආරම්භක මාසයේ සිට months_back + months_ahead ප්‍රමාණයට ඉදිරියට යමින් scan කරනවා
    all_events = _parse_calendar_events(soup)
    for _ in range(months_back + months_ahead):
        next_link = soup.select_one("a.arrow_link.next")
        if not next_link or not next_link.get("href"):
            break
        page.goto(next_link["href"])
        page.wait_for_load_state("networkidle")
        soup = BeautifulSoup(page.content(), "html.parser")
        all_events += _parse_calendar_events(soup)

    return all_events