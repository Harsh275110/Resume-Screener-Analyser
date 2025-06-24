import re
import logging
import numpy as np
from utils.nlp_utils import calculate_similarity, preprocess_text, extract_entities, nlp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InterviewAnalyzer:
    """Class to analyze interview responses."""
    
    def __init__(self, question_bank=None):
        """
        Initialize InterviewAnalyzer.
        
        Args:
            question_bank (dict, optional): Dictionary of questions and expected answers/keywords. Defaults to None.
        """
        self.question_bank = question_bank if question_bank else {}
        
        # Default weights for scoring
        self.weights = {
            'relevance': 0.4,
            'completeness': 0.3,
            'clarity': 0.15,
            'technical_accuracy': 0.15
        }
    
    def add_question(self, question, expected_answer=None, keywords=None, category=None):
        """
        Add a question to the question bank.
        
        Args:
            question (str): The interview question
            expected_answer (str, optional): Expected answer or answer template. Defaults to None.
            keywords (list, optional): List of keywords that should be in the answer. Defaults to None.
            category (str, optional): Category of the question (technical, behavioral, etc.). Defaults to None.
        """
        self.question_bank[question] = {
            'expected_answer': expected_answer,
            'keywords': keywords if keywords else [],
            'category': category
        }
    
    def remove_question(self, question):
        """
        Remove a question from the question bank.
        
        Args:
            question (str): The question to remove
        """
        if question in self.question_bank:
            del self.question_bank[question]
    
    def calculate_relevance_score(self, question, answer):
        """
        Calculate how relevant the answer is to the question.
        
        Args:
            question (str): The interview question
            answer (str): The candidate's answer
            
        Returns:
            float: Relevance score between 0 and 100
        """
        if not question or not answer:
            return 0
        
        # Calculate semantic similarity
        similarity = calculate_similarity(question, answer)
        
        return round(similarity * 100, 2)
    
    def calculate_completeness_score(self, answer, expected_answer=None, keywords=None):
        """
        Calculate how complete the answer is.
        
        Args:
            answer (str): The candidate's answer
            expected_answer (str, optional): Expected answer. Defaults to None.
            keywords (list, optional): List of expected keywords. Defaults to None.
            
        Returns:
            float: Completeness score between 0 and 100
        """
        if not answer:
            return 0
        
        score = 0
        
        # If we have keywords, check how many are present
        if keywords:
            answer_lower = answer.lower()
            found_keywords = [keyword for keyword in keywords if keyword.lower() in answer_lower]
            keyword_score = len(found_keywords) / len(keywords) if keywords else 0
            score += keyword_score * 0.6  # Weight for keywords
        
        # If we have an expected answer, calculate similarity
        if expected_answer:
            similarity = calculate_similarity(expected_answer, answer)
            score += similarity * 0.4  # Weight for expected answer similarity
        else:
            # If no expected answer, just consider keywords
            score = keyword_score if keywords else 0.5  # Default middle score
        
        return round(score * 100, 2)
    
    def calculate_clarity_score(self, answer):
        """
        Calculate the clarity of the answer.
        
        Args:
            answer (str): The candidate's answer
            
        Returns:
            float: Clarity score between 0 and 100
        """
        if not answer:
            return 0
        
        # Simple metrics for clarity
        words = answer.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Very long words might indicate complexity
        word_length_score = 1.0 if 4 <= avg_word_length <= 8 else 0.7
        
        # Sentence length analysis
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Very long sentences might indicate lack of clarity
        sentence_length_score = 1.0 if 8 <= avg_sentence_length <= 20 else 0.7
        
        # Combine scores
        clarity_score = (word_length_score * 0.4) + (sentence_length_score * 0.6)
        
        return round(clarity_score * 100, 2)
    
    def calculate_technical_accuracy(self, answer, technical_keywords=None):
        """
        Calculate technical accuracy of the answer.
        
        Args:
            answer (str): The candidate's answer
            technical_keywords (list, optional): List of technical keywords. Defaults to None.
            
        Returns:
            float: Technical accuracy score between 0 and 100
        """
        if not answer or not technical_keywords:
            return 50  # Default middle score
        
        # Check for technical keywords
        answer_lower = answer.lower()
        found_keywords = [keyword for keyword in technical_keywords if keyword.lower() in answer_lower]
        
        technical_score = len(found_keywords) / len(technical_keywords) if technical_keywords else 0.5
        
        return round(technical_score * 100, 2)
    
    def analyze_response(self, question, answer):
        """
        Analyze a single interview response.
        
        Args:
            question (str): The interview question
            answer (str): The candidate's answer
            
        Returns:
            dict: Dictionary containing analysis results
        """
        if not question or not answer:
            logger.error("Question or answer is empty")
            return None
        
        # Get question details from bank if available
        question_details = self.question_bank.get(question, {
            'expected_answer': None,
            'keywords': [],
            'category': None
        })
        
        # Calculate individual scores
        relevance_score = self.calculate_relevance_score(question, answer)
        completeness_score = self.calculate_completeness_score(
            answer, 
            question_details.get('expected_answer'), 
            question_details.get('keywords')
        )
        clarity_score = self.calculate_clarity_score(answer)
        technical_accuracy = self.calculate_technical_accuracy(answer, question_details.get('keywords'))
        
        # Calculate overall score
        overall_score = (
            relevance_score * self.weights['relevance'] +
            completeness_score * self.weights['completeness'] +
            clarity_score * self.weights['clarity'] +
            technical_accuracy * self.weights['technical_accuracy']
        ) / 100
        
        # Prepare result
        result = {
            'question': question,
            'category': question_details.get('category', 'General'),
            'answer': answer,
            'overall_score': round(overall_score, 2),
            'relevance_score': relevance_score,
            'completeness_score': completeness_score,
            'clarity_score': clarity_score,
            'technical_accuracy': technical_accuracy,
            'feedback': self.generate_feedback(
                relevance_score, 
                completeness_score, 
                clarity_score, 
                technical_accuracy,
                question_details.get('keywords', [])
            )
        }
        
        return result
    
    def generate_feedback(self, relevance, completeness, clarity, technical_accuracy, expected_keywords=None):
        """
        Generate feedback based on scores.
        
        Args:
            relevance (float): Relevance score
            completeness (float): Completeness score
            clarity (float): Clarity score
            technical_accuracy (float): Technical accuracy score
            expected_keywords (list, optional): Expected keywords. Defaults to None.
            
        Returns:
            str: Feedback
        """
        feedback = []
        
        # Relevance feedback
        if relevance >= 80:
            feedback.append("Your answer was highly relevant to the question.")
        elif relevance >= 60:
            feedback.append("Your answer was mostly relevant to the question.")
        else:
            feedback.append("Your answer could be more focused on the question asked.")
        
        # Completeness feedback
        if completeness >= 80:
            feedback.append("You provided a comprehensive answer covering the key points.")
        elif completeness >= 60:
            feedback.append("Your answer covered many important aspects but could be more comprehensive.")
        else:
            if expected_keywords:
                feedback.append(f"Consider addressing these points in your answer: {', '.join(expected_keywords[:3])}...")
            else:
                feedback.append("Your answer could be more complete with additional details.")
        
        # Clarity feedback
        if clarity >= 80:
            feedback.append("Your answer was clear and easy to understand.")
        elif clarity >= 60:
            feedback.append("Your answer was generally clear but could be more concise in some areas.")
        else:
            feedback.append("Try to express your thoughts more clearly and concisely.")
        
        # Technical accuracy feedback
        if technical_accuracy >= 80:
            feedback.append("You demonstrated strong technical knowledge in your answer.")
        elif technical_accuracy >= 60:
            feedback.append("Your technical points were mostly accurate but could be strengthened.")
        else:
            feedback.append("Consider reviewing the technical aspects of your answer for accuracy.")
        
        return " ".join(feedback)
    
    def analyze_interview(self, interview_data):
        """
        Analyze a complete interview with multiple questions and answers.
        
        Args:
            interview_data (list): List of dictionaries containing questions and answers
            
        Returns:
            dict: Dictionary containing analysis results
        """
        if not interview_data:
            logger.error("No interview data provided")
            return None
        
        analysis_results = []
        for item in interview_data:
            question = item.get('question')
            answer = item.get('answer')
            
            if question and answer:
                result = self.analyze_response(question, answer)
                if result:
                    analysis_results.append(result)
        
        # Calculate average scores
        if analysis_results:
            avg_overall = sum(r['overall_score'] for r in analysis_results) / len(analysis_results)
            avg_relevance = sum(r['relevance_score'] for r in analysis_results) / len(analysis_results)
            avg_completeness = sum(r['completeness_score'] for r in analysis_results) / len(analysis_results)
            avg_clarity = sum(r['clarity_score'] for r in analysis_results) / len(analysis_results)
            avg_technical = sum(r['technical_accuracy'] for r in analysis_results) / len(analysis_results)
            
            # Group results by category
            categories = {}
            for result in analysis_results:
                category = result['category']
                if category not in categories:
                    categories[category] = {
                        'count': 0,
                        'score_sum': 0
                    }
                categories[category]['count'] += 1
                categories[category]['score_sum'] += result['overall_score']
            
            # Calculate average score per category
            category_scores = {
                category: round(data['score_sum'] / data['count'], 2)
                for category, data in categories.items()
            }
            
            summary = {
                'overall_score': round(avg_overall, 2),
                'average_scores': {
                    'relevance': round(avg_relevance, 2),
                    'completeness': round(avg_completeness, 2),
                    'clarity': round(avg_clarity, 2),
                    'technical_accuracy': round(avg_technical, 2)
                },
                'category_scores': category_scores,
                'question_count': len(analysis_results),
                'detailed_results': analysis_results
            }
            
            return summary
        
        return None 