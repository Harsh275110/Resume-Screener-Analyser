import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import plotly.express as px
import tempfile
from pathlib import Path
import logging
import plotly.graph_objects as go
import json

from resume_parser.parser import ResumeParser
from skills_analyzer.analyzer import SkillsAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="AI Resume Screener & Analyzer",
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
    .metric-card {
        border-radius: 5px;
        background-color: #f8f9fa;
        padding: 1rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 1rem;
        color: #6c757d;
    }
    .highlight {
        background-color: #ffed4a;
        padding: 0 0.2rem;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'parsed_resumes' not in st.session_state:
    st.session_state.parsed_resumes = []
if 'analyzed_resumes' not in st.session_state:
    st.session_state.analyzed_resumes = []
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'required_skills' not in st.session_state:
    st.session_state.required_skills = []
if 'preferred_skills' not in st.session_state:
    st.session_state.preferred_skills = []
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()

# Custom functions for the app
def process_resume_files(uploaded_files):
    """Process uploaded resume files."""
    if not uploaded_files:
        return
    
    parser = ResumeParser()
    
    for file in uploaded_files:
        # Save uploaded file to temp directory
        file_path = os.path.join(st.session_state.temp_dir, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        
        # Parse resume
        resume_data = parser.parse_resume(file_path)
        
        if resume_data:
            # Add to session state if not already present
            if not any(r.get('filename') == resume_data.get('filename') for r in st.session_state.parsed_resumes):
                st.session_state.parsed_resumes.append(resume_data)
                st.success(f"Successfully parsed resume: {file.name}")
            else:
                st.info(f"Resume already processed: {file.name}")
        else:
            st.error(f"Failed to parse resume: {file.name}")

def analyze_resumes():
    """Analyze all parsed resumes."""
    if not st.session_state.parsed_resumes:
        st.warning("No resumes to analyze. Please upload resumes first.")
        return
    
    if not st.session_state.job_description:
        st.warning("Please enter a job description first.")
        return
    
    analyzer = SkillsAnalyzer(
        job_description=st.session_state.job_description,
        required_skills=st.session_state.required_skills,
        preferred_skills=st.session_state.preferred_skills
    )
    
    analyzed_resumes = []
    for resume in st.session_state.parsed_resumes:
        analysis = analyzer.analyze_resume(resume)
        if analysis:
            analyzed_resumes.append(analysis)
    
    st.session_state.analyzed_resumes = analyzed_resumes
    
    if analyzed_resumes:
        st.success(f"Successfully analyzed {len(analyzed_resumes)} resumes.")
    else:
        st.error("Failed to analyze resumes.")

def display_resume_details(resume_data):
    """Display detailed information for a selected resume."""
    if not resume_data:
        return
    
    st.markdown(f"<h2 class='sub-header'>{resume_data.get('name', 'Unknown Candidate')}</h2>", unsafe_allow_html=True)
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'green' if resume_data.get('overall_score', 0) >= 70 else 'orange' if resume_data.get('overall_score', 0) >= 50 else 'red'};">
                    {resume_data.get('overall_score', 0)}%
                </div>
                <div class="metric-label">Overall Score</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'green' if resume_data.get('skills_match', {}).get('score', 0) >= 70 else 'orange' if resume_data.get('skills_match', {}).get('score', 0) >= 50 else 'red'};">
                    {resume_data.get('skills_match', {}).get('score', 0)}%
                </div>
                <div class="metric-label">Skills Match</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'green' if resume_data.get('experience_score', 0) >= 70 else 'orange' if resume_data.get('experience_score', 0) >= 50 else 'red'};">
                    {resume_data.get('experience_score', 0)}%
                </div>
                <div class="metric-label">Experience Match</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'green' if resume_data.get('education_score', 0) >= 70 else 'orange' if resume_data.get('education_score', 0) >= 50 else 'red'};">
                    {resume_data.get('education_score', 0)}%
                </div>
                <div class="metric-label">Education Match</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
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
            for skill in matched_required:
                st.markdown(f"<span style='background-color:#d4edda;padding:3px 8px;border-radius:10px;margin-right:5px;'>{skill}</span>", unsafe_allow_html=True)
        
        if missing_required:
            st.markdown("<p><strong>Missing Required Skills:</strong></p>", unsafe_allow_html=True)
            for skill in missing_required:
                st.markdown(f"<span style='background-color:#f8d7da;padding:3px 8px;border-radius:10px;margin-right:5px;'>{skill}</span>", unsafe_allow_html=True)
        
        # Preferred skills
        matched_preferred = resume_data.get('skills_match', {}).get('matched_preferred', [])
        
        if matched_preferred:
            st.markdown("<p><strong>Matched Preferred Skills:</strong></p>", unsafe_allow_html=True)
            for skill in matched_preferred:
                st.markdown(f"<span style='background-color:#d1ecf1;padding:3px 8px;border-radius:10px;margin-right:5px;'>{skill}</span>", unsafe_allow_html=True)
    
    with col2:
        # Radar chart for skills analysis
        categories = ['Required Skills', 'Preferred Skills', 'Experience', 'Education']
        values = [
            resume_data.get('skills_match', {}).get('required_match_percent', 0),
            resume_data.get('skills_match', {}).get('preferred_match_percent', 0),
            resume_data.get('experience_score', 0),
            resume_data.get('education_score', 0)
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Candidate Profile'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
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

# Main App UI
def main():
    # Sidebar for inputs
    with st.sidebar:
        st.markdown("<h2>Job Requirements</h2>", unsafe_allow_html=True)
        
        # Job Description
        st.markdown("<h3>Job Description</h3>", unsafe_allow_html=True)
        job_description = st.text_area("Enter job description", st.session_state.job_description, height=200)
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
        uploaded_files = st.file_uploader("Upload resumes", accept_multiple_files=True, type=["pdf", "docx", "txt"])
        
        if uploaded_files:
            if st.button("Process Resumes"):
                process_resume_files(uploaded_files)
        
        # Analyze button
        if st.session_state.parsed_resumes:
            if st.button("Analyze Resumes"):
                analyze_resumes()
        
        # Reset button
        if st.button("Reset All"):
            st.session_state.parsed_resumes = []
            st.session_state.analyzed_resumes = []
            st.experimental_rerun()
    
    # Main content
    st.markdown("<h1 class='main-header'>AI Resume Screener & Analyzer</h1>", unsafe_allow_html=True)
    
    # Summary Dashboard
    if st.session_state.analyzed_resumes:
        st.markdown("<h2 class='sub-header'>Resume Analysis Results</h2>", unsafe_allow_html=True)
        
        # Create dataframe from analyzed resumes
        df = pd.DataFrame([{
            'Name': r.get('name', 'Unknown'),
            'Overall Score': r.get('overall_score', 0),
            'Skills Match': r.get('skills_match', {}).get('score', 0),
            'Experience Match': r.get('experience_score', 0),
            'Education Match': r.get('education_score', 0),
            'Missing Required Skills': len(r.get('missing_required_skills', [])),
            'data': r  # Store the full data for later use
        } for r in st.session_state.analyzed_resumes])
        
        # Sort by overall score
        df = df.sort_values(by='Overall Score', ascending=False)
        
        # Create two columns for visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart of top candidates
            fig = px.bar(
                df.head(10),
                x='Name',
                y='Overall Score',
                color='Overall Score',
                color_continuous_scale=px.colors.sequential.Viridis,
                title="Top Candidates by Overall Score"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Scatter plot of skills vs experience
            fig = px.scatter(
                df,
                x='Skills Match',
                y='Experience Match',
                size='Overall Score',
                color='Overall Score',
                hover_name='Name',
                color_continuous_scale=px.colors.sequential.Viridis,
                title="Skills vs Experience Match"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Table of candidates
        st.markdown("<h3>Candidate Rankings</h3>", unsafe_allow_html=True)
        
        # Display dataframe without the 'data' column
        display_df = df.drop(columns=['data']).reset_index(drop=True)
        display_df.index = display_df.index + 1  # Start index from 1 instead of 0
        st.dataframe(display_df, use_container_width=True)
        
        # Detailed view for selected candidate
        st.markdown("<h3>Candidate Details</h3>", unsafe_allow_html=True)
        selected_candidate = st.selectbox(
            "Select a candidate to view details",
            options=df['Name'].tolist(),
            index=0
        )
        
        # Get the full data for the selected candidate
        selected_data = df[df['Name'] == selected_candidate]['data'].iloc[0]
        display_resume_details(selected_data)
    else:
        # Instructions if no resumes analyzed
        st.info("""
        👈 Start by uploading resumes and setting job requirements in the sidebar.
        
        This AI-powered resume screening tool will help you:
        - Extract key information from resumes automatically
        - Match candidate skills with job requirements
        - Score and rank candidates based on their qualifications
        - Analyze experience and education relevance
        
        Upload PDF, DOCX, or TXT resume files to get started.
        """)

if __name__ == "__main__":
    main() 