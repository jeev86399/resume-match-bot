# ResumeMatch AI

A Telegram-only Job Description + Multiple Resume Analyzer Bot.

## Overview
ResumeMatch AI allows you to upload a Job Description (JD) and one or more candidate resumes directly in Telegram. It parses the documents, structuring them via LLM, and calculates a match score along with a detailed report (matched skills, missing skills, suggestions, and corrections). Everything happens entirely within Telegram.

## Features
- **Telegram Only**: No external dashboards or web interfaces.
- **Multiple File Support**: Upload PDFs, DOCX, and TXT files.
- **Smart Parsing**: Robust text extraction from documents.
- **LLM Structured Analysis**: AI identifies candidate's skills and maps them accurately against the JD.
- **Fair Scoring Formula**: Python-calculated score based on weights for skills, experience, keywords, education, and projects.
- **Actionable Feedback**: Generates max 5 suggestions and max 3 core corrections for the resume.
- **Curated Resources**: Provides direct learning links for missing skills.

## Architecture
- **Language**: Python 3.11+
- **Bot Framework**: `python-telegram-bot` v20+
- **Web Server**: `FastAPI` (for `/health` endpoint)
- **Document Parsers**: `PyMuPDF` (fitz) for PDF, `python-docx` for DOCX
- **LLM Integration**: `OpenAI` API (via `AsyncOpenAI`)
- **Data Persistence**: `SQLite` (lightweight per-user session isolation)
- **Validation**: `Pydantic`

## Setup

### Prerequisites
- Python 3.11+
- A Telegram Bot Token from BotFather
- An OpenAI API Key

### Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   # macOS/Linux
   source venv/bin/activate
   # Windows
   # venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in your keys:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   LLM_MODEL=gpt-4o-mini
   ```

### Telegram BotFather Setup
1. Open Telegram.
2. Search for `@BotFather`.
3. Send `/newbot` and follow instructions.
4. Copy the HTTP API Token provided.
5. Paste it into your `.env` file as `TELEGRAM_BOT_TOKEN`.

### How to Run

Start the bot and the FastAPI health server:
```bash
python run.py
```

Check the health endpoint (optional):
```bash
curl http://localhost:8000/health
```

## Commands
* `/start` - Start a new session.
* `/analyze` - Run analysis on the uploaded JD and resumes.
* `/status` - View current session details (JD status, resume count).
* `/report [number]` - View a detailed report for a specific resume (e.g., `/report 1`).
* `/report all` - View reports for all resumes sequentially.
* `/reset` - Clear your session data and start over.

## Security Notes
* Never hardcode API keys or Bot Tokens in your source code.
* `uploads/` and `.db` files are ignored by git to protect data.
* Session data is strictly partitioned per Telegram User ID.
