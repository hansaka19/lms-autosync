# Playwright + Python + Chromium පෙර-install කරපු official image එක
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

COPY lms_autosync/ ./lms_autosync/
COPY webapp/ ./webapp/

# Logs/output dirs (container එක ඇතුළේ)
RUN mkdir -p logs output /tmp/lms_jobs

# Hugging Face Spaces default port = 7860; Render 'PORT' env එකක් දෙනවා
ENV PORT=7860
EXPOSE 7860

CMD uvicorn webapp.app:app --host 0.0.0.0 --port ${PORT}
