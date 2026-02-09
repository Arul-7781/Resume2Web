# Chain of Thought (CoT) Prompting - Deep Dive

## 🧠 What is Chain of Thought?

Chain of Thought is a prompting technique where you ask an AI to show its reasoning steps before giving the final answer.

### **Traditional Prompting (Zero-Shot)**

```
Prompt: "Extract JSON from this resume: [text]"

AI Output: {"name": "John", ...}
```

**Problems:**
- ❌ Black box (no visibility into reasoning)
- ❌ Inconsistent results
- ❌ Hard to debug errors
- ❌ Lower accuracy on complex tasks

---

### **Chain of Thought Prompting**

```
Prompt: "Think step-by-step to extract data from this resume:

Step 1: Identify sections (Education, Experience, etc.)
Step 2: Extract entities (names, dates, companies)
Step 3: Validate logical consistency
Step 4: Structure into JSON

[Resume text]"

AI Output:
Step 1: I see sections: "EXPERIENCE", "EDUCATION", "SKILLS"
Step 2: Name appears to be "John Doe" at the top...
Step 3: Dates are consistent (2020 < 2023)...
Step 4: {"name": "John Doe", ...}
```

**Benefits:**
- ✅ Transparent reasoning
- ✅ More accurate (30-80% improvement)
- ✅ Easier to debug (see where it went wrong)
- ✅ More consistent

---

## 📊 Research Findings

### **Original Paper** (Wei et al., 2022)

**Experiment:** Solve math word problems

```
Traditional:
"What is 5 + 7?"
Answer: 12
Accuracy: 60%

Chain of Thought:
"What is 5 + 7? Let's think step by step."
Step 1: I need to add 5 and 7
Step 2: 5 + 7 = 12
Answer: 12
Accuracy: 85%
```

**Key Findings:**
- CoT improves accuracy by 30-80% on reasoning tasks
- Works better with larger models (GPT-4 > GPT-3.5)
- Especially effective for multi-step problems

---

## 🔍 How We Use CoT in Resume Parsing

### **Our CoT Prompt Structure**

```python
prompt = """
You are an expert resume parsing AI.

CHAIN OF THOUGHT PROCESS:

Step 1: ANALYZE STRUCTURE
- Identify main sections (Personal Info, Experience, Education, Skills, Projects)
- Note the formatting style (bullet points, paragraphs, etc.)
- Determine the chronological order

Step 2: EXTRACT ENTITIES
- Names: Look for capitalized words at the top
- Contact: Email format (contains @), phone (numbers with dashes)
- Dates: Month/Year patterns (Jan 2020, 2020-2023, etc.)
- Companies: Usually after job titles
- Skills: Technical terms, programming languages, tools

Step 3: VALIDATE CONSISTENCY
- Do dates make logical sense? (start < end)
- Are job titles consistent with descriptions?
- Do skills match project descriptions?

Step 4: STRUCTURE DATA
- Group related information
- Normalize date formats
- Extract achievements from job descriptions

=== RESUME TEXT ===
{resume_text}

=== REASONING (Think out loud) ===
[AI writes its analysis here]

=== FINAL JSON OUTPUT ===
[AI outputs structured JSON here]
"""
```

---

## 💡 CoT Variations

### **1. Zero-Shot CoT (Our Approach)**

```
Prompt: "Let's think step-by-step..."
```

- No examples needed
- Works with any model
- Fast to implement

---

### **2. Few-Shot CoT**

```
Prompt: "Here are examples of step-by-step reasoning:

Example 1:
Input: [Resume A]
Reasoning:
Step 1: I see "Software Engineer" as the title...
Step 2: Email is john@example.com...
Output: {JSON}

Example 2:
Input: [Resume B]
Reasoning: ...

Now parse this resume: [New Resume]"
```

- Better accuracy (shows AI the pattern)
- Requires crafting examples
- Longer prompts (more tokens = cost)

---

### **3. Self-Consistency CoT**

```
Prompt: "Generate 3 different reasoning paths, then vote on the best answer."

Path 1: Name is "John Doe" → Output: {"name": "John Doe"}
Path 2: Name is "John Doe" → Output: {"name": "John Doe"}
Path 3: Name is "Jon Doe" → Output: {"name": "Jon Doe"}

Majority vote: "John Doe" ✅
```

- Highest accuracy
- 3-5x more API calls (expensive)
- Slower (sequential calls)

---

## 🛠️ Implementation Patterns

### **Pattern 1: Explicit Steps**

