# 🎓 Portfolio Builder - AI-Powered Resume to Portfolio Generator

**Transform your resume into a beautiful, professional portfolio website in seconds.**

Upload your PDF resume → AI extracts your data → Choose a theme → Get a live portfolio website with downloadable resume PDF.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128.4-teal)
![License](https://img.shields.io/badge/license-MIT-purple)

---

## ✨ Features

### 🤖 AI-Powered Parsing
- Upload PDF resume and let Gemini AI extract all information automatically
- Smart validation to ensure parsing quality
- Manual editing option if AI parsing needs refinement

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
- Gemini API key ([Get one free](https://aistudio.google.com/app/apikey))
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
# Required
GEMINI_API_KEY=your_gemini_api_key_here
NETLIFY_ACCESS_TOKEN=your_netlify_token_here

# Optional (for Cloudflare deployment - currently disabled in UI)
CLOUDFLARE_API_TOKEN=your_token_here
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
```

**How to get API keys:**
- **Gemini**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey) → Create API Key
- **Netlify**: [Your Netlify Account](https://app.netlify.com/user/applications) → New Access Token → Generate Token

5. **Run the application**
```bash
uvicorn app.main:app --reload
```

6. **Open your browser**
```
http://localhost:8000
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
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and environment variables
│   ├── models/
│   │   └── portfolio.py        # Pydantic data models
│   ├── services/
│   │   ├── ai_parser.py        # Gemini AI resume parser
│   │   ├── artifact_gen.py     # HTML/PDF generator
│   │   ├── netlify_deploy.py   # Netlify deployment
│   │   ├── cloudflare_deploy.py # Cloudflare deployment (hidden in UI)
│   │   └── validator.py        # AI validation service
│   ├── templates/
│   │   ├── portfolio_template_new.html  # Portfolio HTML template (10 themes)
│   │   └── resume_template.html         # ATS-friendly PDF template
│   ├── static/
│   │   └── index.html          # Frontend UI
│   └── utils/
│       └── pdf_extractor.py    # PDF text extraction
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

### Gemini API Quota Exceeded
**Error:** `429 Resource has been exhausted`

**Solution:** 
- Gemini free tier has daily limits
- Use the "Quick Validation" fallback (automatically enabled)
- Wait 24 hours for quota reset
- Or upgrade to paid tier

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

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for AI parsing |
| `NETLIFY_ACCESS_TOKEN` | Yes | Netlify personal access token |
| `CLOUDFLARE_API_TOKEN` | No | Cloudflare API token (optional) |
| `CLOUDFLARE_ACCOUNT_ID` | No | Cloudflare account ID (optional) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

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

- **Google Gemini** for AI parsing
- **Netlify** for free hosting
- **FastAPI** for the amazing Python framework
- **WeasyPrint** for PDF generation
- **Tailwind CSS** for styling

---

## 💡 Future Enhancements

- [ ] Multi-LLM support for better uptime (cycle between Gemini, GPT, Claude)
- [ ] Auto-detect GitHub/LinkedIn from email or name
- [ ] More themes and customization options
- [ ] Export portfolio as static HTML for self-hosting
- [ ] Resume template variations (one-page, two-page, etc.)
- [ ] Analytics integration
- [ ] Custom domain support

---

## 📧 Support

Having issues? 
1. Check [Troubleshooting](#-troubleshooting) section
2. Review documentation in `/docs`
3. Open an issue on GitHub

---

**Built with ❤️ using FastAPI, Gemini AI, and Netlify**
