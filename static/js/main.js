// Main JavaScript file for SHL Assessment Recommendation Engine

document.addEventListener('DOMContentLoaded', function() {
    // Get form and elements
    const form = document.getElementById('jobDescriptionForm');
    const jobDescriptionTextarea = document.getElementById('jobDescription');
    const testTypeSelect = document.getElementById('testType');
    const remoteCheckbox = document.getElementById('remoteAvailable');
    const adaptiveCheckbox = document.getElementById('adaptiveTesting');
    const resultCountBadge = document.getElementById('resultCount');
    const recommendationsContainer = document.getElementById('recommendationsContainer');
    const recommendationsList = document.getElementById('recommendationsList');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const noResultsMessage = document.getElementById('noResultsMessage');
    
    // Modal elements
    const assessmentDetailModal = new bootstrap.Modal(document.getElementById('assessmentDetailModal'));
    const modalTitle = document.getElementById('assessmentDetailModalLabel');
    const modalBody = document.getElementById('assessmentModalBody');
    const assessmentLink = document.getElementById('assessmentLink');
    
    // Handle form submission
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Get job description and validate
        const jobDescription = jobDescriptionTextarea.value.trim();
        if (!jobDescription) {
            showAlert('Please enter a job description', 'danger');
            return;
        }
        
        // Get filters
        const filters = {
            test_type: testTypeSelect.value || null,
            remote_available: remoteCheckbox.checked ? true : null,
            adaptive_testing: adaptiveCheckbox.checked ? true : null
        };
        
        // Show loading indicator
        showLoading(true);
        
        // Make API request
        fetchRecommendations(jobDescription, filters);
    });
    
    // Function to fetch recommendations from the API
    function fetchRecommendations(jobDescription, filters) {
        fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                job_description: jobDescription,
                filters: filters
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            showLoading(false);
            
            // Handle response
            displayRecommendations(data.recommendations);
            
            // Update count badge
            resultCountBadge.textContent = `${data.count} results`;
        })
        .catch(error => {
            console.error('Error fetching recommendations:', error);
            showLoading(false);
            showAlert(`Error: ${error.message}`, 'danger');
        });
    }
    
    // Function to display recommendations
    function displayRecommendations(recommendations) {
        // Clear previous recommendations
        recommendationsList.innerHTML = '';
        
        if (recommendations.length === 0) {
            // Show no results message
            noResultsMessage.classList.remove('d-none');
            recommendationsContainer.classList.add('d-none');
            return;
        }
        
        // Hide no results message and show container
        noResultsMessage.classList.add('d-none');
        recommendationsContainer.classList.remove('d-none');
        
        // Add each recommendation to the list
        recommendations.forEach(assessment => {
            const score = assessment.similarity_score;
            let scoreClass = 'bg-danger';
            
            // Determine color class based on score
            if (score >= 0.8) {
                scoreClass = 'bg-success';
            } else if (score >= 0.6) {
                scoreClass = 'bg-primary';
            } else if (score >= 0.4) {
                scoreClass = 'bg-warning';
            }
            
            // Format score as percentage
            const scorePercent = Math.round(score * 100);
            
            // Create list item
            const listItem = document.createElement('div');
            listItem.className = 'list-group-item recommendation-card d-flex align-items-center gap-3 py-3';
            listItem.dataset.assessmentId = assessment.id;
            
            // Create score indicator
            const scoreIndicator = document.createElement('div');
            scoreIndicator.className = `similarity-indicator ${scoreClass} text-white flex-shrink-0`;
            scoreIndicator.textContent = `${scorePercent}%`;
            
            // Create content container
            const content = document.createElement('div');
            content.className = 'flex-grow-1';
            
            // Create header with type badge
            const header = document.createElement('div');
            header.className = 'd-flex justify-content-between align-items-center mb-1';
            
            const title = document.createElement('h5');
            title.className = 'mb-0';
            title.textContent = assessment.name;
            
            const typeBadge = document.createElement('span');
            typeBadge.className = `badge badge-${assessment.type.toLowerCase()}`;
            typeBadge.textContent = assessment.type;
            
            header.appendChild(title);
            header.appendChild(typeBadge);
            
            // Duration and other details
            const details = document.createElement('div');
            details.className = 'text-muted mb-2';
            details.innerHTML = `<i class="far fa-clock me-1"></i>${assessment.duration_minutes} minutes`;
            
            // Add remote and adaptive badges if applicable
            if (assessment.remote_available) {
                const remoteBadge = document.createElement('span');
                remoteBadge.className = 'badge bg-info ms-2';
                remoteBadge.innerHTML = '<i class="fas fa-wifi me-1"></i>Remote';
                details.appendChild(remoteBadge);
            }
            
            if (assessment.adaptive_testing) {
                const adaptiveBadge = document.createElement('span');
                adaptiveBadge.className = 'badge bg-secondary ms-2';
                adaptiveBadge.innerHTML = '<i class="fas fa-cogs me-1"></i>Adaptive';
                details.appendChild(adaptiveBadge);
            }
            
            // Description (truncated)
            const description = document.createElement('p');
            description.className = 'mb-1';
            description.textContent = truncateText(assessment.description, 100);
            
            // Assemble content
            content.appendChild(header);
            content.appendChild(details);
            content.appendChild(description);
            
            // Assemble list item
            listItem.appendChild(scoreIndicator);
            listItem.appendChild(content);
            
            // Add click handler to show details
            listItem.addEventListener('click', () => {
                showAssessmentDetails(assessment);
            });
            
            // Add to recommendations list
            recommendationsList.appendChild(listItem);
        });
    }
    
    // Function to show assessment details in modal
    function showAssessmentDetails(assessment) {
        // Set modal title
        modalTitle.textContent = assessment.name;
        
        // Set modal content
        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <p class="lead">${assessment.description}</p>
                    
                    <h6>Assessment Details:</h6>
                    <ul class="list-group mb-3">
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Type
                            <span class="badge badge-${assessment.type.toLowerCase()}">${assessment.type}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Duration
                            <span>${assessment.duration_minutes} minutes</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Remote Available
                            <span>${assessment.remote_available ? 'Yes' : 'No'}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Adaptive Testing
                            <span>${assessment.adaptive_testing ? 'Yes' : 'No'}</span>
                        </li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Match Score</h5>
                            <div class="similarity-indicator ${getScoreColorClass(assessment.similarity_score)} text-white mx-auto mb-2">
                                ${Math.round(assessment.similarity_score * 100)}%
                            </div>
                            <p class="card-text small text-muted">Based on cosine similarity between job description and assessment</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <h6 class="mt-3">Skills Assessed:</h6>
            <div class="mb-3">
                ${generateSkillTags(assessment.skills)}
            </div>
        `;
        
        // Set the link to the assessment
        assessmentLink.href = assessment.link;
        
        // Show the modal
        assessmentDetailModal.show();
    }
    
    // Helper functions
    
    // Function to truncate text with ellipsis
    function truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
    
    // Function to get color class based on score
    function getScoreColorClass(score) {
        if (score >= 0.8) return 'bg-success';
        if (score >= 0.6) return 'bg-primary';
        if (score >= 0.4) return 'bg-warning';
        return 'bg-danger';
    }
    
    // Function to generate skill tags from comma-separated string
    function generateSkillTags(skillsString) {
        if (!skillsString) return '';
        
        const skills = skillsString.split(',').map(skill => skill.trim());
        return skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('');
    }
    
    // Function to show/hide loading indicator
    function showLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.classList.remove('d-none');
            recommendationsContainer.classList.add('d-none');
            noResultsMessage.classList.add('d-none');
        } else {
            loadingIndicator.classList.add('d-none');
        }
    }
    
    // Function to show alert messages
    function showAlert(message, type = 'primary') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert at the top of the form
        form.prepend(alertDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
    
    // Example job descriptions for different roles
    const examples = {
        datascientist: `Data Scientist

Job Description:
We are looking for a Data Scientist to join our growing analytics team. The ideal candidate will have strong statistical analysis skills, experience with machine learning algorithms, and proficiency in Python and R. This role involves analyzing large datasets, developing predictive models, and creating data visualizations to communicate insights to stakeholders.

Responsibilities:
- Develop machine learning models and algorithms to solve business problems
- Clean, preprocess, and analyze large datasets
- Create data visualizations and dashboards
- Collaborate with cross-functional teams to implement data-driven solutions
- Present findings and recommendations to stakeholders

Requirements:
- Bachelor's or Master's degree in Statistics, Computer Science, or related field
- 2+ years of experience in data science or similar role
- Proficiency in Python and/or R
- Experience with SQL and database systems
- Knowledge of machine learning techniques and statistical analysis
- Excellent communication and presentation skills`,

        bankassistant: `Bank Administrative Assistant

Job Description:
ICICI Bank is seeking an Administrative Assistant for our branch operations team. This role will support branch managers and banking staff with administrative tasks, customer service coordination, and document processing. The ideal candidate is detail-oriented, organized, and possesses excellent communication skills.

Responsibilities:
- Process banking forms and documents according to established procedures
- Coordinate schedules, appointments, and meetings for branch management
- Provide basic customer service support and direct customers to appropriate departments
- Assist with data entry and maintenance of banking records
- Handle correspondence and maintain filing systems
- Prepare reports and presentations for branch leadership

Requirements:
- High school diploma required, Associate's degree preferred
- 0-2 years of experience in administrative or clerical roles
- Proficiency in Microsoft Office Suite (Excel, Word, Outlook)
- Strong attention to detail and organizational skills
- Excellent verbal and written communication abilities
- Customer service orientation with a professional demeanor`,

        salesmanager: `Sales Manager - Regional Team

Job Description:
We are seeking an experienced Sales Manager to lead our regional sales team and drive revenue growth. The ideal candidate will have a proven track record of sales leadership, team development, and client relationship management. This role will be responsible for setting sales targets, coaching representatives, and implementing sales strategies.

Responsibilities:
- Lead and develop a team of 10-15 sales representatives
- Build and maintain strategic relationships with key clients
- Establish sales targets and develop strategies to achieve them
- Analyze sales data and market trends to optimize sales performance
- Provide regular coaching and performance feedback to team members
- Collaborate with marketing and product teams to refine sales approach

Requirements:
- Bachelor's degree in Business, Marketing, or related field
- 5+ years in sales with at least 2 years in a management role
- Proven track record of exceeding sales targets
- Strong leadership, coaching, and team development skills
- Excellent negotiation and client relationship management abilities
- Experience with CRM systems and sales analytics tools`
    };
    
    // Set default example to data scientist
    document.getElementById('jobDescription').value = examples.datascientist;
    
    // Add example selector buttons
    const exampleButtonsContainer = document.createElement('div');
    exampleButtonsContainer.className = 'mb-3 d-flex gap-2';
    exampleButtonsContainer.innerHTML = `
        <small class="text-muted me-2">Try example:</small>
        <button class="btn btn-sm btn-outline-secondary active" data-example="datascientist">Data Scientist</button>
        <button class="btn btn-sm btn-outline-secondary" data-example="bankassistant">Bank Assistant</button>
        <button class="btn btn-sm btn-outline-secondary" data-example="salesmanager">Sales Manager</button>
    `;
    
    // Insert before the form
    form.insertBefore(exampleButtonsContainer, form.firstChild);
    
    // Add event listeners to example buttons
    exampleButtonsContainer.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', (event) => {
            // Set active class
            exampleButtonsContainer.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Set example text
            const exampleKey = event.target.dataset.example;
            document.getElementById('jobDescription').value = examples[exampleKey];
        });
    });
});
