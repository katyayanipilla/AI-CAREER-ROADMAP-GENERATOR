import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

# =====================================================
# ENV SETUP
# =====================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise Exception("GROQ_API_KEY not found. Add it inside .env file")

client = Groq(api_key=api_key)

MODEL = "llama-3.1-8b-instant"


# =====================================================
# SAFE JSON PARSER
# =====================================================

def safe_json_parse(text):

    try:

        if not text:
            return None

        text = re.sub(r"```json|```", "", text).strip()

        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)

        if not match:
            print("No JSON found")
            print(text)
            return None

        json_str = match.group(0)

        json_str = re.sub(r",\s*}", "}", json_str)
        json_str = re.sub(r",\s*]", "]", json_str)

        return json.loads(json_str)

    except Exception as e:

        print("JSON ERROR:", e)
        print(text)
        return None


# =====================================================
# AI CALL ENGINE
# =====================================================

def ask_ai(system_prompt, user_prompt, temperature=0.3, max_tokens=4000):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("🔥 GROQ ERROR:", e)
        raise e


# =====================================================
# ROADMAP GENERATOR
# =====================================================

def generate_roadmap(role, duration_months, level):
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed

    weeks = duration_months * 4
    chunk_size = 4  # ← bigger chunks = fewer API calls

    system_prompt = """You are a curriculum designer.
Return ONLY valid JSON array. No markdown, no extra text.
Start with [ and end with ]."""

    def generate_chunk(start, end):
        count = end - start + 1
        user_prompt = f"""Role: {role}, Level: {level}
Generate exactly {count} weeks (week {start} to week {end}).
[
  {{
    "week_number": {start},
    "title": "Short title",
    "concepts": ["c1", "c2", "c3"],
    "learning_resources": [{{"title": "Resource", "url": "https://..."}}],
    "project": "Project",
    "outcome": "Outcome"
  }}
]
Return ONLY JSON array. week_number from {start} to {end}."""

        for attempt in range(3):
            try:
                response = ask_ai(
                    system_prompt, user_prompt,
                    temperature=0.1,
                    max_tokens=count * 350 + 400
                )
                result = safe_json_parse(response)
                if result:
                    return result
            except Exception as e:
                print(f"Chunk {start}-{end} failed attempt {attempt+1}: {e}")
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
        return []

    # Build chunks
    chunks = [(start, min(start + chunk_size - 1, weeks))
              for start in range(1, weeks + 1, chunk_size)]

    all_weeks = [None] * len(chunks)

    # Parallel with staggered start to avoid rate limit spikes
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_idx = {}
        for i, (s, e) in enumerate(chunks):
            time.sleep(i * 0.3)  # ← stagger launches by 300ms
            future_to_idx[executor.submit(generate_chunk, s, e)] = i

        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                all_weeks[idx] = future.result()
            except Exception:
                all_weeks[idx] = []

    return [week for chunk in all_weeks if chunk for week in chunk]
# =====================================================
# DAILY QUIZ
# =====================================================

def generate_daily_quiz(topic, difficulty="Beginner", num_questions=10, covered_subtopics=None):

    if covered_subtopics is None:
        covered_subtopics = []

    # 10 questions needs ~2000 tokens, 20 needs ~4000
    max_tokens = num_questions * 200 + 500

    system_prompt = """You are a technical exam creator.
Return ONLY a valid JSON array. No markdown, no explanation, no extra text.
Start your response with [ and end with ]."""

    user_prompt = f"""Topic: {topic}
Difficulty: {difficulty}

Generate exactly {num_questions} multiple choice questions.

Return a JSON array like this:
[
  {{
    "question": "What is ...?",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "correct_answer": "A) option1",
    "explanation": "Brief explanation",
    "subtopic": "subtopic name"
  }}
]

IMPORTANT:
- Generate exactly {num_questions} questions, no more no less
- correct_answer must exactly match one of the options strings
- Return ONLY the JSON array, nothing else"""

    response = ask_ai(system_prompt, user_prompt, max_tokens=max_tokens)
    return safe_json_parse(response) or []

# =====================================================
# INTERVIEW QUESTION
# =====================================================

def generate_interview_question(role, round_type="technical"):

    system_prompt = "You are a FAANG interviewer."

    user_prompt = f"""
Role: {role}
Round: {round_type}

Generate 5 strong interview questions.

Return JSON list like:

[
{{"question":"question1"}},
{{"question":"question2"}},
{{"question":"question3"}},
{{"question":"question4"}},
{{"question":"question5"}}
]
"""

    response = ask_ai(system_prompt, user_prompt)

    return safe_json_parse(response) or []

# =====================================================
# INTERVIEW EVALUATION
# =====================================================

def evaluate_interview_answer(role, question, answer):

    system_prompt = """
You are a FAANG interview evaluator.

Return ONLY valid JSON.
No explanations outside JSON.
"""

    user_prompt = f"""
Role: {role}

Question: {question}

Candidate Answer: {answer}

Return JSON in this exact format:

{{
"technical_score": 0-100,
"communication_score": 0-100,
"confidence_score": 0-100,
"feedback": "short feedback",
"ideal_answer": "best possible answer",
"improvement_suggestions": "how candidate can improve"
}}
"""

    response = ask_ai(system_prompt, user_prompt)

    return safe_json_parse(response)

