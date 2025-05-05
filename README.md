# Assessment Matcher – Internship Project

This project is an AI-powered assessment recommendation engine designed to help hiring managers select the most suitable tests based on job descriptions. It intelligently parses job descriptions and matches them with relevant assessments using natural language processing (NLP) techniques.

## 🧠 What It Does

Given a job description or hiring query, the system recommends assessments (e.g., coding tests, cognitive ability, personality, sales aptitude, etc.) based on skill relevance, domain keywords, and time constraints.

Example queries it can handle:
- "Hiring a Java developer who can collaborate with the business team"
- "Looking to screen analysts using cognitive and personality assessments within 45 mins"
- "Hiring mid-level Python, SQL, and JavaScript developers – test should be within 60 mins"

## 🚀 Tech Stack

- **Python 3**
- **scikit-learn** (TF-IDF, cosine similarity)
- **Numpy**
- **Regex (re)**
- **Logging**
- **Vercel** (for API/frontend deployment)
- **GitHub** (for version control)
- **Replit** (used for quick testing and prototyping parts of the logic)

## 💡 Features

- Smart job-to-assessment matching using TF-IDF + cosine similarity
- Preprocessing of job descriptions and assessments with domain-specific keyword boosts
- Filters for test duration, test type, remote availability, and adaptive testing
- Handles technical and non-technical roles
- Easily extendable with new assessment categories

## 🛠️ Problems Faced & How I Solved Them

### 1. **Mismatch of SEO roles to coding assessments**
- **Problem:** SEO job descriptions were being matched to programming tests.
- **Solution:** Refined the keyword boosting and added domain-specific penalties to avoid matching unrelated assessments (e.g., penalize coding tests for administrative or SEO roles).

### 2. **No matching assessments for some job roles**
- **Problem:** Some job categories like "SEO" were not returning good results.
- **Solution:** Realized the dataset lacked SEO-specific assessments. Implemented fallback logic to ensure at least one recommendation is returned and expanded the keyword categories to improve coverage.

### 3. **Complexity in boosting relevant categories**
- **Problem:** Basic TF-IDF similarity wasn’t enough for precise matches.
- **Solution:** Built a custom boosting layer on top of TF-IDF scores using domain-specific keyword categories and role-based overrides.

### 4. **API/website deployment confusion**
- **Problem:** Confusion about where and how to deploy the app.
- **Solution:** Used **Vercel** for frontend/API hosting and **Replit** during prototyping to test small modules before integration.

## 📦 Deployment

The project is deployed on **Vercel**.

You can deploy it yourself:

```bash
# If using frontend
vercel deploy