```python
def build_cot_prompt(resume_text):
    return f"""
    Task: Extract resume data
    
    Step 1: Find the name (usually at the top, in larger font)
    Step 2: Find contact info (email has @, phone has digits)
    Step 3: Find experience (look for dates and company names)
    
    Resume: {resume_text}
    
    Now execute each step:
    """
```

**Best for:** Structured tasks with clear steps

---

### **Pattern 2: Question Decomposition**

```python
def build_cot_prompt(resume_text):
    return f"""
    Resume: {resume_text}
    
    Question 1: What is the candidate's name?
    Question 2: What is their email?
    Question 3: Where did they work?
    Question 4: What skills do they have?
    
    Answer each question, then combine into JSON.
    """
```

**Best for:** Complex information extraction

---

### **Pattern 3: Role-Based Reasoning**

```python
def build_cot_prompt(resume_text):
    return f"""
    You are a professional recruiter reviewing this resume.
    
    First, skim the resume and note key sections.
    Then, carefully extract each detail.
    Finally, organize the information logically.
    
    Resume: {resume_text}
    
    Your analysis:
    """
```

**Best for:** Tasks requiring expertise

---

## 📈 Measuring CoT Effectiveness

### **Metrics**

1. **Accuracy:** % of correctly extracted fields
2. **Consistency:** Same resume → same output?
3. **Completeness:** % of fields populated
4. **Speed:** Tokens used (more steps = slower)

### **A/B Testing CoT**

```python
# Test 100 resumes with both approaches
results = {
    "traditional": {"accuracy": 0.72, "time": 2.3},
    "cot": {"accuracy": 0.91, "time": 3.1}
}

# CoT is 26% more accurate but 35% slower
```

---

## 🎯 When to Use CoT

### **✅ Use CoT for:**

- Complex reasoning tasks
- Multi-step problems
- Structured data extraction (resumes, invoices)
- High accuracy requirements
- Debugging (need to see reasoning)

### **❌ Don't use CoT for:**

- Simple classification ("Is this spam?")
- Speed-critical applications
- Cost-sensitive use cases
- Well-defined narrow tasks

---

## 🔬 Advanced Techniques

### **1. CoT with Verification**

```
Step 1: Extract data
Step 2: Double-check each field
Step 3: Flag uncertain extractions
Step 4: Output JSON with confidence scores

Output:
{
  "name": "John Doe",  // confidence: 0.95
  "email": "john@example.com",  // confidence: 1.0
  "phone": null  // confidence: 0.3 (not found)
}
```

---

### **2. CoT with Self-Correction**

```
First attempt: Extract data
Review: Check for errors
Corrected output: Fix any mistakes

Example:
First: {"start_date": "2023", "end_date": "2020"}
Review: End date before start date - illogical!
Corrected: {"start_date": "2020", "end_date": "2023"}
```

---

### **3. CoT with Meta-Prompting**

```
Before parsing, generate a parsing strategy:

Strategy:
1. This resume is in chronological format
2. Skills are listed at the bottom
3. Contact info is in the header

Now use this strategy to parse:
[Apply strategy]
```

---

## 📚 Further Reading

1. **Original Paper:**
   - "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (Wei et al., 2022)
   - https://arxiv.org/abs/2201.11903

2. **Self-Consistency:**
   - "Self-Consistency Improves Chain of Thought Reasoning" (Wang et al., 2022)
   - https://arxiv.org/abs/2203.11171

3. **Tree of Thoughts:**
   - "Tree of Thoughts: Deliberate Problem Solving with Large Language Models" (Yao et al., 2023)
   - https://arxiv.org/abs/2305.10601

4. **Automatic CoT:**
   - "Automatic Chain of Thought Prompting in Large Language Models" (Zhang et al., 2022)
   - https://arxiv.org/abs/2210.03493

---

## 💻 Code Example: Testing CoT

```python
# Compare traditional vs CoT prompting

def traditional_prompt(resume_text):
    return f"Extract JSON from this resume: {resume_text}"

def cot_prompt(resume_text):
    return f"""
    Let's think step-by-step to extract data from this resume.
    
    Step 1: Identify sections
    Step 2: Extract entities
    Step 3: Validate consistency
    Step 4: Format as JSON
    
    Resume: {resume_text}
    
    Your reasoning:
    """

# Test on sample resume
resume = "John Doe\njohn@example.com\nSoftware Engineer at Google"

# Traditional (less accurate)
response1 = model.generate(traditional_prompt(resume))

# CoT (more accurate)
response2 = model.generate(cot_prompt(resume))

# Compare outputs
print("Traditional:", response1)
print("CoT:", response2)
```

---

Chain of Thought transforms LLMs from pattern matchers to reasoners!
