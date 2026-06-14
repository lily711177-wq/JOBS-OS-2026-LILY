#!/usr/bin/env python3
"""
FETCH ENGINE — LILY EDITION (JOBS OS 2026)
Student Job Search Engine: Indeed + HiringCafe + WorkBC + campus portals
Target: Tutor, admin assistant, receptionist, library assistant, retail, student services
Location: Burnaby (SFU area) / Surrey (KPU) / transit-accessible Vancouver

Usage:
  python3 33_FETCH_ENGINE.py              # Full fetch: generate all search URLs
  python3 33_FETCH_ENGINE.py --easy       # Tutor/admin roles only (no retail/food)
  python3 33_FETCH_ENGINE.py --score      # Score a pasted JD
"""

import requests
import re
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SYSTEM_ROOT = Path("/mnt/c/Users/muska/JOBS-OS-2026-LILY")
CORPUS_FILE = SYSTEM_ROOT / "01_MASTER_CORPUS.md"
TRACKING_FILE = SYSTEM_ROOT / "TRACKING.md"
JOBS_DB = SYSTEM_ROOT / "data" / "jobs.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TIMEOUT = 15

STUDENT_ROLES = [
    "tutor", "teaching assistant", "peer tutor", "academic coach",
    "administrative assistant", "office assistant", "receptionist", "front desk",
    "library assistant", "student services", "program assistant",
    "customer service", "retail associate", "sales associate",
    "campus ambassador", "research assistant", "data entry",
    "community assistant", "youth worker", "settlement assistant",
]

EASY_ROLES = [
    "tutor", "teaching assistant", "peer tutor", "academic coach",
    "administrative assistant", "receptionist", "front desk",
    "library assistant", "office assistant", "program assistant",
    "student services", "data entry",
]

PIPES = {
    "Tutoring": {
        "label": "📚 TUTORING & EDUCATION",
        "description": "Tutor, TA, peer tutor, academic coach",
        "queries": [
            "tutor Burnaby",
            "tutor Vancouver part-time",
            "teaching assistant Burnaby",
            "peer tutor Surrey",
            "math tutor Burnaby",
            "academic coach Vancouver",
            "tutor SFU",
            "tutor KPU",
        ],
        "companies": [
            ("KPU Learning Centre", "https://www.kpu.ca/learningcentres"),
            ("SFU Student Learning Commons", "https://www.lib.sfu.ca/about/branches-depts/slc"),
            ("TutorBright", "https://tutorbright.com/careers/"),
            ("Oxford Learning", "https://www.oxfordlearning.com/careers/"),
            ("Sylvan Learning", "https://www.sylvanlearning.com/careers"),
            ("GradeSlam", "https://gradeslam.com/careers"),
            ("Paper", "https://paper.co/careers"),
        ],
    },
    "Admin": {
        "label": "📋 ADMIN & RECEPTION",
        "description": "Admin assistant, receptionist, front desk, office assistant",
        "queries": [
            "administrative assistant Burnaby part-time",
            "receptionist Burnaby",
            "front desk Burnaby",
            "office assistant SFU",
            "administrative assistant Vancouver part-time",
            "receptionist Vancouver part-time",
            "program assistant Burnaby",
            "office assistant North Vancouver",
        ],
        "companies": [
            ("SFU Career Services", "https://www.sfu.ca/career.html"),
            ("WorkBC", "https://www.workbc.ca/jobs"),
            ("Robert Half", "https://www.roberthalf.ca/jobs"),
            ("Express Employment", "https://www.expresspros.com/ca/"),
        ],
    },
    "Campus": {
        "label": "🎓 CAMPUS & STUDENT SERVICES",
        "description": "Student union jobs, campus roles, student services",
        "queries": [
            "student job SFU",
            "student job KPU",
            "student services Burnaby",
            "campus job Vancouver",
            "student union job Burnaby",
            "international student job Vancouver",
            "work study Burnaby",
            "student assistant SFU",
        ],
        "companies": [
            ("SFU Student Union", "https://sfss.ca/jobs/"),
            ("KPU Student Association", "https://www.kusa.ca/jobs"),
            ("SFU Career Portal", "https://www.sfu.ca/career/students.html"),
            ("KPU Career Portal", "https://www.kpu.ca/career"),
        ],
    },
    "Library": {
        "label": "📚 LIBRARY & ACADEMIC SUPPORT",
        "description": "Library assistant, research assistant, academic support",
        "queries": [
            "library assistant Burnaby",
            "library assistant Vancouver part-time",
            "research assistant Burnaby",
            "library page Vancouver",
            "library technician Burnaby",
            "academic assistant SFU",
        ],
        "companies": [
            ("Burnaby Public Library", "https://bpl.bc.ca/about/careers"),
            ("Vancouver Public Library", "https://www.vpl.ca/careers"),
            ("SFU Library", "https://www.lib.sfu.ca/about/jobs"),
            ("KPU Library", "https://www.kpu.ca/library"),
        ],
    },
    "Retail": {
        "label": "🛍️ RETAIL & CUSTOMER SERVICE",
        "description": "Retail associate, customer service, sales associate",
        "queries": [
            "retail associate Burnaby part-time",
            "customer service Burnaby part-time",
            "sales associate Burnaby",
            "retail SFU area",
            "cashier Burnaby part-time",
            "customer service Vancouver part-time student",
        ],
        "companies": [
            ("Metrotown Mall", "https://metropolisatmetrotown.com/careers"),
            ("Loblaws", "https://www.loblaws.ca/careers"),
            ("Shoppers Drug Mart", "https://careers.shoppersdrugmart.ca/"),
            ("Walmart", "https://careers.walmart.ca/"),
            ("Canadian Tire", "https://corp.canadiantire.ca/careers"),
        ],
    },
}

