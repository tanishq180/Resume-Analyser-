import re
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')


except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')

# Common technical skills to look for (same as in resume_parser.py)
COMMON_SKILLS = [
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
    'go', 'rust', 'perl', 'scala', 'r', 'matlab', 'bash', 'shell', 'powershell', 'sql',
    # Web Development
    'html', 'css', 'react', 'angular', 'vue', 'node', 'express', 'django', 'flask', 'spring',
    'asp.net', 'jquery', 'bootstrap', 'tailwind', 'sass', 'less', 'webpack', 'babel', 'nextjs',
    # Databases
    'mysql', 'postgresql', 'mongodb', 'oracle', 'sql server', 'sqlite', 'nosql', 'redis', 
    'dynamodb', 'cassandra', 'elasticsearch', 'firebase',
    # DevOps & Cloud
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions', 
    'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'prometheus', 'grafana',
    # Data Science & AI
    'machine learning', 'deep learning', 'artificial intelligence', 'nlp', 'neural networks',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'scipy', 'matplotlib',
    'tableau', 'power bi', 'data mining', 'computer vision', 'big data',
    # Mobile Development
    'android', 'ios', 'react native', 'flutter', 'xamarin', 'cordova', 'ionic',
    # Tools & Methodologies
    'git', 'svn', 'agile', 'scrum', 'kanban', 'jira', 'confluence', 'trello', 'slack',
    'continuous integration', 'continuous deployment', 'ci/cd', 'tdd', 'bdd', 'devops',
    # Soft Skills
    'problem solving', 'teamwork', 'communication', 'leadership', 'project management',
    'time management', 'critical thinking', 'decision making', 'adaptability', 'creativity'
]

def extract_company_name(text):
    """Extract company name from job description."""
    lines = text.split("\n")
    company = ""
    
    # Look for typical company indicators
    company_indicators = ["company:", "organization:", "employer:", "at ", "with "]
    for line in lines[:10]:  # Check first few lines only
        line_lower = line.lower()
        for indicator in company_indicators:
            if indicator in line_lower:
                parts = line.split(indicator, 1)
                if len(parts) > 1:
                    company = parts[1].strip()
                    break
        if company:
            break
    
    # If no company found, make an educated guess
    if not company:
        # First line might be job title, second might be company
        if len(lines) > 1:
            company = lines[1].strip()
    
    return company

def extract_required_skills(text):
    """Extract required skills from job description."""
    required_skills = []
    
    # Check for skills sections
    skill_sections = []
    
    # Pattern for requirements/qualifications sections
    req_pattern = r'(?i)(?:requirements|qualifications|skills required|required skills|key skills|technical skills)(?:[^\n]*\n){1,30}?(?=\n\s*(?:benefits|about us|company|application|how to apply|\Z))'
    skill_sections.extend(re.findall(req_pattern, text))
    
    # If no specific sections found, use the entire text
    if not skill_sections:
        skill_sections = [text]
    
    # Process each section
    for section in skill_sections:
        # Look for bullet points or numbered lists
        bullet_patterns = [
            r'[•\-\*] (.*?)(?:\n|$)',  # Bullets
            r'^\d+\.\s*(.*?)(?:\n|$)',  # Numbered
            r'(?:^|\n)(?!•|\-|\*|\d+\.)(.*?)(?=\n|$)'  # Regular lines
        ]
        
        for pattern in bullet_patterns:
            items = re.findall(pattern, section, re.MULTILINE)
            for item in items:
                item = item.strip().lower()
                
                # Check if this bullet contains a known skill
                for skill in COMMON_SKILLS:
                    # Match whole words only
                    pattern = r'\b' + re.escape(skill) + r'\b'
                    if re.search(pattern, item):
                        if skill not in required_skills:
                            required_skills.append(skill)
                
                # Also add any items that include years of experience
                if re.search(r'\b(\d+)[\+]?\s*(?:years|yr|yrs)(?:\s+of)?\s+(?:experience|exp)', item):
                    # Extract the technology mentioned with years
                    for skill in COMMON_SKILLS:
                        if skill in item and skill not in required_skills:
                            required_skills.append(skill)
    
    # If skills list is too short, fallback to checking the entire text for common skills
    if len(required_skills) < 3:
        text_lower = text.lower()
        for skill in COMMON_SKILLS:
            # Match whole words only
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower) and skill not in required_skills:
                required_skills.append(skill)
    
    return sorted(required_skills)

