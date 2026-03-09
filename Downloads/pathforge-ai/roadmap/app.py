from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from ai_engine import *
from datetime import datetime
from database import (
    init_db,
    save_quiz_attempt,
    save_interview_result,
    save_skill_gap,
    save_resume,
    register_user,
    login_user
)
from public_profile import show_public_profile
from fpdf import FPDF



# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Career Roadmap Generator",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>

/* Make sidebar wider */
section[data-testid="stSidebar"] {
    width: 340px !important;
    background: linear-gradient(180deg,#0f1c2e,#1b2b45);
    border-right: 2px solid #2e3f5c;
}

/* Reduce empty space at top */
section[data-testid="stSidebar"] .css-1d391kg {
    padding-top: 20px;
}

/* Increase sidebar text size */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p {
    font-size: 18px !important;
    font-weight: 600;
}

/* Navigation title */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-size: 24px !important;
    color: #4da3ff;
}

/* Sidebar radio buttons (menu items) */
section[data-testid="stSidebar"] .stRadio label {
    font-size: 18px !important;
    padding: 8px 10px;
}

/* Reduce spacing between menu items */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 5px;
}

/* Hover effect for menu */
section[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #2e5ea8;
    border-radius: 8px;
    padding-left: 10px;
    transition: 0.2s;
}

