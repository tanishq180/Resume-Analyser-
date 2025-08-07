import logging
import nltk
from nltk.corpus import wordnet
import random

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Download NLTK data if not already present
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Dictionary of related skills
RELATED_SKILLS = {
    'python': ['django', 'flask', 'fastapi', 'pandas', 'numpy', 'scikit-learn', 'tensorflow'],
    'java': ['spring', 'hibernate', 'maven', 'gradle', 'junit', 'j2ee'],
    'javascript': ['typescript', 'react', 'angular', 'vue', 'node', 'express', 'jquery'],
    'typescript': ['javascript', 'angular', 'react', 'node'],
    'c++': ['c', 'stl', 'boost', 'qt', 'unreal engine'],
    'c#': ['.net', 'asp.net', 'entity framework', 'xamarin'],
    'sql': ['mysql', 'postgresql', 'oracle', 'sql server', 'sqlite'],
    'html': ['css', 'javascript', 'bootstrap', 'sass', 'less'],
    'css': ['html', 'sass', 'less', 'bootstrap', 'tailwind'],
    'react': ['javascript', 'typescript', 'redux', 'nextjs', 'webpack'],
    'angular': ['typescript', 'rxjs', 'ngrx'],
    'vue': ['javascript', 'vuex', 'nuxt'],
    'node': ['javascript', 'express', 'nestjs', 'npm'],
    'aws': ['ec2', 's3', 'lambda', 'cloudformation', 'dynamodb'],
    'azure': ['azure functions', 'azure storage', 'azure devops'],
    'gcp': ['google cloud functions', 'google cloud storage', 'bigquery'],
    'docker': ['kubernetes', 'containerization', 'docker-compose'],
    'machine learning': ['deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp'],
    'agile': ['scrum', 'kanban', 'jira'],
    'git': ['github', 'gitlab', 'bitbucket']
}

