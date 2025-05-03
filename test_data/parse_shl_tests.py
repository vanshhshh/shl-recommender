"""
Parse SHL test data into a format suitable for the recommendation engine.
"""
import re
import json
import os

def parse_test_data(file_path):
    """
    Parse the SHL test data into queries and expected assessments.
    
    Returns:
        list: List of dictionaries with query and expected assessments
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip the header line
    content = re.sub(r'^Query\s+Assessments\s+URL\s*\n', '', content)
    
    # Split into test cases - each test case is separated by multiple blank lines
    test_blocks = re.split(r'\n\s*\n\s*\n+', content)
    
    test_cases = []
    
    for block in test_blocks:
        if not block.strip():
            continue
            
        # Split the block into lines
        lines = block.strip().split('\n')
        
        # Determine where the query ends and assessments begin
        query_lines = []
        assessment_lines = []
        
        # First gather all lines
        query_ended = False
        for line in lines:
            # If we see a line with a URL, we've definitely reached the assessments
            if 'http' in line:
                query_ended = True
                assessment_lines.append(line)
            # If we see a line with "| SHL", it's the start of an assessment
            elif '| SHL' in line or query_ended:
                query_ended = True
                assessment_lines.append(line)
            # Otherwise it's part of the query
            else:
                query_lines.append(line)
        
        # Join query lines
        query = ' '.join(query_lines).strip()
        
        # Parse assessments
        expected_assessments = []
        i = 0
        assessment_lines = [line for line in assessment_lines if line.strip()]
        
        while i < len(assessment_lines):
            # Find lines with "| SHL" - these are assessment names
            if '| SHL' in assessment_lines[i]:
                assessment_name = assessment_lines[i].split('| SHL')[0].strip()
                
                # The next line should be the URL
                if i + 1 < len(assessment_lines) and 'http' in assessment_lines[i + 1]:
                    assessment_url = assessment_lines[i + 1].strip()
                    
                    expected_assessments.append({
                        'name': assessment_name,
                        'url': assessment_url
                    })
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        
        if query and expected_assessments:
            test_cases.append({
                'query': query,
                'expected_assessments': expected_assessments
            })
    
    # Add the last query if there is one
    if current_query is not None:
        test_cases.append({
            'query': current_query,
            'expected_assessments': expected_assessments
        })
    
    return test_cases

def create_assessment_mappings(test_cases):
    """
    Create a mapping of assessment names from test data to our dataset.
    
    Args:
        test_cases: List of test cases with queries and expected assessments
        
    Returns:
        dict: Mapping of assessment names from test data to our dataset
    """
    # Extract all unique assessment names from test data
    all_assessments = set()
    for test_case in test_cases:
        for assessment in test_case['expected_assessments']:
            all_assessments.add(assessment['name'])
    
    # Create mapping to our dataset (simplified for now)
    mapping = {}
    for assessment_name in all_assessments:
        # Strip any parentheses and content
        base_name = re.sub(r'\s*\([^)]*\)\s*', ' ', assessment_name).strip()
        mapping[assessment_name] = base_name
    
    return mapping

def save_to_json(data, output_path):
    """Save data to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    # Parse test data
    test_cases = parse_test_data('shl_test_data.txt')
    
    # Save test cases for reference
    save_to_json(test_cases, 'parsed_test_cases.json')
    
    # Create assessment name mappings
    mappings = create_assessment_mappings(test_cases)
    save_to_json(mappings, 'assessment_mappings.json')
    
    print(f"Parsed {len(test_cases)} test cases with {len(mappings)} unique assessments")
    
    # Print first test case as an example
    if test_cases:
        print("\nExample Test Case:")
        print(f"Query: {test_cases[0]['query']}")
        print("Expected Assessments:")
        for assessment in test_cases[0]['expected_assessments']:
            print(f"- {assessment['name']}")

if __name__ == "__main__":
    main()