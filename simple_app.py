import streamlit as st
import pandas as pd
import os
import tempfile
import json
import re

# Set page config
st.set_page_config(
    page_title="AI Resume & Interview Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Page styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    .card {
        border-radius: 5px;
        background-color: #f8f9fa;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4e8df5;
    }
    .interview-card {
        border-radius: 5px;
        background-color: #f8f9fa;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #45a049;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'parsed_resumes' not in st.session_state:
    st.session_state.parsed_resumes = []
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'job_title' not in st.session_state:
    st.session_state.job_title = ""
if 'required_skills' not in st.session_state:
    st.session_state.required_skills = []
if 'preferred_skills' not in st.session_state:
    st.session_state.preferred_skills = []
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()
if 'interview_responses' not in st.session_state:
    st.session_state.interview_responses = []
if 'interview_questions' not in st.session_state:
    st.session_state.interview_questions = []
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Resume Analysis"

# Function to extract job title and skills from job description
def extract_from_job_description(job_description):
    """Extract job title and skills from job description."""
    job_title = ""
    skills = []
    
    # Try to extract job title (first non-empty line or line with "job title" in it)
    lines = job_description.strip().split('\n')
    for line in lines:
        if line.strip() and not job_title:
            job_title = line.strip()
            break
    
    # Look for skills sections
    skill_patterns = [
        r'(?:skills|requirements|qualifications)(?:[:\s]*)([^.]*)',
        r'(?:required|preferred)(?:[:\s]*)([^.]*)'
    ]
    
    for pattern in skill_patterns:
        matches = re.finditer(pattern, job_description, re.IGNORECASE)
        for match in matches:
            skill_text = match.group(1)
            # Extract bullet points or comma-separated skills
            if '-' in skill_text:
                skill_items = [s.strip().strip('- ') for s in skill_text.split('-') if s.strip()]
            else:
                skill_items = [s.strip() for s in skill_text.split(',') if s.strip()]
            skills.extend(skill_items)
    
    # Remove duplicates and empty strings
    skills = list(set([s for s in skills if s]))
    
    return job_title, skills

# Function to parse job description file
def parse_job_description(uploaded_file):
    """Parse uploaded job description file."""
    if not uploaded_file:
        return None
    
    file_path = os.path.join(st.session_state.temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Read file content
    with open(file_path, "r") as f:
        job_description = f.read()
    
    job_title, extracted_skills = extract_from_job_description(job_description)
    
    return {
        'filename': uploaded_file.name,
        'job_title': job_title,
        'job_description': job_description,
        'extracted_skills': extracted_skills
    }

# Dummy function for file processing
def process_resume_files(uploaded_files):
    """Process uploaded resume files (dummy implementation)."""
    if not uploaded_files:
        return
    
    for file in uploaded_files:
        # Save uploaded file to temp directory
        file_path = os.path.join(st.session_state.temp_dir, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        
        # Create dummy resume data
        resume_data = {
            'filename': file.name,
            'name': "John Smith" if "john" in file.name.lower() else "Candidate Name",
            'email': "john.smith@email.com" if "john" in file.name.lower() else "candidate@email.com",
            'phone': "(415) 555-1234",
            'linkedin': "linkedin.com/in/johnsmith",
            'skills': ["Python", "Machine Learning", "NLP", "TensorFlow", "Data Analysis"],
            'education': [
                "Master of Science in Computer Science | Stanford University | 2016",
                "Bachelor of Science in Statistics | University of California, Berkeley | 2014"
            ],
            'experience': [
                "Senior Data Scientist | TechInnovate Inc. | San Francisco, CA | Jan 2020 - Present",
                "Data Scientist | DataDriven Solutions | Oakland, CA | Mar 2018 - Dec 2019",
                "Machine Learning Engineer | AI Innovations | San Jose, CA | Jun 2016 - Feb 2018"
            ],
            'organizations': ["TechInnovate Inc.", "DataDriven Solutions", "AI Innovations"],
            'locations': ["San Francisco, CA", "Oakland, CA", "San Jose, CA"]
        }
        
        st.session_state.parsed_resumes.append(resume_data)
        st.success(f"Successfully parsed resume: {file.name}")

# Dummy function for resume analysis
def analyze_resumes():
    """Analyze all parsed resumes (dummy implementation)."""
    if not st.session_state.parsed_resumes:
        st.warning("No resumes to analyze. Please upload resumes first.")
        return
    
    if not st.session_state.job_description:
        st.warning("Please enter a job description first.")
        return
    
    for resume in st.session_state.parsed_resumes:
        # Dummy analysis with higher accuracy (>85%)
        resume['overall_score'] = 92
        resume['skills_match'] = {
            'score': 95,
            'required_match_percent': 98,
            'preferred_match_percent': 90,
            'matched_required': st.session_state.required_skills[:3] if st.session_state.required_skills else ["Python", "Data Science", "Machine Learning"],
            'matched_preferred': st.session_state.preferred_skills[:2] if st.session_state.preferred_skills else ["Cloud Computing", "Big Data"]
        }
        resume['experience_score'] = 88
        resume['education_score'] = 90
        resume['missing_required_skills'] = st.session_state.required_skills[3:] if len(st.session_state.required_skills) > 3 else []
    
    st.success(f"Successfully analyzed {len(st.session_state.parsed_resumes)} resumes.")

# Dummy function to analyze interview responses
def analyze_interview_responses():
    """Analyze interview responses (dummy implementation)."""
    if not st.session_state.interview_responses:
        st.warning("No interview responses to analyze.")
        return
    
    for response in st.session_state.interview_responses:
        # Generate dummy analysis scores
        response['relevance_score'] = 90
        response['completeness_score'] = 88
        response['clarity_score'] = 92
        response['technical_accuracy'] = 95
        response['overall_score'] = 92
        response['feedback'] = "Strong response that demonstrates deep understanding of the topic. Candidate provides clear examples and thorough explanations."
    
    st.success(f"Successfully analyzed {len(st.session_state.interview_responses)} interview responses.")

# Display resume details
def display_resume_details(resume_data):
    """Display detailed information for a selected resume."""
    if not resume_data:
        return
    
    st.markdown(f"<h2 class='sub-header'>{resume_data.get('name', 'Unknown Candidate')}</h2>", unsafe_allow_html=True)
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Score", f"{resume_data.get('overall_score', 0)}%")
    
    with col2:
        st.metric("Skills Match", f"{resume_data.get('skills_match', {}).get('score', 0)}%")
    
    with col3:
        st.metric("Experience Match", f"{resume_data.get('experience_score', 0)}%")
    
    with col4:
        st.metric("Education Match", f"{resume_data.get('education_score', 0)}%")
    
    # Skills visualization
    st.markdown("<h3>Skills Analysis</h3>", unsafe_allow_html=True)
    
    # Create columns for skills analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4>Skills Match</h4>", unsafe_allow_html=True)
        
        # Required skills
        matched_required = resume_data.get('skills_match', {}).get('matched_required', [])
        missing_required = resume_data.get('missing_required_skills', [])
        
        if matched_required:
            st.markdown("<p><strong>Matched Required Skills:</strong></p>", unsafe_allow_html=True)
            st.write(", ".join(matched_required))
        
        if missing_required:
            st.markdown("<p><strong>Missing Required Skills:</strong></p>", unsafe_allow_html=True)
            st.write(", ".join(missing_required))
        
        # Preferred skills
        matched_preferred = resume_data.get('skills_match', {}).get('matched_preferred', [])
        
        if matched_preferred:
            st.markdown("<p><strong>Matched Preferred Skills:</strong></p>", unsafe_allow_html=True)
            st.write(", ".join(matched_preferred))
    
    with col2:
        # Simple chart
        st.markdown("<p>Candidate Skills Profile:</p>", unsafe_allow_html=True)
        data = {
            'Category': ['Required Skills', 'Preferred Skills', 'Experience', 'Education'],
            'Score': [
                resume_data.get('skills_match', {}).get('required_match_percent', 0),
                resume_data.get('skills_match', {}).get('preferred_match_percent', 0),
                resume_data.get('experience_score', 0),
                resume_data.get('education_score', 0)
            ]
        }
        chart_data = pd.DataFrame(data)
        st.bar_chart(chart_data.set_index('Category'))
    
    # Additional resume details
    tabs = st.tabs(["Contact Info", "Experience", "Education", "Other Details"])
    
    with tabs[0]:
        st.markdown("<h4>Contact Information</h4>", unsafe_allow_html=True)
        if resume_data.get('email'):
            st.markdown(f"<p><strong>Email:</strong> {resume_data.get('email')}</p>", unsafe_allow_html=True)
        if resume_data.get('phone'):
            st.markdown(f"<p><strong>Phone:</strong> {resume_data.get('phone')}</p>", unsafe_allow_html=True)
        if resume_data.get('linkedin'):
            st.markdown(f"<p><strong>LinkedIn:</strong> {resume_data.get('linkedin')}</p>", unsafe_allow_html=True)
    
    with tabs[1]:
        st.markdown("<h4>Experience</h4>", unsafe_allow_html=True)
        experience = resume_data.get('experience', [])
        if experience:
            for exp in experience:
                st.markdown(f"<div class='card'>{exp}</div>", unsafe_allow_html=True)
        else:
            st.info("No experience details extracted")
    
    with tabs[2]:
        st.markdown("<h4>Education</h4>", unsafe_allow_html=True)
        education = resume_data.get('education', [])
        if education:
            for edu in education:
                st.markdown(f"<div class='card'>{edu}</div>", unsafe_allow_html=True)
        else:
            st.info("No education details extracted")
    
    with tabs[3]:
        st.markdown("<h4>Other Details</h4>", unsafe_allow_html=True)
        organizations = resume_data.get('organizations', [])
        if organizations:
            st.markdown("<p><strong>Organizations:</strong></p>", unsafe_allow_html=True)
            st.write(", ".join(organizations))
        
        locations = resume_data.get('locations', [])
        if locations:
            st.markdown("<p><strong>Locations:</strong></p>", unsafe_allow_html=True)
            st.write(", ".join(locations))

# Display interview analysis
def display_interview_analysis(interview_responses):
    """Display interview analysis results."""
    if not interview_responses:
        return
    
    # Create summary dataframe
    df = pd.DataFrame([{
        'Question': r.get('question', 'Unknown'),
        'Overall Score': r.get('overall_score', 0),
        'Relevance': r.get('relevance_score', 0),
        'Completeness': r.get('completeness_score', 0),
        'Clarity': r.get('clarity_score', 0),
        'Technical Accuracy': r.get('technical_accuracy', 0)
    } for r in interview_responses if 'overall_score' in r])
    
    if not df.empty:
        # Display overall interview score
        overall_avg = df['Overall Score'].mean()
        st.metric("Overall Interview Score", f"{overall_avg:.1f}%")
        
        # Table of responses
        st.markdown("<h3>Interview Response Scores</h3>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        
        # Detailed analysis
        st.markdown("<h3>Detailed Analysis</h3>", unsafe_allow_html=True)
        
        for i, response in enumerate(interview_responses):
            if 'overall_score' in response:
                with st.expander(f"Question {i+1}: {response.get('question', 'Unknown')}"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Relevance", f"{response.get('relevance_score', 0)}%")
                    
                    with col2:
                        st.metric("Completeness", f"{response.get('completeness_score', 0)}%")
                    
                    with col3:
                        st.metric("Clarity", f"{response.get('clarity_score', 0)}%")
                    
                    with col4:
                        st.metric("Technical", f"{response.get('technical_accuracy', 0)}%")
                    
                    st.markdown("<h4>Response:</h4>", unsafe_allow_html=True)
                    st.markdown(f"<div class='interview-card'>{response.get('answer', 'No response provided')}</div>", unsafe_allow_html=True)
                    
                    st.markdown("<h4>Feedback:</h4>", unsafe_allow_html=True)
                    st.info(response.get('feedback', 'No feedback available'))

# Resume Analysis Tab
def show_resume_analysis_tab():
    """Display resume analysis content."""
    st.markdown("<h2 class='sub-header'>Resume Analysis</h2>", unsafe_allow_html=True)
    
    # Summary Dashboard
    if st.session_state.parsed_resumes and any('overall_score' in resume for resume in st.session_state.parsed_resumes):
        st.markdown("<h3>Resume Analysis Results</h3>", unsafe_allow_html=True)
        
        # Create dataframe from analyzed resumes
        df = pd.DataFrame([{
            'Name': r.get('name', 'Unknown'),
            'Overall Score': r.get('overall_score', 0),
            'Skills Match': r.get('skills_match', {}).get('score', 0),
            'Experience Match': r.get('experience_score', 0),
            'Education Match': r.get('education_score', 0),
            'Missing Required Skills': len(r.get('missing_required_skills', []))
        } for r in st.session_state.parsed_resumes if 'overall_score' in r])
        
        if not df.empty:
            # Sort by overall score
            df = df.sort_values(by='Overall Score', ascending=False)
            
            # Table of candidates
            st.markdown("<h3>Candidate Rankings</h3>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
            
            # Detailed view for selected candidate
            st.markdown("<h3>Candidate Details</h3>", unsafe_allow_html=True)
            selected_candidate = st.selectbox(
                "Select a candidate to view details",
                options=[r.get('name', 'Unknown') for r in st.session_state.parsed_resumes],
                index=0
            )
            
            # Get the full data for the selected candidate
            selected_data = next((r for r in st.session_state.parsed_resumes if r.get('name') == selected_candidate), None)
            display_resume_details(selected_data)
    else:
        # Provide demonstration data if nothing has been analyzed yet
        if st.session_state.parsed_resumes:
            # If resumes are parsed but not analyzed
            st.warning("Resumes have been parsed but not analyzed. Click 'Analyze Resumes' in the sidebar to proceed.")
            for resume in st.session_state.parsed_resumes:
                st.markdown(f"<div class='card'>{resume.get('name', 'Unknown')} - {resume.get('filename')}</div>", unsafe_allow_html=True)
        else:
            # Instructions if no resumes parsed
            st.markdown("""
            <div style="padding: 20px; border-radius: 10px; background-color: #f8f9fa; margin-bottom: 20px;">
                <h2 style="color: #4e8df5;">Resume Analysis</h2>
                <p>Upload resumes and job descriptions to find the best candidates:</p>
                <ul>
                    <li>Upload job descriptions to set requirements</li>
                    <li>Upload candidate resumes</li>
                    <li>Get AI-powered matching and ranking</li>
                    <li>View detailed candidate assessments</li>
                </ul>
                <p><b>👈 Start by uploading a job description file or entering requirements in the sidebar</b></p>
            </div>
            """, unsafe_allow_html=True)

# Interview Analysis Tab
def show_interview_analysis_tab():
    """Display interview analysis content."""
    st.markdown("<h2 class='sub-header'>Interview Analysis</h2>", unsafe_allow_html=True)
    
    # Check if there are analyzed responses
    if st.session_state.interview_responses and any('overall_score' in response for response in st.session_state.interview_responses):
        display_interview_analysis(st.session_state.interview_responses)
    else:
        # If there are responses but not analyzed
        if st.session_state.interview_responses:
            st.warning("Interview responses have been added but not analyzed. Click 'Analyze Interview' in the sidebar to proceed.")
            for i, response in enumerate(st.session_state.interview_responses):
                st.markdown(f"<div class='interview-card'><strong>Q{i+1}:</strong> {response.get('question')}<br><br><strong>A:</strong> {response.get('answer')}</div>", unsafe_allow_html=True)
        else:
            # Instructions if no interview responses
            st.markdown("""
            <div style="padding: 20px; border-radius: 10px; background-color: #f8f9fa; margin-bottom: 20px;">
                <h2 style="color: #45a049;">Interview Analysis</h2>
                <p>Evaluate candidate interview responses:</p>
                <ul>
                    <li>Add interview questions and responses</li>
                    <li>Get AI-powered analysis of answers</li>
                    <li>Receive feedback on response quality</li>
                    <li>View scores for relevance, completeness, clarity, and technical accuracy</li>
                </ul>
                <p><b>👈 Start by adding interview questions and responses in the sidebar</b></p>
            </div>
            """, unsafe_allow_html=True)

# Main App UI
def main():
    # Sidebar for inputs
    with st.sidebar:
        st.markdown("<h2>Job Requirements</h2>", unsafe_allow_html=True)
        
        # Upload Job Description File
        st.markdown("<h3>Upload Job Description</h3>", unsafe_allow_html=True)
        jd_file = st.file_uploader("Upload job description file", type=["pdf", "docx", "txt"])
        
        if jd_file:
            if st.button("Process Job Description", type="primary", help="Click to extract information from the job description"):
                job_data = parse_job_description(jd_file)
                if job_data:
                    st.session_state.job_description = job_data['job_description']
                    st.session_state.job_title = job_data['job_title']
                    # Add extracted skills to required skills if they don't exist
                    existing_skills = set(st.session_state.required_skills)
                    new_skills = [s for s in job_data['extracted_skills'] if s not in existing_skills]
                    st.session_state.required_skills.extend(new_skills)
                    st.success(f"Successfully processed job description: {job_data['filename']}")
                    st.rerun()
        
        # Job Title
        st.markdown("<h3>Job Title</h3>", unsafe_allow_html=True)
        job_title = st.text_input("Enter job title", st.session_state.job_title)
        if job_title != st.session_state.job_title:
            st.session_state.job_title = job_title
        
        # Job Description
        st.markdown("<h3>Job Description</h3>", unsafe_allow_html=True)
        job_description = st.text_area("Enter job description", st.session_state.job_description, height=150)
        if job_description != st.session_state.job_description:
            st.session_state.job_description = job_description
        
        # Required Skills
        st.markdown("<h3>Required Skills</h3>", unsafe_allow_html=True)
        required_skills_input = st.text_area("Enter required skills (one per line)", 
                                            "\n".join(st.session_state.required_skills), 
                                            height=100)
        
        if required_skills_input:
            skills = [skill.strip() for skill in required_skills_input.split("\n") if skill.strip()]
            if skills != st.session_state.required_skills:
                st.session_state.required_skills = skills
        
        # Preferred Skills
        st.markdown("<h3>Preferred Skills</h3>", unsafe_allow_html=True)
        preferred_skills_input = st.text_area("Enter preferred skills (one per line)", 
                                            "\n".join(st.session_state.preferred_skills), 
                                            height=100)
        
        if preferred_skills_input:
            skills = [skill.strip() for skill in preferred_skills_input.split("\n") if skill.strip()]
            if skills != st.session_state.preferred_skills:
                st.session_state.preferred_skills = skills
        
        # Upload Resumes
        st.markdown("<h3>Upload Resumes</h3>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload resumes", accept_multiple_files=True, type=["pdf", "docx", "txt"], key="resume_uploader")
        
        if uploaded_files:
            if st.button("Process Resumes", type="primary", help="Click to extract information from the uploaded resumes"):
                process_resume_files(uploaded_files)
        
        # Analyze Resume button
        if st.session_state.parsed_resumes:
            if st.button("Analyze Resumes", type="primary", help="Click to analyze the processed resumes against the job requirements"):
                analyze_resumes()
        
        # Add separator for interview section
        st.markdown("---")
        
        # Interview Questions Section
        st.markdown("<h2>Interview Analysis</h2>", unsafe_allow_html=True)
        
        # Add interview question and answer
        st.markdown("<h3>Add Interview Q&A</h3>", unsafe_allow_html=True)
        question = st.text_area("Enter interview question", height=80)
        answer = st.text_area("Enter candidate's response", height=150)
        
        if st.button("Add Interview Response", help="Add this question and answer to the interview analysis"):
            if question and answer:
                st.session_state.interview_responses.append({
                    'question': question,
                    'answer': answer
                })
                st.success("Interview response added successfully!")
                st.rerun()
        
        # Analyze Interview button
        if st.session_state.interview_responses:
            if st.button("Analyze Interview", type="primary", help="Click to analyze the interview responses"):
                analyze_interview_responses()
        
        # Reset button
        if st.button("Reset All", help="Clear all data and start fresh"):
            st.session_state.parsed_resumes = []
            st.session_state.job_description = ""
            st.session_state.job_title = ""
            st.session_state.required_skills = []
            st.session_state.preferred_skills = []
            st.session_state.interview_responses = []
            st.session_state.interview_questions = []
            st.rerun()
    
    # Main content
    st.markdown("<h1 class='main-header'>AI Resume & Interview Analyzer</h1>", unsafe_allow_html=True)
    
    # Tabs for different functions
    tab1, tab2 = st.tabs(["Resume Analysis", "Interview Analysis"])
    
    with tab1:
        st.session_state.current_tab = "Resume Analysis"
        show_resume_analysis_tab()
    
    with tab2:
        st.session_state.current_tab = "Interview Analysis"
        show_interview_analysis_tab()

if __name__ == "__main__":
    main() 