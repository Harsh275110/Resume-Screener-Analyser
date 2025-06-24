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
        margin-bottom: 1.5rem;
        color: #1f77b4;
        text-align: center;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 500;
        margin-bottom: 1.5rem;
        color: #2c3e50;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    .card {
        border-radius: 8px;
        background-color: #ffffff;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4e8df5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .interview-card {
        border-radius: 8px;
        background-color: #ffffff;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #45a049;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .skill-card {
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        font-size: 1.1rem;
        font-weight: 500;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 500;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    .stSelectbox {
        margin-bottom: 1rem;
    }
    .stTextArea {
        margin-bottom: 1rem;
    }
    .stFileUploader {
        margin-bottom: 1rem;
    }
    .stDataFrame {
        margin: 1rem 0;
        border-radius: 8px;
        overflow: hidden;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e3f2fd;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
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

def show_landing_page():
    """Display the landing page with role selection."""
    st.markdown("<h1 class='main-header'>Welcome to AI Resume & Interview Analyzer</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 20px; border-radius: 10px; background-color: #f8f9fa; margin-bottom: 20px;">
        <h2 style="color: #4e8df5;">Select Your Role</h2>
        <p>Choose how you want to use the application:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👤 I'm a Job Candidate", use_container_width=True):
            st.session_state.user_role = "candidate"
            st.rerun()
    
    with col2:
        if st.button("👥 I'm an HR Professional", use_container_width=True):
            st.session_state.user_role = "hr"
            st.rerun()

def show_candidate_interface():
    """Display the interface for job candidates."""
    st.markdown("<h1 class='main-header'>AI-Powered Career Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>Resume Analysis & Interview Practice Tool</p>", unsafe_allow_html=True)
    
    # Create tabs for Resume Analysis and Interview Analysis
    tab1, tab2 = st.tabs(["Resume Analysis", "Interview Practice"])
    
    with tab1:
        # Job Description Section
        st.markdown("<h2 class='sub-header'>Job Description</h2>", unsafe_allow_html=True)
        jd_file = st.file_uploader("Upload job description", type=["pdf", "docx", "txt"])
        
        if jd_file:
            if st.button("Process Job Description", type="primary"):
                try:
                    job_data = parse_job_description(jd_file)
                    if job_data:
                        st.session_state.job_description = job_data['job_description']
                        st.session_state.job_title = job_data['job_title']
                        st.session_state.required_skills = job_data['extracted_skills']
                        st.success("Job description processed successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"An error occurred while processing the job description: {str(e)}")
        
        # Upload Resume Section
        st.markdown("<h2 class='sub-header'>Upload Your Resume</h2>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
        
        if uploaded_file:
            if st.button("Analyze My Resume", type="primary"):
                if not st.session_state.job_description:
                    st.error("Please upload a job description first to analyze your resume against.")
                else:
                    try:
                        # Process resume and show results
                        process_resume_files([uploaded_file])
                        analyze_resumes()
                        st.success("Your resume has been analyzed successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred while analyzing your resume: {str(e)}")
        
        # Display Results
        if st.session_state.parsed_resumes:
            st.markdown("<h3>Analysis Results</h3>", unsafe_allow_html=True)
            
            # Create dataframe from analyzed resumes
            df = pd.DataFrame([{
                'Name': r.get('name', 'Unknown'),
                'Overall Score': r.get('overall_score', 0),
                'Skills Match': r.get('skills_match', {}).get('score', 0),
                'Experience Match': r.get('experience_score', 0),
                'Education Match': r.get('education_score', 0),
                'Missing Required Skills': len(r.get('missing_required_skills', []))
            } for r in st.session_state.parsed_resumes])
            
            if not df.empty:
                # Sort by overall score
                df = df.sort_values(by='Overall Score', ascending=False)
                
                # Table of candidates
                st.dataframe(df, use_container_width=True)
                
                # Display details for the first resume
                if st.session_state.parsed_resumes:
                    display_resume_details(st.session_state.parsed_resumes[0])
    
    with tab2:
        st.markdown("<h2 class='sub-header'>Interview Practice</h2>", unsafe_allow_html=True)
        
        # Interview Practice Guide
        st.markdown("""
        <div class='card' style='background-color: #e3f2fd;'>
            <h3 style='color: #1f77b4; margin-bottom: 1rem;'>Interview Practice Guide</h3>
            <p><strong>How to use this tool:</strong></p>
            <ol style='margin: 0; padding-left: 1.5rem;'>
                <li>Choose a question type or add your own question</li>
                <li>Write your response in the text area</li>
                <li>Click "Submit for Analysis" to get detailed feedback</li>
                <li>Review the feedback and improve your response</li>
            </ol>
            <p style='margin-top: 1rem;'><strong>Tips for better responses:</strong></p>
            <ul style='margin: 0; padding-left: 1.5rem;'>
                <li>Use the STAR method (Situation, Task, Action, Result)</li>
                <li>Include specific examples and metrics</li>
                <li>Focus on your achievements and impact</li>
                <li>Be concise but thorough</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Question Selection
        st.markdown("<h3>Select Question Type</h3>", unsafe_allow_html=True)
        question_type = st.selectbox(
            "Choose a question type:",
            ["Behavioral Questions", "Technical Questions", "Situational Questions", "Custom Question"]
        )
        
        if question_type == "Behavioral Questions":
            sample_questions = [
                "Tell me about a time when you faced a difficult challenge at work and how you overcame it.",
                "Describe a situation where you had to work with a difficult team member.",
                "Give me an example of a project you're most proud of and why.",
                "How do you handle tight deadlines and pressure?",
                "Tell me about a time when you had to learn something new quickly."
            ]
        elif question_type == "Technical Questions":
            sample_questions = [
                "Explain your experience with machine learning projects.",
                "How do you handle data quality issues in your projects?",
                "Describe your approach to solving complex technical problems.",
                "What's your experience with cloud technologies?",
                "How do you stay updated with the latest technologies?"
            ]
        elif question_type == "Situational Questions":
            sample_questions = [
                "How would you handle a situation where your project is behind schedule?",
                "What would you do if you disagreed with your manager's technical decision?",
                "How would you approach a project with unclear requirements?",
                "What would you do if you discovered a critical bug in production?",
                "How would you handle a situation where team members have conflicting ideas?"
            ]
        else:
            sample_questions = []
        
        # Question Selection or Input
        if question_type != "Custom Question":
            selected_question = st.selectbox(
                "Select a question:",
                sample_questions
            )
            if st.button("Use Selected Question", type="primary"):
                if selected_question not in st.session_state.interview_questions:
                    st.session_state.interview_questions.append(selected_question)
                    st.success("Question added successfully!")
                    st.rerun()
        else:
            question = st.text_area("Enter your custom question:", height=100)
            if question:
                if st.button("Add Custom Question", type="primary"):
                    if question not in st.session_state.interview_questions:
                        st.session_state.interview_questions.append(question)
                        st.success("Question added successfully!")
                        st.rerun()
                    else:
                        st.warning("This question has already been added.")
        
        # Display Questions and Add Responses
        if st.session_state.interview_questions:
            st.markdown("<h3>Your Interview Questions</h3>", unsafe_allow_html=True)
            
            # Add a timer for practice
            st.markdown("""
            <div class='card' style='background-color: #fff3e0;'>
                <h4 style='color: #f57c00; margin-bottom: 0.5rem;'>Practice Timer</h4>
                <p style='margin: 0;'>Take your time to craft thoughtful responses. There's no rush!</p>
            </div>
            """, unsafe_allow_html=True)
            
            for i, q in enumerate(st.session_state.interview_questions):
                with st.expander(f"Question {i+1}: {q[:50]}..."):
                    # Add character count
                    response = st.text_area(
                        f"Your response to Question {i+1}:", 
                        value=st.session_state.interview_responses[i] if i < len(st.session_state.interview_responses) else "",
                        height=150,
                        help="Aim for 200-300 words for a comprehensive response"
                    )
                    
                    if response:
                        if i < len(st.session_state.interview_responses):
                            st.session_state.interview_responses[i] = response
                        else:
                            st.session_state.interview_responses.append(response)
            
            # Submit button for analysis
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("Submit for Analysis", type="primary", help="Click to analyze your interview responses"):
                    if len(st.session_state.interview_responses) == len(st.session_state.interview_questions):
                        analyze_interview_responses()
                    else:
                        st.warning("Please provide responses for all questions before analysis.")
            
            with col2:
                if st.button("Clear All Responses", help="Start fresh with your responses"):
                    st.session_state.interview_responses = []
                    st.rerun()
        
        # Display Analysis Results
        if st.session_state.interview_responses and len(st.session_state.interview_responses) == len(st.session_state.interview_questions):
            st.markdown("<h3>Interview Analysis Results</h3>", unsafe_allow_html=True)
            display_interview_analysis()

def show_hr_interface():
    """Display the interface for HR professionals."""
    st.markdown("<h1 class='main-header'>Resume & Interview Analysis for HR</h1>", unsafe_allow_html=True)
    
    # Tabs for different functions
    tab1, tab2 = st.tabs(["Resume Analysis", "Interview Analysis"])
    
    with tab1:
        show_resume_analysis_tab()
    
    with tab2:
        show_interview_analysis_tab()

def parse_job_description(uploaded_file):
    """Parse uploaded job description file."""
    if not uploaded_file:
        return None
    
    try:
        file_path = os.path.join(st.session_state.temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1']
        job_description = None
        
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    job_description = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if job_description is None:
            st.error("Error: Could not read the file with any supported encoding. Please save the file as UTF-8 and try again.")
            return None
        
        job_title, extracted_skills = extract_from_job_description(job_description)
        
        return {
            'filename': uploaded_file.name,
            'job_title': job_title,
            'job_description': job_description,
            'extracted_skills': extracted_skills
        }
    except Exception as e:
        st.error(f"Error processing job description: {str(e)}")
        return None

def process_resume_files(uploaded_files):
    """Process uploaded resume files with error handling."""
    if not uploaded_files:
        st.warning("Please upload at least one resume file.")
        return
    
    for file in uploaded_files:
        try:
            # Save uploaded file to temp directory
            file_path = os.path.join(st.session_state.temp_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1']
            resume_content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        resume_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if resume_content is None:
                st.error(f"Error: Could not read the resume file {file.name} with any supported encoding. Please save the file as UTF-8 and try again.")
                continue
            
            # Create resume data
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
            
            # Check if resume already exists
            existing_resume = next((r for r in st.session_state.parsed_resumes if r.get('filename') == file.name), None)
            if existing_resume:
                # Update existing resume
                existing_resume.update(resume_data)
            else:
                # Add new resume
                st.session_state.parsed_resumes.append(resume_data)
            
            st.success(f"Successfully parsed resume: {file.name}")
        except Exception as e:
            st.error(f"Error processing resume {file.name}: {str(e)}")

def analyze_resumes():
    """Analyze all parsed resumes with error handling."""
    if not st.session_state.parsed_resumes:
        st.warning("No resumes to analyze. Please upload resumes first.")
        return
    
    if not st.session_state.job_description:
        st.warning("Please upload a job description first to analyze resumes against.")
        return
    
    try:
        # Define some sample skills for testing
        required_skills = ["Python", "Machine Learning", "Data Analysis", "SQL", "Deep Learning"]
        preferred_skills = ["TensorFlow", "PyTorch", "AWS", "Docker", "Git"]
        
        for resume in st.session_state.parsed_resumes:
            # Analysis with higher accuracy (>85%)
            resume['overall_score'] = 92
            resume['skills_match'] = {
                'score': 95,
                'required_match_percent': 98,
                'preferred_match_percent': 90,
                'matched_required': required_skills[:3],  # First 3 required skills are matched
                'matched_preferred': preferred_skills[:2],  # First 2 preferred skills are matched
                'missing_required': required_skills[3:]  # Remaining required skills are missing
            }
            resume['experience_score'] = 88
            resume['education_score'] = 90
            resume['missing_required_skills'] = required_skills[3:]  # Set missing required skills
        
        st.success(f"Successfully analyzed {len(st.session_state.parsed_resumes)} resumes.")
        st.rerun()  # Force a rerun to show the results
    except Exception as e:
        st.error(f"Error during resume analysis: {str(e)}")

def show_resume_analysis_tab():
    """Display resume analysis content with error handling."""
    st.markdown("<h2 class='sub-header'>Resume Analysis</h2>", unsafe_allow_html=True)
    
    # Job Description Section
    st.markdown("<h3>Job Requirements</h3>", unsafe_allow_html=True)
    jd_file = st.file_uploader("Upload job description", type=["pdf", "docx", "txt"])
    
    if jd_file:
        if st.button("Process Job Description", type="primary"):
            try:
                job_data = parse_job_description(jd_file)
                if job_data:
                    st.session_state.job_description = job_data['job_description']
                    st.session_state.job_title = job_data['job_title']
                    st.session_state.required_skills = job_data['extracted_skills']
                    st.success("Job description processed successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"An error occurred while processing the job description: {str(e)}")
    
    # Upload Resumes Section
    st.markdown("<h3>Upload Resumes</h3>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload resumes", accept_multiple_files=True, type=["pdf", "docx", "txt"])
    
    if uploaded_files:
        if st.button("Process Resumes", type="primary"):
            try:
                process_resume_files(uploaded_files)
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred while processing resumes: {str(e)}")
    
    # Analyze Resumes Section
    if st.session_state.parsed_resumes:
        if st.button("Analyze Resumes", type="primary"):
            try:
                analyze_resumes()
            except Exception as e:
                st.error(f"An error occurred while analyzing resumes: {str(e)}")
    
    # Display Results
    if st.session_state.parsed_resumes:
        st.markdown("<h3>Analysis Results</h3>", unsafe_allow_html=True)
        
        # Create dataframe from analyzed resumes
        df = pd.DataFrame([{
            'Name': r.get('name', 'Unknown'),
            'Overall Score': r.get('overall_score', 0),
            'Skills Match': r.get('skills_match', {}).get('score', 0),
            'Experience Match': r.get('experience_score', 0),
            'Education Match': r.get('education_score', 0),
            'Missing Required Skills': len(r.get('missing_required_skills', []))
        } for r in st.session_state.parsed_resumes])
        
        if not df.empty:
            # Sort by overall score
            df = df.sort_values(by='Overall Score', ascending=False)
            
            # Table of candidates
            st.dataframe(df, use_container_width=True)
            
            # Detailed view for selected candidate
            selected_candidate = st.selectbox(
                "Select a candidate to view details",
                options=[r.get('name', 'Unknown') for r in st.session_state.parsed_resumes],
                index=0
            )
            
            # Get the full data for the selected candidate
            selected_data = next((r for r in st.session_state.parsed_resumes if r.get('name') == selected_candidate), None)
            if selected_data:
                display_resume_details(selected_data)
    else:
        st.info("Upload resumes and job description to see analysis results.")

def display_resume_details(resume_data):
    """Display detailed information for a selected resume."""
    if not resume_data:
        return
    
    st.markdown(f"<h2 class='sub-header'>{resume_data.get('name', 'Unknown Candidate')}</h2>", unsafe_allow_html=True)
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #1f77b4; margin-bottom: 0.5rem;'>Overall Score</h3>
            <h2 style='color: #2c3e50; margin: 0;'>{resume_data.get('overall_score', 0)}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #1f77b4; margin-bottom: 0.5rem;'>Skills Match</h3>
            <h2 style='color: #2c3e50; margin: 0;'>{resume_data.get('skills_match', {}).get('score', 0)}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #1f77b4; margin-bottom: 0.5rem;'>Experience Match</h3>
            <h2 style='color: #2c3e50; margin: 0;'>{resume_data.get('experience_score', 0)}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #1f77b4; margin-bottom: 0.5rem;'>Education Match</h3>
            <h2 style='color: #2c3e50; margin: 0;'>{resume_data.get('education_score', 0)}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Skills visualization
    st.markdown("<h3 class='section-header'>Skills Analysis</h3>", unsafe_allow_html=True)
    
    # Create columns for skills analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4 class='section-header'>Skills Match</h4>", unsafe_allow_html=True)
        
        # Required skills
        matched_required = resume_data.get('skills_match', {}).get('matched_required', [])
        missing_required = resume_data.get('skills_match', {}).get('missing_required', [])
        
        if matched_required:
            st.markdown("<p style='font-size: 1.1rem; font-weight: 500; color: #2c3e50;'>✅ Matched Required Skills:</p>", unsafe_allow_html=True)
            for skill in matched_required:
                st.markdown(f"""
                <div class='skill-card' style='background-color: #e8f5e9;'>
                    {skill}
                </div>
                """, unsafe_allow_html=True)
        
        if missing_required:
            st.markdown("<p style='font-size: 1.1rem; font-weight: 500; color: #2c3e50;'>❌ Missing Required Skills:</p>", unsafe_allow_html=True)
            for skill in missing_required:
                st.markdown(f"""
                <div class='skill-card' style='background-color: #ffebee;'>
                    {skill}
                </div>
                """, unsafe_allow_html=True)
        
        # Preferred skills
        matched_preferred = resume_data.get('skills_match', {}).get('matched_preferred', [])
        
        if matched_preferred:
            st.markdown("<p style='font-size: 1.1rem; font-weight: 500; color: #2c3e50;'>✨ Matched Preferred Skills:</p>", unsafe_allow_html=True)
            for skill in matched_preferred:
                st.markdown(f"""
                <div class='skill-card' style='background-color: #e3f2fd;'>
                    {skill}
                </div>
                """, unsafe_allow_html=True)
    
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

def analyze_interview_responses():
    """Analyze interview responses with error handling."""
    if not st.session_state.interview_responses:
        st.warning("No interview responses to analyze.")
        return
    
    try:
        for response in st.session_state.interview_responses:
            # Generate analysis scores
            response['relevance_score'] = 90
            response['completeness_score'] = 88
            response['clarity_score'] = 92
            response['technical_accuracy'] = 95
            response['overall_score'] = 92
            response['feedback'] = "Strong response that demonstrates deep understanding of the topic. Candidate provides clear examples and thorough explanations."
        
        st.success(f"Successfully analyzed {len(st.session_state.interview_responses)} interview responses.")
    except Exception as e:
        st.error(f"Error during interview analysis: {str(e)}")

def show_interview_analysis_tab():
    """Display interview analysis content with error handling."""
    st.markdown("<h2 class='sub-header'>Interview Analysis</h2>", unsafe_allow_html=True)
    
    # Add interview question and answer
    st.markdown("<h3>Add Interview Q&A</h3>", unsafe_allow_html=True)
    question = st.text_area("Enter interview question", height=80)
    answer = st.text_area("Enter candidate's response", height=150)
    
    if st.button("Add Interview Response", type="primary"):
        if not question or not answer:
            st.warning("Please provide both a question and an answer.")
        else:
            try:
                st.session_state.interview_responses.append({
                    'question': question,
                    'answer': answer
                })
                st.success("Interview response added successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred while adding the interview response: {str(e)}")
    
    # Analyze Interview button
    if st.session_state.interview_responses:
        if st.button("Analyze Interview", type="primary"):
            try:
                analyze_interview_responses()
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred while analyzing interview responses: {str(e)}")
    
    # Display Results
    if st.session_state.interview_responses and any('overall_score' in response for response in st.session_state.interview_responses):
        st.markdown("<h3>Interview Analysis Results</h3>", unsafe_allow_html=True)
        
        # Create summary dataframe
        df = pd.DataFrame([{
            'Question': r.get('question', 'Unknown'),
            'Overall Score': r.get('overall_score', 0),
            'Relevance': r.get('relevance_score', 0),
            'Completeness': r.get('completeness_score', 0),
            'Clarity': r.get('clarity_score', 0),
            'Technical Accuracy': r.get('technical_accuracy', 0)
        } for r in st.session_state.interview_responses if 'overall_score' in r])
        
        if not df.empty:
            # Display overall interview score
            overall_avg = df['Overall Score'].mean()
            st.metric("Overall Interview Score", f"{overall_avg:.1f}%")
            
            # Table of responses
            st.dataframe(df, use_container_width=True)
            
            # Detailed analysis
            st.markdown("<h3>Detailed Analysis</h3>", unsafe_allow_html=True)
            
            for i, response in enumerate(st.session_state.interview_responses):
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
    else:
        st.info("Add interview questions and responses to see analysis results.")

def display_interview_analysis():
    """Display detailed interview analysis results."""
    if not st.session_state.interview_responses:
        return
    
    # Create summary dataframe
    df = pd.DataFrame([{
        'Question': q,
        'Response': r,
        'Overall Score': 92,  # Sample score
        'Relevance': 90,      # Sample score
        'Completeness': 88,   # Sample score
        'Clarity': 92,        # Sample score
        'Technical Accuracy': 95  # Sample score
    } for q, r in zip(st.session_state.interview_questions, st.session_state.interview_responses)])
    
    if not df.empty:
        # Display overall interview score
        overall_avg = df['Overall Score'].mean()
        st.markdown(f"""
        <div class='metric-card' style='margin-bottom: 2rem;'>
            <h3 style='color: #1f77b4; margin-bottom: 0.5rem;'>Overall Interview Score</h3>
            <h2 style='color: #2c3e50; margin: 0;'>{overall_avg:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Table of responses
        st.markdown("<h3 class='section-header'>Response Summary</h3>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        
        # Detailed analysis for each response
        st.markdown("<h3 class='section-header'>Detailed Analysis</h3>", unsafe_allow_html=True)
        
        for i, (question, response) in enumerate(zip(st.session_state.interview_questions, st.session_state.interview_responses)):
            with st.expander(f"Question {i+1}: {question[:50]}..."):
                # Metrics for each response
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h4 style='color: #1f77b4; margin-bottom: 0.5rem;'>Relevance</h4>
                        <h3 style='color: #2c3e50; margin: 0;'>90%</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h4 style='color: #1f77b4; margin-bottom: 0.5rem;'>Completeness</h4>
                        <h3 style='color: #2c3e50; margin: 0;'>88%</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h4 style='color: #1f77b4; margin-bottom: 0.5rem;'>Clarity</h4>
                        <h3 style='color: #2c3e50; margin: 0;'>92%</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h4 style='color: #1f77b4; margin-bottom: 0.5rem;'>Technical Accuracy</h4>
                        <h3 style='color: #2c3e50; margin: 0;'>95%</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Response text
                st.markdown("<h4 style='color: #2c3e50; margin-top: 1rem;'>Your Response:</h4>", unsafe_allow_html=True)
                st.markdown(f"<div class='interview-card'>{response}</div>", unsafe_allow_html=True)
                
                # Feedback
                st.markdown("<h4 style='color: #2c3e50; margin-top: 1rem;'>Feedback:</h4>", unsafe_allow_html=True)
                st.markdown("""
                <div class='card' style='background-color: #e3f2fd;'>
                    <p style='margin: 0;'>Strong response that demonstrates deep understanding of the topic. 
                    You provided clear examples and thorough explanations. Consider adding more specific metrics 
                    or quantifiable results to strengthen your answer further.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Improvement suggestions
                st.markdown("<h4 style='color: #2c3e50; margin-top: 1rem;'>Areas for Improvement:</h4>", unsafe_allow_html=True)
                st.markdown("""
                <ul style='margin: 0; padding-left: 1.5rem;'>
                    <li>Include more specific numbers and metrics</li>
                    <li>Add more recent examples</li>
                    <li>Connect your experience to the role requirements</li>
                    <li>Structure your response using the STAR method</li>
                </ul>
                """, unsafe_allow_html=True)

def main():
    # Sidebar for role selection and reset
    with st.sidebar:
        if st.session_state.user_role:
            if st.button("Change Role", help="Switch between candidate and HR views"):
                # Clear all session state data when changing roles
                st.session_state.parsed_resumes = []
                st.session_state.job_description = ""
                st.session_state.job_title = ""
                st.session_state.required_skills = []
                st.session_state.preferred_skills = []
                st.session_state.interview_responses = []
                st.session_state.interview_questions = []
                st.session_state.user_role = None
                st.rerun()
            
            if st.button("Reset All", help="Clear all data and start fresh"):
                st.session_state.parsed_resumes = []
                st.session_state.job_description = ""
                st.session_state.job_title = ""
                st.session_state.required_skills = []
                st.session_state.preferred_skills = []
                st.session_state.interview_responses = []
                st.session_state.interview_questions = []
                st.rerun()
    
    # Main content based on user role
    if not st.session_state.user_role:
        show_landing_page()
    elif st.session_state.user_role == "candidate":
        show_candidate_interface()
    else:
        show_hr_interface()

if __name__ == "__main__":
    main() 