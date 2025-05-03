"""
Parse SHL test data for our recommendation engine.
"""
import re
import json

def extract_test_cases(file_path):
    """
    Extract test cases from the SHL test data.
    
    A test case consists of:
    1. A job description query
    2. A list of recommended assessments
    
    Args:
        file_path: Path to the test data file
        
    Returns:
        list: List of dictionaries, each containing a query and list of expected assessments
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove header if it exists
    if content.startswith("Query"):
        content = re.sub(r'^Query.*?URL\s*\n', '', content, flags=re.DOTALL)
    
    # First, we'll split the content based on double newlines to identify each section
    test_cases = []
    
    # Split by sections with empty lines between them
    sections = re.split(r'\n\n+', content)
    
    current_query = None
    current_assessments = []
    
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        
        # If the section contains "https://" URLs, it's likely an assessment list
        if any('https://' in line for line in lines):
            # Process assessment section
            i = 0
            while i < len(lines):
                # Find assessment name (typically ends with "| SHL")
                if '| SHL' in lines[i]:
                    name = lines[i].split('| SHL')[0].strip()
                    
                    # The next line should be the URL
                    if i + 1 < len(lines) and 'https://' in lines[i + 1]:
                        url = lines[i + 1].strip()
                        
                        current_assessments.append({
                            'name': name,
                            'url': url
                        })
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
        else:
            # This is a query section
            
            # If we already have a query and assessments, save them as a test case
            if current_query and current_assessments:
                test_cases.append({
                    'query': current_query,
                    'expected_assessments': current_assessments
                })
            
            # Start a new test case
            current_query = section.strip()
            current_assessments = []
    
    # Add the last test case if there is one
    if current_query and current_assessments:
        test_cases.append({
            'query': current_query,
            'expected_assessments': current_assessments
        })
    
    return test_cases

def main():
    # Extract test cases
    test_cases = extract_test_cases('shl_test_data.txt')
    
    # Save test cases to JSON for reference
    with open('parsed_test_cases.json', 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, indent=2)
    
    # Print summary
    print(f"Extracted {len(test_cases)} test cases")
    
    # Print the first test case as an example
    if test_cases:
        print("\nExample Test Case:")
        print(f"Query: {test_cases[0]['query']}")
        print("Expected Assessments:")
        for assessment in test_cases[0]['expected_assessments']:
            print(f"- {assessment['name']}")
            
        # Count total assessments
        total_assessments = sum(len(tc['expected_assessments']) for tc in test_cases)
        print(f"\nTotal number of assessments across all test cases: {total_assessments}")

if __name__ == "__main__":
    main()