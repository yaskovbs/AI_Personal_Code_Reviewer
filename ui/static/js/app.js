/**
 * AI Personal Code Reviewer - Main Application JavaScript
 */

// Global variables
let currentUser = null;
let analysisResults = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadUserSession();
    updateLineNumbers();
});

/**
 * Initialize application
 */
function initializeApp() {
    // Check session
    fetch('/api/session')
        .then(response => response.json())
        .then(data => {
            if (data.logged_in) {
                currentUser = data.user_id;
                updateUserInterface(data.user_id);
                loadUserStatistics();
            }
        })
        .catch(error => console.error('Error checking session:', error));
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Login button
    document.getElementById('loginBtn').addEventListener('click', showLoginModal);
    
    // Login form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Modal close
    document.querySelector('.close').addEventListener('click', hideLoginModal);
    
    // File upload
    document.getElementById('uploadBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
    
    document.getElementById('fileInput').addEventListener('change', handleFileUpload);
    
    // Code editor
    document.getElementById('codeEditor').addEventListener('input', updateLineNumbers);
    document.getElementById('codeEditor').addEventListener('scroll', syncScroll);
    
    // Action buttons
    document.getElementById('analyzeBtn').addEventListener('click', analyzeCode);
    document.getElementById('clearBtn').addEventListener('click', clearEditor);
    document.getElementById('exampleBtn').addEventListener('click', loadExample);
    
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', switchTab);
    });
}

/**
 * Show login modal
 */
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
}

/**
 * Hide login modal
 */
function hideLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

/**
 * Handle login/registration
 */
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('usernameInput').value;
    const email = document.getElementById('emailInput').value;
    
    try {
        const response = await fetch('/api/profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email })
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user_id;
            updateUserInterface(username);
            hideLoginModal();
            loadUserStatistics();
            showNotification('התחברת בהצלחה!', 'success');
        } else {
            showNotification('שגיאה בהתחברות', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('שגיאה בהתחברות', 'error');
    }
}

/**
 * Update user interface after login
 */
function updateUserInterface(username) {
    document.getElementById('username').textContent = username;
    document.getElementById('loginBtn').innerHTML = '<i class="fas fa-sign-out-alt"></i> התנתק';
    document.getElementById('loginBtn').removeEventListener('click', showLoginModal);
    document.getElementById('loginBtn').addEventListener('click', handleLogout);
}

/**
 * Handle logout
 */
async function handleLogout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        currentUser = null;
        document.getElementById('username').textContent = 'אורח';
        document.getElementById('loginBtn').innerHTML = '<i class="fas fa-user"></i> התחבר';
        document.getElementById('loginBtn').removeEventListener('click', handleLogout);
        document.getElementById('loginBtn').addEventListener('click', showLoginModal);
        clearStatistics();
        showNotification('התנתקת בהצלחה', 'info');
    } catch (error) {
        console.error('Logout error:', error);
    }
}

/**
 * Handle file upload
 */
function handleFileUpload(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('codeEditor').value = e.target.result;
            updateLineNumbers();
            
            // Detect language from file extension
            const ext = file.name.split('.').pop().toLowerCase();
            const langMap = {
                'py': 'python',
                'js': 'javascript',
                'java': 'java',
                'cpp': 'cpp',
                'cs': 'csharp'
            };
            if (langMap[ext]) {
                document.getElementById('languageSelect').value = langMap[ext];
            }
        };
        reader.readAsText(file);
    }
}

/**
 * Update line numbers in editor
 */
function updateLineNumbers() {
    const textarea = document.getElementById('codeEditor');
    const lineNumbers = document.getElementById('lineNumbers');
    const lines = textarea.value.split('\n').length;
    
    let numbersHtml = '';
    for (let i = 1; i <= lines; i++) {
        numbersHtml += `<div>${i}</div>`;
    }
    lineNumbers.innerHTML = numbersHtml;
}

/**
 * Sync scroll between editor and line numbers
 */
function syncScroll() {
    const textarea = document.getElementById('codeEditor');
    const lineNumbers = document.getElementById('lineNumbers');
    lineNumbers.scrollTop = textarea.scrollTop;
}

/**
 * Analyze code
 */