def extract_preferred_skills(text):
    """Extract preferred/nice-to-have skills from job description."""
    preferred_skills = []
    
    # Look for preferred skills sections
    pref_pattern = r'(?i)(?:preferred|plus|nice to have|bonus|additionally|desirable)(?:[^\n]*\n){1,15}?(?=\n\s*(?:benefits|about us|company|application|how to apply|\Z))'
    pref_sections = re.findall(pref_pattern, text)
    
    # Process each section
    for section in pref_sections:
        # Look for bullet points or numbered lists
        bullet_patterns = [
            r'[•\-\*] (.*?)(?:\n|$)',  # Bullets
            r'^\d+\.\s*(.*?)(?:\n|$)',  # Numbered
            r'(?:^|\n)(?!•|\-|\*|\d+\.)(.*?)(?=\n|$)'  # Regular lines
        ]
        
        for pattern in bullet_patterns:
            items = re.findall(pattern, section, re.MULTILINE)
            for item in items:
                item = item.strip().lower()
                
                # Check if this bullet contains a known skill
                for skill in COMMON_SKILLS:
                    # Match whole words only
                    pattern = r'\b' + re.escape(skill) + r'\b'
                    if re.search(pattern, item):
                        if skill not in preferred_skills:
                            preferred_skills.append(skill)
    
    # Make sure preferred skills don't overlap with required skills
    required = extract_required_skills(text)
    preferred_skills = [skill for skill in preferred_skills if skill not in required]
    
    return sorted(preferred_skills)

def extract_experience_requirements(text):
    """Extract years of experience requirements."""
    experience_req = {
        'overall': None,
        'specific': {}
    }
    
    # Look for overall experience
    overall_exp_pattern = r'(?i)(\d+)[\+]?\s*(?:years|yr|yrs)(?:\s+of)?\s+(?:experience|exp)(?!\s+in\s+)'
    overall_match = re.search(overall_exp_pattern, text)
    if overall_match:
        experience_req['overall'] = int(overall_match.group(1))
    
    # Look for specific experience in technologies
    for skill in COMMON_SKILLS:
        pattern = r'(?i)(\d+)[\+]?\s*(?:years|yr|yrs)(?:\s+of)?\s+(?:experience|exp)(?:\s+with|\s+in)?\s+' + re.escape(skill)
        match = re.search(pattern, text)
        if match:
            experience_req['specific'][skill] = int(match.group(1))
    
    return experience_req

def extract_education_requirements(text):
    """Extract education requirements."""
    education_req = {
        'degree': None,
        'field': None
    }
    
    # Look for degree requirements
    degree_pattern = r'(?i)(bachelor\'?s?|master\'?s?|phd|doctorate|bs|ms|ba|ma)(?:\s+degree)?(?:\s+in\s+([^,\.;]+))?'
    degree_match = re.search(degree_pattern, text)
    if degree_match:
        education_req['degree'] = degree_match.group(1)
        if degree_match.group(2):
            education_req['field'] = degree_match.group(2).strip()
    
    return education_req

def analyze_job_description(job_text, job_title=""):
    """Analyze job description and extract key information."""
    try:
        # Extract company name
        company = extract_company_name(job_text)
        
        # Extract skills
        required_skills = extract_required_skills(job_text)
        preferred_skills = extract_preferred_skills(job_text)
        
        # Extract experience requirements
        experience_req = extract_experience_requirements(job_text)
        
        # Extract education requirements
        education_req = extract_education_requirements(job_text)
        
        # Combine all extracted information
        job_data = {
            'title': job_title,
            'company': company,
            'required_skills': required_skills,
            'preferred_skills': preferred_skills,
            'experience_req': experience_req,
            'education_req': education_req,
            'raw_text': job_text
        }
        
        return job_data
    
    except Exception as e:
        logger.error(f"Error analyzing job description: {str(e)}")
        raise
