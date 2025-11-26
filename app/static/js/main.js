// Main JavaScript for AI Internship Matching System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Skills input helper
    const skillsInputs = document.querySelectorAll('textarea[name*="skills"], input[name*="skills"]');
    skillsInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            // Clean up skills format (remove extra spaces, normalize commas)
            let value = this.value;
            if (value) {
                value = value.split(',')
                           .map(skill => skill.trim())
                           .filter(skill => skill.length > 0)
                           .join(', ');
                this.value = value;
            }
        });
    });

    // Dynamic form enhancements
    enhanceMatchingInterface();
    enhanceProfileCompleteness();
    enhanceInterestButtons();
});

// Enhance matching interface with loading states
function enhanceMatchingInterface() {
    const generateMatchButtons = document.querySelectorAll('a[href*="generate-matches"]');
    
    generateMatchButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            // Add loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating Matches...';
            this.classList.add('disabled');
            
            // Show progress indicator
            showMatchingProgress();
        });
    });
}

// Show matching progress animation
function showMatchingProgress() {
    const progressModal = createProgressModal();
    document.body.appendChild(progressModal);
    
    const modal = new bootstrap.Modal(progressModal);
    modal.show();
    
    // Simulate progress
    const progressBar = progressModal.querySelector('.progress-bar');
    let progress = 0;
    
    const progressInterval = setInterval(function() {
        progress += Math.random() * 20;
        if (progress > 100) progress = 100;
        
        progressBar.style.width = progress + '%';
        progressBar.textContent = Math.round(progress) + '%';
        
        if (progress >= 100) {
            clearInterval(progressInterval);
            setTimeout(function() {
                modal.hide();
                progressModal.remove();
            }, 1000);
        }
    }, 300);
}

// Create progress modal
function createProgressModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content" style="background: rgba(255,255,255,0.95); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.2); border-radius: 16px;">
                <div class="modal-header" style="background: linear-gradient(90deg, #75b8f7, #6ac0f1); border-bottom: none; border-radius: 16px 16px 0 0; color: white;">
                    <h5 class="modal-title" style="color: white; font-weight: 600;">
                        <i class="fas fa-robot me-2"></i>AI Matching in Progress
                    </h5>
                </div>
                <div class="modal-body text-center" style="padding: 2rem;">
                    <div class="mb-3">
                        <i class="fas fa-brain fa-3x mb-3" style="color: #3b82f6; animation: pulse 2s infinite;"></i>
                        <p style="color: #1f2937; font-weight: 500; font-size: 1.1rem;">Our AI is analyzing your profile and finding the best matches...</p>
                    </div>
                    <div class="progress" style="height: 24px; background-color: #e5e7eb; border-radius: 12px; overflow: hidden;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 0%; background: linear-gradient(90deg, #3b82f6, #1d4ed8); border-radius: 12px; font-weight: 600; color: white;">0%</div>
                    </div>
                    <div class="mt-3">
                        <small style="color: #4b5563; font-weight: 500;">
                            Analyzing skills • Checking preferences • Applying fairness criteria
                        </small>
                    </div>
                </div>
            </div>
        </div>
        <style>
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        </style>
    `;
    return modal;
}

// Enhance profile completeness with interactive feedback
function enhanceProfileCompleteness() {
    const completenessSection = document.querySelector('.profile-completeness');
    if (!completenessSection) return;
    
    // Add interactive tips for improving profile
    const missingItems = completenessSection.querySelectorAll('li');
    missingItems.forEach(function(item) {
        item.style.cursor = 'pointer';
        item.title = 'Click for tips on improving this section';
        
        item.addEventListener('click', function() {
            showProfileTip(this.textContent);
        });
    });
}

// Show profile improvement tips
function showProfileTip(section) {
    const tips = {
        'Technical Skills': 'Add programming languages, software tools, and technical abilities you possess. Be specific (e.g., "Python, Django, MySQL" instead of just "Programming").',
        'Sector Interests': 'List the industries or sectors you\'re interested in working for (e.g., "Technology, Fintech, Healthcare, E-commerce").',
        'Preferred Locations': 'Specify cities or regions where you\'d like to work, or mention if you\'re open to remote work.',
        'CGPA/Percentage': 'Adding your academic performance helps in better matching with internships that fit your academic level.',
        'Year of Study': 'This helps companies find interns at the right academic level for their programs.'
    };
    
    const tip = tips[section] || 'Complete this section to improve your profile and get better matches.';
    
    // Show tooltip or modal with tip
    showTipModal(section, tip);
}

// Show tip modal
function showTipModal(title, tip) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-lightbulb me-2"></i>Profile Tip: ${title}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${tip}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Got it!</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    modal.addEventListener('hidden.bs.modal', function() {
        modal.remove();
    });
}

// Enhance interest buttons with feedback
function enhanceInterestButtons() {
    // This would be expanded to handle actual interest submission
    window.showInterest = function(internshipId) {
        const button = event.target;
        const originalText = button.innerHTML;
        
        // Simulate API call
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
        button.disabled = true;
        
        setTimeout(function() {
            button.innerHTML = '<i class="fas fa-check me-2"></i>Interest Shown!';
            button.classList.remove('btn-primary');
            button.classList.add('btn-success');
            
            // Show success message
            showNotification('Interest submitted successfully! The department will be notified.', 'success');
        }, 1500);
    };
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 350px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatScore(score) {
    return Math.round(score * 100) + '%';
}

// Initialize any charts or data visualizations
function initializeCharts() {
    // This would be expanded to include Chart.js or D3.js visualizations
    // for match statistics, profile analytics, etc.
}

// Export functions for use in other scripts
window.InternshipMatching = {
    showInterest: window.showInterest,
    showNotification: showNotification,
    formatDate: formatDate,
    formatScore: formatScore
};
