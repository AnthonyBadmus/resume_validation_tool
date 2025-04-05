# 📄 Resume Validation Tool

The **Resume Validation Tool** is a Streamlit-based web application that allows users to upload resumes (PDF or Word documents) and validate them against job requirements using semantic similarity. It also provides functionality to extract key sections from resumes, save results to a database, and export the data as a CSV file.

---

## 🚀 Features

- **Resume Upload**: Supports PDF and Word document formats.
- **Semantic Matching**: Uses Sentence Transformers to calculate a similarity score between the resume and job requirements.
- **Resume Section Extraction**: Extracts key sections like skills, experience, education, and technical strengths using spaCy.
- **Database Integration**: Saves processed resumes and their scores in an SQLite database.
- **Filter and Export**: Allows filtering resumes by score or job title and exporting the database as a CSV file.

---

## 🛠️ Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/resume_validation_tool.git
   cd resume_validation_tool
