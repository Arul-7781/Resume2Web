# AGENTS.md - Developer Guide

This repository contains an AI-powered portfolio generator built with FastAPI and multi-LLM architecture.

## 🏗️ Architecture
- **API**: FastAPI (`app/main.py`)
- **Parsers**: `app/services/multi_llm_parser.py` orchestrates various LLM providers (Groq, Mistral, Cohere, etc.).
- **Generation**: `app/services/artifact_gen.py` uses Jinja2 templates and WeasyPrint for PDF generation.
- **Frontend**: Single-page application in `app/static/index.html`.

## 🧪 Testing
Run tests using `pytest`:
```bash
python -m pytest tests/
```
Ensure you have the dependencies installed (`pip install -r requirements.txt`).

## ⚠️ Known Issues / Deprecations
- **`AIParserService`**: This service was removed as it was legacy code. Use `MultiLLMParser` instead.
- **Template Logic**: `ArtifactGeneratorService` must pass `dark_mode` explicitly to templates.

## 🚀 Deployment
- Deploy to Netlify or Cloudflare Pages.
- Ensure API keys are set in environment variables (`.env`).
