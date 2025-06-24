import re
import logging
import numpy as np
import pandas as pd
import os
from utils.nlp_utils import calculate_similarity, preprocess_text, remove_stopwords, lemmatize_text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SkillsAnalyzer:
    """Class to analyze and score resumes based on job requirements."""
    
    def __init__(self, job_description=None, required_skills=None, preferred_skills=None):
        """
        Initialize SkillsAnalyzer.
        
        Args:
            job_description (str, optional): Job description text. Defaults to None.
            required_skills (list, optional): List of required skills. Defaults to None.
            preferred_skills (list, optional): List of preferred skills. Defaults to None.
        """
        self.job_description = job_description
        self.required_skills = required_skills if required_skills else []
        self.preferred_skills = preferred_skills if preferred_skills else []
        
        # Weights for scoring
        self.weights = {
            'required_skills': 0.4,
            'preferred_skills': 0.2,
            'experience': 0.25,
            'education': 0.15
        }
    
    def set_job_description(self, job_description):
        """
        Set the job description.
        
        Args:
            job_description (str): Job description text
        """
        self.job_description = job_description
    
    def set_required_skills(self, required_skills):
        """
        Set the required skills.
        
        Args:
            required_skills (list): List of required skills
        """
        self.required_skills = required_skills
    
    def set_preferred_skills(self, preferred_skills):
        """
        Set the preferred skills.
        
        Args:
            preferred_skills (list): List of preferred skills
        """
        self.preferred_skills = preferred_skills
    
    def calculate_skills_match(self, candidate_skills):
        """
        Calculate the skills match score.
        
        Args:
            candidate_skills (list): List of candidate skills
            
        Returns:
            dict: Dictionary containing skills match information
        """
        if not candidate_skills:
            return {'score': 0, 'matched_required': [], 'matched_preferred': []}
        
        # Convert lists to lowercase for case-insensitive matching
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        required_skills_lower = [skill.lower() for skill in self.required_skills]
        preferred_skills_lower = [skill.lower() for skill in self.preferred_skills]
        
        # Find matched skills
        matched_required = [skill for skill in required_skills_lower if skill in candidate_skills_lower]
        matched_preferred = [skill for skill in preferred_skills_lower if skill in candidate_skills_lower]
        
        # Calculate match percentages
        required_match = len(matched_required) / len(required_skills_lower) if required_skills_lower else 0
        preferred_match = len(matched_preferred) / len(preferred_skills_lower) if preferred_skills_lower else 0
        
        # Calculate weighted score
        score = (required_match * self.weights['required_skills'] + 
                preferred_match * self.weights['preferred_skills'])
        
        # Normalize to percentage
        score = score / (self.weights['required_skills'] + self.weights['preferred_skills']) * 100
        
        return {
            'score': round(score, 2),
            'matched_required': matched_required,
            'matched_preferred': matched_preferred,
            'required_match_percent': round(required_match * 100, 2),
            'preferred_match_percent': round(preferred_match * 100, 2)
        }
    
    def calculate_experience_score(self, experience_text):
        """
        Calculate experience relevance score.
        
        Args:
            experience_text (str): Experience text from resume
            
        Returns:
            float: Experience score
        """
        if not experience_text or not self.job_description:
            return 0
        
        # Preprocess texts
        job_desc = preprocess_text(self.job_description)
        job_desc = remove_stopwords(job_desc)
        job_desc = lemmatize_text(job_desc)
        
        if isinstance(experience_text, list):
            experience_text = ' '.join(experience_text)
        
        exp_text = preprocess_text(experience_text)
        exp_text = remove_stopwords(exp_text)
        exp_text = lemmatize_text(exp_text)
        
        # Calculate similarity
        similarity = calculate_similarity(job_desc, exp_text)
        
        return round(similarity * 100, 2)
    
    def calculate_education_score(self, education_text):
        """
        Calculate education relevance score.
        
        Args:
            education_text (str): Education text from resume
            
        Returns:
            float: Education score
        """
        if not education_text or not self.job_description:
            return 0
        
        # Preprocess texts
        job_desc = preprocess_text(self.job_description)
        job_desc = remove_stopwords(job_desc)
        job_desc = lemmatize_text(job_desc)
        
        if isinstance(education_text, list):
            education_text = ' '.join(education_text)
        
        edu_text = preprocess_text(education_text)
        edu_text = remove_stopwords(edu_text)
        edu_text = lemmatize_text(edu_text)
        
        # Calculate similarity
        similarity = calculate_similarity(job_desc, edu_text)
        
        return round(similarity * 100, 2)
    
    def analyze_resume(self, resume_data):
        """
        Analyze resume data and calculate scores.
        
        Args:
            resume_data (dict): Resume data from ResumeParser
            
        Returns:
            dict: Dictionary containing analysis results
        """
        if not resume_data:
            logger.error("No resume data provided for analysis")
            return None
        
        # Extract skills
        candidate_skills = resume_data.get('skills', [])
        
        # Calculate skills match
        skills_match = self.calculate_skills_match(candidate_skills)
        
        # Calculate experience score
        experience_text = resume_data.get('experience', [])
        experience_score = self.calculate_experience_score(experience_text)
        
        # Calculate education score
        education_text = resume_data.get('education', [])
        education_score = self.calculate_education_score(education_text)
        
        # Calculate overall score
        overall_score = (
            skills_match['score'] * (self.weights['required_skills'] + self.weights['preferred_skills']) +
            experience_score * self.weights['experience'] +
            education_score * self.weights['education']
        ) / 100
        
        # Prepare result
        result = {
            'name': resume_data.get('name', 'Unknown'),
            'filename': resume_data.get('filename', 'Unknown'),
            'overall_score': round(overall_score, 2),
            'skills_match': skills_match,
            'experience_score': experience_score,
            'education_score': education_score,
            'skills': candidate_skills,
            'missing_required_skills': [skill for skill in self.required_skills if skill.lower() not in [s.lower() for s in skills_match['matched_required']]]
        }
        
        return result 