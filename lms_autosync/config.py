import os

LMS_BASE_URL = os.environ.get("LMS_BASE_URL", "https://oulms.ou.ac.lk")
LMS_LOGIN_PATH = "/login/index.php"
LMS_DASHBOARD_PATH = "/my/"
LMS_CALENDAR_PATH = "/calendar/view.php?view=upcoming"

OUTPUT_XLSX = "output/LMS_Schedule.xlsx"
STATE_FILE = "data/state.json"
LOG_FILE = "logs/run.log"

DUE_SOON_DAYS = 7
# Debug කරන්න browser එක පෙනෙන්න ඕන නම්: HEADLESS=0 uvicorn ...
HEADLESS = os.environ.get("HEADLESS", "1") != "0"