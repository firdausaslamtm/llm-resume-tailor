#!/usr/bin/env python3
"""
LLM Resume Tailor - Tailor resume to job description using local Ollama
"""
import argparse
import re
from datetime import datetime
from pathlib import Path
import requests

DEFAULT_MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/generate"

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = BASE_DIR / "output"

DEFAULT_PROMPTS = {
    "tailor_resume.txt": """You are a senior technical recruiter and ATS optimization specialist.

GOAL
Transform the BASE RESUME into a highly targeted resume for the JOB DESCRIPTION, maximizing interview conversion while staying 100% truthful.

STRICT RULES
1. TRUTH ONLY: Never invent jobs, dates, companies, degrees, or skills.
2. KEEP IDENTITY: Name, contact, education, job titles, companies, dates must stay exactly as in base resume.
3. ATS FIRST: Mirror exact keywords from JD where candidate truly has them.
4. IMPACT: Rewrite bullets using Action + Context + Result. Use metrics only if present.
5. RELEVANCE: Put most relevant experience first. Reorder skills by JD priority.

OUTPUT: Clean Markdown resume only.

BASE RESUME:
{resume}

JOB DESCRIPTION:
{job_description}
""",
    "cover_letter.txt": """You are a senior recruiter writing a high-converting cover letter.

RULES
1. TRUTH ONLY
2. 3-4 paragraphs, 200-280 words
3. Para1: Role + company + top fit hook
4. Para2: Top 2-3 achievements mapping to JD
5. Para3: Why this company
6. Close with name

BASE RESUME:
{resume}

JOB DESCRIPTION:
{job_description}
""",
    "extract_keywords.txt": """You are an ATS analyst.

Extract from JOB DESCRIPTION:
1. Role title
2. Top 10 hard skills/tools
3. Top 5 responsibilities
4. Must-have qualifications
5. Nice-to-haves
6. Suggested resume keywords

Return as Markdown table: Category | Items

JOB DESCRIPTION:
{job_description}
"""
}

def ensure_prompts():
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in DEFAULT_PROMPTS.items():
        p = PROMPTS_DIR / name
        if not p.exists():
            p.write_text(content, encoding='utf-8')

def load_file(path):
    p = Path(path)
    if not p.is_absolute():
        p = BASE_DIR / p
    return p.read_text(encoding='utf-8')

def save_file(path, content):
    p = Path(path)
    if not p.is_absolute():
        p = BASE_DIR / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')

def query_ollama(prompt, model=DEFAULT_MODEL):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3}
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=180)
        resp.raise_for_status()
        return resp.json()["response"].strip()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot connect to Ollama. Run 'ollama serve' first.")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}")

def tailor_resume(resume, job_desc, model):
    prompt_template = load_file(PROMPTS_DIR / "tailor_resume.txt")
    prompt = prompt_template.format(resume=resume, job_description=job_desc)
    return query_ollama(prompt, model)

def write_cover_letter(resume, job_desc, model):
    prompt_template = load_file(PROMPTS_DIR / "cover_letter.txt")
    prompt = prompt_template.format(resume=resume, job_description=job_desc)
    return query_ollama(prompt, model)

def analyze_keywords(job_desc, model):
    prompt_template = load_file(PROMPTS_DIR / "extract_keywords.txt")
    prompt = prompt_template.format(job_description=job_desc)
    return query_ollama(prompt, model)

def sanitize_filename(s):
    s = s.strip().split("\n")[0]
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'\s+', '_', s)
    return s[:50]

def main():
    parser = argparse.ArgumentParser(description="Tailor resume to job description")
    parser.add_argument("--resume", default="resume_base.md")
    parser.add_argument("--job", required=True)
    parser.add_argument("--output", default=str(OUTPUT_DIR))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--cover-letter", action="store_true")
    parser.add_argument("--analyze", action="store_true", help="Generate keyword analysis")
    args = parser.parse_args()

    ensure_prompts()

    resume = load_file(args.resume)
    job_desc = load_file(args.job)

    company = sanitize_filename(job_desc)
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.analyze:
        print("Analyzing keywords...")
        analysis = analyze_keywords(job_desc, args.model)
        analysis_path = out_dir / f"keywords_{date_str}_{company}.md"
        save_file(analysis_path, analysis)
        print(f"✓ Analysis saved to {analysis_path}")

    print("Tailoring resume...")
    tailored = tailor_resume(resume, job_desc, args.model)
    resume_path = out_dir / f"tailored_resume_{date_str}_{company}.md"
    save_file(resume_path, tailored)
    print(f"✓ Resume saved to {resume_path}")

    if args.cover_letter:
        print("Writing cover letter...")
        cover = write_cover_letter(resume, job_desc, args.model)
        cover_path = out_dir / f"cover_letter_{date_str}_{company}.md"
        save_file(cover_path, cover)
        print(f"✓ Cover letter saved to {cover_path}")

if __name__ == "__main__":
    main()
