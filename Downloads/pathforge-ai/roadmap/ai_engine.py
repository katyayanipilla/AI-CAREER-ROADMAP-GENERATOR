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

def ask_ai(system_prompt, user_prompt, temperature=0.3, max_tokens=8000):

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


# =====================================================
# ROADMAP GENERATOR
# =====================================================

def generate_roadmap(role, duration_months, level):

    weeks = duration_months * 4

    system_prompt = """
You are a professional AI curriculum designer.
Return ONLY valid JSON.
"""

    user_prompt = f"""
Create a structured career roadmap.

Role: {role}
User Level: {level}
Duration: {duration_months} months
Total Weeks: {weeks}

Generate EXACTLY {weeks} weeks.

Each week must include:
- week_number
- title
- concepts (list)
- learning_resources (list with title and url)
- project
- outcome

Return ONLY JSON array.

Example format:

[
{{
"week_number":1,
"title":"Introduction",
"concepts":["concept1","concept2"],
"learning_resources":[{{"title":"resource","url":"link"}}],
"project":"mini project",
"outcome":"learning outcome"
}}
]
"""

    response = ask_ai(system_prompt, user_prompt)

    return safe_json_parse(response) or []


# =====================================================
# DAILY QUIZ
# =====================================================

def generate_daily_quiz(topic, difficulty="Beginner", covered_subtopics=None):

    if covered_subtopics is None:
        covered_subtopics = []

    system_prompt = """
You are a technical exam creator.
Return ONLY valid JSON.
"""

    user_prompt = f"""
Topic: {topic}
Difficulty: {difficulty}

Avoid these subtopics:
{covered_subtopics}

Generate 25 MCQs.

Each question must include:

- question
- options
- correct_answer
- explanation
- subtopic

Return JSON list
"""

    response = ask_ai(system_prompt, user_prompt)

    return safe_json_parse(response) or []


# =====================================================
# INTERVIEW QUESTION
# =====================================================

def generate_interview_question(role, round_type="technical"):

    system_prompt = "You are a FAANG interviewer."

    user_prompt = f"""
Role: {role}
Round: {round_type}

Ask ONE strong interview question.
"""

    return ask_ai(system_prompt, user_prompt)


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

    system_prompt = "You are a hiring manager. Return JSON."

    user_prompt = f"""
Current Skills: {current_skills}
Target Role: {target_role}

Return JSON:

{{
"strengths":[],
"missing_skills":[],
"recommended_projects":[],
"certifications":[],
"interview_preparation":[],
"job_readiness_score":0,
"final_advice":""
}}
"""

    response = ask_ai(system_prompt, user_prompt)

    return safe_json_parse(response) or {}


# =====================================================
# RESUME GENERATOR
# =====================================================

def generate_advanced_resume(details, target_role):

    system_prompt = """
You are a resume expert.
Create ATS optimized resume.
"""

    user_prompt = f"""
Target Role: {target_role}

User Details:
{details}
"""

    return ask_ai(system_prompt, user_prompt)


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

    system_prompt = "You are an AI career strategist. Return JSON."

    user_prompt = f"""
Skills: {skills}
Interests: {interests}

Return JSON:

{{
"best_career_paths":[],
"reasoning":"",
"growth_potential":"",
"salary_projection":""
}}
"""

    response = ask_ai(system_prompt, user_prompt)

    return safe_json_parse(response) or {}


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