# SkillSync AI - Resume Analyzer & Job Matcher

A modern web application built with Python (Flask) and NLP that analyzes resumes, matches them against job descriptions, calculates skill compatibility percentages, and provides personalized upskilling roadmaps.

## 🚀 Features

- **Resume Parsing**: Extracts candidate name, contact details, detected skills, work experience timeline, and education from `.pdf` and `.docx` files.
- **Job Description Analysis**: Parses required skills, preferred qualifications, experience requirements, and education criteria from job postings.
- **Skill Gap & Compatibility Scoring**: Computes match percentage and categorizes skills into matched, missing, and related foundational capabilities.
- **Curated Upskilling Roadmaps**: Recommends learning resources, online documentation, courses, and estimated study time for missing skills.
- **Modern Obsidian Glassmorphism UI**: Fast, responsive dark interface with animated SVG score gauges and quick-fill sample roles.

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
```

### 3. Open in Browser
Navigate to:
```
http://127.0.0.1:5000
```