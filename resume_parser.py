import logging
import PyPDF2
import docx
import re
import os
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

# Common technical skills to look for
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

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise
    
    return text

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(docx_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise
    
    return text

def extract_contact_info(text):
    """Extract contact information from text."""
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    email = email_matches[0] if email_matches else ""
    
    # Extract phone
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?(\d{3}[-.\s]?)?\d{3}[-.\s]?\d{4}'
    phone_matches = re.findall(phone_pattern, text)
    phone = ""
    if phone_matches:
        # Handle the case where the first match might be a string or a tuple
        match = phone_matches[0]
        if isinstance(match, tuple):
            # Join all parts of the tuple
            phone = ''.join([part for part in match if part])
        else:
            # Just use the match directly if it's already a string
            phone = match
    
    # Extract name (this is an approximation - first 2-3 words at the start)
    lines = text.split('\n')
    name = ""
    for line in lines:
        if line.strip():
            # Take first non-empty line and extract first 2-3 words as name
            words = line.strip().split()
            if 2 <= len(words) <= 3:
                name = line.strip()
            else:
                name = ' '.join(words[:2])
            break
    
    return {
        'name': name,
        'email': email,
        'phone': phone
    }

def extract_skills(text):
    """Extract skills from text."""
    skills = []
    
    # Tokenize and clean text
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    
    # Check for common skills
    text_lower = text.lower()
    for skill in COMMON_SKILLS:
        # Match whole words only
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            if skill not in skills:
                skills.append(skill)
    
    # Look for skill sections
    skill_section_matches = re.findall(r'(?i)(?:skills|technical skills|proficiencies|competencies)(?:[^\n]*\n){1,20}', text)
    for match in skill_section_matches:
        lines = match.split('\n')
        for line in lines[1:]:  # Skip the header line
            # Split by commas, bullets, or other separators
            skill_items = re.split(r'[,•|]', line)
            for item in skill_items:
                item = item.strip().lower()
                if item and len(item) >= 2 and item not in skills and item not in stop_words:
                    skills.append(item)
    
    return sorted(skills)

def extract_experience(text):
    """Extract work experience from text."""
    experience = []
    
    # Look for experience sections
    exp_pattern = r'(?i)(?:experience|work experience|employment|work history)(?:[^\n]*\n){1,30}?(?=\n\s*(?:education|skills|projects|certifications|references|\Z))'
    exp_sections = re.findall(exp_pattern, text)
    
    # Process each experience section
    for section in exp_sections:
        lines = section.split('\n')
        current_exp = {}
        
        for i, line in enumerate(lines):
            if i == 0:  # Skip the header
                continue
                
            line = line.strip()
            if not line:
                continue
            
            # Try to identify company and position
            if not current_exp.get('company'):
                parts = line.split(' at ', 1)
                if len(parts) > 1:
                    current_exp['position'] = parts[0].strip()
                    current_exp['company'] = parts[1].strip()
                else:
                    # Alternative format: Company - Position
                    parts = line.split(' - ', 1)
                    if len(parts) > 1:
                        current_exp['company'] = parts[0].strip()
                        current_exp['position'] = parts[1].strip()
                    else:
                        # Just store as company for now
                        current_exp['company'] = line
            
            # Look for dates
            date_pattern = r'(?:\d{1,2}/\d{4}|\d{1,2}-\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}|(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4})\s*(?:-|to|–)\s*(?:\d{1,2}/\d{4}|\d{1,2}-\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}|(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}|Present|Current)'
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            if date_match and not current_exp.get('duration'):
                current_exp['duration'] = date_match.group(0)
            
            # Collect responsibilities and descriptions
            if i > 2 and line and not line.startswith(('Company', 'Position', 'Duration')):
                if 'description' not in current_exp:
                    current_exp['description'] = []
                current_exp['description'].append(line)
            
            # If we have enough information, add this experience
            if i > 2 and current_exp.get('company') and len(current_exp.get('description', [])) > 0:
                if current_exp not in experience:
                    experience.append(current_exp)
                current_exp = {}
    
    return experience

def extract_education(text):
    """Extract education information from text."""
    education = []
    
    # Look for education sections
    edu_pattern = r'(?i)(?:education|academic background|qualifications)(?:[^\n]*\n){1,20}?(?=\n\s*(?:experience|skills|projects|certifications|references|\Z))'
    edu_sections = re.findall(edu_pattern, text)
    
    # Process each education section
    for section in edu_sections:
        lines = section.split('\n')
        current_edu = {}
        
        for i, line in enumerate(lines):
            if i == 0:  # Skip the header
                continue
                
            line = line.strip()
            if not line:
                continue
            
            # Try to identify institution and degree
            if not current_edu.get('institution'):
                # First non-empty line is likely the institution
                current_edu['institution'] = line
            elif not current_edu.get('degree'):
                # Second line is likely the degree
                current_edu['degree'] = line
            
            # Look for dates
            date_pattern = r'(?:\d{1,2}/\d{4}|\d{1,2}-\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}|(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4})\s*(?:-|to|–)\s*(?:\d{1,2}/\d{4}|\d{1,2}-\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}|(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}|Present|Current)'
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            if date_match and not current_edu.get('period'):
                current_edu['period'] = date_match.group(0)
            
            # If we have enough information, add this education
            if current_edu.get('institution') and current_edu.get('degree'):
                if i > 3 or i == len(lines)-1:
                    if current_edu not in education:
                        education.append(current_edu)
                    current_edu = {}
    
    return education

def parse_resume(file_path):
    """Parse resume file and extract information."""
    try:
        # Extract text based on file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            text = extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Extract information
        contact_info = extract_contact_info(text)
        skills = extract_skills(text)
        experience = extract_experience(text)
        education = extract_education(text)
        
        # Combine all extracted information
        resume_data = {
            'name': contact_info['name'],
            'email': contact_info['email'],
            'phone': contact_info['phone'],
            'skills': skills,
            'experience': experience,
            'education': education,
            'raw_text': text
        }
        
        return resume_data
    
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        raise
