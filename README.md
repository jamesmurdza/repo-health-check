# GitHub Repository Health Dashboard

Get meaningful health metrics for any GitHub repository.

![Preview](https://github.com/user-attachments/assets/d1050e7f-469b-4c69-8232-25e552a46b23)

This web app takes the URL of a public GitHub repository, and provides relevant and up-to-date data on the GitHub's open source activity and community.

This is useful for maintainers to see where the project can improve, and for users to see if the project is well maintained.

### Metrics Measured
| Responsiveness | Activity | Community Engagement |
|---|---|---|
| Median issue close time<br>Median PR merge time<br>Number of stale issues<br>Number of stale PRs | Commits in the last 30 days<br>Active contributors<br>Issue close rate<br>PR merge rate | Health score<br>New contributors<br>Good first issues<br>External contribution percentage |

## Technical Implementation

The core technical components are outlined below:

**Backend:**
*   Flask-based backend
*   Integration with the [GitHub REST API v3](https://docs.github.com/en/rest) and the [Community Health API](https://docs.github.com/en/rest/metrics/community)
*  File-based caching to store GitHub API responses for 24 hours.

**Frontend:**
*   Bootstrap for responsive CSS styling
*   Font Awesome for scalable icons
*   Chart.js for interactive data visualizations

## Setup Instructions

### On Replit

To use this as a Replit template:

1.  **Remix on Replit:** Click the "Remix" button to create your own copy.
2.  **Connect to GitHub:** When prompted, sign into your GitHub account to authorize access.

### Local Setup

To run this application locally, run the following:

```
pip install -r requirements.txt
python app.py
```

## Development Process

I developed this application iteratively using Replit Agent 3, starting with an [extensive initial prompt](attached_assets/Pasted--GitHub-Repository-Health-Dashboard-Build-a-Flask-web-app-analyzing-GitHub-repo-health-metrics-w--1758717270345_1758717270345.txt).

Following the initial version, I used series of focused follow-up prompts to make improvements in:
*   UX/UI and aesthetics.
*   Structural adjustments.
*   Information clarity.
*   Data visualizations.
*   Bug fixes and optimization.

## Future Improvements

*   Refine repository health metrics using real-world repository examples for better accuracy and relevance.
*   Provide detailed explanations for each metric's calculation and significance.
*   Add additional data visualizations.
