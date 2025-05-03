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

# Health check endpoint for assignment requirement
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify({
        "status": "ok",
        "message": "API is operational"
    }), 200

# Assignment-specific endpoint for recommendations
@app.route('/v1/recommend', methods=['POST'])
def assignment_recommend():
    """
    Assignment-specific recommendation endpoint that follows required format.
    Accepts job description or natural language query and returns up to 10 relevant assessments.
    """
    if not nlp_processor:
        return jsonify({"error": "Service unavailable", "message": "NLP processor not initialized"}), 503
    
    try:
        data = request.get_json()
        
        # Support both 'job_description' or 'query' as input
        query = data.get('job_description', data.get('query', ''))
        
        if not query:
            return jsonify({
                "error": "Bad request", 
                "message": "Job description or query is required"
            }), 400
                
        # Get top 10 recommendations (minimum 1)
        recommendations = nlp_processor.get_recommendations(query, top_k=10)
        
        # Ensure we return at least 1 recommendation
        if not recommendations:
            return jsonify({
                "error": "No results",
                "message": "No matching assessments found for the given query"
            }), 404
            
        # Format the response according to assignment requirements
        response = []
        for rec in recommendations:
            response.append({
                "name": rec.get('name', ''),
                "type": rec.get('type', ''),
                "description": rec.get('description', ''),
                "match_score": rec.get('similarity', 0),
                "skills": rec.get('skills', []),
                "remote_available": rec.get('remote_available', False),
                "duration_minutes": rec.get('duration_minutes', 0)
            })
            
        return jsonify({
            "success": True,
            "data": {
                "assessments": response,
                "count": len(response)
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing assignment recommendation: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