/* Remove bottom empty padding */
section[data-testid="stSidebar"] {
    padding-bottom: 10px !important;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# LOAD CSS
# =====================================================

def load_css():
    with open("styles/ui.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# =====================================================
# DATABASE INIT
# =====================================================

init_db()


# =====================================================
# SHAREABLE PUBLIC PROFILE LINK
# =====================================================

query_params = st.query_params

if "profile" in query_params:
    show_public_profile(query_params["profile"])
    st.stop()


# =====================================================
# SESSION STATE
# =====================================================

if "interview_scores" not in st.session_state:
    st.session_state.interview_scores = []

if "job_readiness_score" not in st.session_state:
    st.session_state.job_readiness_score = 0

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "mastery" not in st.session_state:
    st.session_state.mastery = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "interview_question" not in st.session_state:
    st.session_state.interview_question = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# =====================================================
# LOGIN PAGE
# =====================================================

if not st.session_state.logged_in:

    st.markdown("<h1 class='center-title'>🚀 AI Career Roadmap Generator</h1>", unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    with col2:
        if st.button("Register"):
            if register_user(username, password):
                st.success("Account created. Please login.")
            else:
                st.error("Username already exists")

    st.stop()


# =====================================================
# HEADER
# =====================================================

st.markdown(
"""
<h1 class="center-title">🚀 AI Career Roadmap Generator</h1>
""",
unsafe_allow_html=True
)

# =====================================================
# SIDEBAR
# =====================================================

page = st.sidebar.radio("🚀Navigation", [
    "🏠Dashboard",
    "📚Roadmap",
    "🧠Daily Quiz",
    "📊Skill Gap",
    "🎤Interview",
    "👩‍🏫Mentor Chat",
    "📄Resume Builder",
    "🎓Career Predictor",
    "👤Public Profile"
])


# =====================================================
# DASHBOARD
# =====================================================

if page == "🏠Dashboard":

    st.subheader("AI Career Intelligence Dashboard")

    quiz_scores = list(st.session_state.mastery.values())

    avg_quiz = sum(quiz_scores)/len(quiz_scores) if quiz_scores else 0
    avg_interview = sum(st.session_state.interview_scores)/len(st.session_state.interview_scores) if st.session_state.interview_scores else 0
    job_ready = st.session_state.job_readiness_score

    career_score = (avg_quiz*0.4) + (avg_interview*0.3) + (job_ready*0.3)

    st.markdown("### Career Intelligence Score")
    st.progress(career_score/100)
    st.metric("Score", f"{round(career_score,2)}/100")

    st.markdown(f"""

    <div class="main-score-box">
    <h2>🏆 Career Intelligence Score</h2>
    <div class="score-highlight">{round(career_score,2)}/100</div>
    </div>

    <div style="display:flex; gap:20px">

    <div class="dashboard-card">
    <div class="dashboard-title">🧠 Quiz Performance</div>
    <div class="score-highlight">{round(avg_quiz,2)}</div>
    </div>

    <div class="dashboard-card">
    <div class="dashboard-title">🎤 Interview Performance</div>
    <div class="score-highlight">{round(avg_interview,2)}</div>
    </div>

    <div class="dashboard-card">
    <div class="dashboard-title">🚀 Job Readiness</div>
    <div class="score-highlight">{round(job_ready,2)}</div>
    </div>

    </div>

    """, unsafe_allow_html=True)
    
    st.subheader("Update Profile")

    bio = st.text_area("Bio")

    profile_pic = st.file_uploader(
    "Upload Profile Picture",
    type=["png", "jpg", "jpeg"]
    )

    if st.button("Save Profile"):

        if profile_pic:

            path = f"profile_{st.session_state.username}.png"

            with open(path, "wb") as f:
                f.write(profile_pic.getbuffer())

            conn = sqlite3.connect("career_platform.db")
            c = conn.cursor()

            c.execute("""
            UPDATE users
            SET bio=?, profile_pic=?
            WHERE username=?
            """, (bio, path, st.session_state.username))

            conn.commit()
            conn.close()

            st.success("Profile Updated")
            
        
# =====================================================
# ROADMAP
# =====================================================

elif page == "📚Roadmap":

    st.title("AI Career Roadmap")

    role = st.text_input("Target Role")
    duration = st.selectbox("Duration (Months)", [3,6,9])
    level = st.selectbox("Your Level", ["Beginner","Intermediate","Advanced"])
    
    roadmap_text = ""
    
    if st.button("Generate Roadmap"):

        with st.spinner("Generating roadmap..."):
            roadmap = generate_roadmap(role,duration,level)

        

        for week in roadmap:

            concepts = "".join([f"<li>{c}</li>" for c in week["concepts"]])

            resources = ""
            for r in week["learning_resources"]:
                if "url" in r:
                    resources += f"<li>📚 <b>{r['title']}</b> — <a href='{r['url']}' target='_blank'>Open</a></li>"
                else:
                    resources += f"<li>📚 <b>{r['title']}</b></li>"

            st.markdown(f"""
            <div class="card">

            <h2>📅 Week {week['week_number']} — {week['title']}</h2>

            <h4>🧠 Concepts</h4>
            <ul>{concepts}</ul>

            <h4>📖 Learning Resources</h4>
            <ul>{resources}</ul>

            <h4>💻 Project</h4>
            <p>{week["project"]}</p>

            <h4>🎯 Outcome</h4>
            <p>{week["outcome"]}</p>

            </div>
            """, unsafe_allow_html=True)

            roadmap_text += f"""
        Week {week['week_number']} — {week['title']}

        Concepts:
        {', '.join(week['concepts'])}

        Project:
        {week['project']}

        Outcome:
        {week['outcome']}

    ------------------------------------
    """
    def generate_pdf(text):

        text = text.replace("—", "-")  # replace long dash
        text = text.replace("📚", "")
        text = text.replace("🧠", "")
        text = text.replace("🎯", "")
        text = text.replace("💻", "")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in text.split("\n"):
            pdf.cell(0, 8, txt=line, ln=True)

        pdf.output("roadmap.pdf")

        with open("roadmap.pdf","rb") as f:
            return f.read()
    pdf_data = generate_pdf(roadmap_text)

    st.download_button(
        "📄 Download Roadmap PDF",
        pdf_data,
        file_name="career_roadmap.pdf"
    )

# =====================================================
# DAILY QUIZ
# =====================================================

elif page == "🧠Daily Quiz":

    st.title("Adaptive Daily Quiz")

    topic = st.text_input("Topic")
    difficulty = st.selectbox("Difficulty",["Beginner","Intermediate","Advanced"])

    if st.button("Generate Quiz"):

        st.session_state.quiz_data = generate_daily_quiz(topic,difficulty)
        st.session_state.quiz_submitted = False

    if st.session_state.quiz_data:

        for i,q in enumerate(st.session_state.quiz_data):

            st.write(f"Q{i+1}: {q['question']}")

            st.radio("Answer",q["options"],key=f"quiz{i}")

        if st.button("Submit Quiz"):

            score = 0

            for i,q in enumerate(st.session_state.quiz_data):

                if st.session_state[f"quiz{i}"] == q["correct_answer"]:
                    score+=1

            percentage = (score/len(st.session_state.quiz_data))*100

            save_quiz_attempt(st.session_state.username,topic,percentage)

            st.success(f"Score: {percentage}%")


# =====================================================
# INTERVIEW
# =====================================================

elif page == "🎤Interview":

    role = st.text_input("Target Role")

    if st.button("Generate Question"):
        st.session_state.interview_question = generate_interview_question(role)

    if st.session_state.interview_question:

        st.write(st.session_state.interview_question)

        answer = st.text_area("Your Answer")

        if st.button("Evaluate"):

            result = evaluate_interview_answer(
            role,
            st.session_state.interview_question,
            answer
            )

            if result:

                tech = result.get("technical_score", 0)
                comm = result.get("communication_score", 0)
                conf = result.get("confidence_score", 0)

                save_interview_result(
                st.session_state.username,
                role,
                tech,
                comm,
                conf
                )

                st.subheader("Evaluation")

                st.write("Technical Score:", tech)
                st.write("Communication Score:", comm)
                st.write("Confidence Score:", conf)

                st.write("Feedback:", result.get("feedback",""))
                st.write("Ideal Answer:", result.get("ideal_answer",""))
                st.write("Suggestions:", result.get("improvement_suggestions",""))

            else:

                st.error("AI could not evaluate the answer. Try again.")


# =====================================================
# MENTOR CHAT
# =====================================================

elif page == "👩‍🏫Mentor Chat":

    msg = st.text_input("Ask career question")

    if st.button("Ask Mentor"):
        st.write(mentor_chat(msg))


# =====================================================
# RESUME BUILDER
# =====================================================

elif page == "📄Resume Builder":

    st.title("AI Resume Builder")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    linkedin = st.text_input("LinkedIn")
    skills = st.text_area("Skills")
    experience = st.text_area("Experience")
    projects = st.text_area("Projects")
    education = st.text_area("Education")
    target_role = st.text_input("Target Role")

    if st.button("Generate Professional Resume"):

        details = f"""
Name: {name}
Email: {email}
LinkedIn: {linkedin}

Skills:
{skills}

Experience:
{experience}

Projects:
{projects}

Education:
{education}
"""

        with st.spinner("Generating ATS optimized resume..."):

            resume = generate_advanced_resume(details, target_role)

        st.markdown("### Generated Resume")

        st.text_area("Resume", resume, height=400)

        save_resume(
            st.session_state.username,
            target_role,
            resume
        )

        st.download_button(
            "Download Resume",
            resume,
            file_name="resume.txt"
        )

# =====================================================
# CAREER PREDICTOR
# =====================================================

elif page == "🎓Career Predictor":

    skills = st.text_input("Skills")
    interests = st.text_input("Interests")

    if st.button("Predict Career"):
        st.write(career_predictor(skills,interests))


# =====================================================
# PUBLIC PROFILE
# =====================================================

elif page == "👤Public Profile":

    username = st.text_input("Enter Username")

    if st.button("View"):
        show_public_profile(username)

#======================================================
#skill gp
#======================================================
elif page == "📊Skill Gap":

    st.title("Skill Gap Analysis")

    current_skills = st.text_area("Enter Your Current Skills (comma separated)")
    target_role = st.text_input("Target Role")

    if st.button("Analyze Skill Gap"):

        with st.spinner("Analyzing your skills..."):

            result = skill_gap_analysis(current_skills, target_role)

        if result:

            st.subheader("Your Strengths")
            for s in result["strengths"]:
                st.write("✅", s)

            st.subheader("Missing Skills")
            for s in result["missing_skills"]:
                st.write("❌", s)

            st.subheader("Recommended Projects")
            for p in result["recommended_projects"]:
                st.write("📌", p)

            st.subheader("Certifications")
            for c in result["certifications"]:
                st.write("🎓", c)

            st.subheader("Interview Preparation")
            for i in result["interview_preparation"]:
                st.write("💡", i)

            st.metric("Job Readiness Score", result["job_readiness_score"])

            st.info(result["final_advice"])

            save_skill_gap(
                st.session_state.username,
                target_role,
                result["job_readiness_score"]
            )