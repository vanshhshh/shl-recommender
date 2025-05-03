import os
import logging
from flask import Flask, render_template, request, jsonify
from utils.nlp_processor import NLPProcessor
from utils.data_loader import load_assessments

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Load assessment data
try:
    assessments = load_assessments()
    logger.info(f"Loaded {len(assessments)} assessments")
except Exception as e:
    logger.error(f"Error loading assessments: {e}")
    assessments = []

# Initialize NLP processor
try:
    nlp_processor = NLPProcessor(assessments)
    logger.info("NLP processor initialized successfully")
except Exception as e:
    logger.error(f"Error initializing NLP processor: {e}")
    nlp_processor = None

@app.route('/')
def index():
    """Render the main page."""
    # Get unique assessment types for filtering
    assessment_types = list(set([a.get('type', 'Unknown') for a in assessments]))
    return render_template('index.html', assessment_types=assessment_types)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """API endpoint to get assessment recommendations based on job description."""
    if not nlp_processor:
        return jsonify({"error": "NLP processor not initialized"}), 500
    
    try:
        data = request.get_json()
        job_description = data.get('job_description', '')
        
        if not job_description:
            return jsonify({"error": "Job description is required"}), 400
            
        # Get filters if provided
        filters = data.get('filters', {})
        test_type = filters.get('test_type')
        remote_available = filters.get('remote_available')
        adaptive_testing = filters.get('adaptive_testing')
        
        # Get recommendations
        recommendations = nlp_processor.get_recommendations(
            job_description, 
            test_type=test_type,
            remote_available=remote_available,
            adaptive_testing=adaptive_testing
        )
        
        return jsonify({
            "recommendations": recommendations,
            "count": len(recommendations)
        })
    
    except Exception as e:
        logger.error(f"Error processing recommendation: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
