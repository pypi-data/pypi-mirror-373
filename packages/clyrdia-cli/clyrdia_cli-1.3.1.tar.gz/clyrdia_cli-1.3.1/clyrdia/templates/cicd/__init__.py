"""
CI/CD Templates package for Clyrdia CLI.
Provides real, working templates for popular CI/CD platforms.
"""

from .github_actions import GitHubActionsTemplate
from .gitlab_ci import GitLabCITemplate
from .jenkins import JenkinsTemplate
from .circleci import CircleCITemplate
from .azure_devops import AzureDevOpsTemplate

__all__ = [
    'GitHubActionsTemplate',
    'GitLabCITemplate', 
    'JenkinsTemplate',
    'CircleCITemplate',
    'AzureDevOpsTemplate'
]
