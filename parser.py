import re
import logging
import spacy
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

from utils.file_utils import extract_text_from_file
from utils.nlp_utils import preprocess_text, extract_entities, nlp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResumeParser:
    """Class to parse resume data from various file formats."""
    
    def __init__(self, skills_file=None):
        """
        Initialize ResumeParser.
        
        Args:
            skills_file (str, optional): Path to CSV file containing skills. Defaults to None.
        """
        self.skills = []
        
        # Load skills from file if provided
        if skills_file and os.path.exists(skills_file):
            try:
                skills_df = pd.read_csv(skills_file)
                self.skills = skills_df['skill'].str.lower().tolist()
            except Exception as e:
                logger.error(f"Error loading skills file: {str(e)}")
        
        # Default skills list if no file provided or loading failed
        if not self.skills:
            self.skills = [
                'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'php', 'swift', 'kotlin',
                'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express',
                'html', 'css', 'bootstrap', 'jquery', 'rest api', 'graphql',
                'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite', 'nosql',
                'aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'terraform',
                'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence',
                'machine learning', 'deep learning', 'nlp', 'computer vision', 'ai',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
                'data analysis', 'data science', 'data visualization', 'tableau', 'power bi',
                'agile', 'scrum', 'kanban', 'waterfall', 'sdlc',
                'devops', 'ci/cd', 'test automation', 'unit testing'
            ]
    
    def extract_contact_info(self, text):
        """
        Extract contact information from text.
        
        Args:
            text (str): Resume text
            
        Returns:
            dict: Dictionary containing contact information
        """
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Extract phone number
        phone_pattern = r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()
        
        return contact_info
    
    def extract_education(self, text):
        """
        Extract education information from text.
        
        Args:
            text (str): Resume text
            
        Returns:
            list: List of education entries
        """
        education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'bs', 'ms', 'ba', 'ma', 'mba',
            'degree', 'university', 'college', 'institute', 'school'
        ]
        
        doc = nlp(text)
        education = []
        
        # Split text into sentences and look for education-related sentences
        for sent in doc.sents:
            sent_text = sent.text.lower()
            if any(keyword in sent_text for keyword in education_keywords):
                education.append(sent.text.strip())
        
        return education
    
    def extract_experience(self, text):
        """
        Extract work experience information from text.
        
        Args:
            text (str): Resume text
            
        Returns:
            list: List of experience entries
        """
        experience_keywords = [
            'experience', 'work', 'employment', 'job', 'career',
            'position', 'role', 'title', 'company', 'employer',
            'worked', 'working', 'responsible', 'responsibilities'
        ]
        
        doc = nlp(text)
        experience = []
        
        # Split text into sentences and look for experience-related sentences
        for sent in doc.sents:
            sent_text = sent.text.lower()
            if any(keyword in sent_text for keyword in experience_keywords):
                experience.append(sent.text.strip())
        
        return experience
    
    def extract_skills_from_text(self, text):
        """
        Extract skills from text based on predefined skills list.
        
        Args:
            text (str): Resume text
            
        Returns:
            list: List of extracted skills
        """
        text = text.lower()
        extracted_skills = []
        
        for skill in self.skills:
            skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(skill_pattern, text):
                extracted_skills.append(skill)
        
        return extracted_skills
    
    def parse_resume(self, file_path):
        """
        Parse resume from file.
        
        Args:
            file_path (str): Path to resume file
            
        Returns:
            dict: Dictionary containing extracted resume information
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
        
        # Extract text from file
        logger.info(f"Parsing resume: {file_path}")
        resume_text = extract_text_from_file(file_path)
        
        if not resume_text:
            logger.error(f"Could not extract text from file: {file_path}")
            return None
        
        # Create result dictionary
        result = {
            'filename': os.path.basename(file_path),
            'full_text': resume_text,
            'parsed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Extract entities
        entities = extract_entities(resume_text)
        
        # Extract contact information
        result.update(self.extract_contact_info(resume_text))
        
        # Extract person name if available
        if 'PERSON' in entities and entities['PERSON']:
            result['name'] = entities['PERSON'][0]
        else:
            result['name'] = None
        
        # Extract education
        result['education'] = self.extract_education(resume_text)
        
        # Extract experience
        result['experience'] = self.extract_experience(resume_text)
        
        # Extract skills
        result['skills'] = self.extract_skills_from_text(resume_text)
        
        # Extract organizations
        if 'ORG' in entities and entities['ORG']:
            result['organizations'] = entities['ORG']
        else:
            result['organizations'] = []
        
        # Extract locations
        if 'GPE' in entities and entities['GPE']:
            result['locations'] = entities['GPE']
        else:
            result['locations'] = []
        
        logger.info(f"Successfully parsed resume: {file_path}")
        return result 