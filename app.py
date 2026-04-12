from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import sqlite3
from database import update_streak
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
    with open("ui.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ✅ CALL FUNCTION OUTSIDE
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
    "🏠Dashboard", "📚Roadmap", "🧠Daily Quiz",
    "📊Skill Gap", "🎤Interview", "👩‍🏫Mentor Chat",
    "📄Resume Builder", "🎓Career Predictor", "👤Public Profile"
], key="nav_page")

# =====================================================
# DASHBOARD
# =====================================================

if page == "🏠Dashboard":

    conn = sqlite3.connect("career_platform.db")
    c = conn.cursor()

    c.execute("SELECT streak, max_streak, last_active FROM users WHERE username=?", (st.session_state.username,))
    data = c.fetchone()

    conn.close()

    streak = data[0] if data and data[0] else 0
    max_streak = data[1] if data and data[1] else 0
    last_active = data[2] if data else None
  
    st.subheader("AI Career Intelligence Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        
        <div class="dashboard-card streak-current">
            🔥 <b>Current Streak</b><br>
            <div class="score-highlight">{streak} days</div>
            <div class="streak-text">Keep going!</div>
        </div>
    """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="dashboard-card streak-max">
            🏆 <b>Max Streak</b><br>
            <div class="score-highlight">{max_streak} days</div>
            <div class="streak-text">Your best record</div>
        </div>
    """, unsafe_allow_html=True)


    today = datetime.now().date()

    if last_active:
        last_active_date = datetime.fromisoformat(last_active).date()
    else:
        last_active_date = None

    if last_active_date != today:
        st.warning("⚠️ You haven't completed today's quiz! Keep your streak alive 🔥")
        if st.button("👉 Go to Daily Quiz"):
            st.session_state["nav_page"] = "🧠Daily Quiz"   # ← NEW
            st.rerun()                                        # ← NEW
    else:
        st.success("✅ Great! You've completed today's quiz")
    
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
    duration = st.selectbox("Duration (Months)", [3,6,9,])
    level = st.selectbox("Your Level", ["Beginner","Intermediate","Advanced"])

    roadmap_text = ""

    if st.button("Generate Roadmap"):

        with st.spinner("Generating roadmap..."):
            roadmap = generate_roadmap(role, duration, level)

        if not roadmap:
            st.error("Roadmap generation failed. Check terminal for raw AI response.")

        else:
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

                text = text.replace("—", "-")
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
    difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
    num_questions = st.selectbox("Number of Questions", [10, 20])  # ← ADD THIS

    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz..."):
            st.session_state.quiz_data = generate_daily_quiz(topic, difficulty, num_questions)  # ← pass it here
        st.session_state.quiz_submitted = False

    if st.session_state.quiz_data:

        for i, q in enumerate(st.session_state.quiz_data):
            st.write(f"Q{i+1}: {q['question']}")
            st.radio("Answer", q["options"], key=f"quiz{i}")

        if st.button("Submit Quiz"):
            score = 0
            for i, q in enumerate(st.session_state.quiz_data):
                if st.session_state[f"quiz{i}"] == q["correct_answer"]:
                    score += 1

            percentage = (score / len(st.session_state.quiz_data)) * 100
            save_quiz_attempt(st.session_state.username, topic, percentage)
            update_streak(st.session_state.username)
            st.session_state.mastery[topic] = percentage
            st.success(f"Score: {percentage:.1f}%")
# =====================================================
# INTERVIEW
# =====================================================

