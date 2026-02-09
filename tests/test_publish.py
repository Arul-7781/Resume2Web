"""
Quick test script to debug publish endpoint
"""
import requests
import json

# Test data matching the Pydantic model
test_data = {
    "personal_info": {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "location": "San Francisco, CA"
    },
    "summary": "Software engineer",
    "skills": ["Python", "FastAPI"],
    "experience": [
        {
            "role": "Engineer",
            "company": "Test Corp",
            "start_date": "2022",
            "end_date": "2024",
            "description": "Built stuff"
        }
    ],
    "education": [
        {
            "degree": "B.S. CS",
            "school": "State U",
            "year": "2022"
        }
    ],
    "projects": [
        {
            "title": "Test Project",
            "tech_stack": "Python",
            "description": "A test",
            "link": "https://example.com"
        }
    ],
    "theme": "minimalist"
}

# Send request
print("Sending request...")
response = requests.post(
    "http://localhost:8000/api/publish",
    json=test_data,
    headers={"Content-Type": "application/json"}
)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
