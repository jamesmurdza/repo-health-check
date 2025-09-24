import os
import json
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import requests
from dateutil.parser import parse

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')

# GitHub API configuration
GITHUB_API_BASE = 'https://api.github.com'
CACHE_DIR = 'cache'
CACHE_DURATION_HOURS = 24

# Create cache directory
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_github_headers():
    """Get GitHub API headers with optional authentication"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'GitHub-Health-Dashboard'
    }
    
    # Check for GitHub token from environment
    github_token = os.environ.get('GITHUB_TOKEN')
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    return headers

def get_cache_key(url):
    """Generate cache key from URL"""
    return hashlib.md5(url.encode()).hexdigest()

def is_cache_valid(cache_file):
    """Check if cache file is still valid (within 24 hours)"""
    if not os.path.exists(cache_file):
        return False
    
    cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
    return datetime.now() - cache_time < timedelta(hours=CACHE_DURATION_HOURS)

def get_cached_data(url):
    """Get data from cache if valid, otherwise fetch from API"""
    cache_key = get_cache_key(url)
    cache_file = os.path.join(CACHE_DIR, f'{cache_key}.json')
    
    # Check cache first
    if is_cache_valid(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    # Fetch from API
    try:
        response = requests.get(url, headers=get_github_headers())
        response.raise_for_status()
        data = response.json()
        
        # Cache the response
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

def parse_github_url(url):
    """Parse GitHub repository URL to extract owner and repo"""
    url = url.strip().rstrip('/')
    
    if url.startswith('https://github.com/'):
        path = url.replace('https://github.com/', '')
    elif url.startswith('github.com/'):
        path = url.replace('github.com/', '')
    else:
        # Assume it's already in owner/repo format
        path = url
    
    parts = path.split('/')
    if len(parts) >= 2:
        return parts[0], parts[1]
    else:
        raise ValueError("Invalid GitHub repository URL")

@app.route('/')
def home():
    """Home page with repository URL input form"""
    return render_template('home.html')

@app.route('/analyze', methods=['POST'])
def analyze_repository():
    """Analyze repository and redirect to results"""
    repo_url = request.form.get('repo_url', '').strip()
    
    if not repo_url:
        flash('Please enter a GitHub repository URL', 'error')
        return redirect(url_for('home'))
    
    try:
        owner, repo = parse_github_url(repo_url)
        return redirect(url_for('results', owner=owner, repo=repo))
    except ValueError as e:
        flash('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)', 'error')
        return redirect(url_for('home'))

@app.route('/results/<owner>/<repo>')
def results(owner, repo):
    """Results page showing repository health metrics"""
    return render_template('results.html', owner=owner, repo=repo)

@app.route('/api/analyze/<owner>/<repo>')
def api_analyze(owner, repo):
    """API endpoint to analyze repository and return health metrics"""
    try:
        analyzer = GitHubHealthAnalyzer(owner, repo)
        metrics = analyzer.analyze()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

class GitHubHealthAnalyzer:
    def __init__(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.base_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    
    def analyze(self):
        """Analyze repository and return all health metrics"""
        # Get basic repository info
        repo_data = get_cached_data(self.base_url)
        if not repo_data:
            raise Exception("Repository not found or API limit exceeded")
        
        metrics = {
            'repo_name': f"{self.owner}/{self.repo}",
            'responsiveness': self._analyze_responsiveness(),
            'activity': self._analyze_activity(repo_data),
            'community': self._analyze_community()
        }
        
        return metrics
    
    def _analyze_responsiveness(self):
        """Analyze responsiveness metrics"""
        # Get closed issues (last 100)
        issues_url = f"{GITHUB_API_BASE}/search/issues?q=repo:{self.owner}/{self.repo}+type:issue+state:closed&sort=updated&order=desc&per_page=100"
        issues_data = get_cached_data(issues_url)
        
        # Get merged PRs (last 100)  
        prs_url = f"{GITHUB_API_BASE}/search/issues?q=repo:{self.owner}/{self.repo}+type:pr+state:closed+is:merged&sort=updated&order=desc&per_page=100"
        prs_data = get_cached_data(prs_url)
        
        # Get stale issues/PRs
        stale_date = (datetime.now() - timedelta(days=60)).isoformat()
        stale_issues_url = f"{GITHUB_API_BASE}/search/issues?q=repo:{self.owner}/{self.repo}+state:open+updated:<{stale_date}"
        stale_data = get_cached_data(stale_issues_url)
        
        # Calculate metrics
        issue_close_times = self._calculate_close_times(issues_data)
        pr_merge_times = self._calculate_close_times(prs_data)
        
        return {
            'median_issue_close_time': self._calculate_median(issue_close_times),
            'median_pr_merge_time': self._calculate_median(pr_merge_times),
            'stale_items': stale_data.get('total_count', 0) if stale_data else 0,
            'issue_close_times_distribution': self._create_time_distribution(issue_close_times),
            'pr_merge_times_distribution': self._create_time_distribution(pr_merge_times)
        }
    
    def _analyze_activity(self, repo_data):
        """Analyze activity metrics"""
        # Get commits from last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        commits_url = f"{self.base_url}/commits?since={thirty_days_ago}&per_page=100"
        commits_data = get_cached_data(commits_url)
        
        # Get contributors
        contributors_url = f"{self.base_url}/contributors?per_page=100"
        contributors_data = get_cached_data(contributors_url)
        
        # Get all issues and PRs for rates
        all_issues_url = f"{GITHUB_API_BASE}/search/issues?q=repo:{self.owner}/{self.repo}+type:issue"
        all_issues_data = get_cached_data(all_issues_url)
        
        closed_issues_url = f"{GITHUB_API_BASE}/search/issues?q=repo:{self.owner}/{self.repo}+type:issue+state:closed"
        closed_issues_data = get_cached_data(closed_issues_url)
        
        all_prs_url = f"{GITHUB_API_BASE}/search/issues?q=repo:{self.owner}/{self.repo}+type:pr"
        all_prs_data = get_cached_data(all_prs_url)
        
        merged_prs_url = f"{GITHUB_API_BASE}/search/issues?q=repo:{self.owner}/{self.repo}+type:pr+is:merged"
        merged_prs_data = get_cached_data(merged_prs_url)
        
        # Calculate active contributors this month
        active_contributors = self._count_active_contributors(commits_data)
        
        # Calculate rates
        total_issues = all_issues_data.get('total_count', 0) if all_issues_data else 0
        closed_issues = closed_issues_data.get('total_count', 0) if closed_issues_data else 0
        issue_close_rate = (closed_issues / total_issues * 100) if total_issues > 0 else 0
        
        total_prs = all_prs_data.get('total_count', 0) if all_prs_data else 0
        merged_prs = merged_prs_data.get('total_count', 0) if merged_prs_data else 0
        pr_merge_rate = (merged_prs / total_prs * 100) if total_prs > 0 else 0
        
        return {
            'commits_last_30_days': len(commits_data) if commits_data else 0,
            'active_contributors': active_contributors,
            'issue_close_rate': round(issue_close_rate, 1),
            'pr_merge_rate': round(pr_merge_rate, 1),
            'top_contributors': self._get_top_contributors(contributors_data)
        }
    
    def _analyze_community(self):
        """Analyze community metrics"""
        # Get community profile (health score)
        community_url = f"{self.base_url}/community/profile"
        community_data = get_cached_data(community_url)
        
        # Get good first issues
        first_issues_url = f"{GITHUB_API_BASE}/search/issues?q=repo:{self.owner}/{self.repo}+label:'good first issue'+state:open"
        first_issues_data = get_cached_data(first_issues_url)
        
        # Calculate new contributors (simplified - contributors this month vs last month)
        new_contributors = self._calculate_new_contributors()
        
        # Calculate external contribution percentage
        external_contrib_pct = self._calculate_external_contributions()
        
        health_score = 0
        health_files = []
        if community_data and 'health_percentage' in community_data:
            health_score = community_data['health_percentage']
            if 'files' in community_data:
                health_files = self._format_health_files(community_data['files'])
        
        return {
            'health_score': health_score,
            'new_contributors': new_contributors,
            'good_first_issues': first_issues_data.get('total_count', 0) if first_issues_data else 0,
            'external_contribution_pct': external_contrib_pct,
            'health_files': health_files
        }
    
    def _calculate_close_times(self, data):
        """Calculate time between creation and closure for issues/PRs"""
        if not data or 'items' not in data:
            return []
        
        close_times = []
        for item in data['items']:
            if item.get('created_at') and item.get('closed_at'):
                created = parse(item['created_at'])
                closed = parse(item['closed_at'])
                days = (closed - created).days
                close_times.append(days)
        
        return close_times
    
    def _calculate_median(self, values):
        """Calculate median of a list of values"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
    
    def _create_time_distribution(self, times):
        """Create distribution of close times for histogram"""
        if not times:
            return {}
        
        bins = {'<1d': 0, '1-2d': 0, '2-7d': 0, '1-2w': 0, '2-4w': 0, '1-3m': 0, '>3m': 0}
        
        for days in times:
            if days < 1:
                bins['<1d'] += 1
            elif days < 2:
                bins['1-2d'] += 1
            elif days < 7:
                bins['2-7d'] += 1
            elif days < 14:
                bins['1-2w'] += 1
            elif days < 28:
                bins['2-4w'] += 1
            elif days < 90:
                bins['1-3m'] += 1
            else:
                bins['>3m'] += 1
        
        return bins
    
    def _count_active_contributors(self, commits_data):
        """Count unique contributors from recent commits"""
        if not commits_data:
            return 0
        
        contributors = set()
        for commit in commits_data:
            if commit.get('author') and commit['author'].get('login'):
                contributors.add(commit['author']['login'])
        
        return len(contributors)
    
    def _get_top_contributors(self, contributors_data):
        """Get top 10 contributors by commit count"""
        if not contributors_data:
            return []
        
        # Sort by contributions and take top 10
        sorted_contributors = sorted(contributors_data, key=lambda x: x.get('contributions', 0), reverse=True)[:10]
        
        return [{
            'username': contrib.get('login', 'Unknown'),
            'contributions': contrib.get('contributions', 0)
        } for contrib in sorted_contributors]
    
    def _calculate_new_contributors(self):
        """Calculate new contributors (simplified implementation)"""
        # This is a simplified implementation
        # In a full implementation, you'd compare contributors from this month vs last month
        return 0
    
    def _calculate_external_contributions(self):
        """Calculate external contribution percentage (simplified implementation)"""
        # This is a simplified implementation
        # In a full implementation, you'd check if contributors are org members
        return 0
    
    def _format_health_files(self, files):
        """Format health files data for display"""
        file_checks = []
        standard_files = ['readme', 'license', 'contributing', 'code_of_conduct', 'issue_template', 'pull_request_template']
        
        for file_type in standard_files:
            present = file_type in files and files[file_type] is not None
            file_checks.append({
                'name': file_type.replace('_', ' ').title(),
                'present': present
            })
        
        return file_checks

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)