# Portfolio Design Templates - Quick Guide

## 🎨 Available Design Templates

### 1. **Split Screen Hero** (`split_screen_hero`)
**Best for:** Designers, Product Managers, Modern Professionals

**Key Features:**
- 50/50 split screen layout (photo left, content right)
- Professional photo with accent border effect
- Floating "Let's Talk" CTA button
- Dark navy (#0F1419) background
- Cyan accent color (#4ECDC4)
- Bold, modern typography
- Smooth gradient text effects
- Project cards with hover animations

**Design Philosophy:** Bold, confident, tech-forward

---

### 2. **Single Page Scroll** (`single_page_scroll`)
**Best for:** Developers, Freelancers, Creative Professionals

**Key Features:**
- Smooth single-page scroll experience
- Wave dividers between sections
- Circular profile photo
- Colorful social media icons
- Skills with progress bars (visual percentage)
- Filter tabs for work showcase
- Contact form integrated
- Vibrant green (#4CAF50) primary color
- Yellow/Orange accent colors

**Design Philosophy:** Friendly, approachable, energetic

---

### 3. **Elegant Professional** (`elegant_professional`)
**Best for:** Consultants, Coaches, Corporate Professionals

**Key Features:**
- Curved section dividers (organic shapes)
- Script font for special headings
- Numbered service cards (01, 02, etc.)
- Stats showcase section (clients served, industries, ROI)
- Email signup form integration
- Warm color palette: Forest green (#2F5233) + Beige/Pink
- Playfair Display + Montserrat font pairing
- Quote-style content blocks

**Design Philosophy:** Warm, trustworthy, sophisticated

---

## 📂 File Structure

```
app/templates/
├── split_screen_hero.html          # Modern split-screen design
├── single_page_scroll.html         # Friendly scrolling design
├── elegant_professional.html       # Sophisticated professional design
├── portfolio_template_new.html     # Legacy template (color themes)
└── portfolio_template.html         # Original simple template
```

---

## 🔧 How to Use

### In Code (Backend)

The `design_template` field in `PortfolioData` model determines which template is used:

```python
from app.models.portfolio import PortfolioData

portfolio = PortfolioData(
    personal_info=...,
    skills=...,
    design_template="split_screen_hero",  # Choose template here
    theme="minimal-pro",                   # Theme applies to legacy template only
    dark_mode=False
)
```

### In Frontend (User Selection)

Users select their design template in the UI:
- **AI Upload Tab:** Radio buttons under "Choose Your Design Style"
- **Manual Entry Tab:** Radio buttons under "Portfolio Design Style"

The selected template is automatically applied when:
1. Previewing portfolio
2. Publishing portfolio
3. Downloading artifacts

---

## 🎯 Template Mapping

| Field Value | Template File | Style |
|------------|---------------|-------|
| `split_screen_hero` | `split_screen_hero.html` | Modern, Bold |
| `single_page_scroll` | `single_page_scroll.html` | Friendly, Colorful |
| `elegant_professional` | `elegant_professional.html` | Warm, Sophisticated |
| `portfolio_template_new` | `portfolio_template_new.html` | Legacy (color themes) |

**Default:** If no `design_template` specified, defaults to `split_screen_hero`

---

## 🎨 Design Differences

### NOT Just Color Swaps!

Each template has:

#### **Different Layouts**
- **Split Screen:** 2-column grid hero, sidebar navigation
- **Single Page:** Stacked sections with wave dividers
- **Elegant:** Curved sections, numbered cards

#### **Unique Typography**
- **Split Screen:** Inter (modern, tech)
- **Single Page:** Poppins (friendly, rounded)
- **Elegant:** Playfair Display + Montserrat (serif + sans)

#### **Custom Components**
- **Split Screen:** Floating CTA, gradient text, accent borders
- **Single Page:** Progress bars, filter tabs, wave dividers
- **Elegant:** Script fonts, number circles, quote blocks

#### **Different UX Flows**
- **Split Screen:** Anchor navigation, smooth scroll
- **Single Page:** Continuous scroll, section-based
- **Elegant:** Service showcase, email capture focus

---

## 🚀 Adding New Templates

To add a new design template:

1. **Create HTML Template**
   ```bash
   touch app/templates/my_new_design.html
   ```

2. **Design the Template**
   - Use Jinja2 templating: `{{ personal_info.name }}`
   - Include all sections: hero, skills, experience, projects, education
   - Make it responsive (mobile-friendly)

3. **Update Template Map**
   
   In `app/services/artifact_gen.py`:
   ```python
   template_map = {
       'split_screen_hero': 'split_screen_hero.html',
       'single_page_scroll': 'single_page_scroll.html',
       'elegant_professional': 'elegant_professional.html',
       'my_new_design': 'my_new_design.html',  # Add here
   }
   ```

4. **Add to Frontend UI**
   
   In `app/static/index.html`, add radio button option:
   ```html
   <label class="theme-option-card">
       <input type="radio" name="design_template" value="my_new_design" class="hidden">
       <div>
           <h4>My New Design</h4>
           <p>Description...</p>
       </div>
   </label>
   ```

5. **Update Model Description**
   
   In `app/models/portfolio.py`:
   ```python
   design_template: str = Field(
       default="split_screen_hero",
       description="Portfolio design layout: split_screen_hero, single_page_scroll, elegant_professional, my_new_design"
   )
   ```

---

## 📊 Template Selection Strategy

### By Profession

| Profession | Recommended Template | Why |
|-----------|---------------------|-----|
| Software Engineer | Split Screen Hero | Modern, tech-forward |
| Product Designer | Split Screen Hero | Portfolio showcase focus |
| Frontend Developer | Single Page Scroll | Shows personality |
| Freelancer | Single Page Scroll | Approachable, friendly |
| Consultant | Elegant Professional | Trust, credibility |
| Coach | Elegant Professional | Warm, personal |
| Backend Developer | Split Screen Hero | Professional, clean |
| Full-Stack Developer | Single Page Scroll | Versatile, colorful |

### By Personality

- **Bold, Confident:** Split Screen Hero
- **Friendly, Creative:** Single Page Scroll
- **Trustworthy, Established:** Elegant Professional

---

## 🐛 Troubleshooting

### Template Not Changing

**Issue:** Selected template doesn't apply to preview/download

**Solution:**
1. Check browser console for JavaScript errors
2. Verify `design_template` field is being sent in API request
3. Check server logs: `tail -f server.log | grep template`

### Missing Sections

**Issue:** Some data (projects, skills) not showing in template

**Solution:**
1. Verify template includes all Jinja2 blocks: `{% if projects %}`
2. Check data is populated: `console.log(portfolioData)`
3. Ensure template has loops: `{% for project in projects %}`

### Styling Broken

**Issue:** Template looks wrong, CSS not applying

**Solution:**
1. Check Tailwind CDN is loading: `<script src="https://cdn.tailwindcss.com"></script>`
2. Clear browser cache
3. Verify custom styles in `<style>` tag are not conflicting

---

## 📝 Template Checklist

When creating a new template, ensure it includes:

- [ ] Responsive design (mobile, tablet, desktop)
- [ ] All data sections (personal info, skills, experience, education, projects, achievements)
- [ ] Social media links (LinkedIn, GitHub, Email)
- [ ] Download Resume button/link
- [ ] Contact section or CTA
- [ ] Proper Jinja2 syntax (`{{ }}`, `{% %}`)
- [ ] Null checks (`{% if variable %}`)
- [ ] Loop handling (`{% for item in items %}`)
- [ ] Fallback content (when optional fields empty)
- [ ] Accessibility (semantic HTML, alt text)
- [ ] Print-friendly styles (optional)

---

## 🎓 Design Inspiration Sources

- **Split Screen Hero:** Inspired by Lily Squire's portfolio
- **Single Page Scroll:** Inspired by Ari Darsan's design
- **Elegant Professional:** Inspired by Nadejiah Joseph's coaching site

---

## 🔮 Future Template Ideas

1. **Dark Tech Modern** - Futuristic, neon accents (crypto/blockchain)
2. **Minimalist Sidebar** - Fixed left nav, content right
3. **Card-Based Grid** - Pinterest-style masonry layout
4. **Video Background Hero** - Autoplay video header
5. **Interactive Timeline** - Scroll-triggered animations
6. **3D Isometric** - Three.js background effects

---

**Last Updated:** February 10, 2026  
**Version:** 1.0.0
