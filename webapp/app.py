"""LMS Auto-Sync Web UI — FastAPI backend.

Security notes:
  * Passwords කවදාවත් disk එකට / log වලට යන්නේ නෑ — request → thread → login විතරයි.
  * Job dict එකේ password save වෙන්නේ නෑ.
  * Excel files /tmp එකේ — server restart උනාම මැකෙනවා.
"""
import os
import threading
import time
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from lms_autosync import main as lms_main

app = FastAPI(title="LMS Auto-Sync")

JOBS = {}                    # job_id -> {status, progress, error, summary, file}
JOBS_LOCK = threading.Lock()
SYNC_LOCK = threading.Semaphore(1)   # එක වතාවකට එක sync එකයි (free tier RAM බේරගන්න)
JOB_TTL_SECONDS = 30 * 60
OUTPUT_DIR = "/tmp/lms_jobs"
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


class SyncRequest(BaseModel):
    username: str
    password: str


def _cleanup_old_jobs():
    now = time.time()
    with JOBS_LOCK:
        expired = [jid for jid, j in JOBS.items() if now - j["created"] > JOB_TTL_SECONDS]
        for jid in expired:
            f = JOBS[jid].get("file")
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass
            del JOBS[jid]


def _run_job(job_id, username, password):
    def progress(msg):
        with JOBS_LOCK:
            if job_id in JOBS:
                JOBS[job_id]["progress"] = msg

    acquired = SYNC_LOCK.acquire(timeout=600)
    if not acquired:
        with JOBS_LOCK:
            JOBS[job_id].update(status="error",
                                error="Server busy — ටිකකින් ආයෙ try කරන්න.")
        return
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, f"{job_id}.xlsx")
        result = lms_main.run(username=username, password=password,
                              output_path=out_path, progress_cb=progress)
        summary = {
            "courses": result["courses"],
            "deadlines": [
                {"course": d.get("course"), "name": d.get("name"),
                 "type": d.get("type"), "due_date": d.get("due_date"),
                 "urgency": d.get("urgency"), "url": d.get("url")}
                for d in result["deadlines"]
            ],
            "lab_quiz": [
                {"course": i.get("course"), "name": i.get("name"),
                 "category": i.get("category"), "opened_at": i.get("opened_at"),
                 "due_at_full": i.get("due_at_full"), "url": i.get("url")}
                for i in result["lab_quiz"]
            ],
            "announcements": [
                {"course": a.get("course"), "title": a.get("title"),
                 "author": a.get("author"), "date": a.get("date"), "url": a.get("url")}
                for a in result["announcements"]
            ],
            "counts": {
                "deadlines": len(result["deadlines"]),
                "resources": len(result["resources"]),
                "announcements": len(result["announcements"]),
                "lab_quiz": len(result["lab_quiz"]),
            },
        }
        with JOBS_LOCK:
            JOBS[job_id].update(status="done", summary=summary, file=out_path,
                                progress="සම්පූර්ණයි!")
    except Exception as e:
        msg = str(e)
        if msg.startswith("LOGIN_INVALID"):
            msg = ("Login failed — username/password එක වැරදියි. "
                   f"(LMS එකෙන් ආපු message එක: {msg.split(':', 1)[1].strip()})")
        elif msg.startswith("LOGIN_TIMEOUT"):
            msg = ("Login උනාට LMS එකට redirect උනේ නෑ — LMS site එක slow/down "
                   f"වෙන්න පුළුවන්. ටිකකින් ආයෙ try කරන්න. [{msg}]")
        with JOBS_LOCK:
            JOBS[job_id].update(status="error", error=msg)
    finally:
        SYNC_LOCK.release()


@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(STATIC_DIR, "index.html"), encoding="utf-8") as f:
        return f.read()


@app.post("/api/sync")
def start_sync(req: SyncRequest):
    _cleanup_old_jobs()
    if not req.username.strip() or not req.password:
        raise HTTPException(400, "Username/password දෙකම ඕන.")
    job_id = uuid.uuid4().hex
    with JOBS_LOCK:
        JOBS[job_id] = {"status": "running", "progress": "Queue එකේ...",
                        "error": None, "summary": None, "file": None,
                        "created": time.time()}
    t = threading.Thread(target=_run_job, args=(job_id, req.username.strip(), req.password),
                         daemon=True)
    t.start()
    return {"job_id": job_id}


@app.get("/api/status/{job_id}")
def status(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise HTTPException(404, "Job not found (expire වෙලා ඇති — ආයෙ sync කරන්න).")
        return {"status": job["status"], "progress": job["progress"],
                "error": job["error"], "summary": job["summary"]}


@app.get("/api/download/{job_id}")
def download(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job or job["status"] != "done" or not job["file"] or not os.path.exists(job["file"]):
        raise HTTPException(404, "File not ready.")
    return FileResponse(job["file"], filename="LMS_Schedule.xlsx",
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.get("/api/health")
def health():
    return {"ok": True}
