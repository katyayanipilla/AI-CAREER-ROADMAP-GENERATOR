import sqlite3
from datetime import datetime
import hashlib
from fpdf import FPDF
DB_NAME = "career_platform.db"

# =====================================================
# INIT DATABASE
# =====================================================

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE users ADD COLUMN bio TEXT")
    except:
        pass

    try:
        c.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
    except:
        pass

    # Users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Quiz Attempts
    c.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        topic TEXT,
        score REAL,
        date TEXT
    )
    """)

    # Interview Results
    c.execute("""
    CREATE TABLE IF NOT EXISTS interview_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT,
        technical_score REAL,
        communication_score REAL,
        confidence_score REAL,
        date TEXT
    )
    """)

    # Skill Gap Reports
    c.execute("""
    CREATE TABLE IF NOT EXISTS skill_gap (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        target_role TEXT,
        job_readiness_score REAL,
        date TEXT
    )
    """)

    # Resume History
    c.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        target_role TEXT,
        content TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

# =====================================================
# SAVE FUNCTIONS
# =====================================================

def save_quiz_attempt(username, topic, score):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    INSERT INTO quiz_attempts (username, topic, score, date)
    VALUES (?, ?, ?, ?)
    """, (username, topic, score, datetime.now()))

    conn.commit()
    conn.close()


def save_interview_result(username, role, tech, comm, conf):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    INSERT INTO interview_results 
    (username, role, technical_score, communication_score, confidence_score, date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (username, role, tech, comm, conf, datetime.now()))

    conn.commit()
    conn.close()


def save_skill_gap(username, role, score):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    INSERT INTO skill_gap (username, target_role, job_readiness_score, date)
    VALUES (?, ?, ?, ?)
    """, (username, role, score, datetime.now()))

    conn.commit()
    conn.close()


def save_resume(username, role, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    INSERT INTO resumes (username, target_role, content, date)
    VALUES (?, ?, ?, ?)
    """, (username, role, content, datetime.now()))

    conn.commit()
    conn.close()
    
def get_user_dashboard(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Average Quiz Score
    c.execute("SELECT AVG(score) FROM quiz_attempts WHERE username=?", (username,))
    quiz_avg = c.fetchone()[0] or 0

    # Latest Interview Score
    c.execute("""
        SELECT technical_score, communication_score, confidence_score
        FROM interview_results
        WHERE username=?
        ORDER BY date DESC LIMIT 1
    """, (username,))
    interview = c.fetchone()

    # Latest Skill Gap
    c.execute("""
        SELECT job_readiness_score
        FROM skill_gap
        WHERE username=?
        ORDER BY date DESC LIMIT 1
    """, (username,))
    skill_gap = c.fetchone()

    conn.close()

    return {
        "quiz_avg": round(quiz_avg, 2),
        "interview": interview,
        "skill_gap": skill_gap[0] if skill_gap else 0
    }

def get_user_stats(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Target Role (latest skill gap entry)
    c.execute("""
        SELECT target_role
        FROM skill_gap
        WHERE username=?
        ORDER BY date DESC LIMIT 1
    """, (username,))
    role_data = c.fetchone()
    target_role = role_data[0] if role_data else "Not Selected"

    # Average Quiz Score
    c.execute("SELECT AVG(score) FROM quiz_attempts WHERE username=?", (username,))
    quiz_avg = c.fetchone()[0]
    quiz_avg = round(quiz_avg, 2) if quiz_avg else 0

    # Average Interview Score
    c.execute("""
        SELECT AVG((technical_score + communication_score + confidence_score)/3)
        FROM interview_results
        WHERE username=?
    """, (username,))
    interview_avg = c.fetchone()[0]
    interview_avg = round(interview_avg, 2) if interview_avg else 0

    c.execute("""
        SELECT content FROM resumes
        WHERE username=?
        ORDER BY date DESC LIMIT 1
        """, (username,))
    resume = c.fetchone()
    resume = resume[0] if resume else None
    
    # Latest Job Readiness
    c.execute("""
        SELECT job_readiness_score
        FROM skill_gap
        WHERE username=?
        ORDER BY date DESC LIMIT 1
    """, (username,))
    readiness = c.fetchone()
    job_readiness = readiness[0] if readiness else 0

    conn.close()

    # Career Score Calculation (you can modify logic)
    career_score = round((quiz_avg + interview_avg + job_readiness) / 3, 2)

    return {
    "profile_pic": None,  # add this line
    "target_role": target_role,
    "career_score": career_score,
    "avg_quiz": quiz_avg,
    "avg_interview": interview_avg,
    "job_readiness": job_readiness
    }
    

def calculate_user_rank(career_score):

    if career_score >= 90:
        return "Diamond"
    elif career_score >= 75:
        return "Platinum"
    elif career_score >= 60:
        return "Gold"
    elif career_score >= 40:
        return "Silver"
    else:
        return "Bronze"
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )

    data = c.fetchone()
    conn.close()

    if data and data[0] == hash_password(password):
        return True
    return False