# 🎓 Portfolio Builder - AI-Powered Resume to Portfolio Generator

**Transform your resume into a beautiful, professional portfolio website in seconds.**

Upload your PDF resume → AI extracts your data → Choose a theme → Get a live portfolio website with downloadable resume PDF.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128.4-teal)
![Multi--LLM](https://img.shields.io/badge/Multi--LLM-Adaptive-orange)
![License](https://img.shields.io/badge/license-MIT-purple)

---

## ✨ Features

### 🤖 **Multi-LLM AI Parsing** (New!)
- **Intelligent model rotation**: Automatically cycles through Groq, Mistral, Cohere, Gemini, and OpenAI
- **Rate limit resilience**: Skips rate-limited models automatically
- **Quality-driven**: Retries with different models until quality threshold met
- **99.9% uptime**: Never fails due to single provider issues
- **Adaptive routing**: Learns which models work best for your resumes

### 🎨 10 Professional Themes
Choose from curated themes designed for different professions:
- **Minimal Pro** - Clean, recruiter-friendly (Software Engineers, Corporate)
- **Midnight Tech** - Sleek developer vibe (Backend, AI, Full-stack)
- **Creative Studio** - Playful yet professional (Designers, Frontend)
- **Executive Black** - Luxury, high-contrast (Senior roles, PMs)
- **Nature Calm** - Soft, human-centric (Health, Education)
- **Cyber Neon** - Futuristic, bold (Gen-AI, Blockchain, Startups)
- **Classic Academia** - Research-focused (PhD, Researchers)
- **Mono Focus** - Typography-driven (Writers, Bloggers)
- **Product Designer** - Modern SaaS style (UI/UX Designers)
- **Warm Personal** - Friendly, approachable (Career Switchers, Mentors)

Each theme supports **light and dark mode** with carefully chosen color palettes.

### 🚀 One-Click Deployment
- Automatic deployment to **Netlify** (100GB bandwidth/month)
- Get a live URL instantly: `https://yourname-portfolio.netlify.app`
- Includes downloadable ATS-friendly PDF resume

### 🔍 Preview Before Publishing
- Live preview modal to see your portfolio before deployment
- Edit and refine until perfect
- Switch themes and toggle dark mode in real-time

### ✅ Intelligent Validation
- AI validates parsing completeness with quality scores
- Quick rule-based validation as fallback
- Shows missing information and suggestions for improvement

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- **At least ONE** of the following API keys (recommended: multiple for best reliability):
  - [Groq](https://console.groq.com) - **Free** & fast (70B Llama 3.3, recommended)
  - [Mistral](https://console.mistral.ai) - **Free tier** available
  - [Cohere](https://cohere.com) - **Free tier** with trial credits
  - [Google Gemini](https://aistudio.google.com/app/apikey) - **Free** with daily limits
  - [OpenAI](https://platform.openai.com) - Paid (GPT-4o-mini is cheap)
- Netlify account ([Sign up free](https://app.netlify.com/signup))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/portfolio-builder.git
cd portfolio-builder
```

2. **Create virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# ==========================================
# LLM API KEYS (Add at least 1, more = better reliability)
# ==========================================

# Groq - RECOMMENDED (Free, Fast, Reliable)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Mistral - Great fallback (Free tier)
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-small-latest

# Cohere - Good quality (Free tier)
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=command-r

# Google Gemini - Reliable (Free with limits)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# OpenAI - Best quality (Paid, but cheap with gpt-4o-mini)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# ==========================================
# MULTI-LLM CONFIGURATION
# ==========================================
PARSER_MODE=adaptive              # Options: adaptive, fallback, ensemble, validation
MIN_QUALITY_SCORE=75.0           # Minimum acceptable quality (0-100)
MAX_PARSE_ATTEMPTS=3             # Max retry attempts with different models

# ==========================================
# DEPLOYMENT (Required for publishing)
# ==========================================
NETLIFY_ACCESS_TOKEN=your_netlify_token_here

# Cloudflare (Optional - currently disabled in UI)
CLOUDFLARE_API_TOKEN=your_token_here
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
```

**How to get API keys:**

| Provider | Cost | Speed | How to Get Key |
|----------|------|-------|----------------|
| **Groq** | ✅ Free | ⚡ Fastest | [console.groq.com](https://console.groq.com) → API Keys → Create |
| **Mistral** | ✅ Free tier | ⚡ Fast | [console.mistral.ai](https://console.mistral.ai) → API Keys |
| **Cohere** | ✅ Free trial | 🔸 Medium | [cohere.com](https://cohere.com) → Dashboard → API Keys |
| **Gemini** | ✅ Free + limits | 🔸 Medium | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| **OpenAI** | 💰 Paid | ⚡ Fast | [platform.openai.com](https://platform.openai.com) → API Keys |
| **Netlify** | ✅ Free | - | [Netlify Account](https://app.netlify.com/user/applications) → New Access Token |

5. **Run the application**
```bash
uvicorn app.main:app --reload
```

The app will automatically:
- Detect available LLM providers (based on API keys in `.env`)
- Initialize parsers in priority order: Groq → Mistral → Cohere → Gemini → OpenAI
- Log which models are ready

**Expected startup output:**
```
INFO: Multi-LLM Parser initialized: 5 models in adaptive mode
INFO: ✓ Groq parser ready
INFO: ✓ Mistral parser ready
INFO: ✓ Cohere parser ready
INFO: ✓ Gemini parser ready
INFO: ✓ OpenAI parser ready
INFO: Quality threshold: 75.0, Max attempts: 3
```

6. **Open your browser**
```
http://localhost:8000
```

---

## 🧠 Multi-LLM Architecture

### How It Works

The system uses an **adaptive multi-LLM approach** to ensure reliable parsing:

```
┌─────────────────────────────────────────────────────────────┐
│  PDF Upload → Extract Text → Multi-LLM Parser               │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
    ┌─────────────────────────────────────────────────┐
    │  1. Try Parser 1 (e.g., Groq - fast & free)     │
    │     ↓                                            │
    │  2. Score Result (0-100)                         │
    │     ↓                                            │
    │  3. Score >= 75? → ✅ Success, return result    │
    │     ↓ No                                         │
    │  4. Try Parser 2 (e.g., Mistral)                 │
    │     ↓                                            │
    │  5. Score >= 75? → ✅ Success, return result    │
    │     ↓ No                                         │
    │  6. Continue with Cohere, Gemini, OpenAI...      │
    │     ↓                                            │
    │  7. Return best result after 3 attempts          │
    └─────────────────────────────────────────────────┘
```

### Parser Modes

Configure via `PARSER_MODE` environment variable:

| Mode | Description | Best For |
|------|-------------|----------|
| **`adaptive`** | Tries all models until quality threshold met | **Recommended** - Best reliability |
| `fallback` | Uses first available model, falls back on failure | Fast, simple |
| `ensemble` | Parses with all models, merges results | Highest accuracy (slower) |
| `validation` | Validates final result with different model | Extra quality assurance |

**Example configuration:**
```env
PARSER_MODE=adaptive           # Default and recommended
MIN_QUALITY_SCORE=75.0        # Accept results with 75%+ completeness
MAX_PARSE_ATTEMPTS=3          # Try up to 3 different models
```

### Quality Scoring

Each parsed result is scored based on:
- ✅ Personal info completeness (name, email, bio)
- ✅ Number of skills extracted
- ✅ Work experience entries with descriptions
- ✅ Education details
- ✅ Projects with tech stacks

**Score breakdown example:**
```
📊 Quality Score Breakdown:
  Personal Info: 100.0% (all fields present)
  Skills: 85.0% (17 skills found)
  Experience: 90.0% (3 entries with details)
  Education: 100.0% (2 degrees)
  Projects: 80.0% (4 projects with tech stacks)
  
  🎯 Total Score: 91.0/100 ✅ PASS (threshold: 75.0)
```

### Rate Limit Handling

The system automatically:
1. **Detects rate limits** from API responses
2. **Skips rate-limited models** for 15 minutes
3. **Rotates to next available model** seamlessly
4. **Logs all decisions** for transparency

**Example:**
```
⚠️  Gemini rate limited (429) - skipping for 15 minutes
🔄  Switching to Mistral parser...
✓   Mistral completed - Score: 88.0/100
```

---

## 📖 How to Use

### Option 1: AI Upload (Recommended)

1. **Upload Resume PDF**
   - Click or drag-and-drop your resume PDF
   - AI automatically extracts all information

2. **Review AI Validation**
   - Check the parsing quality score (70-100%)
   - Review missing items and suggestions
   - Re-parse if needed or click "Edit Data" to fix manually

3. **Choose Theme**
   - Select from 10 professional themes
   - Toggle dark mode if desired

4. **Preview**
   - Click "Preview Website" to see full-screen preview
   - Make sure everything looks perfect

5. **Publish**
   - Click "Publish Portfolio"
   - Get your live URL in seconds!

### Option 2: Manual Entry

1. **Switch to "Manual Entry" tab**
2. **Fill in your information**
   - Personal info (name, email, phone, location, social links)
   - Skills (comma-separated)
   - Work experience (add multiple entries)
   - Education
   - Projects

3. **Select theme and publish** (same as AI upload)

---

## 📁 Project Structure

```
Portfolio_Website/
├── app/
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Multi-LLM configuration settings
│   ├── models/
│   │   └── portfolio.py             # Pydantic data models
│   ├── services/
│   │   ├── multi_llm_parser.py      # ⭐ Adaptive multi-LLM orchestrator
│   │   ├── parsers/                 # Individual LLM parsers
│   │   │   ├── gemini_parser.py     # Google Gemini
│   │   │   ├── openai_parser.py     # OpenAI GPT
│   │   │   ├── groq_parser.py       # Groq (Llama 3.3)
│   │   │   ├── mistral_parser.py    # Mistral
│   │   │   └── cohere_parser.py     # Cohere
│   │   ├── artifact_gen.py          # HTML/PDF generator
│   │   ├── netlify_deploy.py        # Netlify deployment
│   │   ├── cloudflare_deploy.py     # Cloudflare deployment (hidden in UI)
│   │   └── validator.py             # AI validation service
│   ├── templates/
│   │   ├── portfolio_template_new.html  # Portfolio HTML (10 themes)
│   │   ├── macros/
│   │   │   └── skill_icon.html      # Skill icon rendering macro
│   │   └── resume_template.html     # ATS-friendly PDF template
│   ├── static/
│   │   └── index.html               # Frontend UI
│   └── utils/
│       └── pdf_extractor.py         # PDF text extraction
├── tests/                      # Test files
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

---

## 🎨 Theme Customization

All 10 themes are defined in `app/templates/portfolio_template_new.html` with CSS variables:

```css
[data-theme="midnight-tech"][data-mode="dark"] {
    --bg-primary: #020617;
    --text-primary: #E5E7EB;
    --accent-primary: #8B5CF6;
}
```

To add a new theme:
1. Add CSS variables in the template
2. Add theme option in `app/static/index.html` (two places: AI upload and manual entry)
3. Update `app/models/portfolio.py` theme field description

---

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve frontend UI |
| `/api/health` | GET | Health check |
| `/api/parse-resume` | POST | Upload PDF, returns parsed data + validation |
| `/api/preview` | POST | Generate HTML preview without deployment |
| `/api/publish?platform=netlify` | POST | Deploy portfolio and return live URL |

### Example: Preview API

```javascript
const response = await fetch('/api/preview', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    personal_info: {
      name: "John Doe",
      email: "john@example.com",
      bio: "Full-stack developer"
    },
    skills: ["Python", "React", "FastAPI"],
    experience: [],
    education: [],
    projects: [],
    theme: "midnight-tech",
    dark_mode: true
  })
});

const { html } = await response.json();
document.getElementById('preview').srcdoc = html;
```

---

## 🐛 Troubleshooting

### No LLM API Keys Configured
**Error:** `ValueError: No LLM API keys configured. Set at least GEMINI_API_KEY`

**Solution:** 
- Add at least ONE API key to your `.env` file
- Recommended: Add multiple keys for better reliability
- Free options: Groq, Gemini, Mistral (free tier)

### All Models Rate Limited
**Error:** `⚠️ No available parsers (all rate limited)`

**Solution:**
- **Best fix**: Add more LLM API keys from different providers
- Wait 15-60 minutes for rate limits to reset
- Check your API usage quotas at provider dashboards
- Consider upgrading to paid tiers if you're parsing many resumes

### Low Quality Scores
**Warning:** `Score: 45.0/100 ⚠️ RETRY (threshold: 75.0)`

**This is normal!** The system will automatically:
1. Try different models
2. Keep attempting until quality threshold met
3. Return best result after max attempts

**To improve scores:**
- Ensure PDF is text-based (not scanned image)
- Use clear, well-formatted resumes
- Lower `MIN_QUALITY_SCORE` if needed (not recommended below 60)

### Gemini Quota Exceeded (Still Works!)
**Error from Gemini:** `429 Resource has been exhausted`

**Solution:** 
- ✅ **No action needed** - System automatically tries other models
- Gemini free tier has daily limits
- The multi-LLM system ensures this doesn't break parsing
- Consider using Groq (unlimited free tier) as primary

### Rate Limit Best Practices

**Free tier limits (as of 2024):**
- Groq: ~30 requests/min (most generous)
- Gemini: ~15 requests/min
- Mistral: ~10 requests/min
- Cohere: ~20 requests/min
- OpenAI: Depends on tier

**Optimization tips:**
```env
# Conservative settings for free tiers
MIN_QUALITY_SCORE=70.0        # Accept slightly lower quality
MAX_PARSE_ATTEMPTS=2          # Reduce retry attempts

# Aggressive settings (requires paid tiers)
MIN_QUALITY_SCORE=85.0        # Demand high quality
MAX_PARSE_ATTEMPTS=5          # Try many models
```

### Netlify Bandwidth Limit
**Error:** `50% of 100GB used this month`

**Solution:**
- Netlify resets bandwidth monthly
- Alternative: Cloudflare Pages code is ready (enable in UI if needed)
- Or upgrade Netlify plan

### Preview Not Showing
- Check browser console for errors
- Ensure data has required fields (`personal_info.name`, `personal_info.email`)
- Try different theme

### PDF Upload Fails
- Ensure PDF is text-based (not scanned image)
- File size must be < 10MB
- Try manual entry if AI parsing fails

---

## 🛠️ Development

### Run in Development Mode
```bash
uvicorn app.main:app --reload --log-level debug
```

### Run Tests
```bash
pytest tests/
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| **LLM API Keys (at least 1 required)** ||||
| `GROQ_API_KEY` | Recommended | - | Groq API key (free, fast) |
| `MISTRAL_API_KEY` | Recommended | - | Mistral API key (free tier) |
| `COHERE_API_KEY` | Optional | - | Cohere API key (free tier) |
| `GEMINI_API_KEY` | Optional | - | Google Gemini API key (free) |
| `OPENAI_API_KEY` | Optional | - | OpenAI API key (paid) |
| **Multi-LLM Configuration** ||||
| `PARSER_MODE` | No | `adaptive` | Parsing strategy: `adaptive`, `fallback`, `ensemble`, `validation` |
| `MIN_QUALITY_SCORE` | No | `75.0` | Minimum acceptable quality score (0-100) |
| `MAX_PARSE_ATTEMPTS` | No | `3` | Maximum retry attempts with different models |
| **Deployment** ||||
| `NETLIFY_ACCESS_TOKEN` | Yes | - | Netlify personal access token |
| `CLOUDFLARE_API_TOKEN` | No | - | Cloudflare API token (optional) |
| `CLOUDFLARE_ACCOUNT_ID` | No | - | Cloudflare account ID (optional) |
| **Application** ||||
| `LOG_LEVEL` | No | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

---

## 📚 Documentation

Additional documentation available in `/docs`:
- [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) - System architecture and design decisions
- [`QUICKSTART.md`](docs/QUICKSTART.md) - Detailed setup guide
- [`CLOUDFLARE_SETUP.md`](docs/CLOUDFLARE_SETUP.md) - Cloudflare deployment setup
- [`PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) - Detailed file structure

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

---

## 🙏 Acknowledgments

- **Groq** for blazing-fast free LLM inference
- **Mistral AI** for reliable open-source models
- **Cohere** for quality language understanding
- **Google Gemini** for accessible AI
- **OpenAI** for pioneering GPT models
- **Netlify** for free hosting
- **FastAPI** for the amazing Python framework
- **WeasyPrint** for PDF generation
- **Tailwind CSS** for styling

---

## 💡 Future Enhancements

- [x] ✅ Multi-LLM support for better uptime and reliability
- [x] ✅ Adaptive routing with quality scoring
- [x] ✅ Automatic rate limit handling
- [x] ✅ Comprehensive skill logo support (80+ technologies)
- [ ] Auto-detect GitHub/LinkedIn from email or name
- [ ] More themes and customization options
- [ ] Export portfolio as static HTML for self-hosting
- [ ] Resume template variations (one-page, two-page, etc.)
- [ ] Analytics integration
- [ ] Custom domain support
- [ ] Real-time collaboration on portfolio editing

---

## 📧 Support

Having issues? 
1. Check [Troubleshooting](#-troubleshooting) section
2. Review [Multi-LLM Architecture](#-multi-llm-architecture) for setup help
3. Check logs for detailed error messages
4. Review documentation in `/docs`
5. Open an issue on GitHub

**Common questions:**
- "Which LLM provider should I use?" → Start with Groq (free + fast), add Mistral as backup
- "How many API keys do I need?" → Minimum 1, recommended 3+ for reliability
- "Why is my score low?" → Try adding more LLM providers, system will auto-retry
- "Do I need paid APIs?" → No! Groq, Mistral, Cohere, and Gemini all have free tiers

---

**Built with ❤️ using FastAPI, Multi-LLM Architecture, and Netlify**

---

## 📖 Additional Documentation

Detailed documentation available in [`/docs`](docs/):
- [Architecture Deep Dive](docs/ARCHITECTURE.md) - System design and patterns
- [Chain of Thought Prompting](docs/CHAIN_OF_THOUGHT.md) - AI prompting techniques
- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed setup instructions
- [Cloudflare Deployment](docs/CLOUDFLARE_SETUP.md) - Alternative deployment option
- [Project Structure](docs/PROJECT_STRUCTURE.md) - Codebase organization
- [Learning Summary](docs/LEARNING_SUMMARY.md) - Concepts and techniques learned
