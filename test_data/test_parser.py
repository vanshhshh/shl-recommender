"""
Simple parser for SHL test data.
"""
import json
import re

def clean_content(file_path):
    """Clean and normalize the test content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove header
    content = re.sub(r'^Query\s+Assessments\s+URL\s*\n', '', content)
    
    # Fix multi-line assessment names with URL on next line
    # This combines them properly for easier parsing
    content = re.sub(r'([^\n]+)\n(https://[^\n]+)', r'\1 \2', content)
    
    return content

def parse_data(content):
    """Parse the content into test cases."""
    # Split by empty lines to get blocks
    blocks = re.split(r'\n\s*\n+', content)
    
    test_cases = []
    
    for i in range(0, len(blocks), 2):
        # Skip if we don't have both a query and assessments block
        if i + 1 >= len(blocks):
            break
            
        query_block = blocks[i].strip()
        assessments_block = blocks[i + 1].strip()
        
        # Process the assessments block
        assessments = []
        lines = assessments_block.split('\n')
        
        j = 0
        while j < len(lines):
            line = lines[j]
            if '| SHL' in line and 'https://' in line:
                # Line has both name and URL
                parts = line.split('| SHL')
                name = parts[0].strip()
                url_part = parts[1].strip()
                
                assessments.append({
                    'name': name,
                    'url': url_part
                })
                j += 1
            elif '| SHL' in line and j + 1 < len(lines) and 'https://' in lines[j + 1]:
                # Name and URL on separate lines
                name = line.split('| SHL')[0].strip()
                url = lines[j + 1].strip()
                
                assessments.append({
                    'name': name,
                    'url': url
                })
                j += 2
            else:
                j += 1
        
        # Create the test case
        if query_block and assessments:
            test_cases.append({
                'query': query_block,
                'expected_assessments': assessments
            })
    
    return test_cases

def manually_parse():
    """Manually parse the file for the specific format."""
    test_cases = []
    
    # First test case - Java developers
    java_query = """I am hiring for Java developers who
can also collaborate effectively with
my business teams. Looking for an
assessment(s) that can be
completed in 40 minutes.""".replace('\n', ' ')
    
    java_assessments = [
        {"name": "Automata - Fix (New)", "url": "https://www.shl.com/solutions/products/productcatalog/view/automata-fix-new/"},
        {"name": "Core Java (Entry Level) (New)", "url": "https://www.shl.com/solutions/products/productcatalog/view/core-java-entry-level-new/"},
        {"name": "Java 8 (New)", "url": "https://www.shl.com/solutions/products/productcatalog/view/java-8-new/"},
        {"name": "Core Java (Advanced Level) (New)", "url": "https://www.shl.com/solutions/products/productcatalog/view/core-java-advanced-level-new/"},
        {"name": "Agile Software Development", "url": "https://www.shl.com/solutions/products/productcatalog/view/agile-software-development/"},
        {"name": "Technology Professional 8.0 Job Focused Assessment", "url": "https://www.shl.com/solutions/products/productcatalog/view/technology-professional-8-0-jobfocused-assessment/"},
        {"name": "Computer Science (New)", "url": "https://www.shl.com/solutions/products/productcatalog/view/computer-science-new/"}
    ]
    
    # Second test case - Sales role
    sales_query = """I want to hire new graduates for a
sales role in my company, the
budget is for about an hour for each
test. Give me some options""".replace('\n', ' ')
    
    sales_assessments = [
        {"name": "Entry level Sales 7.1 (International)", "url": "https://www.shl.com/solutions/products/productcatalog/view/entry-level-sales-7-1/"},
        {"name": "Entry Level Sales Sift Out 7.1", "url": "https://www.shl.com/solutions/products/productcatalog/view/entry-level-sales-sift-out-7-1/"},
        {"name": "Entry Level Sales Solution", "url": "https://www.shl.com/solutions/products/productcatalog/view/entry-level-sales-solution/"},
        {"name": "Sales Representative Solution", "url": "https://www.shl.com/solutions/products/productcatalog/view/sales-representative-solution/"},
        {"name": "Sales Support Specialist Solution", "url": "https://www.shl.com/solutions/products/productcatalog/view/sales-support-specialist-solution/"},
        {"name": "Technical Sales Associate Solution", "url": "https://www.shl.com/solutions/products/productcatalog/view/technical-sales-associate-solution/"},
        {"name": "SVAR - Spoken English (Indian Accent) (New)", "url": "https://www.shl.com/solutions/products/productcatalog/view/svar-spoken-english-indian-accentnew/"},
        {"name": "Sales & Service Phone Solution", "url": "https://www.shl.com/solutions/products/productcatalog/view/sales-and-service-phone-solution/"},
        {"name": "Sales & Service Phone Simulation", "url": "https://www.shl.com/solutions/products/productcatalog/view/sales-and-service-phone-simulation/"},
        {"name": "English Comprehension (New)", "url": "https://www.shl.com/solutions/products/productcatalog/view/english-comprehension-new/"}
    ]
    
    test_cases.append({
        'query': java_query,
        'expected_assessments': java_assessments
    })
    
    test_cases.append({
        'query': sales_query,
        'expected_assessments': sales_assessments
    })
    
    return test_cases

def main():
    # First try to parse automatically
    content = clean_content('shl_test_data.txt')
    test_cases = parse_data(content)
    
    # If automatic parsing doesn't work, use manual parsing
    if not test_cases:
        print("Automatic parsing failed, using manual parsing...")
        test_cases = manually_parse()
    
    # Save results
    with open('parsed_test_cases.json', 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, indent=2)
    
    # Print summary
    print(f"Saved {len(test_cases)} test cases with {sum(len(tc['expected_assessments']) for tc in test_cases)} total assessments")
    
    # Print example
    if test_cases:
        print("\nExample Test Case:")
        print(f"Query: {test_cases[0]['query']}")
        print(f"Number of assessments: {len(test_cases[0]['expected_assessments'])}")
        print("First 3 expected assessments:")
        for assessment in test_cases[0]['expected_assessments'][:3]:
            print(f"- {assessment['name']}")

if __name__ == "__main__":
    main()