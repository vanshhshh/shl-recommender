"""
Test the recommendation engine with SHL test data.
"""
import json
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.abspath('..'))

# Import our application modules
from utils.data_loader import load_assessments
from utils.nlp_processor import NLPProcessor

def load_test_data(file_path):
    """Load test data from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def evaluate_recommendations(nlp_processor, test_cases, top_k=10):
    """
    Evaluate recommendations against expected assessments.
    
    Args:
        nlp_processor: NLP processor instance
        test_cases: List of test cases with queries and expected assessments
        top_k: Number of recommendations to evaluate
        
    Returns:
        dict: Evaluation metrics
    """
    results = []
    overall_recall = 0
    overall_precision = 0
    
    for test_case in test_cases:
        query = test_case['query']
        expected = [a['name'] for a in test_case['expected_assessments']]
        
        # Get recommendations
        recommendations = nlp_processor.get_recommendations(query, top_k=top_k)
        recommended_names = [r['name'] for r in recommendations]
        
        # Calculate metrics
        true_positives = [name for name in recommended_names if any(exp in name or name in exp for exp in expected)]
        false_positives = [name for name in recommended_names if not any(exp in name or name in exp for exp in expected)]
        false_negatives = [name for name in expected if not any(rec in name or name in rec for rec in recommended_names)]
        
        recall = len(true_positives) / len(expected) if expected else 0
        precision = len(true_positives) / len(recommended_names) if recommended_names else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        overall_recall += recall
        overall_precision += precision
        
        # Create result entry
        result = {
            'query': query,
            'recommendations': recommended_names,
            'expected': expected,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'recall': recall,
            'precision': precision,
            'f1': f1
        }
        
        results.append(result)
    
    # Calculate overall metrics
    avg_recall = overall_recall / len(test_cases) if test_cases else 0
    avg_precision = overall_precision / len(test_cases) if test_cases else 0
    avg_f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0
    
    return {
        'results': results,
        'avg_recall': avg_recall,
        'avg_precision': avg_precision,
        'avg_f1': avg_f1
    }

def print_evaluation_summary(evaluation):
    """Print a summary of the evaluation results."""
    print(f"Overall Metrics:")
    print(f"  Average Recall: {evaluation['avg_recall']:.4f}")
    print(f"  Average Precision: {evaluation['avg_precision']:.4f}")
    print(f"  Average F1 Score: {evaluation['avg_f1']:.4f}")
    print()
    
    for i, result in enumerate(evaluation['results']):
        print(f"Test Case {i+1}:")
        print(f"  Query: {result['query']}")
        print(f"  Recall: {result['recall']:.4f}")
        print(f"  Precision: {result['precision']:.4f}")
        print(f"  F1 Score: {result['f1']:.4f}")
        print()
        print("  Expected Assessments:")
        for name in result['expected']:
            print(f"    - {name}")
        print()
        print("  Recommended Assessments:")
        for name in result['recommendations']:
            status = "✓" if name in result['true_positives'] else "✗"
            print(f"    {status} {name}")
        print("\n" + "-" * 80 + "\n")

def main():
    # Load assessments from our system
    assessments = load_assessments()
    print(f"Loaded {len(assessments)} assessments from our system")
    
    # Initialize NLP processor
    nlp_processor = NLPProcessor(assessments)
    print("NLP processor initialized")
    
    # Load test data
    test_cases = load_test_data('shl_manual_test_data.json')
    print(f"Loaded {len(test_cases)} test cases")
    
    # Evaluate recommendations
    evaluation = evaluate_recommendations(nlp_processor, test_cases)
    
    # Print evaluation summary
    print_evaluation_summary(evaluation)
    
    # Save evaluation results
    with open('evaluation_results.json', 'w', encoding='utf-8') as f:
        json.dump(evaluation, f, indent=2)
    print("Evaluation results saved to evaluation_results.json")

if __name__ == "__main__":
    main()