/**
 * SkillSync AI (ResumePilot UI) — Extraction, Section Highlighter, Flask Analysis & Dashboard Helpers
 */
(function () {
  'use strict';

  const $ = (id) => document.getElementById(id);

  // Configure PDF.js Worker if loaded on the page
  if (window.pdfjsLib) {
    window.pdfjsLib.GlobalWorkerOptions.workerSrc =
      'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  }

  // =========================================================================
  // 1. Theme Toggle (persisted across all SkillSync AI routes)
  // =========================================================================
  function initThemeToggle() {
    const themeBtn = $('themeBtn');
    if (!themeBtn) return;

    const currentTheme = localStorage.getItem('rp_theme') || 'auto';
    if (currentTheme !== 'auto') {
      document.documentElement.setAttribute('data-theme', currentTheme);
    }

    themeBtn.onclick = () => {
      const activeTheme = document.documentElement.getAttribute('data-theme');
      const isDark =
        activeTheme === 'dark' ||
        (!activeTheme && window.matchMedia('(prefers-color-scheme: dark)').matches);
      const newTheme = isDark ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('rp_theme', newTheme);
    };
  }

  // =========================================================================
  // 2. Shared UI Utilities (Toast & Flash Dismiss)
  // =========================================================================
  function escapeHtml(s) {
    return String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  }

  function showToast(title, desc) {
    const container = $('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<strong>${escapeHtml(title)}</strong><div style="font-size:12px;color:var(--ink-muted);margin-top:2px">${escapeHtml(desc)}</div>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function initFlashDismiss() {
    document.querySelectorAll('.flash-close').forEach((btn) => {
      btn.addEventListener('click', () => {
        const alert = btn.closest('.flash-alert');
        if (alert) {
          alert.style.opacity = '0';
          alert.style.transform = 'translateY(-8px)';
          setTimeout(() => alert.remove(), 220);
        }
      });
    });
  }

  // =========================================================================
  // 3. ResumePilot Home Page (Extraction, Highlighter & Flask /analyze Submit)
  // =========================================================================
  function initResumePilotInput() {
    const dropEl = $('drop');
    const pasteEl = $('paste');
    if (!dropEl && !pasteEl) return;

    const MAX_FILE_SIZE = 16 * 1024 * 1024; // Matches Flask 16MB limit
    const SECTIONS = [
      'Summary',
      'Experience',
      'Education',
      'Skills',
      'Projects',
      'Certifications',
      'Contact'
    ];

    const SECTION_RX =
      /^[ \t]*(?:#+\s*)?(summary|profile|objective|overview|(?:work\s+|professional\s+|employment\s+)?experience|employment\s+history|work\s+history|education|academic\s+background|qualifications|(?:technical\s+)?skills|core\s+competencies|technologies|(?:key\s+|personal\s+|selected\s+)?projects|project\s+portfolio|certifications?|certificates|licenses|credentials|contact(?:\s+information|\s+info)?)\b/i;

    const SAMPLE_RESUME = `ALEX MORGAN
alex.morgan@email.com • (555) 349-2810 • San Francisco, CA • linkedin.com/in/alexmorgan

SUMMARY
Results-driven Senior Frontend Engineer with 6+ years of experience designing and scaling high-performance web applications. Specialized in JavaScript, TypeScript, React, modern CSS architectures, and accessible user interfaces.

EXPERIENCE
Lead UI Engineer | TechNova Solutions
2022 – Present | San Francisco, CA
• Led the migration of core dashboard to React and TypeScript, improving page speed by 42% and increasing user engagement by 28%.
• Built reusable design system components used across 8 engineering teams, ensuring WCAG 2.1 AA accessibility compliance.
• Mentored 6 junior and mid-level engineers in modern JavaScript standards and CI/CD automated testing best practices.

Frontend Developer | PixelCraft Studios
2019 – 2022 | Austin, TX
• Developed and deployed 14 customer-facing web applications using JavaScript, HTML, CSS, and Node.js.
• Optimized client-side asset parsing and reduced bundle size by 35% through code splitting and Webpack optimization.
• Collaborated closely with product designers and backend engineers using Git, Agile, and Scrum workflows.

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2015 – 2019

SKILLS
• Languages & Web: JavaScript, TypeScript, HTML, CSS, React, Node, Python, SQL
• Frameworks & Tools: Git, CI/CD, Webpack, Docker, AWS
• Practices: Agile, Scrum, Problem Solving, Teamwork, Communication

PROJECTS
• ResumePilot: Browser-based resume inspection tool that extracts and highlights key resume sections.
• CanvasFlow: Lightweight vector manipulation and canvas animation library.

CERTIFICATIONS
• AWS Certified Cloud Practitioner (2023)
• Meta Certified Frontend Developer Specialization (2022)`;

    let text = '';
    let activeFileName = '';
    let activeFile = null;
    let isPasteMode = false;

    function showError(msg) {
      if ($('err')) $('err').textContent = msg || '';
    }

    function classifyHeading(matchedStr) {
      const k = matchedStr.toLowerCase();
      if (/summary|profile|objective|overview/.test(k)) return 'Summary';
      if (/experience|employment|work/.test(k)) return 'Experience';
      if (/education|academic|qualification/.test(k)) return 'Education';
      if (/skill|competenc|technolog/.test(k)) return 'Skills';
      if (/project|portfolio/.test(k)) return 'Projects';
      if (/cert|license|credential/.test(k)) return 'Certifications';
      if (/contact/.test(k)) return 'Contact';
      return '';
    }

    function render(rawText) {
      text = (rawText || '').trim();
      const foundSections = new Set();

      const renderedHtml = text
        .split('\n')
        .map((line) => {
          const trimmed = line.trim();
          const match = trimmed.length < 50 && trimmed.match(SECTION_RX);
          if (match) {
            const sectionName = classifyHeading(match[1]);
            if (sectionName) foundSections.add(sectionName);
            return `<mark>${escapeHtml(line)}</mark>`;
          }
          if (
            !foundSections.has('Contact') &&
            /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/.test(line)
          ) {
            foundSections.add('Contact');
          }
          return escapeHtml(line);
        })
        .join('\n');

      if ($('txt')) $('txt').innerHTML = renderedHtml;

      if ($('chips')) {
        $('chips').innerHTML = SECTIONS.map((s) => {
          const isFound = foundSections.has(s);
          return `<span class="chip${isFound ? ' on' : ''}">${escapeHtml(s)}</span>`;
        }).join('');
      }

      const words = text ? text.split(/\s+/).length : 0;
      const hasContent = text.length > 0 || !!activeFile;

      if ($('go')) $('go').disabled = !hasContent;
      if ($('note')) {
        $('note').textContent = hasContent
          ? `${words.toLocaleString()} ${words === 1 ? 'word' : 'words'} ready to analyze with SkillSync AI.`
          : 'Add a resume to get started.';
      }
    }

    async function extractText(file) {
      const ext = file.name.split('.').pop().toLowerCase();

      if (ext === 'txt') {
        return file.text();
      }

      const buf = await file.arrayBuffer();

      if (ext === 'docx') {
        if (!window.mammoth) throw new Error('Mammoth.js not loaded');
        const res = await window.mammoth.extractRawText({ arrayBuffer: buf });
        return res.value || '';
      }

      if (ext === 'pdf') {
        if (!window.pdfjsLib) throw new Error('PDF.js not loaded');
        const pdf = await window.pdfjsLib.getDocument({ data: buf }).promise;
        let fullText = '';
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          let lastY = null;
          for (const item of content.items) {
            if (lastY !== null && Math.abs(item.transform[5] - lastY) > 2) {
              fullText += '\n';
            } else if (lastY !== null) {
              fullText += ' ';
            }
            fullText += item.str;
            lastY = item.transform[5];
          }
          fullText += '\n\n';
        }
        return fullText;
      }

      if (ext === 'doc') {
        return '';
      }

      throw new Error('Unsupported file extension');
    }

    async function handleFile(file) {
      showError('');
      if (!file) return;

      const ext = file.name.split('.').pop().toLowerCase();
      if (!['pdf', 'docx', 'doc', 'txt'].includes(ext)) {
        return showError('Please upload a PDF, DOCX, DOC, or TXT file.');
      }

      if (file.size > MAX_FILE_SIZE) {
        return showError('That file is over 16 MB. Please upload a smaller file.');
      }

      try {
        const extracted = await extractText(file);
        if (!extracted || !extracted.trim()) {
          if (ext !== 'doc') throw new Error('Empty text');
        }

        activeFile = file;
        activeFileName = file.name;
        if ($('fname')) $('fname').textContent = file.name;
        if (dropEl) dropEl.hidden = true;
        if ($('doc')) $('doc').hidden = false;

        render(extracted || `${file.name} selected — ready for server-side parsing.`);
        showToast('Resume loaded', `Ready to analyze ${file.name}`);
      } catch (err) {
        console.error(err);
        showError('No readable text found. If this is a scanned PDF, please upload a text-based PDF, DOCX, or TXT.');
      }
    }

    function resetAll() {
      activeFile = null;
      activeFileName = '';
      if ($('input')) $('input').value = '';
      if ($('doc')) $('doc').hidden = true;
      if (dropEl) dropEl.hidden = false;
      if (pasteEl) pasteEl.value = '';
      render('');
      showError('');
    }

    function switchTab(pasteSelected) {
      isPasteMode = pasteSelected;
      if ($('t-pa')) $('t-pa').setAttribute('aria-selected', String(pasteSelected));
      if ($('t-up')) $('t-up').setAttribute('aria-selected', String(!pasteSelected));
      if (pasteEl) pasteEl.hidden = !pasteSelected;

      if (pasteSelected) {
        if (dropEl) dropEl.hidden = true;
        if ($('doc')) $('doc').hidden = true;
        render(pasteEl ? pasteEl.value : '');
        if (pasteEl) pasteEl.focus();
      } else {
        const hasFile = !!activeFileName && (!!text || !!activeFile);
        if ($('doc')) $('doc').hidden = !hasFile;
        if (dropEl) dropEl.hidden = hasFile;
        if (hasFile) render(text);
        else render('');
      }
    }

    if ($('t-up')) $('t-up').onclick = () => switchTab(false);
    if ($('t-pa')) $('t-pa').onclick = () => switchTab(true);

    if ($('input')) {
      $('input').onchange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
          handleFile(e.target.files[0]);
        }
      };
    }

    if ($('remove')) $('remove').onclick = resetAll;

    if (dropEl) {
      ['dragenter', 'dragover'].forEach((t) => {
        dropEl.addEventListener(t, (e) => {
          e.preventDefault();
          dropEl.classList.add('over');
        });
      });

      ['dragleave', 'drop'].forEach((t) => {
        dropEl.addEventListener(t, (e) => {
          e.preventDefault();
          dropEl.classList.remove('over');
        });
      });

      dropEl.addEventListener('drop', (e) => {
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          handleFile(e.dataTransfer.files[0]);
        }
      });
    }

    if (pasteEl) {
      pasteEl.oninput = (e) => {
        render(e.target.value.trim());
      };
    }

    if ($('sampleBtn')) {
      $('sampleBtn').onclick = () => {
        activeFile = null;
        activeFileName = 'alex_morgan_resume.pdf';
        isPasteMode = false;
        if ($('t-up')) $('t-up').setAttribute('aria-selected', 'true');
        if ($('t-pa')) $('t-pa').setAttribute('aria-selected', 'false');
        if (pasteEl) {
          pasteEl.hidden = true;
          pasteEl.value = SAMPLE_RESUME;
        }
        if ($('fname')) $('fname').textContent = activeFileName;
        if (dropEl) dropEl.hidden = true;
        if ($('doc')) $('doc').hidden = false;
        if ($('role')) $('role').value = 'Senior Frontend Engineer';
        if ($('jd')) {
          $('jd').value =
            'We are seeking a Senior Frontend Engineer proficient in JavaScript, TypeScript, React, Python, SQL, Docker, AWS, and accessible design systems.';
        }

        render(SAMPLE_RESUME);
        showToast('Sample Loaded', 'Loaded sample resume with 7 detected sections.');
      };
    }

    // Submit to Flask /analyze endpoint
    if ($('go')) {
      $('go').onclick = async () => {
        if (!text.trim() && !activeFile) return;

        showError('');
        const goBtn = $('go');
        const overlay = $('loading-overlay');
        const loadingText = $('loading-text');
        const roleVal = $('role') ? $('role').value.trim() : '';
        const jdVal = $('jd') ? $('jd').value.trim() : '';

        const formData = new FormData();
        if (!isPasteMode && activeFile) {
          formData.append('resume', activeFile);
          if (text.trim()) formData.append('resume_text', text.trim());
        } else {
          formData.append('resume_text', text.trim());
          formData.append('file_name', activeFileName || 'Pasted Text');
        }
        formData.append('job_title', roleVal);
        formData.append('job_description', jdVal);

        goBtn.disabled = true;
        if ($('note')) $('note').textContent = 'Analyzing your resume…';
        if (loadingText) {
          loadingText.textContent = jdVal
            ? 'Parsing resume & calculating skill gaps...'
            : 'Parsing resume and extracting skills...';
        }
        if (overlay) overlay.style.display = 'flex';

        try {
          const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              Accept: 'application/json'
            },
            body: formData
          });

          const data = await response.json();
          if (!response.ok || data.error) {
            throw new Error(data.error || 'Failed to analyze resume.');
          }

          if (data.redirect) {
            window.location.href = data.redirect;
            return;
          }
          throw new Error('Unexpected response from server.');
        } catch (err) {
          if (overlay) overlay.style.display = 'none';
          goBtn.disabled = false;
          render(text);
          showError(err.message || 'Could not analyze resume. Please try again.');
          showToast('Analysis Failed', err.message || 'Please check your input and try again.');
        }
      };
    }

    render('');
  }

  // =========================================================================
  // 4. Dashboard Helpers (resume_analysis.html & skill_gaps.html)
  // =========================================================================
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
    const titleInput = $('job_title');
    const descTextarea = $('job_description');

    chips.forEach((chip) => {
      chip.addEventListener('click', () => {
        const type = chip.dataset.sample;
        if (samples[type] && titleInput && descTextarea) {
          titleInput.value = samples[type].title;
          descTextarea.value = samples[type].description;
          descTextarea.focus();
        }
      });
    });
  }

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
    }, 180);
  }

  function initLoadingTriggers() {
    const analyzeForm = $('analyze-job-form');
    const overlay = $('loading-overlay');
    const loadingText = $('loading-text');

    if (analyzeForm && overlay) {
      analyzeForm.addEventListener('submit', () => {
        if (loadingText) loadingText.textContent = 'Analyzing job requirements and matching skills...';
        overlay.style.display = 'flex';
      });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initFlashDismiss();
    initResumePilotInput();
    initSampleJobs();
    initGaugeAnimation();
    initLoadingTriggers();
  });
})();
