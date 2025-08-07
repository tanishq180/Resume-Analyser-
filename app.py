import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import uuid
from werkzeug.utils import secure_filename
import tempfile
import os.path

from resume_parser import parse_resume
from job_analyzer import analyze_job_description
from skill_matcher import match_skills, calculate_skill_gaps, get_recommendations

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "resume-analyzer-secret")

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# In-memory storage for user data
user_data = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    # Check if a file was submitted
    if 'resume' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['resume']
    
    # Check if filename is empty
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    
    # Check if file type is allowed
    if file and allowed_file(file.filename):
        # Generate a session ID if not exists
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())
        
        user_id = session['user_id']
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Parse resume
            resume_data = parse_resume(file_path)
            
            # Store data in memory
            if user_id not in user_data:
                user_data[user_id] = {}
            
            user_data[user_id]['resume'] = resume_data
            
            # Redirect to resume analysis page
            return redirect(url_for('resume_analysis'))
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            flash(f'Error parsing resume: {str(e)}', 'danger')
            return redirect(url_for('index'))
        finally:
            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        flash('File type not allowed. Please upload a PDF or Word document.', 'danger')
        return redirect(url_for('index'))

@app.route('/resume_analysis')
def resume_analysis():
    user_id = session.get('user_id')
    if not user_id or user_id not in user_data or 'resume' not in user_data[user_id]:
        flash('Please upload your resume first', 'warning')
        return redirect(url_for('index'))
    
    resume_data = user_data[user_id]['resume']
    return render_template('resume_analysis.html', resume=resume_data)

@app.route('/analyze_job', methods=['POST'])
def analyze_job():
    user_id = session.get('user_id')
    if not user_id or user_id not in user_data or 'resume' not in user_data[user_id]:
        flash('Please upload your resume first', 'warning')
        return redirect(url_for('index'))
    
    job_description = request.form.get('job_description', '')
    job_title = request.form.get('job_title', 'Job Position')
    
    if not job_description:
        flash('Please enter a job description', 'warning')
        return redirect(url_for('resume_analysis'))
    
    # Analyze job description
    job_data = analyze_job_description(job_description, job_title)
    
    # Store job data
    if 'jobs' not in user_data[user_id]:
        user_data[user_id]['jobs'] = []
    
    user_data[user_id]['jobs'].append(job_data)
    
    # Match skills and calculate gaps
    resume_skills = user_data[user_id]['resume']['skills']
    match_percentage, matching_skills, missing_skills = match_skills(resume_skills, job_data['required_skills'])
    skill_gaps = calculate_skill_gaps(resume_skills, job_data['required_skills'])
    recommendations = get_recommendations(missing_skills)
    
    # Store analysis results
    job_data['match_percentage'] = match_percentage
    job_data['matching_skills'] = matching_skills
    job_data['missing_skills'] = missing_skills
    job_data['skill_gaps'] = skill_gaps
    job_data['recommendations'] = recommendations
    
    return redirect(url_for('skill_gaps', job_index=len(user_data[user_id]['jobs']) - 1))

@app.route('/skill_gaps/<int:job_index>')
def skill_gaps(job_index):
    user_id = session.get('user_id')
    if not user_id or user_id not in user_data or 'resume' not in user_data[user_id]:
        flash('Please upload your resume first', 'warning')
        return redirect(url_for('index'))
    
    if 'jobs' not in user_data[user_id] or job_index >= len(user_data[user_id]['jobs']):
        flash('Job not found', 'danger')
        return redirect(url_for('resume_analysis'))
    
    resume = user_data[user_id]['resume']
    job = user_data[user_id]['jobs'][job_index]
    
    return render_template(
        'skill_gaps.html', 
        resume=resume, 
        job=job, 
        job_index=job_index
    )

# Removed job listing and job matches routes to focus only on the analysis section

@app.route('/clear_data', methods=['POST'])
def clear_data():
    if 'user_id' in session:
        user_id = session['user_id']
        if user_id in user_data:
            del user_data[user_id]
        session.pop('user_id', None)
    
    flash('Your data has been cleared', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
