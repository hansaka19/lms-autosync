from datetime import datetime
from bs4 import BeautifulSoup

DEADLINE_TYPES = {"assign", "quiz", "choice"}
RESOURCE_TYPES = {"resource", "url", "page", "folder"}


def parse_course_page(html, course_name):
    """FR-4/5/6: course page එකේ තියෙන හැම activity එකක්ම classify කරලා
    එකම flat list එකක් return කරනවා."""
    soup = BeautifulSoup(html, "html.parser")
    items = []

    for li in soup.select("li.activity.activity-wrapper"):
        classes = li.get("class")
        if isinstance(classes, str):
            classes = [classes]
        elif classes is None:
            classes = []
        modtype = next((c.replace("modtype_", "") for c in classes if c.startswith("modtype_")), "other")

        item_div = li.select_one(".activity-item")
        name = item_div.get("data-activityname") if item_div else None
        if not name:
            continue

        if isinstance(name, list):
            name = " ".join(name)

        link_el = li.select_one("a.aalink")
        url = link_el.get("href") if link_el else None
        if isinstance(url, list):
            url = "".join(url)

        items.append({
            "course": course_name,
            "name": name,
            "type": modtype,
            "url": url,
            "is_deadline": modtype in DEADLINE_TYPES,
            "is_resource": modtype in RESOURCE_TYPES,
            "is_zoom": bool(url) and "zoom" in (name + (url or "")).lower(),
        })

    return items


def find_announcements_forum(items):
    """course items ටිකෙන් 'Announcements' forum එක හොයාගන්නවා."""
    return next((i for i in items if i["type"] == "forum" and "announce" in i["name"].lower()), None)


def parse_announcements(html, course_name):
    """Announcements forum page එකේ discussion list එක parse කරනවා."""
    soup = BeautifulSoup(html, "html.parser")
    posts = []
    for row in soup.select("tr.discussion"):
        title_el = row.select_one("th.topic a")
        author_el = row.select_one("td.author .text-truncate")
        time_el = row.select_one("td.author time")
        if not title_el:
            continue
        ts = time_el.get("data-timestamp") if time_el else None
        if isinstance(ts, str):
            date_str = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
        else:
            date_str = time_el.get_text(strip=True) if time_el else None
        posts.append({
            "course": course_name,
            "title": title_el.get_text(strip=True),
            "author": author_el.get_text(strip=True) if author_el else None,
            "date": date_str,
            "url": title_el["href"],
        })
    return posts


def is_lab_test_or_quiz(item):
    """Lab Test, TMA, Mini Project (assignments) සහ Online Quiz items ටික
    identify කරනවා - මේවට exact Opened/Due date+time ගන්නවා."""
    name_lower = item["name"].lower()
    if item["type"] == "quiz":
        return True
    keywords = ("lab", "tma", "mini project")
    if item["type"] in ("assign", "choice") and any(k in name_lower for k in keywords):
        return True
    return False


def categorize_lab_quiz(item):
    """Lab Test / Online Quiz / Mini Project / TMA කියලා category එක තීරණය කරනවා."""
    name_lower = item["name"].lower()
    if item["type"] == "quiz":
        return "Online Quiz"
    if "mini project" in name_lower:
        return "Mini Project"
    if "tma" in name_lower:
        return "TMA"
    if "lab" in name_lower:
        return "Lab Test"
    return "Other"




def parse_activity_dates(html):
    """assignment/quiz activity එකේම page එකේ 'Opened:'/'Due:'/'Closed:'
    කියලා පේන full date+time කොටස extract කරනවා."""
    soup = BeautifulSoup(html, "html.parser")
    dates_block = soup.select_one('div[data-region="activity-dates"]')
    if not dates_block:
        return {}

    result = {}
    for div in dates_block.find_all("div", recursive=False):
        strong = div.find("strong")
        if not strong:
            continue
        label = strong.get_text(strip=True).rstrip(":")
        val = div.get_text().replace(strong.get_text(), "", 1).strip()
        result[label] = val

    return result