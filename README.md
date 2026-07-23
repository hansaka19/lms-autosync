---
title: OUSL LMS Auto-Sync
emoji: 📚
colorFrom: blue
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

# 📚 OUSL LMS Auto-Sync

OUSL LMS (Moodle) එකේ තියෙන **deadlines, lab tests, quizzes, TMAs, announcements** ඔක්කොම
automatic scan කරලා ලස්සන **Excel schedule** එකක් හදලා දෙන free open-source tool එකක්.

## Students ලාට — use කරන විදිහ

1. Web app එකට යන්න (link එක class group එකේ තියෙනවා)
2. ඔයාගේ LMS username (S-number) + password එක දාන්න
3. **Sync කරන්න** click කරලා මිනිත්තු 2–4ක් ඉන්න
4. Deadlines table එක බලන්න + Excel file එක download කරන්න

## 🔒 Privacy

- Password එක **server එකේ save වෙන්නේ නෑ** — LMS login එකට විතරක් memory එකේ use වෙනවා
- Logs වලට passwords යන්නේ නෑ
- Code එක සම්පූර්ණයෙන්ම open-source — ඕන කෙනෙක්ට බලලා verify කරන්න පුළුවන්

## Developers ලාට — local run

```bash
pip install -r requirements-web.txt
playwright install chromium
uvicorn webapp.app:app --reload
# http://localhost:8000
```

CLI mode (Excel එක local machine එකේම හදන්න):

```bash
pip install -r requirements.txt
playwright install chromium
python -m lms_autosync.vault    # credentials keychain එකේ save කරන්න
python -m lms_autosync.main
```

## Tech stack

Python · Playwright · FastAPI · BeautifulSoup · openpyxl · HTML/CSS/JS (vanilla)

Made with ❤️ for OUSL students by [hansaka19](https://github.com/hansaka19)
