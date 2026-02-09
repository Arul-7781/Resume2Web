"""
Test the validation and preview features
"""
import json
from app.services.validator import ResumeValidator
from app.models.portfolio import PortfolioData, PersonalInfo, Experience

# Sample data
sample_resume_text = """
John Doe
Software Engineer
john@example.com | 555-1234 | San Francisco, CA
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

SKILLS
Python, JavaScript, React, Node.js, Docker, AWS, PostgreSQL, MongoDB

EXPERIENCE
Senior Software Engineer - Tech Corp (Jan 2020 - Present)
• Led development of microservices architecture serving 1M+ users
• Built CI/CD pipelines reducing deployment time by 60%
• Mentored 5 junior engineers on best practices

Software Engineer - StartupXYZ (June 2018 - Dec 2019)
• Developed RESTful APIs using Python and Flask
• Implemented real-time chat feature using WebSockets
• Optimized database queries improving response time by 40%

EDUCATION
Bachelor of Science in Computer Science - MIT (2018)
GPA: 3.8/4.0

PROJECTS
E-commerce Platform
Built full-stack e-commerce site using React, Node.js, and MongoDB
Features: User authentication, payment processing, admin dashboard
"""

# Incomplete parsed data (missing some info)
incomplete_data = PortfolioData(
    personal_info=PersonalInfo(
        name="John Doe",
        email="john@example.com",
        phone="555-1234",
        location="San Francisco, CA",
        linkedin="https://linkedin.com/in/johndoe",
        github="https://github.com/johndoe",
        bio="Software Engineer"
    ),
    skills=["Python", "JavaScript", "React"],  # Missing: Node.js, Docker, AWS, PostgreSQL, MongoDB
    experience=[
        Experience(
            role="Senior Software Engineer",
            company="Tech Corp",
            start_date="Jan 2020",
            end_date="Present",
            description="Led development of microservices"  # Incomplete description
        )
        # Missing second job!
    ],
    education=[],  # Missing education!
    projects=[],  # Missing projects!
    theme="professional"
)

# Test validation
print("=" * 60)
print("TESTING AI-POWERED RESUME VALIDATOR")
print("=" * 60)

validator = ResumeValidator()

print("\n1️⃣ Quick Validation (Rule-based)")
print("-" * 60)
quick_result = validator.quick_validate(incomplete_data)
print(f"Score: {quick_result['completeness_score']}%")
print(f"Is Complete: {quick_result['is_complete']}")
print(f"Issues found: {len(quick_result['missing_items'])}")
for issue in quick_result['missing_items']:
    print(f"  ❌ {issue}")

print("\n2️⃣ AI Validation (Semantic comparison)")
print("-" * 60)
print("Calling Gemini AI to compare resume text with parsed data...")
print("This may take 5-10 seconds...\n")

ai_result = validator.validate(sample_resume_text, incomplete_data)
print(f"Score: {ai_result['completeness_score']}%")
print(f"Is Complete: {ai_result['is_complete']}")
print(f"\nMissing Items ({len(ai_result['missing_items'])}):")
for item in ai_result['missing_items'][:5]:  # Show first 5
    print(f"  ❌ {item}")

print(f"\nSuggestions ({len(ai_result['suggestions'])}):")
for sugg in ai_result['suggestions'][:5]:  # Show first 5
    print(f"  💡 {sugg}")

if 'validation_details' in ai_result:
    print(f"\nDetailed Breakdown:")
    for key, value in ai_result['validation_details'].items():
        print(f"  {key}: {value}")

print("\n" + "=" * 60)
print("✅ Validation test complete!")
print("=" * 60)
