# Overview

The GitHub Repository Health Dashboard is a Flask web application that analyzes the health and activity metrics of GitHub repositories. The app provides a comprehensive view of repository responsiveness, activity levels, and community engagement through an intuitive dashboard interface. Users can input any GitHub repository URL and receive detailed analytics with visual indicators, charts, and modal popups containing supporting data.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The frontend uses a traditional server-side rendered architecture with Flask templates and Bootstrap 5 for styling:

- **Template Structure**: Base template (`base.html`) provides common layout with Bootstrap, Font Awesome icons, and Chart.js integration
- **Home Page**: Simple form interface for repository URL input with client-side validation
- **Results Page**: Dynamic dashboard with loading indicators and metric cards organized into three main sections (Responsiveness, Activity, Community)
- **Interactive Components**: Modal dialogs for detailed metric analysis with charts and supporting data tables
- **Responsive Design**: Bootstrap grid system ensures mobile-friendly layout across all screen sizes

## Backend Architecture
The Flask application follows a simple monolithic architecture pattern:

- **Single Application File**: All route handlers and business logic contained in `app.py`
- **API Integration**: Direct integration with GitHub REST API v3 for repository data fetching
- **Caching Strategy**: File-based caching system to reduce API calls and improve performance
- **Error Handling**: Flash message system for user feedback on form validation and API errors

## Data Management
The application implements a lightweight caching mechanism without a traditional database:

- **File-Based Cache**: JSON files stored in `/cache` directory with MD5-hashed filenames
- **Cache Invalidation**: Time-based expiration (24 hours) to ensure data freshness
- **Data Processing**: In-memory processing of GitHub API responses to calculate health metrics
- **Metric Calculations**: Real-time computation of responsiveness, activity, and community metrics from cached API data

## Authentication Strategy
The application uses optional GitHub token authentication:

- **Environment-Based**: GitHub personal access token loaded from `GITHUB_TOKEN` environment variable
- **Fallback Support**: Graceful degradation to unauthenticated API requests when token unavailable
- **Rate Limit Handling**: Caching strategy designed to work within GitHub API rate limits

# External Dependencies

## Third-Party Services
- **GitHub REST API v3**: Primary data source for repository information, issues, pull requests, commits, and contributors
- **GitHub Community Health API**: Provides repository health scores and documentation analysis

## Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework for responsive design and UI components
- **Font Awesome 6.4.0**: Icon library for visual indicators and UI elements
- **Chart.js**: JavaScript charting library for data visualizations in modal dialogs

## Python Libraries
- **Flask**: Web framework for routing, templating, and request handling
- **requests**: HTTP library for GitHub API communication
- **python-dateutil**: Date parsing and manipulation for timestamp processing

## Development Tools
- **Environment Variables**: Configuration management for sensitive data like API tokens
- **Session Management**: Flask's built-in session handling with configurable secret keys