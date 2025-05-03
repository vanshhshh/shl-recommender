import numpy as np
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cosine

class NLPProcessor:
    """
    Handles all NLP processing for matching job descriptions to assessments.
    Uses TF-IDF vectorization and cosine similarity for matching.
    """
    
    def __init__(self, assessments):
        """
        Initialize the NLP processor with assessments data.
        
        Args:
            assessments (list): List of assessment dictionaries
        """
        self.logger = logging.getLogger(__name__)
        self.assessments = assessments
        
        # Initialize TF-IDF vectorizer
        self.logger.info("Initializing TF-IDF vectorizer...")
        try:
            self.vectorizer = TfidfVectorizer(stop_words='english')
            
            # Pre-compute vectors for all assessments
            self._compute_assessment_vectors()
            self.logger.info("Vectorizer initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing vectorizer: {e}")
            raise
    
    def _compute_assessment_vectors(self):
        """
        Pre-compute TF-IDF vectors for all assessments to avoid recomputing for each query.
        """
        self.logger.info("Computing assessment vectors...")
        
        # Prepare text for each assessment by combining relevant fields
        self.assessment_texts = []
        for assessment in self.assessments:
            text = f"{assessment.get('name', '')} {assessment.get('description', '')} "
            text += f"{assessment.get('skills', '')} {assessment.get('type', '')}"
            self.assessment_texts.append(text)
        
        # Generate TF-IDF vectors
        self.assessment_vectors = self.vectorizer.fit_transform(self.assessment_texts)
        self.logger.info(f"Computed vectors for {len(self.assessment_texts)} assessments")
    
    def get_recommendations(self, job_description, top_k=10, test_type=None, 
                           remote_available=None, adaptive_testing=None):
        """
        Get recommended assessments for a job description.
        
        Args:
            job_description (str): The job description text
            top_k (int): Number of recommendations to return
            test_type (str, optional): Filter by test type
            remote_available (bool, optional): Filter by remote availability
            adaptive_testing (bool, optional): Filter by adaptive testing feature
            
        Returns:
            list: Recommended assessments with similarity scores
        """
        try:
            # Transform job description using the same vectorizer
            job_vector = self.vectorizer.transform([job_description])
            
            # Calculate cosine similarity between job description and all assessments
            similarity_matrix = cosine_similarity(job_vector, self.assessment_vectors)
            
            # Get similarity scores (first row contains all scores)
            similarity_scores = similarity_matrix[0]
            
            # Create list of (index, score) tuples and sort by score (descending)
            similarities = [(i, float(score)) for i, score in enumerate(similarity_scores)]
            
            # Extract key terms from job description for boosting
            job_terms = set(job_description.lower().split())
            skill_boosts = {}
            
            # Boost assessments that match key skills or terms in the job description
            for i, (idx, score) in enumerate(similarities):
                assessment = self.assessments[idx]
                boost = 0
                
                # Boost score based on skill matches
                skills = assessment.get('skills', '').lower()
                name = assessment.get('name', '').lower()
                
                # Check for key term matches in the assessment name and skills
                term_matches = sum(1 for term in job_terms if term in name or term in skills)
                boost += term_matches * 0.05  # Small boost per term match
                
                # Additional boost for specific job roles/skills if they appear in assessment
                key_terms = ['java', 'python', 'sales', 'developer', 'engineer', 'leadership', 
                           'management', 'analysis', 'customer', 'technical']
                for term in key_terms:
                    if term in job_description.lower() and (term in name or term in skills):
                        boost += 0.2  # Strong boost for matching key terms
                
                # Apply the boost
                similarities[i] = (idx, score + boost)
            
            # Sort by adjusted scores
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Filter and prepare results
            recommendations = []
            max_score = max([score for _, score in similarities]) if similarities else 1
            
            for i, similarity in similarities:
                assessment = self.assessments[i]
                
                # Apply filters if specified
                if test_type and assessment.get('type') != test_type:
                    continue
                if remote_available is not None and assessment.get('remote_available') != remote_available:
                    continue
                if adaptive_testing is not None and assessment.get('adaptive_testing') != adaptive_testing:
                    continue
                
                # Add similarity score to assessment (normalize to 0-1 range)
                assessment_copy = assessment.copy()
                normalized_score = float(similarity) / max_score if max_score > 0 else 0
                assessment_copy['similarity_score'] = normalized_score
                assessment_copy['similarity'] = normalized_score  # For v1/recommend endpoint
                recommendations.append(assessment_copy)
                
                # Break when we have enough recommendations
                if len(recommendations) >= top_k:
                    break
            
            # Ensure at least one recommendation if available
            if not recommendations and self.assessments:
                # If no matches found but we have assessments, return the first one
                assessment_copy = self.assessments[0].copy()
                assessment_copy['similarity_score'] = 0.0
                assessment_copy['similarity'] = 0.0
                recommendations.append(assessment_copy)
            
            self.logger.info(f"Found {len(recommendations)} recommendations for job description")
            return recommendations
        
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            raise