PIPE_KEYS = list(PIPES.keys())


def load_corpus():
    if not CORPUS_FILE.exists():
        return {"keywords": []}
    text = CORPUS_FILE.read_text()
    keywords = [
        "tutoring", "mathematics", "peer tutor", "1:1 instruction", "lesson planning",
        "student support", "communication", "organization", "time management",
        "bilingual", "trilingual", "customer service", "administrative support",
        "scheduling", "record keeping", "problem solving", "attention to detail",
        "teamwork", "collaboration", "reliable", "punctual", "flexible",
    ]
    return {"keywords": list(set(k.lower() for k in keywords))}


def score_job(title, description=""):
    corpus = load_corpus()
    kw = corpus["keywords"]
    text = (title + " " + description).lower()
    matches = sum(1 for k in kw if k.lower() in text)
    total = len(kw)
    if total == 0:
        return 0, {"matched": 0, "total": 0, "matched_terms": []}
    matched_terms = [k for k in kw if k.lower() in text][:20]
    raw_score = (matches / min(total, 100)) * 100
    role_bonus = 10 if any(r in title.lower() for r in STUDENT_ROLES) else 0
    fit = min(round(raw_score + role_bonus), 99)
    return fit, {"matched": matches, "total": total, "role_bonus": role_bonus, "matched_terms": matched_terms}


def print_pipe_urls(pipe_name, easy_only=False):
    pipe = PIPES[pipe_name]
    label = pipe["label"]

    print(f"\n  {'─'*60}")
    print(f"  {label}")
    print(f"  {'─'*60}")
    print(f"  {pipe['description']}")

    print(f"\n  🔍 INDEED SEARCHES (open in browser):")
    for q in pipe["queries"]:
        encoded = q.replace(" ", "+")
        url = f"https://ca.indeed.com/jobs?q={encoded}&l=Burnaby%2C+BC"
        print(f"     {url}")

    print(f"\n  🔍 HIRINGCAFE SEARCHES (open in browser):")
    for q in pipe["queries"]:
        encoded = q.replace(" ", "+")
        url = f"https://hiring.cafe/search?q={encoded}+Burnaby"
        print(f"     {url}")

    print(f"\n  🏢 COMPANY/TARGET PAGES:")
    for name, url in pipe["companies"]:
        print(f"     {name:30s} → {url}")


def score_paste():
    print("\n  Paste job title + description (Ctrl+D to finish):")
    try:
        text = sys.stdin.read().strip()
    except:
        text = ""
    if not text:
        print("  No input.")
        return
    lines = text.split("\n")
    title = lines[0].strip()
    desc = " ".join(lines[1:])
    fit, details = score_job(title, desc)
    terms = details["matched_terms"]
    print(f"\n{'='*60}")
    print(f"  SCORE: {fit}%")
    print(f"{'='*60}")
    print(f"  Title: {title}")
    print(f"  Keywords matched: {details['matched']}/{min(details['total'], 100)}")
    if terms:
        print(f"  Top matches: {', '.join(terms[:10])}")
    print()
    if fit >= 70:
        print("  VERDICT: 🔥 GOOD MATCH — Apply")
    elif fit >= 50:
        print("  VERDICT: 👍 DECENT — Can apply with tailoring")
    else:
        print("  VERDICT: 👎 WEAK — Better options likely available")


def main():
    print(f"{'='*60}")
    print(f"  JOBS OS — LILY EDITION (Student Job Fetcher)")
    print(f"  Target: Tutor / Admin / Reception / Retail / Campus Jobs")
    print(f"  Location: Burnaby / SFU / Surrey / Vancouver (transit)")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    if "--score" in sys.argv:
        score_paste()
        return

    easy_only = "--easy" in sys.argv

    roles_to_show = EASY_ROLES if easy_only else STUDENT_ROLES
    print(f"\n  Looking for: {', '.join(roles_to_show[:5])}...")
    print(f"  Location: Burnaby / SFU area / Surrey / transit-accessible Vancouver")
    print(f"  Pay: DYNAMIC — always target upper range. Tutor: up to $60/hr, Admin: up to $28/hr")
    print(f"  Hours: 10-24 hrs/week, flexible")

    print(f"\n{'='*60}")
    print(f"  GENERATING SEARCH URLs FOR ALL {'EASY ' if easy_only else ''}PIPES")
    print(f"{'='*60}")

    for pipe_name in PIPE_KEYS:
        if easy_only and pipe_name == "Retail":
            continue  # skip retail in easy mode
        print_pipe_urls(pipe_name, easy_only)

    print(f"\n{'='*60}")
    print(f"  NEXT ACTIONS")
    print(f"{'='*60}")
    print(f"  1. Open Indeed + HiringCafe URLs in browser")
    print(f"  2. Filter by: Burnaby/SFU area, part-time, flexible hours")
    print(f"  3. Look for: tutor, admin assistant, reception, library, student services")
    print(f"  4. Cross-check location: transit-accessible ≤45 min from home")
    print(f"  5. Paste JD → I'll score it and build a tailored package")
    print()
    print(f"  TIP: Use --easy to skip retail and show only tutor/admin/reception roles")
    print(f"  TIP: Use --score to paste a JD and get a fit score + verdict")
    print(f"\n  ✓ LILY FETCH ready — {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
