import streamlit as st
import PyPDF2
import re
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.pagesizes import letter
import tempfile

st.set_page_config(page_title="AI Resume Analyzer Pro", layout="wide")

st.title("📄 AI Resume Skill Gap Analyzer - Pro Version")

# ---------------- SKILL DATABASE ---------------- #

SKILL_DB = [
    "python", "java", "c++", "machine learning", "deep learning",
    "data science", "sql", "mysql", "mongodb", "excel",
    "power bi", "tableau", "html", "css", "javascript",
    "react", "node", "django", "flask", "tensorflow",
    "pytorch", "nlp", "aws", "azure", "docker",
    "kubernetes", "git", "linux", "communication",
    "teamwork", "problem solving", "leadership"
]

# ---------------- FUNCTIONS ---------------- #

def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILL_DB:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found_skills.append(skill)

    return set(found_skills)


def calculate_grade(score):
    if score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 50:
        return "C"
    else:
        return "D"


# ---------------- UI ---------------- #

uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area("Paste Job Description")

if uploaded_resume and job_description:

    resume_text = extract_text_from_pdf(uploaded_resume)

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    matched_skills = resume_skills.intersection(jd_skills)
    missing_skills = jd_skills - resume_skills

    if len(jd_skills) > 0:
        match_percentage = int((len(matched_skills) / len(jd_skills)) * 100)
    else:
        match_percentage = 0

    grade = calculate_grade(match_percentage)

    # ---------------- DISPLAY SCORE ---------------- #

    st.subheader("📊 Match Score")
    st.progress(match_percentage / 100)
    st.write(f"### {match_percentage}% Match")
    st.write(f"## 🎓 Grade: {grade}")

    # ---------------- GRAPH ---------------- #

    st.subheader("📈 Skill Comparison Graph")

    fig, ax = plt.subplots()
    categories = ["Matched Skills", "Missing Skills"]
    values = [len(matched_skills), len(missing_skills)]

    ax.bar(categories, values)
    ax.set_ylabel("Number of Skills")
    ax.set_title("Skill Gap Analysis")

    st.pyplot(fig)

    # ---------------- SKILL DISPLAY ---------------- #

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Matched Skills")
        for skill in sorted(matched_skills):
            st.write(f"- {skill.title()}")

    with col2:
        st.subheader("❌ Missing Skills")
        for skill in sorted(missing_skills):
            st.write(f"- {skill.title()}")

    # ---------------- AI SUGGESTIONS ---------------- #

    st.subheader("💡 Improvement Suggestions")

    if missing_skills:
        for skill in sorted(missing_skills):
            st.write(f"• Add projects or certifications in *{skill.title()}*")
    else:
        st.success("Excellent! Your resume matches the job requirements.")

    # ---------------- PDF REPORT GENERATION ---------------- #

    if st.button("📥 Download Report Card (PDF)"):

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp_file.name, pagesize=letter)

        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("AI Resume Analysis Report", styles['Title']))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph(f"Match Percentage: {match_percentage}%", styles['Normal']))
        elements.append(Paragraph(f"Grade: {grade}", styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph("Matched Skills:", styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))

        matched_list = [ListItem(Paragraph(skill.title(), styles['Normal'])) for skill in matched_skills]
        elements.append(ListFlowable(matched_list))

        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph("Missing Skills:", styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))

        missing_list = [ListItem(Paragraph(skill.title(), styles['Normal'])) for skill in missing_skills]
        elements.append(ListFlowable(missing_list))

        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph("Improvement Suggestions:", styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))

        suggestions = [
            ListItem(Paragraph(f"Improve {skill.title()} through projects or certifications.", styles['Normal']))
            for skill in missing_skills
        ]
        elements.append(ListFlowable(suggestions))

        doc.build(elements)

        with open(temp_file.name, "rb") as f:
            st.download_button(
                label="Click Here to Download PDF",
                data=f,
                file_name="Resume_Analysis_Report.pdf",
                mime="application/pdf"
            )

else:
    st.info("Upload resume and paste job description to begin analysis.")