# Resources for learning skills
LEARNING_RESOURCES = {
    'python': [
        {'name': 'Python Official Documentation', 'url': 'https://docs.python.org/3/'},
        {'name': 'Codecademy Python Course', 'url': 'https://www.codecademy.com/learn/learn-python-3'},
        {'name': 'Coursera Python for Everybody', 'url': 'https://www.coursera.org/specializations/python'}
    ],
    'java': [
        {'name': 'Oracle Java Tutorial', 'url': 'https://docs.oracle.com/javase/tutorial/'},
        {'name': 'Codecademy Java Course', 'url': 'https://www.codecademy.com/learn/learn-java'},
        {'name': 'Coursera Java Programming', 'url': 'https://www.coursera.org/specializations/java-programming'}
    ],
    'javascript': [
        {'name': 'Mozilla JavaScript Guide', 'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide'},
        {'name': 'Codecademy JavaScript Course', 'url': 'https://www.codecademy.com/learn/introduction-to-javascript'},
        {'name': 'freeCodeCamp JavaScript Algorithms', 'url': 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/'}
    ],
    'html': [
        {'name': 'Mozilla HTML Guide', 'url': 'https://developer.mozilla.org/en-US/docs/Web/HTML'},
        {'name': 'W3Schools HTML Tutorial', 'url': 'https://www.w3schools.com/html/'},
        {'name': 'Codecademy HTML Course', 'url': 'https://www.codecademy.com/learn/learn-html'}
    ],
    'css': [
        {'name': 'Mozilla CSS Guide', 'url': 'https://developer.mozilla.org/en-US/docs/Web/CSS'},
        {'name': 'W3Schools CSS Tutorial', 'url': 'https://www.w3schools.com/css/'},
        {'name': 'Codecademy CSS Course', 'url': 'https://www.codecademy.com/learn/learn-css'}
    ],
    'sql': [
        {'name': 'W3Schools SQL Tutorial', 'url': 'https://www.w3schools.com/sql/'},
        {'name': 'Codecademy SQL Course', 'url': 'https://www.codecademy.com/learn/learn-sql'},
        {'name': 'Khan Academy SQL Course', 'url': 'https://www.khanacademy.org/computing/computer-programming/sql'}
    ],
    'react': [
        {'name': 'React Official Documentation', 'url': 'https://reactjs.org/docs/getting-started.html'},
        {'name': 'Codecademy React Course', 'url': 'https://www.codecademy.com/learn/react-101'},
        {'name': 'React Tutorial on freeCodeCamp', 'url': 'https://www.freecodecamp.org/learn/front-end-libraries/react/'}
    ],
}

def is_similar_skill(skill1, skill2):
    """Check if two skills are similar."""
    # Exact match
    if skill1.lower() == skill2.lower():
        return True
    
    # Check if one is a substring of the other
    if skill1.lower() in skill2.lower() or skill2.lower() in skill1.lower():
        # Only consider it a match if the difference is small
        # (e.g., "java" vs "javascript" should not match)
        len_diff = abs(len(skill1) - len(skill2))
        if len_diff < 3 or len_diff / max(len(skill1), len(skill2)) < 0.3:
            return True
    
    # Check if they're related in our predefined dictionary
    if skill1.lower() in RELATED_SKILLS and skill2.lower() in RELATED_SKILLS[skill1.lower()]:
        return True
    if skill2.lower() in RELATED_SKILLS and skill1.lower() in RELATED_SKILLS[skill2.lower()]:
        return True
    
    # If wordnet is available, check for synonyms
    try:
        skill1_syns = wordnet.synsets(skill1)
        skill2_syns = wordnet.synsets(skill2)
        
        # Check for shared lemmas
        skill1_lemmas = set(lemma.name() for syn in skill1_syns for lemma in syn.lemmas())
        skill2_lemmas = set(lemma.name() for syn in skill2_syns for lemma in syn.lemmas())
        
        if skill1_lemmas.intersection(skill2_lemmas):
            return True
    except:
        # If wordnet lookup fails, just skip this check
        pass
    
    return False

def match_skills(resume_skills, job_skills):
    """Match skills between resume and job requirements."""
    matching_skills = []
    missing_skills = []
    
    for job_skill in job_skills:
        matched = False
        for resume_skill in resume_skills:
            if is_similar_skill(job_skill, resume_skill):
                matching_skills.append(job_skill)
                matched = True
                break
        
        if not matched:
            missing_skills.append(job_skill)
    
    # Calculate match percentage
    if not job_skills:
        match_percentage = 0
    else:
        match_percentage = (len(matching_skills) / len(job_skills)) * 100
    
    return match_percentage, matching_skills, missing_skills

def calculate_skill_gaps(resume_skills, job_skills):
    """Calculate the skill gaps between resume and job requirements."""
    _, matching_skills, missing_skills = match_skills(resume_skills, job_skills)
    
    # For each missing skill, determine the relevance
    skill_gaps = []
    
    for skill in missing_skills:
        # Determine if there are any related skills on the resume
        related_resume_skills = []
        skill_lower = skill.lower()
        
        # Check if the missing skill has related skills defined
        if skill_lower in RELATED_SKILLS:
            related_skills = RELATED_SKILLS[skill_lower]
            # Check if any of the related skills are in the resume
            for related in related_skills:
                for resume_skill in resume_skills:
                    if is_similar_skill(related, resume_skill):
                        related_resume_skills.append(resume_skill)
        
        # Determine importance (right now just a placeholder)
        importance = "high" if len(related_resume_skills) == 0 else "medium"
        
        skill_gaps.append({
            'skill': skill,
            'importance': importance,
            'related_skills': related_resume_skills
        })
    
    return skill_gaps

def get_recommendations(missing_skills):
    """Get recommendations for learning missing skills."""
    recommendations = []
    
    for skill in missing_skills:
        skill_lower = skill.lower()
        
        # Find learning resources
        resources = LEARNING_RESOURCES.get(skill_lower, [])
        
        # If no specific resources, provide general resources
        if not resources:
            resources = [
                {'name': f'Search "{skill} tutorial" on YouTube', 'url': f'https://www.youtube.com/results?search_query={skill}+tutorial'},
                {'name': f'Take an online course on Coursera, Udemy, or edX', 'url': f'https://www.coursera.org/search?query={skill}'},
                {'name': f'Find projects on GitHub to practice', 'url': f'https://github.com/search?q={skill}+project'}
            ]
        
        # Find related skills that might be easier to learn first
        related = RELATED_SKILLS.get(skill_lower, [])
        
        # Create a recommendation
        recommendation = {
            'skill': skill,
            'resources': resources,
            'related_skills': related[:3] if related else [],
            'estimated_time': estimate_learning_time(skill)
        }
        
        recommendations.append(recommendation)
    
    return recommendations

def estimate_learning_time(skill):
    """Estimate the time required to learn a skill to a basic level."""
    # These are rough estimates in weeks
    skill_difficulty = {
        'python': 4,
        'java': 6,
        'javascript': 4,
        'typescript': 3,
        'html': 2,
        'css': 3,
        'react': 4,
        'angular': 5,
        'vue': 4,
        'node': 4,
        'sql': 3,
        'mongodb': 2,
        'aws': 6,
        'azure': 6,
        'gcp': 6,
        'docker': 3,
        'kubernetes': 5,
        'git': 1,
        'agile': 2,
        'machine learning': 8,
        'deep learning': 10
    }
    
    skill_lower = skill.lower()
    
    # Default to 4 weeks if not in our dictionary
    weeks = skill_difficulty.get(skill_lower, 4)
    
    # Generate a range (e.g., "4-6 weeks")
    upper_bound = int(weeks * 1.5)
    return f"{weeks}-{upper_bound} weeks"
