import json
import os
import logging

logger = logging.getLogger(__name__)

def load_assessments(file_path="data/shl_assessments.json"):
    """
    Load assessment data from JSON file.
    
    Args:
        file_path (str): Path to the assessments JSON file
        
    Returns:
        list: List of assessment dictionaries
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"Assessment data file not found at {file_path}")
            logger.info("Loading sample assessment data instead")
            return _generate_sample_assessments()
        
        # Load from file
        with open(file_path, 'r') as f:
            assessments = json.load(f)
        
        logger.info(f"Successfully loaded {len(assessments)} assessments from {file_path}")
        return assessments
    
    except Exception as e:
        logger.error(f"Error loading assessments: {e}")
        logger.info("Loading sample assessment data instead")
        return _generate_sample_assessments()

def _generate_sample_assessments():
    """
    Generate sample assessment data if no file is available.
    This is a fallback function that creates basic assessment data.
    
    Returns:
        list: List of sample assessment dictionaries
    """
    return [
        {
            "id": "SHL-001",
            "name": "Verbal Reasoning Assessment",
            "description": "Measures the ability to understand and evaluate written information",
            "type": "Cognitive",
            "duration": "25 minutes",
            "skills": "Critical thinking, language comprehension, analytical reasoning",
            "link": "https://www.shl.com/assessments/verbal-reasoning/",
            "remote_available": True,
            "adaptive_testing": False
        },
        {
            "id": "SHL-002",
            "name": "Numerical Reasoning Assessment",
            "description": "Evaluates the ability to interpret numerical data and make logical decisions",
            "type": "Cognitive",
            "duration": "35 minutes",
            "skills": "Numerical ability, data interpretation, problem-solving",
            "link": "https://www.shl.com/assessments/numerical-reasoning/",
            "remote_available": True,
            "adaptive_testing": True
        },
        {
            "id": "SHL-003",
            "name": "Inductive Reasoning Assessment",
            "description": "Assesses logical thinking and pattern recognition ability",
            "type": "Cognitive",
            "duration": "30 minutes",
            "skills": "Pattern recognition, logical thinking, problem-solving",
            "link": "https://www.shl.com/assessments/inductive-reasoning/",
            "remote_available": True,
            "adaptive_testing": False
        },
        {
            "id": "SHL-004",
            "name": "Mechanical Reasoning Assessment",
            "description": "Measures understanding of mechanical and physical principles",
            "type": "Technical",
            "duration": "20 minutes",
            "skills": "Mechanical aptitude, spatial visualization, applied physics",
            "link": "https://www.shl.com/assessments/mechanical-reasoning/",
            "remote_available": False,
            "adaptive_testing": False
        },
        {
            "id": "SHL-005",
            "name": "Coding Assessment for Python",
            "description": "Evaluates programming skills and problem-solving in Python",
            "type": "Technical",
            "duration": "60 minutes",
            "skills": "Python programming, algorithms, data structures",
            "link": "https://www.shl.com/assessments/coding-python/",
            "remote_available": True,
            "adaptive_testing": True
        },
        {
            "id": "SHL-006",
            "name": "Leadership Competency Assessment",
            "description": "Evaluates leadership potential and management capabilities",
            "type": "Behavioral",
            "duration": "45 minutes",
            "skills": "Leadership, decision-making, team management",
            "link": "https://www.shl.com/assessments/leadership-competency/",
            "remote_available": True,
            "adaptive_testing": False
        },
        {
            "id": "SHL-007",
            "name": "Customer Service Assessment",
            "description": "Assesses aptitude for customer-facing roles and service orientation",
            "type": "Behavioral",
            "duration": "30 minutes",
            "skills": "Communication, empathy, problem resolution",
            "link": "https://www.shl.com/assessments/customer-service/",
            "remote_available": True,
            "adaptive_testing": False
        },
        {
            "id": "SHL-008",
            "name": "Excel Skills Assessment",
            "description": "Measures proficiency in Microsoft Excel for data analysis and reporting",
            "type": "Technical",
            "duration": "40 minutes",
            "skills": "Excel, data analysis, formula creation",
            "link": "https://www.shl.com/assessments/excel-skills/",
            "remote_available": True,
            "adaptive_testing": True
        },
        {
            "id": "SHL-009",
            "name": "Personality Assessment",
            "description": "Measures work-related personality traits and behavioral tendencies",
            "type": "Behavioral",
            "duration": "25 minutes",
            "skills": "Self-awareness, workplace behavior, interpersonal style",
            "link": "https://www.shl.com/assessments/personality-profile/",
            "remote_available": True,
            "adaptive_testing": False
        },
        {
            "id": "SHL-010",
            "name": "Situational Judgement Test",
            "description": "Evaluates decision-making in realistic workplace scenarios",
            "type": "Behavioral",
            "duration": "30 minutes",
            "skills": "Decision-making, workplace judgment, conflict resolution",
            "link": "https://www.shl.com/assessments/situational-judgement/",
            "remote_available": True,
            "adaptive_testing": True
        }
    ]
