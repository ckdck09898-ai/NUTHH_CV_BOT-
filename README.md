# NUTHH’ CV Telegram Bot

Python Telegram bot for creating CVs with 100 selectable theme presets, template preview images, PDF/DOCX export, profile photo support, free rule-based writing assistance, cover letters, application emails, ATS completeness checks, and simple job-description keyword matching.

## Important honest limitations
- No paid AI API is used. The writing helper is template/rule-based, not a generative AI model like ChatGPT.
- The 100 templates are 100 selectable combinations of category, accent color, and layout preset. They share a clean document structure; they are not 100 individually hand-designed page compositions yet.
- ATS and job matching are simple estimates, not a guarantee of selection.
- Khmer PDF output requires a compatible Khmer TTF font. Put `NotoSansKhmer-Regular.ttf` into `fonts/`. If omitted, the PDF generator falls back to Helvetica, which may not render Khmer correctly. DOCX usually handles Khmer better if a Khmer font is installed on the viewer's device.
- Local SQLite data persists only while the host keeps the project folder. Back up `nuthh_cv.sqlite3`.

## File structure
```text
NUTHH_CV_BOT/
├── bot.py
├── cv_builder.py
├── database.py
├── templates.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── fonts/                 # Add NotoSansKhmer-Regular.ttf here
├── previews/              # Preview PNGs are generated automatically
└── generated_cvs/         # PDFs, DOCX and uploaded profile photos
```

## Install on Windows 10/11
1. Install Python 3.11+ from https://www.python.org/downloads/ and tick **Add Python to PATH**.
2. Open the folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use `cmd` terminal and run `.venv\\Scripts\\activate.bat`.
5. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
6. Create a Telegram bot using https://t.me/BotFather and `/newbot`.
7. Copy `.env.example` to `.env`, then set `BOT_TOKEN=your_token`. Keep this token secret.
8. Optional: set `ADMIN_ID` to your Telegram numeric user ID for `/admin` statistics.
9. Start the bot:
   ```powershell
   python bot.py
   ```
10. Open your bot in Telegram and send `/start`.

## Usage
- Create CV → category → choose a template → preview → Use this template → fill in fields → send photo or SKIP → export PDF or DOCX.
- My CV shows the saved profile and lets you export the saved CV.
- Cover Letter and Application Email create rule-based drafts using the saved profile.
- ATS / Job Match checks profile completeness and optional keyword overlap with a job description.
- Language supports Khmer, English, Chinese, and French for interface labels and generated writing drafts. User-entered CV fields are not automatically translated.
- `/cancel` cancels the current flow; `/templates` opens the template gallery; `/mycv` shows the saved CV; `/admin` is restricted to configured `ADMIN_ID`.

## Free hosting notes
The bot uses long polling. It needs a host that keeps a Python process running. Free hosting plans may sleep, restrict long-running workers, or delete local files; check the host's current terms before deploying. For durable multi-user hosting, use persistent storage or a managed database and back up uploads.
