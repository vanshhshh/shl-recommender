import numpy as np
import logging
import re
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
        Apply preprocessing to assessment texts for better matching.
        """
        self.logger.info("Computing assessment vectors...")
        
        # Prepare text for each assessment by combining relevant fields
        self.assessment_texts = []
        self.processed_assessments = []
        
        for assessment in self.assessments:
            # Combine all relevant fields
            name = assessment.get('name', '')
            description = assessment.get('description', '')
            skills = assessment.get('skills', '')
            type_info = assessment.get('type', '')
            
            # Weight important fields more by repeating them
            # This ensures more relevant matches for critical fields like name and skills
            text = f"{name} {name} {description} {skills} {skills} {type_info}"
            
            # Apply preprocessing
            processed_text = self._preprocess_text(text)
            
            # Store both the original text and the processed version
            self.assessment_texts.append(text)
            self.processed_assessments.append(processed_text)
            
            # Add special job-role specific keywords to improve matching
            if 'java' in name.lower():
                processed_text += " java_developer coding_java programming_java"
            elif 'python' in name.lower():
                processed_text += " python_developer coding_python programming_python"
            elif 'sales' in name.lower():
                processed_text += " sales_representative sales_professional"
            elif 'leadership' in name.lower() or 'management' in name.lower():
                processed_text += " leadership_skills manager_skills"
            elif 'data' in name.lower() and ('science' in name.lower() or 'analysis' in name.lower()):
                processed_text += " data_scientist data_analysis"
        
        # Generate TF-IDF vectors using the processed texts
        self.assessment_vectors = self.vectorizer.fit_transform(self.processed_assessments)
        self.logger.info(f"Computed vectors for {len(self.processed_assessments)} assessments")
    
    def _preprocess_text(self, text):
        """
        Preprocess text for better matching.
        - Convert to lowercase
        - Handle multi-word phrases
        - Normalize text
        
        Args:
            text (str): Text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Replace special characters with spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Special handling for common job titles and multi-word phrases
        # This ensures they're treated as a single term
        phrases_to_join = [
            'front end', 'back end', 'full stack', 'data science', 'machine learning',
            'artificial intelligence', 'business intelligence', 'project management',
            'product management', 'user experience', 'user interface', 'quality assurance',
            'business analysis', 'database administrator', 'system administrator',
            'human resources', 'sales representative', 'account manager', 'customer service'
        ]
        
        for phrase in phrases_to_join:
            if phrase in text:
                joined_phrase = phrase.replace(' ', '_')
                text = text.replace(phrase, joined_phrase)
        
        return text
    
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
            # Preprocess job description
            processed_job_description = self._preprocess_text(job_description)
            
            # Transform job description using the same vectorizer
            job_vector = self.vectorizer.transform([processed_job_description])
            
            # Calculate cosine similarity between job description and all assessments
            similarity_matrix = cosine_similarity(job_vector, self.assessment_vectors)
            
            # Get similarity scores (first row contains all scores)
            similarity_scores = similarity_matrix[0]
            
            # Create list of (index, score) tuples and sort by score (descending)
            similarities = [(i, float(score)) for i, score in enumerate(similarity_scores)]
            
            # Extract key terms from job description for boosting using more sophisticated approach
            job_description_lower = job_description.lower()
            
            # Define domain-specific categories and their associated keywords
            skill_categories = {
                'programming': ['java', 'python', 'javascript', 'c++', 'c#', '.net', 'ruby', 'php', 'go', 'rust', 'scala', 'perl', 'assembly', 'swift', 'kotlin', 'dart', 'typescript', 'html', 'css', 'sql', 'nosql', 'r', 'matlab', 'programming', 'coding', 'developer', 'software', 'web', 'mobile', 'frontend', 'backend', 'fullstack', 'algorithm', 'data structure'],
                'frameworks': ['spring', 'react', 'angular', 'vue', 'django', 'flask', 'laravel', 'express', 'node', 'rails', 'hibernate', 'bootstrap', 'jquery', '.net', 'aspnet', 'symfony', 'ember', 'gatsby', 'nextjs', 'nuxtjs', 'flutter'],
                'data': ['database', 'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'nosql', 'redis', 'cassandra', 'elasticsearch', 'data', 'analytics', 'big data', 'hadoop', 'spark', 'etl', 'tableau', 'power bi', 'data lake', 'data warehouse', 'bi', 'business intelligence'],
                'cloud': ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes', 'serverless', 'lambda', 'ec2', 's3', 'microservices', 'devops', 'cicd', 'jenkins', 'terraform', 'iaas', 'paas', 'saas'],
                'ai_ml': ['machine learning', 'artificial intelligence', 'ai', 'ml', 'deep learning', 'neural network', 'nlp', 'natural language processing', 'computer vision', 'data science', 'tensorflow', 'pytorch', 'scikit-learn', 'keras', 'regression', 'classification', 'clustering'],
                'sales': ['sales', 'marketing', 'customer', 'account', 'business development', 'client', 'revenue', 'lead', 'pipeline', 'crm', 'salesforce', 'hubspot', 'closing', 'negotiation', 'pitch', 'presentation', 'relationship', 'solution selling', 'b2b', 'b2c', 'retail'],
                'management': ['manager', 'management', 'lead', 'leadership', 'supervisor', 'director', 'executive', 'ceo', 'cto', 'coo', 'cfo', 'vp', 'head', 'chief', 'project manager', 'program manager', 'scrum master', 'agile', 'team lead'],
                'finance': ['accounting', 'finance', 'financial', 'investment', 'banking', 'trading', 'audit', 'tax', 'budget', 'forecast', 'analysis', 'capital', 'risk', 'compliance', 'regulation', 'portfolio', 'bank', 'banker', 'loan', 'credit', 'debit', 'transaction', 'deposit', 'withdrawal', 'interest', 'mortgage', 'payment'],
                'hr': ['hr', 'human resources', 'talent', 'recruitment', 'recruiting', 'hiring', 'onboarding', 'training', 'development', 'performance', 'compensation', 'benefits', 'employee', 'workforce', 'culture', 'diversity', 'inclusion'],
                'design': ['design', 'ux', 'ui', 'user experience', 'user interface', 'graphic', 'visual', 'creative', 'art', 'illustrator', 'photoshop', 'sketch', 'figma', 'adobe', 'wireframe', 'prototype', 'accessibility'],
                'administrative': ['administrative', 'admin', 'assistant', 'clerk', 'receptionist', 'secretary', 'office', 'document', 'filing', 'paperwork', 'correspondence', 'data entry', 'typing', 'word processing', 'spreadsheet', 'scheduling', 'calendar', 'meeting', 'minute taking', 'phone', 'email', 'customer service', 'support', 'clerical', 'organization']
            }
            
            # Create a flattened set of all keywords for basic matching
            all_keywords = set()
            for category_keywords in skill_categories.values():
                all_keywords.update(category_keywords)
            
            # Identify categories present in the job description
            job_categories = {}
            for category, keywords in skill_categories.items():
                category_match_count = 0
                for keyword in keywords:
                    if keyword in job_description_lower:
                        category_match_count += 1
                if category_match_count > 0:
                    job_categories[category] = category_match_count
            
            # Extract basic job terms (words) for simple matching
            job_terms = set(job_description_lower.split())
            
            # Boost assessments that match key skills or terms in the job description
            for i, (idx, score) in enumerate(similarities):
                assessment = self.assessments[idx]
                boost = 0
                
                # Get assessment text fields for matching
                skills = assessment.get('skills', '').lower()
                name = assessment.get('name', '').lower()
                description = assessment.get('description', '').lower()
                assessment_text = f"{name} {description} {skills}"
                
                # Basic term matching (small boost)
                term_matches = sum(1 for term in job_terms if len(term) > 3 and term in assessment_text)
                boost += term_matches * 0.02  # Small boost per term match
                
                # Category matching (larger boost based on relevance)
                for category, count in job_categories.items():
                    category_match_score = 0
                    for keyword in skill_categories[category]:
                        if keyword in assessment_text:
                            category_match_score += 0.05  # Boost for each keyword match in important categories
                    
                    # Scale the boost based on category relevance in job description
                    boost += category_match_score * (count / len(skill_categories[category]))
                
                # Extra boost for exact category matches
                for category in job_categories:
                    if category.lower() in assessment_text:
                        boost += 0.3  # Strong boost for direct category mention
                
                # Special cases - highly specific term matching for key terms
                # These are direct matches that should strongly influence results
                key_exact_matches = {
                    'java developer': ['java', 'core java'],
                    'python developer': ['python', 'coding assessment for python'],
                    'data scientist': ['data science', 'machine learning', 'analytics'],
                    'sales representative': ['sales aptitude', 'sales'],
                    'project manager': ['project management', 'leadership'],
                    'business analyst': ['business analyst', 'requirements analysis'],
                    'ux designer': ['ux design', 'user experience'],
                    'database administrator': ['database', 'sql'],
                    'front end developer': ['front-end', 'html', 'css', 'javascript'],
                    'mobile developer': ['mobile', 'ios', 'android', 'react native', 'flutter'],
                    'bank assistant': ['administrative', 'customer service', 'bank', 'excel', 'numerical', 'verbal', 'clerical'],
                    'administrative assistant': ['administrative', 'office', 'clerical', 'customer service', 'excel', 'verbal'],
                    'bank clerk': ['bank', 'administrative', 'numerical', 'clerical', 'excel', 'data entry'],
                    'icici bank': ['bank', 'financial', 'administrative', 'customer service', 'excel', 'numerical']
                }
                
                for role, match_terms in key_exact_matches.items():
                    if role in job_description_lower:
                        for term in match_terms:
                            if term in assessment_text:
                                boost += 0.5  # Very strong boost for direct role-specific matches
                
                # Apply domain-specific penalties
                # For banking and administrative roles, penalize programming assessments
                if ('bank' in job_description_lower or 'administrative' in job_description_lower or 
                    'admin' in job_description_lower or 'assistant' in job_description_lower or
                    'clerk' in job_description_lower):
                    if ('python' in name or 'java' in name or 'coding' in name or 
                        'programming' in name or 'developer' in name):
                        boost -= 2.0  # Strong penalty for programming assessments
                
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
