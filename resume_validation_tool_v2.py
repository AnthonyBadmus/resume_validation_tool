import streamlit as st
import PyPDF2
from docx import Document
import sqlite3
import os
import spacy
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Load NLP models
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Database setup
def init_db():
    conn = sqlite3.connect("resumes.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS resumes 
                 (id TEXT PRIMARY KEY, resume_text TEXT, job_requirements TEXT, job_title TEXT, score REAL)''')
    conn.commit()
    conn.close()

def save_to_db(resume_id, resume_text, job_requirements, job_title, score):
    conn = sqlite3.connect("resumes.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO resumes (id, resume_text, job_requirements, job_title, score) VALUES (?, ?, ?, ?, ?)", 
              (resume_id, resume_text, job_requirements, job_title, score))
    conn.commit()
    conn.close()

def load_from_db():
    conn = sqlite3.connect("resumes.db")
    c = conn.cursor()
    c.execute("SELECT * FROM resumes")
    rows = c.fetchall()
    conn.close()
    return rows

def count_resumes_in_db():
    conn = sqlite3.connect("resumes.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM resumes")
    count = c.fetchone()[0]
    conn.close()
    return count

# Extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Extract text from Word document
def extract_text_from_word(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Extract specific sections using spaCy
def extract_sections(text):
    doc = nlp(text)
    sections = {"skills": [], "technical strength": [], "experience": [], "education": []}
    for sent in doc.sents:
        s = sent.text.lower()
        if "skills" in s:
            sections["skills"].append(sent.text)
        elif "technical strength" in s:
            sections["technical strength"].append(sent.text)
        elif "experience" in s:
            sections["experience"].append(sent.text)
        elif "education" in s:
            sections["education"].append(sent.text)
    return sections

# Semantic similarity using Sentence Transformers
def semantic_matching(resume_text, job_requirements):
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_requirements, convert_to_tensor=True)
    similarity_score = util.cos_sim(resume_embedding, job_embedding).item()
    return similarity_score * 100

# Streamlit App
def main():
    init_db()
    st.title("📄 Resume Validation Tool")
    st.write("Upload a resume (PDF or Word) and enter the job requirements to validate using semantic similarity.")
    st.markdown(f"**Total Resumes in Database:** {count_resumes_in_db()}")

    uploaded_file = st.file_uploader("Upload Resume (PDF or Word)", type=["pdf", "docx"])
    job_title = st.text_input("Enter Job Title (e.g., Data Scientist, Backend Engineer)")
    job_requirements = st.text_area("Enter Job Requirements (e.g., skills, experience, qualifications):")

    if uploaded_file and job_requirements and job_title:
        file_name = uploaded_file.name
        base_name = os.path.splitext(file_name)[0]
        resume_id = f'C-{base_name}'

        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_word(uploaded_file)
        else:
            st.error("Unsupported file format.")
            return

        sections = extract_sections(resume_text)
        st.subheader("🧩 Extracted Resume Sections")
        st.write("**Skills:**", " ".join(sections["skills"]))
        st.write("**Technical Strength:**", " ".join(sections["technical strength"]))
        st.write("**Experience:**", " ".join(sections["experience"]))
        st.write("**Education:**", " ".join(sections["education"]))

        match_score = semantic_matching(resume_text, job_requirements)
        st.write(f"🧠 Semantic Resume Match Score: **{match_score:.2f}%**")

        if match_score >= 70:
            st.success("✅ This resume is a good match for the job requirements!")
        elif match_score >= 50:
            st.warning("⚠️ This resume partially matches the job requirements.")
        else:
            st.error("❌ This resume does not meet the job requirements.")

        save_to_db(resume_id, resume_text, job_requirements, job_title, match_score)

    st.subheader("🗂️ Previously Processed Resumes")

    min_score = st.slider("Minimum Score to Display", min_value=0, max_value=100, value=0, step=1)
    job_title_filter = st.text_input("Filter by Job Title (optional):")

    if st.button("Load Saved Resumes"):
        rows = load_from_db()
        if rows:
            filtered_rows = [
                row for row in rows 
                if row[4] >= min_score and (job_title_filter.lower() in row[3].lower() if job_title_filter else True)
            ]
            if filtered_rows:
                for row in filtered_rows:
                    with st.expander(f"📁 ID: {row[0]} | Job Title: {row[3]} | Score: {row[4]:.2f}%"):
                        # st.markdown("**Full Resume Text:**")
                        # st.text(row[1])
                        st.markdown("**Job Requirements:**")
                        st.text(row[2])
            else:
                st.info("No resumes match the selected filters.")
        else:
            st.info("No resumes saved in the database yet.")

    st.subheader("📥 Export Resumes Database as CSV")

    if st.button("Export to CSV"):
        conn = sqlite3.connect("resumes.db")
        df = pd.read_sql_query("SELECT * FROM resumes", conn)
        conn.close()
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='resumes_export.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()
