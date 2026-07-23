from bs4 import BeautifulSoup
from datetime import datetime
from . import config

def scan_dashboard(page):
    """FR-2: courses ටිකයි calendar events ටිකයි දෙකම /my/ page එකෙන්ම
    extract කරනවා - වෙනම navigation එකක් ඕන නෑ."""
    page.goto(config.LMS_BASE_URL + config.LMS_DASHBOARD_PATH)
    page.wait_for_load_state("networkidle")
    soup = BeautifulSoup(page.content(), "html.parser")

    courses = _parse_courses(soup)
    events = _parse_calendar_events(soup)
    return courses, events

def _parse_courses(soup):
    courses = []
    for card in soup.select("div.course-summaryitem[data-region='course-content']"):
        name_el = card.select_one(".summary-image .sr-only")
        link_el = card.select_one("a.aalink.coursename")
        if not name_el or not link_el:
            continue
        courses.append({
            "id": card.get("data-course-id"),
            "name": name_el.get_text(strip=True),
            "url": link_el["href"],
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