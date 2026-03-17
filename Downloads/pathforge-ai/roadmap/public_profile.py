import streamlit as st
import matplotlib.pyplot as plt
import sqlite3
from database import get_user_stats, calculate_user_rank

DB_NAME = "career_platform.db"


def show_public_profile(username):

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # get profile info
    c.execute("SELECT bio, profile_pic FROM users WHERE username=?", (username,))
    data = c.fetchone()

    bio = data[0] if data and data[0] else "No bio added"
    profile_pic = data[1] if data and data[1] else None

    # get latest resume
    c.execute("""
    SELECT content
    FROM resumes
    WHERE username=?
    ORDER BY date DESC
    LIMIT 1
    """, (username,))

    resume = c.fetchone()
    resume = resume[0] if resume else "No resume available"

    # get stats
    stats = get_user_stats(username)

    # FIX: define variables from stats
    avg_interview = stats["avg_interview"]
    job_readiness = stats["job_readiness"]
    career_score = stats["career_score"]
    target_role = stats["target_role"]

    rank = calculate_user_rank(career_score)

    st.title("Public Profile")

    # profile header
    col1, col2 = st.columns([1, 3])

    with col1:

        if profile_pic:
            st.image(profile_pic, width=150)

        else:
            st.image(
                "https://cdn-icons-png.flaticon.com/512/149/149071.png",
                width=150
            )

    with col2:

        st.markdown(f"## {username}")
        st.write(bio)

        st.write("**Target Role:**", target_role)
        st.write("**Rank:**", rank)

    st.divider()

    # career score
    st.subheader("Career Score")

    st.progress(career_score / 100)

    st.metric("Score", f"{career_score} / 100")

    st.divider()

    # performance stats
    st.subheader("Performance Analytics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Quiz Average", stats["avg_quiz"])
    col2.metric("Interview Average", avg_interview)
    col3.metric("Job Readiness", job_readiness)

    st.divider()

    # resume preview
    st.subheader("Latest Resume")

    st.text_area("Resume Preview", resume, height=300)

    st.download_button(
        "Download Resume",
        resume,
        file_name=f"{username}_resume.txt"
    )

    # ACHIEVEMENTS
    # ==========================

    st.markdown("### 🏆 Achievements")

    badges = []

    # get quiz scores
    c.execute(
        "SELECT score FROM quiz_attempts WHERE username=?",
        (username,)
    )

    quiz_scores = c.fetchall()

    if quiz_scores:
        avg_quiz = sum([q[0] for q in quiz_scores]) / len(quiz_scores)
    else:
        avg_quiz = 0

    if avg_quiz > 80:
        badges.append("🧠 Quiz Master")

    if avg_interview > 80:
        badges.append("🎤 Interview Pro")

    if job_readiness > 85:
        badges.append("🚀 Job Ready Elite")

    if career_score > 90:
        badges.append("🔥 Top Performer")

    if badges:
        for badge in badges:
            st.success(badge)
    else:
        st.info("No achievements unlocked yet.")

    # ==========================
    # PERFORMANCE GRAPH
    # ==========================

    st.markdown("### 📈 Performance Overview")

    scores = [avg_quiz, avg_interview, job_readiness]
    labels = ["Quiz", "Interview", "Job Readiness"]

    fig = plt.figure()
    plt.plot(labels, scores)
    plt.ylim(0, 100)
    plt.xlabel("Category")
    plt.ylabel("Score")
    plt.title("Performance Overview")

    st.pyplot(fig)

    # ==========================
    # HEADER SECTION
    # ==========================

    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(
            profile_pic or
            "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
            width=140
        )

    with col2:
        st.markdown(f"## {username}")
        st.write(target_role)

        st.markdown(
            f"### 💯 Career Score: {career_score} / 100"
        )

        rank = calculate_user_rank(career_score)
        st.markdown(f"### 🏅 Rank: {rank}")

    # ==========================
    # QUIZ PERFORMANCE
    # ==========================

    st.markdown("### 📊 Quiz Performance")
    st.progress(avg_quiz / 100)
    st.write(f"Average Quiz Score: {round(avg_quiz, 2)}%")

    # ==========================
    # INTERVIEW PERFORMANCE
    # ==========================

    st.markdown("### 🎤 Interview Performance")
    st.progress(avg_interview / 100)
    st.write(f"Average Interview Score: {round(avg_interview, 2)}%")

    # ==========================
    # JOB READINESS
    # ==========================

    st.markdown("### 🚀 Job Readiness")
    st.progress(job_readiness / 100)
    st.write(f"Job Readiness Score: {round(job_readiness, 2)}%")

    

    # ==========================
    # PUBLIC SHAREABLE LINK
    # ==========================

    st.markdown("### 🔗 Public Profile Link")
    public_url = f"http://localhost:8501/?profile={username}"
    st.code(public_url)

    conn.close()