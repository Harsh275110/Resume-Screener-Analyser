# AI Resume & Interview Analyzer

A powerful AI-driven tool for analyzing resumes against job descriptions and evaluating interview responses.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-FF4B4B)

## 🌟 Features

### Resume Analysis
- **Resume Parsing**: Extract key information from PDF, DOCX, and TXT resume files
- **Skills Matching**: Match candidate skills with job requirements
- **Job Description Analysis**: Upload and extract requirements from job descriptions
- **Candidate Ranking**: Score and rank candidates based on qualifications
- **Visualization**: Graphical representation of candidate scores and matches

### Interview Analysis
- **Interview Response Evaluation**: Analyze and score interview answers
- **Multi-Criteria Assessment**: Rate responses based on relevance, completeness, clarity, and technical accuracy
- **Detailed Feedback**: Provide specific feedback for each response
- **Interview Performance Summary**: Generate overall interview performance metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-resume-interview-analyzer.git
cd ai-resume-interview-analyzer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run simple_app.py
```

4. Open your browser and navigate to:
```
http://localhost:8501
```

## 📋 Usage Guide

### Resume Analysis Workflow

1. **Upload Job Description**:
   - Click "Upload Job Description" in the sidebar
   - Select a job description file (PDF, DOCX, or TXT)
   - Click "Process Job Description"
   - The system will extract the job title and required skills

2. **Manually Enter Requirements** (Optional):
   - Enter/edit job title
   - Enter/edit job description
   - Add required skills (one per line)
   - Add preferred skills (one per line)

3. **Upload Resumes**:
   - Click "Upload Resumes" in the sidebar
   - Select one or more resume files
   - Click "Process Resumes"

4. **Analyze Resumes**:
   - Click "Analyze Resumes" to evaluate candidates
   - View the ranking table and detailed analysis

### Interview Analysis Workflow

1. **Add Interview Responses**:
   - Enter an interview question
   - Enter the candidate's response
   - Click "Add Interview Response"
   - Repeat for additional questions

2. **Analyze Interview**:
   - Click "Analyze Interview" to evaluate responses
   - View the analysis results with scores and feedback

## 💻 Sample Files

The repository includes sample files to help you test the system:

- **job_description.txt**: Sample job description for a Data Science Manager
- **required_skills.txt**: List of required skills
- **preferred_skills.txt**: List of preferred skills
- **sarah_johnson_resume.txt**: Sample resume for testing
- **michael_chen_resume.txt**: Another sample resume for testing

## 🔍 Technical Details

The application is built with:

- **Streamlit**: For the web interface
- **Pandas**: For data manipulation and visualization
- **Regular Expressions**: For text extraction and analysis
- **File Handling Libraries**: For processing document formats

## 🚀 Upgrade Paths

The application can be enhanced with enterprise-level features:

### Free Tier Options
- **Cloud Storage**: Google Cloud Storage or AWS S3 (free tier available)
- **Database**: MongoDB Atlas (512MB free) or PostgreSQL via Heroku
- **CI/CD**: GitHub Actions (free for public repositories)
- **Containerization**: Docker (free for personal use)
- **Authentication**: Google OAuth (free)
- **Error Monitoring**: Sentry (free tier available)

### Implementation Timeline
1. **Basic Setup** (1-2 days): Docker containerization
2. **Data Persistence** (1-2 days): MongoDB Atlas integration
3. **Advanced Analysis** (2-3 days): BERT model integration
4. **API Creation** (2-3 days): FastAPI endpoints
5. **Deployment** (1 day): GitHub Actions CI/CD

See the `ENTERPRISE_UPGRADE.md` file for detailed implementation instructions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 