elif page == "🎤Interview":
    st.title("🎤 Interview Practice")   # ADD THIS
    role = st.text_input("Target Role")

    if st.button("Generate Questions"):

        st.session_state.interview_questions = generate_interview_question(role)

    if "interview_questions" in st.session_state:

        for q in st.session_state.interview_questions:

            st.write("🎤", q["question"])

        answer = st.text_area("Your Answer")

        if st.button("Evaluate"):

            result = evaluate_interview_answer(
                role,
                st.session_state.interview_questions[0]["question"],
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

    st.title("📄 AI Resume Builder")

    # -------------------------
    # PERSONAL INFORMATION
    # -------------------------
    st.header("Personal Information")

    col1, col2 = st.columns(2)
    with col1:
        name        = st.text_input("Full Name", key="name")
        email       = st.text_input("Email", key="email")
        phone       = st.text_input("Phone Number", key="phone")
    with col2:
        linkedin    = st.text_input("LinkedIn Profile", key="linkedin")
        github      = st.text_input("GitHub Profile", key="github")
        target_role = st.text_input("Target Role", key="target_role")

    # -------------------------
    # EDUCATION
    # -------------------------
    st.header("Educational Qualifications")

    st.subheader("10th / SSC")
    col1, col2 = st.columns(2)
    with col1:
        tenth_school     = st.text_input("School Name", key="tenth_school")
        tenth_board      = st.text_input("Board", key="tenth_board")
    with col2:
        tenth_percentage = st.text_input("Percentage / CGPA", key="tenth_percentage")
        tenth_year       = st.text_input("Year of Completion", key="tenth_year")

    st.subheader("Intermediate / 12th")
    col1, col2 = st.columns(2)
    with col1:
        inter_college    = st.text_input("College Name", key="inter_college")
        inter_board      = st.text_input("Board", key="inter_board")
    with col2:
        inter_percentage = st.text_input("Percentage / CGPA", key="inter_percentage")
        inter_year       = st.text_input("Year of Completion", key="inter_year")

    st.subheader("Graduation")
    col1, col2 = st.columns(2)
    with col1:
        degree    = st.text_input("Degree", key="degree")
        branch    = st.text_input("Branch", key="branch")
    with col2:
        university = st.text_input("University / College", key="university")
        cgpa       = st.text_input("CGPA", key="cgpa")
        grad_year  = st.text_input("Graduation Year", key="grad_year")

    # -------------------------
    # SKILLS
    # -------------------------
    st.header("Skills")
    programming = st.text_area("Programming Languages", key="programming")
    frameworks  = st.text_area("Frameworks / Libraries", key="frameworks")
    tools       = st.text_area("Tools & Technologies", key="tools")
    soft_skills = st.text_area("Soft Skills", key="soft_skills")

    # -------------------------
    # PROJECTS
    # -------------------------
    st.header("Projects")
    project_count = st.number_input("Number of Projects", 1, 5, 2, key="project_count")
    projects = []
    for i in range(int(project_count)):
        st.subheader(f"Project {i+1}")
        p_title = st.text_input(f"Project Title {i+1}",       key=f"project_title_{i}")
        p_desc  = st.text_area(f"Project Description {i+1}",  key=f"project_desc_{i}")
        p_tech  = st.text_input(f"Technologies Used {i+1}",   key=f"project_tech_{i}")
        projects.append((p_title, p_desc, p_tech))

    # -------------------------
    # EXPERIENCE
    # -------------------------
    st.header("Experience / Internship")
    exp_count = st.number_input("Number of Experiences", 0, 3, 1, key="exp_count")
    experiences = []
    for i in range(int(exp_count)):
        st.subheader(f"Experience {i+1}")
        e_company  = st.text_input(f"Company Name {i+1}",      key=f"company_{i}")
        e_role     = st.text_input(f"Role {i+1}",              key=f"role_{i}")
        e_duration = st.text_input(f"Duration {i+1}",          key=f"duration_{i}")
        e_desc     = st.text_area(f"Work Description {i+1}",   key=f"desc_{i}")
        experiences.append((e_company, e_role, e_duration, e_desc))

    # -------------------------
    # CERTIFICATIONS
    # -------------------------
    st.header("Certifications")
    certifications = st.text_area(
        "List Certifications (one per line)", key="certifications"
    )
    certificate_files = st.file_uploader(
        "Upload Certificates", type=["pdf","png","jpg"],
        accept_multiple_files=True, key="cert_files"
    )

    # -------------------------
    # GENERATE BUTTON
    # -------------------------
    if st.button("🚀 Generate Professional Resume", key="generate_resume"):

        if not name.strip() or not target_role.strip():
            st.warning("⚠️ Please fill in at least your Full Name and Target Role.")
            st.stop()

        # ── Helper: return value or "Not provided" ─────────────
        def val(v, fallback="Not provided"):
            return v.strip() if v and v.strip() else fallback

        # ── Build project text ─────────────────────────────────
        project_text = ""
        for p in projects:
            if p[0].strip():
                project_text += f"\nTitle      : {p[0]}\nDescription: {p[1]}\nTechnologies: {p[2]}\n"
        if not project_text:
            project_text = "No projects provided."

        # ── Build experience text ──────────────────────────────
        exp_text = ""
        for e in experiences:
            if e[0].strip():
                exp_text += f"\nCompany    : {e[0]}\nRole       : {e[1]}\nDuration   : {e[2]}\nDescription: {e[3]}\n"
        if not exp_text:
            exp_text = "No experience provided."

        # ── Build full details string ──────────────────────────
        details = f"""
PERSONAL INFORMATION
Name     : {val(name)}
Email    : {val(email)}
Phone    : {val(phone)}
LinkedIn : {val(linkedin)}
GitHub   : {val(github)}

TARGET ROLE: {val(target_role)}

EDUCATION
10th Grade  : School={val(tenth_school)}, Board={val(tenth_board)}, Marks={val(tenth_percentage)}%, Year={val(tenth_year)}
Intermediate: College={val(inter_college)}, Board={val(inter_board)}, Marks={val(inter_percentage)}%, Year={val(inter_year)}
Graduation  : Degree={val(degree)}, Branch={val(branch)}, University={val(university)}, CGPA={val(cgpa)}, Year={val(grad_year)}

SKILLS
Programming Languages : {val(programming)}
Frameworks/Libraries  : {val(frameworks)}
Tools & Technologies  : {val(tools)}
Soft Skills           : {val(soft_skills)}

PROJECTS
{project_text}

EXPERIENCE / INTERNSHIP
{exp_text}

CERTIFICATIONS
{val(certifications)}
"""

        # ── Generate resume via AI ─────────────────────────────
        with st.spinner("✍️ Generating your professional resume..."):
            resume = generate_advanced_resume(details, target_role)

        if not resume:
            st.error("❌ Resume generation failed. Please try again.")
            st.stop()

        # ── Preview ────────────────────────────────────────────
        st.markdown("---")
        st.subheader("📄 Resume Preview")
        st.text_area("", resume, height=500)

        # ── ATS Score ──────────────────────────────────────────
        skill_count = len([s for s in programming.split(",") if s.strip()])
        ats_score   = min(95, 60 + skill_count * 3)

        st.markdown("### 📊 ATS Score")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Score", f"{ats_score}/100")
        with col2:
            st.progress(ats_score / 100)

        if ats_score < 80:
            st.warning("💡 Tips to improve your ATS score:")
            st.write("• Add measurable achievements (e.g. 'Reduced load time by 40%')")
            st.write("• Include more technical keywords for your target role")
            st.write("• Add GitHub project links inside project descriptions")
            st.write("• Include internship or freelance experience")
        else:
            st.success("✅ Your resume is well-optimized for ATS systems.")

        # ── Save to DB ─────────────────────────────────────────
        save_resume(st.session_state.username, target_role, resume)

        # ── Generate Professional PDF ──────────────────────────
        try:
            from fpdf import FPDF

            BLUE       = (31,  73, 125)
            DARK       = (30,  30,  30)
            GRAY       = (80,  80,  80)
            LIGHT_BLUE = (235, 242, 250)
            WHITE      = (255, 255, 255)

            class ResumePDF(FPDF):
                def header(self):
                    pass
                def footer(self):
                    self.set_y(-12)
                    self.set_font("Arial", "I", 7)
                    self.set_text_color(*GRAY)
                    self.cell(
                        0, 8,
                        f"{name}  |  {target_role}  |  Page {self.page_no()}",
                        align="C"
                    )

            pdf = ResumePDF()
            pdf.set_margins(15, 15, 15)
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # ── Name ───────────────────────────────────────────
            pdf.set_font("Arial", "B", 20)
            pdf.set_text_color(*DARK)
            pdf.cell(0, 10, name.upper(), ln=True, align="C")

            # ── Contact line ───────────────────────────────────
            contact_parts = [
                x for x in [email, phone, linkedin, github] if x and x.strip()
            ]
            contact_line = "  |  ".join(contact_parts)
            pdf.set_font("Arial", "", 8)
            pdf.set_text_color(*GRAY)
            pdf.cell(0, 5, contact_line, ln=True, align="C")
            pdf.ln(2)

            # ── Top rule ───────────────────────────────────────
            pdf.set_draw_color(*BLUE)
            pdf.set_line_width(0.8)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(4)

            # ── Helpers ────────────────────────────────────────
            def section_heading(title):
                pdf.ln(3)
                pdf.set_font("Arial", "B", 10)
                pdf.set_text_color(*WHITE)
                pdf.set_fill_color(*BLUE)
                pdf.cell(0, 6, f"  {title}", ln=True, fill=True)
                pdf.ln(2)

            def bullet_line(text):
                pdf.set_font("Arial", "", 9)
                pdf.set_text_color(*DARK)
                pdf.cell(5, 5, chr(149), ln=False)
                pdf.multi_cell(0, 5, text.strip())

            def key_value(label, value):
                pdf.set_font("Arial", "B", 9)
                pdf.set_text_color(*DARK)
                pdf.cell(52, 5, label + ":", ln=False)
                pdf.set_font("Arial", "", 9)
                pdf.set_text_color(50, 50, 50)
                pdf.multi_cell(0, 5, value)

            def pipe_row(left, right):
                pdf.set_font("Arial", "B", 9)
                pdf.set_text_color(*DARK)
                pdf.cell(110, 6, left.strip(), ln=False)
                pdf.set_font("Arial", "I", 9)
                pdf.set_text_color(*GRAY)
                pdf.cell(0, 6, right.strip(), ln=True, align="R")

            def plain(text):
                pdf.set_font("Arial", "", 9)
                pdf.set_text_color(50, 50, 50)
                pdf.multi_cell(0, 5, text.strip())
                pdf.ln(1)

            # ── Parse resume lines ─────────────────────────────
            lines     = resume.split("\n")
            name_done = False
            idx       = 0

            while idx < len(lines):
                raw  = lines[idx]
                line = raw.strip()

                # Skip name line (already drawn)
                if not name_done and name.lower() in line.lower() and len(line) < 60:
                    name_done = True
                    idx += 1
                    continue

                # Skip contact line (already drawn)
                if "|" in line and (
                    "@" in line
                    or "linkedin" in line.lower()
                    or "github" in line.lower()
                    or (phone and phone in line)
                ):
                    idx += 1
                    continue

                # Skip separator lines  === --- ___
                if line and set(line).issubset(set("=-_ \t")) and len(line) > 3:
                    idx += 1
                    continue

                # Skip lines with markdown bold ** **
                line = line.replace("**", "")

                # Section heading — ALL CAPS, short, no bullets
                if (
                    line.isupper()
                    and 3 < len(line) < 50
                    and not line.startswith("-")
                    and not line.startswith("•")
                ):
                    section_heading(line)
                    idx += 1
                    continue

                # Bullet point
                if line.startswith(("-", "•", "*")):
                    content = line.lstrip("-•* ").strip()
                    if content:
                        bullet_line(content)
                    idx += 1
                    continue

                # Pipe row — "Project Title | Tech"  (no @ sign)
                if "|" in line and "@" not in line and len(line) < 120:
                    parts = line.split("|", 1)
                    pipe_row(parts[0], parts[1] if len(parts) > 1 else "")
                    idx += 1
                    continue

                # Key : Value  (Skills, Education labels)
                if ":" in line and not line.startswith("http") and len(line) < 150:
                    colon = line.index(":")
                    label = line[:colon].strip()
                    value = line[colon+1:].strip()
                    if label and value and len(label) < 35:
                        key_value(label, value)
                        idx += 1
                        continue

                # Non-empty plain line
                if line:
                    plain(line)

                idx += 1

            # ── Save & offer download ──────────────────────────
            safe_name = name.strip().replace(" ", "_")
            safe_role = target_role.strip().replace(" ", "_")
            pdf_path  = f"resume_{safe_name}_{safe_role}.pdf"
            pdf.output(pdf_path)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Professional Resume PDF",
                    data=f,
                    file_name=f"Resume_{safe_name}_{safe_role}.pdf",
                    mime="application/pdf"
                )

            st.success("✅ PDF ready! Click the button above to download.")

        except Exception as e:
            st.error(f"PDF generation error: {e}")
            st.write("You can still copy the resume text from the preview above.")
