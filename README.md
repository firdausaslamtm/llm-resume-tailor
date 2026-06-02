### Update.gitignore

```bash
cat >.gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.pyd
*.pyo
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# Environment
.env
.envrc
*.env

# Project outputs
output/
*.md
!README.md
!resume_base.md

# OS
.DS_Store
.AppleDouble
.LSOverride
Thumbs.db
ehthumbs.db
Desktop.ini

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
```

### Update README.md

```bash
cat > README.md << 'EOF'
# LLM Resume Tailor

Tailor your resume and cover letter to any job description using a local LLM via Ollama. Private, truthful, ATS-friendly.

## Why

Generic resumes get filtered out. This tool rewrites your experience to match keywords from the JD while staying truthful to your actual experience.

## Features

- **Local-first**: Uses Ollama, no data leaves your machine
- **Recruiter-grade prompts**: ATS optimization + truth guardrails
- **Auto-setup**: Prompts auto-create on first run
- **Three outputs**: Tailored resume, cover letter, keyword analysis
- **Safe filenames**: Sanitized output names
- **No API keys needed**

## Quick Start

```bash
git clone <your-repo>
cd llm-resume-tailor
python3 -m venv.venv
source.venv/bin/activate
pip install -r requirements.txt

# Start Ollama
ollama serve
ollama pull llama3.2

# Run
python tailor.py --job examples/job_description.txt --cover-letter --analyze
```

## Usage

### Basic
```bash
python tailor.py --job examples/job_description.txt
```

### Full suite
```bash
python tailor.py --job examples/job_description.txt --cover-letter --analyze --model llama3.2
```

### Custom paths
```bash
python tailor.py --resume my_resume.md --job jds/company.txt --output my_outputs/
```

Output files:
- `output/tailored_resume_YYYY-MM-DD_Company.md`
- `output/cover_letter_YYYY-MM-DD_Company.md`
- `output/keywords_YYYY-MM-DD_Company.md`

## How It Works

1. **Extract** keywords, skills, requirements from JD
2. **Map** to your real experience
3. **Rewrite** bullets with JD language, keep facts intact
4. **Reorder** skills by relevance
5. **Generate** cover letter with top 3 matches

Prompts enforce: no fabrication, keep dates/titles, quantify where possible.

## Project Structure

```
llm-resume-tailor/
├── resume_base.md # Your master resume
├── tailor.py # CLI with auto-prompt setup
├── prompts/ # Auto-created on first run
│ ├── tailor_resume.txt
│ ├── cover_letter.txt
│ └── extract_keywords.txt
├── examples/
│ └── job_description.txt
└── output/ # Generated files, gitignored
```

## Prompts

Prompts are created automatically if missing. Edit `prompts/` to customize tone.

- `tailor_resume.txt`: Senior recruiter + ATS specialist
- `cover_letter.txt`: High-converting, 200-280 words
- `extract_keywords.txt`: ATS keyword table

## Requirements

- Python 3.9+
- Ollama installed
- `requests`

## Tips

- Keep `resume_base.md` comprehensive. The tool will trim.
- Use real metrics in base resume, tool will surface them.
- Run `--analyze` first to see keyword gaps.