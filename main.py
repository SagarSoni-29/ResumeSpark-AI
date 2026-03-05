import streamlit as st
import os
import requests
import json
import hashlib
from io import BytesIO
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from streamlit_lottie import st_lottie
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import pickle

# Config
st.set_page_config(page_title="ResumeSpark AI", layout="wide")

# LOAD ENV
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"

client = InferenceClient(model=HF_MODEL, token=HF_API_KEY)

# Lottie File
def load_lottie_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

lottie_auth = load_lottie_file("lottie_auth.json")
lottie_res = load_lottie_file("Resume.json")

# Session State
USER_FILE = "users.pkl"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "wb") as f:
        pickle.dump(users, f)

# Initializing users properly
if "users" not in st.session_state:
    st.session_state.users = load_users()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "auth"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# PDF Function
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    for line in text.split("\n"):
        if line.strip() == "":
            story.append(Spacer(1, 12))
        else:
            story.append(Paragraph(line, styles["Normal"]))
    doc.build(story)
    buffer.seek(0)
    return buffer

# Authentication
if st.session_state.page == "auth":

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        if lottie_auth:
            st_lottie(lottie_auth, height=200, key="auth_anim")

        st.markdown("<h2 style='text-align:center;'> Member Access</h2>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        # Login Tab
        with tab1:
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login", key="login_btn", use_container_width=True):

                if login_user in st.session_state.users and \
                   st.session_state.users[login_user] == hash_password(login_pass):

                    st.session_state.authenticated = True
                    st.session_state.username = login_user
                    st.session_state.page = "landing"
                    st.rerun()

                else:
                    st.error("Invalid Credentials")

        # Signup Tab
        with tab2:
            new_user = st.text_input("New Username", key="signup_user")
            new_pass = st.text_input("New Password", type="password", key="signup_pass")

            if st.button("Create Account", key="signup_btn", use_container_width=True):

                if new_user.strip() == "" or new_pass.strip() == "":
                    st.error("Fields cannot be empty")

                elif new_user in st.session_state.users:
                    st.error("Username already exists")

                else:
                    st.session_state.users[new_user] = hash_password(new_pass)
                    save_users(st.session_state.users)
                    st.success("Account created successfully!")
# Landing Page
elif st.session_state.page == "landing":
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        if lottie_res:
            st_lottie(lottie_res, height=350, key="landing_main_anim")

    st.markdown("""
###  Welcome to ResumeSpark AI

ResumeSpark AI is an intelligent career document generator designed to create 
ATS-friendly resumes and professional cover letters in seconds.

 What makes it powerful?

- AI-optimized formatting for modern hiring systems  
- Clean corporate structure  
- Personalized career summaries  
- Professional PDF export  
- Designed for students, freshers & professionals  

Build your career documents smarter, faster, and better.
""")
    
    if st.button(" Get Started Now", type="primary", use_container_width=True):
            st.session_state.page = "generator"
            st.rerun()
    st.stop()

# Generator Page
elif st.session_state.page == "generator":

    # Sidebar
    st.sidebar.title(" ResumeSpark AI")
    st.sidebar.markdown("---")

    st.sidebar.info(f"""
         👤 Hii **{st.session_state.username}**   
         Version: 1.0  
         Created by Sagar Soni  
                    """)
    st.sidebar.markdown("---")

    st.sidebar.markdown("###  Tips :")
    st.sidebar.markdown("""
         Use measurable achievements  
        - Keep skills relevant  
        - Be concise  
        - Avoid generic statements  
        """)
    
    st.sidebar.markdown("---")

    st.title(" AI Resume & Cover Letter Generator")
    st.markdown("Create professional, ATS-friendly documents instantly.")

    doc_type = st.sidebar.radio(
        "**Select Document Type**",
        ["Resume", "Cover Letter"]
    )

    if st.sidebar.button(" Logout"):
        st.session_state.page = "auth"
        st.session_state.authenticated = False
        st.rerun()

    # Form
    with st.form("resume_form"):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone Number *")
            education = st.text_area("Education *")
            skills = st.text_area("Skills (comma separated) *")
            strengths = st.text_area("Key Strengths (e.g., leadership, problem-solving, quick learner)")

        with col2:
            experience = st.text_area("Work Experience *")
            projects = st.text_area("Projects *")
            job_role = st.text_input("Job Role Applying For *")
            company = st.text_input("Company Name")
            career_level = st.selectbox( "Career Level", ["Student", "Fresher", "Junior Professional (1-3 yrs)",  "Mid-Level (3-7 yrs)", "Senior Professional (7+ yrs)"])
            career_goal = st.text_area("Career Objective / Goal")

        submit = st.form_submit_button(" Generate Document")

# PDF Function
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def create_pdf(text, name, email, phone):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Styles
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Normal'],
        fontSize=22,
        spaceAfter=6,
        alignment=1,
        leading=26
    )

    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.grey,
        alignment=1,
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Normal'],
        fontSize=13,
        spaceBefore=12,
        spaceAfter=6,
        leading=16
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        spaceAfter=6
    )
     
    # Header
    story.append(Paragraph(f"<b>{name}</b>", name_style))
    story.append(Paragraph(f"{email} | {phone}", contact_style))

    # Body
    for line in text.split("\n"):

        line = line.strip()

        if not line:
            story.append(Spacer(1, 10))

        elif line.isupper():
            story.append(Spacer(1, 14))
            story.append(Paragraph(f"<b>{line}</b>", section_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
            story.append(Spacer(1, 6))

        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

    # Generation Logic
if "submit" in locals() and submit:

        required = [name, email, phone, education, skills, experience, projects, job_role]

        if any(f.strip() == "" for f in required):
            st.error("⚠ Please fill all required fields.")
        else:
            with st.spinner(" AI is crafting your professional document..."):

                # Prompt
                if doc_type == "Resume":
                    inst = """
Generate a clean, ATS-friendly professional resume.

Formatting Rules:
- Do NOT use markdown symbols like ** or *
- Use clear section headings in ALL CAPS
- Add proper line breaks between sections
- Use bullet points using '-' only
- Keep it clean and corporate style
- No decorative symbols

Sections Required:
PROFESSIONAL SUMMARY
EDUCATION
SKILLS
WORK EXPERIENCE
PROJECTS
"""

                elif doc_type == "Cover Letter":
                    inst = f"""
Generate a formal and professional cover letter.

Formatting Rules:
- No markdown formatting
- Proper paragraph spacing
- Business tone
- No asterisks or decorative characters
- Clear introduction, body, and conclusion
- Keep it concise and impactful

Position: {job_role}
Company: {company}
"""

                else:
                    inst = f"""
Generate BOTH a professional ATS-friendly resume AND a formal cover letter.

Formatting Rules:
- No markdown formatting
- Clean section headings
- Professional tone
- Separate Resume and Cover Letter clearly
- No decorative symbols
"""

                prompt = f"""
{inst}

Candidate Details:
Name: {name}
Email: {email}
Phone: {phone}

Education:
{education}

Skills:
{skills}

Work Experience:
{experience}

Projects:
{projects}

Career Level:
{career_level}

Career Objective:
{career_goal}

Key Strengths:
{strengths}
"""

                try:
                    response = client.chat_completion(
                        messages=[
                            {"role": "system", "content": "You are a professional resume and career document writer."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.5,
                        max_tokens=1500
                    )

                    output_text = response.choices[0].message.content
                    output_text = output_text.replace("**", "")
                    output_text = output_text.replace("*", "")

                    st.success(" Document Generated Successfully!")

                    # Preview
                    st.markdown("##  Preview")
                    st.markdown(
                        f"""
                        <div style="
                            background-color:#f8f9fa;
                            padding:25px;
                            border-radius:12px;
                            white-space:pre-line;
                            font-family:Arial;
                            font-size:14px;
                            line-height:1.6;
                        ">
                        {output_text}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # PDF Download
                    pdf_buffer = create_pdf(output_text, name, email, phone)

                    st.download_button(
                        " Download as PDF",
                        data=pdf_buffer,
                        file_name="ResumeSpark_Output.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f" Error: {e}")