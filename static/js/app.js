// Custom JavaScript for GitHub Health Dashboard

// Example repository analysis
function analyzeExample(repoPath) {
    document.getElementById('repo_url').value = repoPath;
    document.getElementById('analyzeForm').submit();
}

// Form validation for home page
document.addEventListener('DOMContentLoaded', function() {
    const analyzeForm = document.getElementById('analyzeForm');
    
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function(e) {
            const repoUrl = document.getElementById('repo_url').value.trim();
            
            if (!repoUrl) {
                e.preventDefault();
                showAlert('Please enter a GitHub repository URL', 'danger');
                return;
            }
            
            // Basic URL validation
            const urlPattern = /(github\.com\/[\w-]+\/[\w-]+|^[\w-]+\/[\w-]+$)/i;
            if (!urlPattern.test(repoUrl)) {
                e.preventDefault();
                showAlert('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)', 'danger');
                return;
            }
        });
    }
});

function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('main .container');
    container.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// Utility functions for results page
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatPercentage(num) {
    return `${Math.round(num)}%`;
}

function formatDays(days) {
    if (days < 1) {
        return '< 1 day';
    } else if (days === 1) {
        return '1 day';
    } else {
        return `${Math.round(days)} days`;
    }
}

// Copy repository URL to clipboard
function copyRepoUrl() {
    const repoName = document.getElementById('repoName').textContent;
    const url = `https://github.com/${repoName}`;
    
    navigator.clipboard.writeText(url).then(() => {
        showAlert('Repository URL copied to clipboard!', 'success');
    }).catch(() => {
        showAlert('Failed to copy URL', 'danger');
    });
}

// Share results functionality
function shareResults() {
    const repoName = document.getElementById('repoName').textContent;
    const url = window.location.href;
    
    if (navigator.share) {
        navigator.share({
            title: `GitHub Health Dashboard - ${repoName}`,
            text: `Check out the health metrics for ${repoName}`,
            url: url
        });
    } else {
        // Fallback: copy URL to clipboard
        navigator.clipboard.writeText(url).then(() => {
            showAlert('Results URL copied to clipboard!', 'success');
        }).catch(() => {
            showAlert('Failed to copy URL', 'danger');
        });
    }
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Smooth scroll for navigation
function smoothScroll(targetId) {
    const target = document.getElementById(targetId);
    if (target) {
        target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // ESC key to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            modal.hide();
        }
    }
    
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const analyzeForm = document.getElementById('analyzeForm');
        if (analyzeForm) {
            analyzeForm.submit();
        }
    }
});

// Lazy loading for charts
function observeChartContainers() {
    const chartContainers = document.querySelectorAll('[data-chart]');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const chartType = entry.target.dataset.chart;
                    loadChart(entry.target, chartType);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        chartContainers.forEach(container => {
            observer.observe(container);
        });
    } else {
        // Fallback for browsers without IntersectionObserver
        chartContainers.forEach(container => {
            const chartType = container.dataset.chart;
            loadChart(container, chartType);
        });
    }
}

function loadChart(container, chartType) {
    // Chart loading logic would go here
    console.log(`Loading ${chartType} chart in container:`, container);
}

// Analytics tracking (placeholder)
function trackEvent(action, category = 'Dashboard', label = '') {
    // Analytics tracking would go here
    console.log(`Track: ${category} - ${action} - ${label}`);
}

// Error handling for API requests
function handleApiError(error) {
    console.error('API Error:', error);
    
    let message = 'An unexpected error occurred. Please try again.';
    
    if (error.message.includes('404')) {
        message = 'Repository not found. Please check the URL and try again.';
    } else if (error.message.includes('403')) {
        message = 'Access denied. This might be a private repository or API limit exceeded.';
    } else if (error.message.includes('rate limit')) {
        message = 'GitHub API rate limit exceeded. Please try again later.';
    }
    
    return message;
}