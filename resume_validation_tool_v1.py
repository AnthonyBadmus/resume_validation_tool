
import streamlit as st
import PyPDF2
from docx import Document
import re
import os 


# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from Word document
def extract_text_from_word(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Function to validate resume against requirements
def validate_resume(resume_text, requirements):
    # Convert both texts to lowercase for case-insensitive comparison
    resume_text = resume_text.lower()
    requirements = requirements.lower()

    # Count matching keywords
    matches = 0
    for word in requirements.split():
        if word in resume_text:
            matches += 1

    # Calculate match score
    total_words = len(requirements.split())
    match_score = (matches / total_words) * 100 if total_words > 0 else 0
    return match_score




# Streamlit App
def main():
    st.title("Resume Validation Tool")
    st.write("Upload a resume (PDF or Word) and enter the job requirements to validate.")

    # File upload
    uploaded_file = st.file_uploader("Upload Resume (PDF or Word)", type=["pdf", "docx"])

    # Job requirements input
    job_requirements = st.text_area("Enter Job Requirements (e.g., skills, experience, qualifications):")

    if uploaded_file and job_requirements:
        # Extract text from the uploaded file
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_word(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a PDF or Word document.")
            return

        # Validate resume
        match_score = validate_resume(resume_text, job_requirements)
        st.write(f"Resume Match Score: {match_score:.2f}%")

        # Display validation result
        if match_score >= 70:
            st.success("This resume is a good match for the job requirements!")
        elif match_score >= 50:
            st.warning("This resume partially matches the job requirements.")
        else:
            st.error("This resume does not meet the job requirements.")

if __name__ == "__main__":
    main()