# =====================================================
# SKILL GAP ANALYSIS
# =====================================================

def skill_gap_analysis(current_skills, target_role):

    system_prompt = """You are a hiring manager and career coach.
Return ONLY valid JSON. No markdown, no explanation, no extra text."""

    user_prompt = f"""Current Skills: {current_skills}
Target Role: {target_role}

Return this exact JSON structure with real values filled in:
{{
  "strengths": ["skill1", "skill2", "skill3"],
  "missing_skills": ["skill1", "skill2", "skill3"],
  "recommended_projects": ["project1", "project2", "project3"],
  "certifications": ["cert1", "cert2"],
  "interview_preparation": ["tip1", "tip2", "tip3"],
  "job_readiness_score": 65,
  "final_advice": "One paragraph of actionable advice."
}}

job_readiness_score must be a number between 0 and 100.
Return ONLY the JSON object."""

    response = ask_ai(system_prompt, user_prompt, max_tokens=2000)
    return safe_json_parse(response) or {}



# =====================================================
# RESUME GENERATOR
# =====================================================

def generate_advanced_resume(details, target_role):

    system_prompt = """You are a professional resume writer.
CRITICAL RULES:
1. Use ONLY the exact information provided by the user. 
2. Do NOT invent, hallucinate, or add any fake data.
3. Do NOT add fake university names, fake percentages, fake companies, fake achievements.
4. If a field is empty or missing, skip that section entirely.
5. Use ONLY real skills, projects, and experience that the user has provided.
6. Do NOT add placeholder text or example data."""

    user_prompt = f"""Create a professional ATS-optimized resume using ONLY the details below.
Do not add anything that is not in the details. Do not invent any data.

Target Role: {target_role}

=== CANDIDATE DETAILS (USE ONLY THIS DATA) ===
{details}
=== END OF CANDIDATE DETAILS ===

Format the resume using this EXACT structure.
Use only real data from above. Skip any section where data is missing or empty.

[FULL NAME]
[Email] | [Phone] | [LinkedIn] | [GitHub]
========================================

PROFESSIONAL SUMMARY
--------------------
Write 3-4 lines using ONLY their actual skills and target role: {target_role}
Do not mention any university, company, or achievement not listed above.

TECHNICAL SKILLS
----------------
Programming Languages : [from details only]
Frameworks & Libraries: [from details only]
Tools & Technologies  : [from details only]
Soft Skills           : [from details only]

EDUCATION
---------
[Degree] in [Branch]                                          [Year]
[University] | CGPA: [cgpa]

Intermediate (12th)                                           [Year]
[College], [Board] | [Percentage]%

Secondary (10th)                                              [Year]
[School], [Board] | [Percentage]%

PROJECTS
--------
[Project Title] | [Technologies from details]
- [Action verb] + what they actually built (from description)
- [Action verb] + key feature from their description
- [Action verb] + outcome from their description

EXPERIENCE / INTERNSHIP
-----------------------
[Role] | [Company]                                            [Duration]
- [Action verb] + actual work they described
- [Action verb] + actual contribution they mentioned

CERTIFICATIONS
--------------
- [Only certifications they listed]

IMPORTANT FINAL CHECK:
- Every name, number, company, university must come from the candidate details above
- If projects section is empty, write only the header and skip
- If experience section is empty, write only the header and skip
- Do NOT add achievements section unless user provided achievements
- Do NOT add any data you made up"""

    return ask_ai(system_prompt, user_prompt, temperature=0.1, max_tokens=4000)

# =====================================================
# MENTOR CHAT
# =====================================================

def mentor_chat(message):

    system_prompt = """
You are a motivational career mentor.
Guide students with clarity.
"""

    return ask_ai(system_prompt, message)


# =====================================================
# CAREER PREDICTOR
# =====================================================

def career_predictor(skills, interests):

    system_prompt = """You are an AI career strategist.
Return ONLY valid JSON. No markdown, no explanation, no extra text.
Start with { and end with }."""

    user_prompt = f"""Skills: {skills}
Interests: {interests}

Return ONLY this exact JSON structure:
{{
  "best_career_paths": [
    {{
      "title": "Career Title",
      "description": "One sentence description.",
      "required_skills": ["skill1", "skill2"],
      "avg_salary": "$120,000/year",
      "growth": "High"
    }}
  ],
  "reasoning": "2-3 sentences explaining why these paths fit.",
  "growth_potential": "High / Medium / Low",
  "salary_projection": "$100,000 - $150,000/year",
  "next_steps": ["Step 1", "Step 2", "Step 3"]
}}

Generate 3 career paths. Return ONLY the JSON."""

    response = ask_ai(system_prompt, user_prompt, max_tokens=2000)
    return safe_json_parse(response) or {}