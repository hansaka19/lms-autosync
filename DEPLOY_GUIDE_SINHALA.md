# 🚀 LMS Auto-Sync — Free Publish කරන විදිහ (සිංහලෙන්)

සල්ලි **බින්දුවක්වත්** නැතුව මේක internet එකේ දාන්න පුළුවන් ක්‍රම දෙකක් — **Hugging Face Spaces (recommended)** සහ Render.

---

## Option 1 (Recommended): Hugging Face Spaces — 100% free, credit card ඕන නෑ

HF Spaces free tier: 2 vCPU + 16GB RAM — Playwright/Chromium වලට ඕනතරම් ඇති.
Free URL එකක් ලැබෙනවා: `https://hansaka19-lms-autosync.hf.space` වගේ.

### පියවර

1. **Account:** `huggingface.co` ගිහින් free account එකක් හදාගන්න.
2. **Space එක හදන්න:** උඩ profile → **"New Space"**:
   - Space name: `lms-autosync`
   - License: `mit`
   - SDK: **Docker** ⚠️ (මේක වැරදුනොත් වැඩ කරන්නේ නෑ)
   - Hardware: **CPU basic (free)**
   - Visibility: **Public**
3. **Files upload කරන්න:** Space page එකේ "Files" tab → "Add file" → "Upload files".
   මේ files/folders ටික upload කරන්න:
   - `Dockerfile`
   - `README.md` (උඩ YAML header එක තියෙන එක — `sdk: docker` කියලා)
   - `requirements-web.txt`
   - `lms_autosync/` folder එකේ `.py` files ඔක්කොම
   - `webapp/` folder එක (`app.py`, `__init__.py`, `static/index.html`)

   ⚠️ `venv/`, `logs/`, `output/`, `data/` upload කරන්න **එපා**.
4. Upload උනාම Space එක automatic **build** වෙනවා (මිනිත්තු 5–10ක් යනවා පළවෙනි වතාවේ).
   "Building" → "Running" උනාම ready.
5. URL එක test කරන්න — ඔයාගේ LMS credentials වලින් sync එකක් run කරලා බලන්න.

### Git වලින් upload කරන්න කැමති නම් (upload button එක වෙනුවට)

```bash
cd /Users/hasa/Documents/lms_autosync_project
git init
git add .
git commit -m "LMS Auto-Sync web app"
git remote add hf https://huggingface.co/spaces/USERNAME/lms-autosync
git push hf main
```
(Password එකට HF **access token** එකක් ඕන: hf.co → Settings → Access Tokens → "write" token)

---

## Option 2: Render.com — free tier

1. `render.com` → GitHub account එකෙන් sign up.
2. ඉස්සෙල්ලා project එක GitHub repo එකකට push කරන්න (පහළ බලන්න).
3. Render dashboard → **"New" → "Web Service"** → repo එක select කරන්න.
4. Environment: **Docker** (Dockerfile එක automatic detect වෙනවා).
5. Instance type: **Free**.

⚠️ Render free tier limits:
- RAM 512MB විතරයි — Chromium වලට සමහර වෙලාවට මදි වෙන්න පුළුවන් (crash උනොත් HF Spaces යන්න)
- මිනිත්තු 15ක් idle උනාම sleep වෙනවා — ඊළඟ visit එකේදී start වෙන්න තත්පර 50ක් විතර යනවා

---

## GitHub repo එක හදලා push කරන විදිහ

1. `github.com/new` → Repository name: `lms-autosync` → Public → **Create repository**.
2. Terminal එකේ:

```bash
cd /Users/hasa/Documents/lms_autosync_project
git init
git add .
git commit -m "LMS Auto-Sync — web app + CLI"
git branch -M main
git remote add origin https://github.com/hansaka19/lms-autosync.git
git push -u origin main
```

3. Password එක අහද්දී GitHub **Personal Access Token** එක දෙන්න
   (github.com → Settings → Developer settings → Personal access tokens → `repo` scope).

`.gitignore` එක දාලා තියෙන නිසා `venv/`, `logs/`, passwords වගේ දේවල් push වෙන්නේ නෑ.

---

## 🔒 Security — අනිත් ළමයින්ට කියන්න ඕන දේවල්

- Passwords **server එකේ save වෙන්නේ නෑ** — login එකට විතරක් use වෙලා memory එකෙන් මැකෙනවා.
- ඒත් ඕනම web tool එකකට password එකක් දෙද්දී trust කරන්න ඕන නිසා — code එක open-source, repo link එක share කරන්න.
- HF Spaces / Render දෙකම **HTTPS** automatic දෙනවා — password එක encrypt වෙලා යනවා.
- කවුරුහරි බය නම්, ඒගොල්ලන්ට ඒගොල්ලන්ගේම free HF Space එකක් duplicate කරගන්නත් පුළුවන් ("Duplicate this Space" button එක).

---

## Students ලාට share කරන message එක (copy/paste)

> 📚 **LMS Auto-Sync** — LMS එකේ deadlines, lab tests, quizzes ඔක්කොම auto scan කරලා Excel sheet එකක් හදලා දෙනවා.
> 👉 Link: https://hansaka19-lms-autosync.hf.space
> LMS username + password එක දාලා "Sync කරන්න" click කරන්න විතරයි. Passwords save වෙන්නේ නෑ — code එක open source: https://github.com/hansaka19/lms-autosync

---

## Troubleshooting

| ප්‍රශ්නය | විසඳුම |
|---|---|
| Build fail වෙනවා | README.md එකේ උඩ YAML header එකේ `sdk: docker` තියෙනවාද බලන්න |
| "Server busy" | එක වතාවකට එක student ගේ sync එකයි යන්නේ — ටිකකින් ආයෙ try කරන්න |
| Login failed | LMS password එක වැරදියි, නැත්නම් LMS site එක down |
| Render එකේ crash | RAM මදි — Hugging Face Spaces වලට මාරු වෙන්න |
