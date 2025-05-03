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
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Filter and prepare results
            recommendations = []
            for i, similarity in similarities:
                assessment = self.assessments[i]
                
                # Apply filters if specified
                if test_type and assessment.get('type') != test_type:
                    continue
                if remote_available is not None and assessment.get('remote_available') != remote_available:
                    continue
                if adaptive_testing is not None and assessment.get('adaptive_testing') != adaptive_testing:
                    continue
                
                # Add similarity score to assessment
                assessment_copy = assessment.copy()
                assessment_copy['similarity_score'] = float(similarity)
                recommendations.append(assessment_copy)
                
                # Break when we have enough recommendations
                if len(recommendations) >= top_k:
                    break
            
            self.logger.info(f"Found {len(recommendations)} recommendations for job description")
            return recommendations
        
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            raise