async function analyzeCode() {
    const code = document.getElementById('codeEditor').value;
    const language = document.getElementById('languageSelect').value;
    
    if (!code.trim()) {
        showNotification('אנא הכנס קוד לניתוח', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code,
                language,
                user_id: currentUser || 'anonymous'
            })
        });
        
        if (response.ok) {
            analysisResults = await response.json();
            displayResults(analysisResults);
            showNotification('הניתוח הושלם בהצלחה!', 'success');
            
            // Update user statistics if logged in
            if (currentUser) {
                loadUserStatistics();
            }
        } else {
            showNotification('שגיאה בניתוח הקוד', 'error');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showNotification('שגיאה בניתוח הקוד', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Display analysis results
 */
function displayResults(results) {
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    
    // Update summary cards
    updateSummaryCards(results);
    
    // Update tabs content
    displayIssues(results.analysis.issues);
    displayRecommendations(results.recommendations);
    displayPatterns(results.patterns);
    displayMetrics(results.analysis.metrics);
    displayStyleAnalysis(results.analysis.style_patterns);
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Update summary cards
 */
function updateSummaryCards(results) {
    // Calculate quality score
    const qualityScore = calculateQualityScore(results);
    document.getElementById('qualityScore').textContent = qualityScore + '%';
    
    // Issues count
    document.getElementById('issuesCount').textContent = results.analysis.issues.length;
    
    // Recommendations count
    document.getElementById('recommendationsCount').textContent = results.recommendations.length;
    
    // Complexity score
    document.getElementById('complexityScore').textContent = results.analysis.metrics.complexity || 0;
}

/**
 * Calculate quality score
 */
function calculateQualityScore(results) {
    let score = 100;
    
    // Deduct for issues
    results.analysis.issues.forEach(issue => {
        if (issue.severity === 'error') score -= 10;
        else if (issue.severity === 'warning') score -= 5;
        else score -= 2;
    });
    
    // Deduct for complexity
    const complexity = results.analysis.metrics.complexity || 0;
    if (complexity > 20) score -= 15;
    else if (complexity > 10) score -= 10;
    else if (complexity > 5) score -= 5;
    
    return Math.max(0, Math.min(100, score));
}

/**
 * Display issues
 */
function displayIssues(issues) {
    const container = document.getElementById('issuesList');
    
    if (issues.length === 0) {
        container.innerHTML = '<p class="no-data">לא נמצאו בעיות! 🎉</p>';
        return;
    }
    
    let html = '';
    issues.forEach(issue => {
        const severityClass = `severity-${issue.severity}`;
        const icon = getSeverityIcon(issue.severity);
        
        html += `
            <div class="issue-item ${severityClass}">
                <div class="issue-header">
                    <span class="issue-icon">${icon}</span>
                    <span class="issue-type">${issue.type}</span>
                    ${issue.line ? `<span class="issue-line">שורה ${issue.line}</span>` : ''}
                </div>
                <div class="issue-message">${issue.message}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Display recommendations
 */
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsList');
    
    if (recommendations.length === 0) {
        container.innerHTML = '<p class="no-data">הקוד שלך מעולה! אין המלצות נוספות.</p>';
        return;
    }
    
    let html = '';
    recommendations.forEach(rec => {
        const priorityClass = `priority-${rec.priority}`;
        const icon = getPriorityIcon(rec.priority);
        
        html += `
            <div class="recommendation-item ${priorityClass}">
                <div class="rec-header">
                    <span class="rec-icon">${icon}</span>
                    <span class="rec-title">${rec.title}</span>
                    <span class="rec-confidence">ביטחון: ${Math.round(rec.confidence * 100)}%</span>
                </div>
                <div class="rec-description">${rec.description}</div>
                ${rec.line_start ? `<div class="rec-location">שורות ${rec.line_start}-${rec.line_end}</div>` : ''}
                <div class="rec-tags">
                    ${rec.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Display patterns
 */
function displayPatterns(patterns) {
    const container = document.getElementById('patternsList');
    
    let html = '<div class="patterns-grid">';
    
    // Bug patterns
    if (patterns.bug_patterns && patterns.bug_patterns.length > 0) {
        html += '<div class="pattern-section"><h4>דפוסי באגים</h4>';
        patterns.bug_patterns.forEach(pattern => {
            html += `
                <div class="pattern-item">
                    <span class="pattern-type">${pattern.type}</span>
                    <span class="pattern-desc">${pattern.description}</span>
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Code smells
    if (patterns.code_smells && patterns.code_smells.length > 0) {
        html += '<div class="pattern-section"><h4>ריחות קוד</h4>';
        patterns.code_smells.forEach(smell => {
            html += `
                <div class="pattern-item">
                    <span class="pattern-type">${smell.type}</span>
                    <span class="pattern-desc">${smell.suggestion}</span>
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Security issues
    if (patterns.security_issues && patterns.security_issues.length > 0) {
        html += '<div class="pattern-section"><h4>בעיות אבטחה</h4>';
        patterns.security_issues.forEach(issue => {
            html += `
                <div class="pattern-item security-issue">
                    <span class="pattern-type">${issue.type}</span>
                    <span class="pattern-desc">${issue.suggestion}</span>
                </div>
            `;
        });
        html += '</div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Display metrics
 */
function displayMetrics(metrics) {
    const container = document.getElementById('metricsList');
    
    let html = '<div class="metrics-grid">';
    
    for (const [key, value] of Object.entries(metrics)) {
        const label = getMetricLabel(key);
        const icon = getMetricIcon(key);
        
        html += `
            <div class="metric-item">
                <div class="metric-icon">${icon}</div>
                <div class="metric-label">${label}</div>
                <div class="metric-value">${value}</div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Display style analysis
 */
function displayStyleAnalysis(stylePatterns) {
    const container = document.getElementById('styleAnalysis');
    
    let html = '<div class="style-grid">';
    
    for (const [category, pattern] of Object.entries(stylePatterns)) {
        html += `
            <div class="style-category">
                <h4>${getStyleCategoryLabel(category)}</h4>
                <div class="style-details">
                    ${formatStylePattern(pattern)}
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Switch tab
 */
function switchTab(e) {
    const tabName = e.currentTarget.dataset.tab;
    
    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.currentTarget.classList.add('active');
    
    // Update active tab content
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

/**
 * Clear editor
 */
function clearEditor() {
    document.getElementById('codeEditor').value = '';
    updateLineNumbers();
    document.getElementById('resultsSection').style.display = 'none';
}

/**
 * Load example code
 */
function loadExample() {
    const exampleCode = `def calculate_average(numbers):
    # Calculate the average of a list of numbers
    total = 0
    for num in numbers:
        total = total + num
    average = total / len(numbers)
    return average

# Test the function
numbers = [1, 2, 3, 4, 5]
result = calculate_average(numbers)
print("The average is: " + str(result))

# This could be improved with better error handling
# and more Pythonic code style`;
    
    document.getElementById('codeEditor').value = exampleCode;
    document.getElementById('languageSelect').value = 'python';
    updateLineNumbers();
}

/**
 * Load user session
 */
async function loadUserSession() {
    try {
        const response = await fetch('/api/session');
        const data = await response.json();
        
        if (data.logged_in && data.user_id !== 'anonymous') {
            currentUser = data.user_id;
            // Load user profile
            const profileResponse = await fetch(`/api/profile/${data.user_id}`);
            if (profileResponse.ok) {
                const profile = await profileResponse.json();
                updateUserInterface(profile.username);
                loadUserStatistics();
            }
        }
    } catch (error) {
        console.error('Error loading session:', error);
    }
}

/**
 * Load user statistics
 */
async function loadUserStatistics() {
    if (!currentUser || currentUser === 'anonymous') return;
    
    try {
        const response = await fetch(`/api/statistics/${currentUser}`);
        if (response.ok) {
            const stats = await response.json();
            updateStatistics(stats);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

/**
 * Update statistics display
 */
function updateStatistics(stats) {
    document.getElementById('totalAnalyses').textContent = stats.total_analyses || 0;
    document.getElementById('totalLines').textContent = stats.total_lines || 0;
    document.getElementById('avgQuality').textContent = 
        stats.average_quality_score ? Math.round(stats.average_quality_score) + '%' : '-';
    document.getElementById('favLanguage').textContent = stats.favorite_language || '-';
}

/**
 * Clear statistics display
 */
function clearStatistics() {
    document.getElementById('totalAnalyses').textContent = '0';
    document.getElementById('totalLines').textContent = '0';
    document.getElementById('avgQuality').textContent = '-';
    document.getElementById('favLanguage').textContent = '-';
}

/**
 * Show loading overlay
 */
function showLoading(show) {
    document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}

/**
 * Show notification
 */
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas ${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Helper functions
function getSeverityIcon(severity) {
    const icons = {
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    return icons[severity] || '📌';
}

function getPriorityIcon(priority) {
    const icons = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    };
    return icons[priority] || '⚪';
}

function getMetricLabel(key) {
    const labels = {
        'lines_of_code': 'שורות קוד',
        'num_functions': 'פונקציות',
        'num_classes': 'מחלקות',
        'num_imports': 'ייבואים',
        'complexity': 'מורכבות',
        'max_line_length': 'אורך שורה מקסימלי',
        'num_comments': 'הערות',
        'docstring_coverage': 'כיסוי תיעוד'
    };
    return labels[key] || key;
}

function getMetricIcon(key) {
    const icons = {
        'lines_of_code': '📝',
        'num_functions': '⚡',
        'num_classes': '📦',
        'num_imports': '📥',
        'complexity': '🔄',
        'max_line_length': '📏',
        'num_comments': '💬',
        'docstring_coverage': '📚'
    };
    return icons[key] || '📊';
}

function getStyleCategoryLabel(category) {
    const labels = {
        'naming_convention': 'סגנון שמות',
        'indentation': 'הזחה',
        'quote_style': 'סגנון מרכאות',
        'spacing': 'רווחים'
    };
    return labels[category] || category;
}

function formatStylePattern(pattern) {
    if (typeof pattern === 'object') {
        return Object.entries(pattern)
            .map(([key, value]) => `<div>${key}: ${value}</div>`)
            .join('');
    }
    return pattern;
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    return icons[type] || 'fa-info-circle';
}