# =====================================================
# CAREER PREDICTOR
# =====================================================

elif page == "🎓Career Predictor":

    st.title("🎓 AI Career Predictor")

    skills = st.text_input("Your Skills (e.g. Python, SQL, Machine Learning)")
    interests = st.text_input("Your Interests (e.g. Data, AI, Web Development)")

    if st.button("Predict Career"):

        if not skills or not interests:
            st.warning("Please enter both skills and interests.")
        else:
            with st.spinner("Analyzing your profile..."):
                result = career_predictor(skills, interests)

            if not result:
                st.error("Could not generate prediction. Please try again.")
            else:
                # ── Reasoning ──────────────────────────────────────
                st.markdown("### 🧠 Why These Careers Fit You")
                st.info(result.get("reasoning", "N/A"))

                # ── Summary metrics ────────────────────────────────
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📈 Growth Potential", result.get("growth_potential", "N/A"))
                with col2:
                    st.metric("💰 Salary Projection", result.get("salary_projection", "N/A"))

                # ── Career Cards ───────────────────────────────────
                st.markdown("### 🚀 Best Career Paths")

                for i, career in enumerate(result.get("best_career_paths", [])):
                    with st.expander(f"#{i+1}  {career.get('title', 'Career')}"):
                        st.write("📋 **Description:**", career.get("description", ""))
                        st.write("💰 **Avg Salary:**", career.get("avg_salary", "N/A"))
                        st.write("📈 **Growth:**", career.get("growth", "N/A"))

                        skills_needed = career.get("required_skills", [])
                        if skills_needed:
                            st.write("🛠️ **Required Skills:**")
                            st.write("  " + "  |  ".join(skills_needed))

                # ── Next Steps ─────────────────────────────────────
                next_steps = result.get("next_steps", [])
                if next_steps:
                    st.markdown("### 👣 Recommended Next Steps")
                    for i, step in enumerate(next_steps, 1):
                        st.write(f"{i}. {step}")
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