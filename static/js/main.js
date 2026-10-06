// ==========================================================================
// SkillSync AI / Resume Analyzer - Interactive Frontend Script
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initFileUpload();
  initSampleJobs();
  initGaugeAnimation();
  initFlashDismiss();
  initLoadingTriggers();
});

// File upload drag & drop handling
function initFileUpload() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('resume-file-input');
  const preview = document.getElementById('file-preview');
  const fileNameDisplay = document.getElementById('file-name-text');
  const fileSizeDisplay = document.getElementById('file-size-text');

  if (!dropzone || !fileInput) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      fileInput.files = files;
      updateFilePreview(files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      updateFilePreview(fileInput.files[0]);
    }
  });

  function updateFilePreview(file) {
    if (!preview || !fileNameDisplay) return;
    fileNameDisplay.textContent = file.name;
    const sizeKB = (file.size / 1024).toFixed(1);
    if (fileSizeDisplay) {
      fileSizeDisplay.textContent = `(${sizeKB} KB)`;
    }
    preview.style.display = 'inline-flex';
  }
}

// Sample job descriptions for quick testing
function initSampleJobs() {
  const samples = {
    'data-analyst': {
      title: 'Senior Data Analyst',
      description: `We are looking for a passionate Senior Data Analyst to join our analytics team.
Key Responsibilities & Qualifications:
• 3+ years of experience with SQL, database querying and relational data modeling
• Hands-on expertise with Python or R for statistical analysis and data transformation
• Proficient in Data visualization tools such as Tableau and Power BI
• Advanced Excel skills (pivot tables, lookup formulas, data modeling)
• Strong critical thinking, analytical problem solving, and attention to detail
• Bachelor's degree in Computer Science, Statistics, Mathematics, or related quantitative field.`
    },
    'software-engineer': {
      title: 'Full Stack Software Engineer',
      description: `Join our core product team building scalable cloud services and interactive applications.
Requirements:
• 3+ years experience with Python, JavaScript, and TypeScript
• Strong proficiency with React, Node.js, and modern CSS/HTML
• Experience designing and managing SQL databases (PostgreSQL or MySQL)
• Familiarity with Docker, Git, CI/CD pipelines, and AWS cloud deployment
• Solid background in RESTful APIs, Agile methodologies, and teamwork
• Bachelor's degree in Computer Science or equivalent practical experience.`
    },
    'marketing-manager': {
      title: 'Digital Marketing Manager',
      description: `We are seeking an energetic Marketing Manager to lead our growth and digital campaigns.
Requirements & Skills:
• Proven track record in SEO/SEM and strategic planning
• Expertise in Social media management and engaging content creation
• In-depth familiarity with Analytics tools (Google Analytics, Mixpanel)
• Budget management and campaign optimization
• Strong communication, leadership, and project management skills.`
    }
  };

  const chips = document.querySelectorAll('.sample-job-chip');
  const titleInput = document.getElementById('job_title');
  const descTextarea = document.getElementById('job_description');

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const type = chip.dataset.sample;
      if (samples[type] && titleInput && descTextarea) {
        titleInput.value = samples[type].title;
        descTextarea.value = samples[type].description;
        descTextarea.focus();
        chip.style.transform = 'scale(0.95)';
        setTimeout(() => chip.style.transform = '', 150);
      }
    });
  });
}

// Circular match gauge animation
function initGaugeAnimation() {
  const circle = document.querySelector('.circle-fill');
  if (!circle) return;

  const percent = parseFloat(circle.dataset.percent) || 0;
  const radius = 68;
  const circumference = 2 * Math.PI * radius;

  circle.style.strokeDasharray = `${circumference} ${circumference}`;
  circle.style.strokeDashoffset = circumference;

  setTimeout(() => {
    const offset = circumference - (percent / 100) * circumference;
    circle.style.strokeDashoffset = offset;
  }, 200);
}

// Flash message dismiss button
function initFlashDismiss() {
  const closeBtns = document.querySelectorAll('.flash-close');
  closeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.flash-alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });
}

// Loading spinner on form submit
function initLoadingTriggers() {
  const uploadForm = document.getElementById('upload-form');
  const analyzeForm = document.getElementById('analyze-job-form');
  const overlay = document.getElementById('loading-overlay');
  const loadingText = document.getElementById('loading-text');

  if (uploadForm && overlay) {
    uploadForm.addEventListener('submit', () => {
      if (loadingText) loadingText.textContent = 'Parsing resume and extracting skills...';
      overlay.style.display = 'flex';
    });
  }

  if (analyzeForm && overlay) {
    analyzeForm.addEventListener('submit', () => {
      if (loadingText) loadingText.textContent = 'Analyzing job requirements and matching skills...';
      overlay.style.display = 'flex';
    });
  }
}
