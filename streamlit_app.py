#!/usr/bin/env python3
"""
GitHub Contribution Graph Hacker - Streamlit Web Application
Based on the original Python implementation

This web app generates fake commits to make your GitHub contribution graph look more active.
Educational purposes only - do not use to mislead employers or others.

Features:
- Interactive web interface
- Multiple commit generation strategies
- Pattern creation
- Commit reversal
- Real-time feedback

Requirements:
- Git installed and configured
- Python 3.6+
- A GitHub repository (preferably private)
"""

import streamlit as st
import datetime
import json
import os
import subprocess
import random
import time
import tempfile
import shutil
from typing import Optional, List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class StreamlitGitHubHacker:
    def __init__(self, repo_path: str = ".", data_file: str = "data.json"):
        """
        Initialize the GitHub Contribution Graph Hacker for Streamlit
        
        Args:
            repo_path: Path to the git repository
            data_file: Name of the JSON file to store commit data
        """
        self.repo_path = repo_path
        self.data_file = data_file
        self.data_path = os.path.join(repo_path, data_file)
        
    def _ensure_git_repo(self):
        """Ensure we're in a git repository"""
        try:
            subprocess.run(["git", "status"], 
                         cwd=self.repo_path, 
                         check=True, 
                         capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def _init_git_repo(self):
        """Initialize git repo if it doesn't exist"""
        try:
            subprocess.run(["git", "init"], cwd=self.repo_path, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _run_git_command(self, command: List[str]) -> tuple[bool, str]:
        """Run a git command and return success status and output"""
        try:
            result = subprocess.run(
                command, 
                cwd=self.repo_path, 
                check=True, 
                capture_output=True, 
                text=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def get_date_string(self, date: datetime.datetime) -> str:
        """Convert datetime to the format GitHub stores internally"""
        return date.strftime("%Y-%m-%d %H:%M:%S")

    def write_data_to_file(self, commit_data: dict) -> bool:
        """Write commit data to JSON file"""
        try:
            # Read existing data if file exists
            existing_data = []
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = []

            # Append new data
            existing_data.append(commit_data)

            # Write back to file
            with open(self.data_path, 'w') as f:
                json.dump(existing_data, f, indent=2)

            return True
        except Exception as e:
            st.error(f"Error writing to file: {e}")
            return False

    def add_commit_and_push(self, date: datetime.datetime, push: bool = True) -> tuple[bool, str]:
        """Add, commit, and optionally push changes"""
        try:
            # Add files to staging (force add to override .gitignore)
            success, output = self._run_git_command(["git", "add", "-f", self.data_file])
            if not success:
                return False, f"Failed to add files: {output}"

            # Create commit message
            commit_message = f"Commit for {self.get_date_string(date)}"

            # Set environment variables for backdating the commit
            env = os.environ.copy()
            date_str = date.strftime("%Y-%m-%d %H:%M:%S")
            env['GIT_AUTHOR_DATE'] = date_str
            env['GIT_COMMITTER_DATE'] = date_str

            # Commit with backdated timestamp
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_path,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, f"Commit failed: {result.stderr}"

            message = f"Committed: {commit_message}"

            # Push if requested
            if push:
                success, push_output = self._run_git_command(["git", "push"])
                if success:
                    message += " and pushed to remote"
                else:
                    message += f" but push failed: {push_output}"

            return True, message

        except Exception as e:
            return False, f"Git operation failed: {e}"

    def get_start_of_year(self, weeks_back: int = 52) -> datetime.datetime:
        """Get the start date for generating commits"""
        today = datetime.datetime.now()
        start_date = today - datetime.timedelta(weeks=weeks_back)
        # Align to start of week (Monday)
        days_since_monday = start_date.weekday()
        start_date = start_date - datetime.timedelta(days=days_since_monday)
        return start_date
    
    def generate_multi_year_commits(self, years: int, min_commits: int = 0, max_commits: int = 3, frequency: float = 0.7, weekend_factor: float = 0.05) -> List[Dict]:
        """Generate commits data for multiple years with weekend frequency adjustment"""
        commits_data = []
        weeks_per_year = 52
        total_weeks = years * weeks_per_year
        
        for x in range(total_weeks):
            for y in range(7):   # 7 days
                # Apply weekend frequency reduction
                adjusted_frequency = apply_weekend_frequency(frequency, y, weekend_factor)
                
                if random.random() < adjusted_frequency:
                    num_commits = random.randint(min_commits, max_commits)
                    for _ in range(num_commits):
                        start_date = self.get_start_of_year(total_weeks)
                        target_date = start_date + datetime.timedelta(weeks=x, days=y)
                        
                        if target_date <= datetime.datetime.now():
                            commits_data.append({
                                'x': x,
                                'y': y,
                                'date': target_date,
                                'date_str': self.get_date_string(target_date)
                            })
        
        return commits_data

    def mark_commit(self, x: int, y: int, push: bool = False) -> tuple[bool, str]:
        """Make a commit at specific X,Y coordinates on the contribution graph"""
        start_date = self.get_start_of_year()
        
        # Calculate the target date
        target_date = start_date + datetime.timedelta(weeks=x, days=y)
        
        # Don't commit in the future
        if target_date > datetime.datetime.now():
            return False, f"Cannot commit in the future: {target_date}"
        
        commit_data = {
            'date': self.get_date_string(target_date),
            'x': x,
            'y': y
        }
        
        # Write data to file
        if not self.write_data_to_file(commit_data):
            return False, "Failed to write data to file"
            
        # Make the commit
        success, message = self.add_commit_and_push(target_date, push=push)
        
        if success:
            return True, f"Marked commit at ({x}, {y}) on {target_date.strftime('%Y-%m-%d')}: {message}"
        else:
            return False, message

    def generate_commits_data(self, num_commits: int = 100, avoid_weekends: bool = True) -> List[Dict]:
        """Generate commit data without actually making commits"""
        commits_data = []
        attempts = 0
        max_attempts = num_commits * 3  # Prevent infinite loop
        
        while len(commits_data) < num_commits and attempts < max_attempts:
            attempts += 1
            
            # Random X coordinate (0-51 weeks)
            x = random.randint(0, 51)
            # Random Y coordinate (0-6 days)
            y = random.randint(0, 6)
            
            # If avoiding weekends, reduce probability for weekend days
            if avoid_weekends and is_weekend_day(y):
                if random.random() > 0.2:  # 80% chance to skip weekend days
                    continue
            
            start_date = self.get_start_of_year()
            target_date = start_date + datetime.timedelta(weeks=x, days=y)
            
            # Don't include future dates
            if target_date <= datetime.datetime.now():
                commits_data.append({
                    'x': x,
                    'y': y,
                    'date': target_date,
                    'date_str': self.get_date_string(target_date)
                })
                
        return commits_data

    def execute_commits(self, commits_data: List[Dict], push_at_end: bool = True) -> tuple[bool, List[str]]:
        """Execute a list of commits"""
        messages = []
        success_count = 0
        
        for i, commit_data in enumerate(commits_data):
            success, message = self.mark_commit(
                commit_data['x'], 
                commit_data['y'], 
                push=False
            )
            
            if success:
                success_count += 1
                messages.append(f"✅ {message}")
            else:
                messages.append(f"❌ {message}")
                
            # Update progress
            if i % 10 == 0:
                st.info(f"Processed {i}/{len(commits_data)} commits...")
        
        # Push all commits at the end if requested
        if push_at_end and success_count > 0:
            success, push_message = self._run_git_command(["git", "push"])
            if success:
                messages.append("✅ All commits pushed to remote repository")
            else:
                messages.append(f"❌ Failed to push: {push_message}")
        
        return success_count > 0, messages

    def create_pattern_commits(self, pattern: List[List[int]]) -> List[Dict]:
        """Create commits data based on a 2D pattern"""
        commits_data = []
        
        for y, row in enumerate(pattern):
            for x, num_commits in enumerate(row):
                if num_commits > 0 and x < 52 and y < 7:  # Ensure within bounds
                    for _ in range(num_commits):
                        start_date = self.get_start_of_year()
                        target_date = start_date + datetime.timedelta(weeks=x, days=y)
                        
                        if target_date <= datetime.datetime.now():
                            commits_data.append({
                                'x': x,
                                'y': y,
                                'date': target_date,
                                'date_str': self.get_date_string(target_date)
                            })
        
        return commits_data

    def get_commit_stats(self) -> Dict[str, Any]:
        """Get statistics about commits in the repository"""
        try:
            # Get total commit count
            success, total_commits = self._run_git_command(['git', 'rev-list', '--count', 'HEAD'])
            if not success:
                return {"error": "Could not get commit count"}
            
            # Get commits by this script
            patterns = [
                '--grep=Commit for 20',
                '--grep=GitHub hack commit',
                '--grep=hack commit'
            ]
            
            script_commits = set()
            for pattern in patterns:
                success, commits = self._run_git_command(['git', 'log', pattern, '--pretty=format:%H'])
                if success and commits.strip():
                    script_commits.update(commits.strip().split('\n'))
            
            script_commits = [c for c in script_commits if c.strip()]
            
            return {
                "total_commits": int(total_commits),
                "script_commits": len(script_commits),
                "script_commit_hashes": script_commits
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_git_config(self) -> Dict[str, Any]:
        """Get Git configuration information"""
        config_info = {}
        
        try:
            # Get user name and email
            success, name = self._run_git_command(['git', 'config', 'user.name'])
            config_info['user_name'] = name if success else "Not configured"
            
            success, email = self._run_git_command(['git', 'config', 'user.email'])
            config_info['user_email'] = email if success else "Not configured"
            
            # Get current branch
            success, branch = self._run_git_command(['git', 'branch', '--show-current'])
            config_info['current_branch'] = branch if success else "Unknown"
            
            # Get remote URL
            success, remote_url = self._run_git_command(['git', 'remote', 'get-url', 'origin'])
            config_info['remote_url'] = remote_url if success else "No remote configured"
            
            # Parse GitHub username from remote URL
            if success and 'github.com' in remote_url:
                if remote_url.startswith('https://github.com/'):
                    # HTTPS format: https://github.com/username/repo.git
                    parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
                    if len(parts) >= 2:
                        config_info['github_username'] = parts[0]
                        config_info['github_repo'] = parts[1]
                elif '@github.com:' in remote_url:
                    # SSH format: git@github.com:username/repo.git
                    parts = remote_url.split(':')[1].replace('.git', '').split('/')
                    if len(parts) >= 2:
                        config_info['github_username'] = parts[0]
                        config_info['github_repo'] = parts[1]
            
            # Get repository status
            success, status = self._run_git_command(['git', 'status', '--porcelain'])
            config_info['has_uncommitted_changes'] = success and bool(status.strip())
            
            # Check if remote is reachable
            success, _ = self._run_git_command(['git', 'ls-remote', '--heads', 'origin'])
            config_info['remote_accessible'] = success
            
            # Get last commit info
            success, last_commit = self._run_git_command(['git', 'log', '-1', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=short'])
            if success and last_commit:
                parts = last_commit.split('|')
                if len(parts) >= 5:
                    config_info['last_commit'] = {
                        'hash': parts[0][:8],
                        'author_name': parts[1],
                        'author_email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    }
            
            return config_info
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get detailed repository information"""
        repo_info = {}
        
        try:
            # Get repository root
            success, repo_root = self._run_git_command(['git', 'rev-parse', '--show-toplevel'])
            repo_info['repo_root'] = repo_root if success else "Unknown"
            
            # Get all branches
            success, branches = self._run_git_command(['git', 'branch', '-a'])
            if success:
                branch_list = [b.strip().replace('* ', '') for b in branches.split('\n') if b.strip()]
                repo_info['branches'] = branch_list
            else:
                repo_info['branches'] = []
            
            # Get number of commits in current branch
            success, commit_count = self._run_git_command(['git', 'rev-list', '--count', 'HEAD'])
            repo_info['total_commits'] = int(commit_count) if success else 0
            
            # Get repository size (approximate)
            success, objects_info = self._run_git_command(['git', 'count-objects', '-v'])
            if success:
                for line in objects_info.split('\n'):
                    if line.startswith('size-pack'):
                        size_kb = line.split()[1]
                        repo_info['size_kb'] = int(size_kb)
                        break
                else:
                    repo_info['size_kb'] = 0
            
            # Check if repository is bare
            success, is_bare = self._run_git_command(['git', 'rev-parse', '--is-bare-repository'])
            repo_info['is_bare'] = success and is_bare.strip().lower() == 'true'
            
            return repo_info
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_available_git_configs(self) -> Dict[str, Any]:
        """Get available Git configurations (global, local, system)"""
        configs = {}
        
        try:
            # Global config
            success, global_name = self._run_git_command(['git', 'config', '--global', 'user.name'])
            success2, global_email = self._run_git_command(['git', 'config', '--global', 'user.email'])
            if success and success2:
                configs['global'] = {
                    'name': global_name,
                    'email': global_email,
                    'scope': 'Global (all repositories)'
                }
            
            # Local config (current repository)
            success, local_name = self._run_git_command(['git', 'config', '--local', 'user.name'])
            success2, local_email = self._run_git_command(['git', 'config', '--local', 'user.email'])
            if success and success2:
                configs['local'] = {
                    'name': local_name,
                    'email': local_email,
                    'scope': 'Local (this repository only)'
                }
            
            # System config
            success, system_name = self._run_git_command(['git', 'config', '--system', 'user.name'])
            success2, system_email = self._run_git_command(['git', 'config', '--system', 'user.email'])
            if success and success2:
                configs['system'] = {
                    'name': system_name,
                    'email': system_email,
                    'scope': 'System (all users)'
                }
            
            return configs
            
        except Exception as e:
            return {"error": str(e)}
    
    def set_git_config(self, name: str, email: str, scope: str = 'local') -> tuple[bool, str]:
        """Set Git configuration for specified scope"""
        try:
            # Set user name
            success1, output1 = self._run_git_command(['git', 'config', f'--{scope}', 'user.name', name])
            # Set user email  
            success2, output2 = self._run_git_command(['git', 'config', f'--{scope}', 'user.email', email])
            
            if success1 and success2:
                return True, f"Git config set successfully for {scope} scope"
            else:
                return False, f"Failed to set config: {output1} {output2}"
                
        except Exception as e:
            return False, str(e)
    
    def get_common_git_accounts(self) -> List[Dict[str, str]]:
        """Get common Git account configurations from git config history"""
        accounts = []
        
        try:
            # Try to get recent commit authors as potential accounts
            success, log_output = self._run_git_command([
                'git', 'log', '--pretty=format:%an|%ae', '--all', '-n', '50'
            ])
            
            if success:
                seen_accounts = set()
                for line in log_output.split('\n'):
                    if '|' in line:
                        name, email = line.split('|', 1)
                        account_key = f"{name}|{email}"
                        if account_key not in seen_accounts and name.strip() and email.strip():
                            seen_accounts.add(account_key)
                            accounts.append({
                                'name': name.strip(),
                                'email': email.strip(),
                                'source': 'Git History'
                            })
                            
                            # Limit to 10 most recent unique accounts
                            if len(accounts) >= 10:
                                break
            
            return accounts
            
        except Exception as e:
            return []
    
    def diagnose_github_profile_issues(self) -> Dict[str, Any]:
        """Diagnose why commits might not appear on GitHub profile"""
        issues = []
        warnings = []
        suggestions = []
        
        try:
            git_config = self.get_git_config()
            
            # Check 1: Email match
            if git_config.get('user_email') == "Not configured":
                issues.append("Git email not configured")
                suggestions.append("Set your Git email: git config user.email 'your@email.com'")
            else:
                warnings.append(f"Current Git email: {git_config['user_email']}")
                suggestions.append("Ensure this email matches one of your GitHub account emails")
            
            # Check 2: Repository visibility
            if 'github_username' in git_config:
                warnings.append(f"Repository: {git_config['github_username']}/{git_config['github_repo']}")
                suggestions.append("Check if this repository is public or if you have private contributions enabled")
            else:
                issues.append("No GitHub remote repository detected")
                suggestions.append("Add a GitHub remote: git remote add origin https://github.com/username/repo.git")
            
            # Check 3: Commits pushed to main branch
            success, current_branch = self._run_git_command(['git', 'branch', '--show-current'])
            if success:
                warnings.append(f"Current branch: {current_branch}")
                if current_branch not in ['main', 'master']:
                    issues.append(f"You're on branch '{current_branch}', not main/master")
                    suggestions.append("GitHub profile only shows commits to the default branch (usually main/master)")
            
            # Check 4: Recent commits
            success, recent_commits = self._run_git_command(['git', 'log', '--oneline', '-5'])
            if success and recent_commits:
                commit_count = len(recent_commits.split('\n'))
                warnings.append(f"Recent commits found: {commit_count}")
            else:
                issues.append("No recent commits found")
                suggestions.append("Make sure commits were actually created and pushed")
            
            # Check 5: Remote push status
            success, push_status = self._run_git_command(['git', 'status', '-uno'])
            if success:
                if "ahead" in push_status:
                    issues.append("You have unpushed commits")
                    suggestions.append("Push your commits: git push origin main")
                elif "up to date" in push_status or "up-to-date" in push_status:
                    warnings.append("Repository is up to date with remote")
            
            # Check 6: Data file in .gitignore
            try:
                with open(os.path.join(self.repo_path, '.gitignore'), 'r') as f:
                    gitignore_content = f.read()
                    if self.data_file in gitignore_content:
                        issues.append(f"Data file '{self.data_file}' is ignored by .gitignore")
                        suggestions.append(f"Remove '{self.data_file}' from .gitignore or use a different filename")
            except FileNotFoundError:
                pass  # No .gitignore file
            
            # Check 7: Fork detection
            if 'github_username' in git_config:
                # This is a basic check - in reality you'd need GitHub API to detect forks properly
                repo_name = git_config['github_repo']
                if 'fork' in repo_name.lower() or 'copy' in repo_name.lower():
                    warnings.append("This might be a fork")
                    suggestions.append("Contributions to forks don't always show on your profile")
            
            return {
                'issues': issues,
                'warnings': warnings, 
                'suggestions': suggestions,
                'git_config': git_config
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def check_commit_authorship(self) -> List[Dict[str, str]]:
        """Check recent commit authorship details"""
        commits = []
        
        try:
            success, log_output = self._run_git_command([
                'git', 'log', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=iso', '-10'
            ])
            
            if success:
                for line in log_output.split('\n'):
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            commits.append({
                                'hash': parts[0][:8],
                                'author_name': parts[1],
                                'author_email': parts[2],
                                'date': parts[3],
                                'message': parts[4]
                            })
            
            return commits
            
        except Exception as e:
            return []
    
    def get_github_profile_tips(self) -> List[str]:
        """Get tips for ensuring commits appear on GitHub profile"""
        return [
            "🔹 Email must match one of your GitHub account emails",
            "🔹 Repository must be public OR you must enable 'Private contributions' in GitHub settings",
            "🔹 Commits must be on the default branch (main/master)",
            "🔹 Commits must be pushed to GitHub (not just committed locally)",
            "🔹 It can take up to 24 hours for contributions to appear",
            "🔹 Commits to forks don't count toward your contribution graph",
            "🔹 Commits must have a valid timestamp (not too far in past/future)",
            "🔹 Your GitHub profile must have the correct timezone settings"
        ]

def create_contribution_graph(commits_data: List[Dict], weeks: int = 52) -> go.Figure:
    """Create a visual representation of the contribution graph"""
    days = 7
    
    # Initialize grid
    grid = [[0 for _ in range(weeks)] for _ in range(days)]
    
    # Fill grid with commit data
    for commit in commits_data:
        x, y = commit['x'], commit['y']
        if 0 <= x < weeks and 0 <= y < days:
            grid[y][x] += 1
    
    # Reverse both axes to match GitHub's layout
    # Y-axis: Sunday at top, Saturday at bottom
    grid = grid[::-1]
    # X-axis: Reverse each row to fix horizontal mirroring
    grid = [row[::-1] for row in grid]
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=grid,
        colorscale='Greens',
        showscale=True,
        hoverongaps=False,
        hovertemplate='Week: %{x}<br>Day: %{customdata}<br>Commits: %{z}<extra></extra>',
        customdata=[['Sun', 'Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon'][i % 7] for i in range(len(grid))]
    ))
    
    fig.update_layout(
        title="GitHub Contribution Graph Preview",
        xaxis_title="Weeks",
        yaxis_title="Days of Week",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(7)),
            ticktext=['Sun', 'Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon']
        ),
        xaxis=dict(
            autorange='reversed'  # Reverse X-axis to fix horizontal mirroring
        ),
        height=300
    )
    
    return fig

def create_pattern_preview(pattern: List[List[int]]) -> go.Figure:
    """Create a visual preview of a pattern"""
    if not pattern or not pattern[0]:
        return go.Figure()
    
    # Reverse both axes to match GitHub's layout and fix mirroring
    # Y-axis: Sunday at top, Saturday at bottom  
    pattern_reversed = pattern[::-1]
    # X-axis: Reverse each row to fix horizontal mirroring
    pattern_reversed = [row[::-1] for row in pattern_reversed]
    
    # Create heatmap for pattern preview
    fig = go.Figure(data=go.Heatmap(
        z=pattern_reversed,
        colorscale='Greens',
        showscale=True,
        hoverongaps=False,
        hovertemplate='Week: %{x}<br>Day: %{customdata}<br>Commits: %{z}<extra></extra>',
        customdata=[['Sun', 'Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon'][i % 7] for i in range(len(pattern_reversed))]
    ))
    
    fig.update_layout(
        title="Pattern Preview",
        xaxis_title="Weeks",
        yaxis_title="Days of Week",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(min(7, len(pattern)))),
            ticktext=['Sun', 'Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon'][:len(pattern)]
        ),
        xaxis=dict(
            autorange='reversed'  # Reverse X-axis to fix horizontal mirroring
        ),
        height=250,
        width=min(800, len(pattern[0]) * 15 + 100)
    )
    
    return fig

def text_to_pattern(text: str, width: int = 50) -> List[List[int]]:
    """Convert text to a pattern suitable for GitHub contribution graph"""
    # Simple character mapping for basic ASCII art
    char_patterns = {
        'A': [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,1,1,1,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1]
        ],
        'B': [
            [1,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,1,1,1,0]
        ],
        'C': [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,1],
            [0,1,1,1,0]
        ],
        'D': [
            [1,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,1,1,1,0]
        ],
        'E': [
            [1,1,1,1,1],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,1]
        ],
        'F': [
            [1,1,1,1,1],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0]
        ],
        'G': [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,0],
            [1,0,1,1,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0]
        ],
        'H': [
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,1,1,1,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1]
        ],
        'I': [
            [1,1,1,1,1],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [1,1,1,1,1]
        ],
        'J': [
            [1,1,1,1,1],
            [0,0,0,1,0],
            [0,0,0,1,0],
            [0,0,0,1,0],
            [0,0,0,1,0],
            [1,0,0,1,0],
            [0,1,1,0,0]
        ],
        'K': [
            [1,0,0,0,1],
            [1,0,0,1,0],
            [1,0,1,0,0],
            [1,1,0,0,0],
            [1,0,1,0,0],
            [1,0,0,1,0],
            [1,0,0,0,1]
        ],
        'L': [
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,1]
        ],
        'M': [
            [1,0,0,0,1],
            [1,1,0,1,1],
            [1,0,1,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1]
        ],
        'N': [
            [1,0,0,0,1],
            [1,1,0,0,1],
            [1,0,1,0,1],
            [1,0,0,1,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1]
        ],
        'O': [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0]
        ],
        'P': [
            [1,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,1,1,1,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0]
        ],
        'Q': [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,1,0,1],
            [1,0,0,1,1],
            [0,1,1,1,1]
        ],
        'R': [
            [1,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,1,1,1,0],
            [1,0,1,0,0],
            [1,0,0,1,0],
            [1,0,0,0,1]
        ],
        'S': [
            [0,1,1,1,1],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [0,1,1,1,0],
            [0,0,0,0,1],
            [0,0,0,0,1],
            [1,1,1,1,0]
        ],
        'T': [
            [1,1,1,1,1],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0]
        ],
        'U': [
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0]
        ],
        'V': [
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,0,1,0],
            [0,0,1,0,0]
        ],
        'W': [
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,1,0,1],
            [1,1,0,1,1],
            [1,0,0,0,1]
        ],
        'X': [
            [1,0,0,0,1],
            [0,1,0,1,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,1,0,1,0],
            [1,0,0,0,1]
        ],
        'Y': [
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,0,1,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0]
        ],
        'Z': [
            [1,1,1,1,1],
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,1,0,0],
            [0,1,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,1]
        ],
        ' ': [
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0]
        ],
        '!': [
            [1],
            [1],
            [1],
            [1],
            [1],
            [0],
            [1]
        ],
        '?': [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,1,0,0],
            [0,0,0,0,0],
            [0,0,1,0,0]
        ],
        '♥': [
            [0,1,1,0,1,1,0],
            [1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1],
            [0,1,1,1,1,1,0],
            [0,0,1,1,1,0,0],
            [0,0,0,1,0,0,0],
            [0,0,0,0,0,0,0]
        ]
    }
    
    text = text.upper().strip()
    if not text:
        return []
    
    # Calculate pattern dimensions
    total_width = 0
    max_height = 7
    
    # Calculate total width needed
    for char in text:
        if char in char_patterns:
            total_width += len(char_patterns[char][0]) + 1  # +1 for spacing
        else:
            total_width += 4  # Default width for unknown characters
    
    if total_width > width:
        # Truncate text if too wide
        truncated_text = ""
        current_width = 0
        for char in text:
            char_width = len(char_patterns.get(char, [[0,0,0,0]])[0]) + 1
            if current_width + char_width <= width:
                truncated_text += char
                current_width += char_width
            else:
                break
        text = truncated_text
    
    # Build the pattern
    pattern = [[0 for _ in range(width)] for _ in range(max_height)]
    
    current_x = 0
    for char in text:
        if char in char_patterns:
            char_pattern = char_patterns[char]
            char_width = len(char_pattern[0])
            
            # Copy character pattern to main pattern
            for y in range(min(len(char_pattern), max_height)):
                for x in range(min(char_width, width - current_x)):
                    if current_x + x < width:
                        pattern[y][current_x + x] = char_pattern[y][x]
            
            current_x += char_width + 1  # +1 for spacing
            
            if current_x >= width:
                break
    
    return pattern

def is_weekend_day(day_of_week: int) -> bool:
    """Check if a day is weekend (Saturday=5, Sunday=6 in 0-6 system where Monday=0)"""
    return day_of_week in [5, 6]  # Saturday and Sunday

def apply_weekend_frequency(base_frequency: float, day_of_week: int, weekend_factor: float = 0.05) -> float:
    """Apply weekend frequency reduction"""
    if is_weekend_day(day_of_week):
        return base_frequency * weekend_factor
    return base_frequency

def main():
    st.set_page_config(
        page_title="GitHub Contribution Graph Hacker",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 GitHub Contribution Graph Hacker")
    st.markdown("""
    **Educational tool for generating fake commits to make your GitHub contribution graph look more active.**
    
    ⚠️ **Warning**: This is for educational purposes only. Do not use to mislead employers or others.
    """)
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Repository path
    repo_path = st.sidebar.text_input(
        "Repository Path", 
        value=".",
        help="Path to your git repository"
    )
    
    # Data file name
    default_data_file = st.session_state.get('data_file', 'data.json')
    data_file = st.sidebar.text_input(
        "Data File Name",
        value=default_data_file,
        help="Name of the JSON file to store commit data. Note: 'data.json' is in .gitignore!"
    )
    
    # Warning if using default data.json
    if data_file == "data.json":
        st.sidebar.warning("⚠️ 'data.json' is ignored by .gitignore! Consider using 'commits.json' instead.")
        if st.sidebar.button("🔧 Use 'commits.json' instead"):
            st.session_state.data_file = "commits.json"
            st.rerun()
    
    # Initialize hacker
    hacker = StreamlitGitHubHacker(repo_path, data_file)
    
    # Account verification section
    if hacker._ensure_git_repo():
        git_config = hacker.get_git_config()
        
        # Check for potential issues and show warnings
        issues = []
        if git_config.get('user_name') == "Not configured":
            issues.append("Git user name not configured")
        if git_config.get('user_email') == "Not configured":
            issues.append("Git user email not configured")
        if not git_config.get('remote_accessible', False):
            issues.append("GitHub remote not accessible")
        if 'github_username' not in git_config:
            issues.append("No GitHub repository detected")
            
        if issues:
            st.error("⚠️ **Configuration Issues Detected:**")
            for issue in issues:
                st.markdown(f"• {issue}")
            st.markdown("**Please check the Repository Information in the sidebar →**")
        else:
            # Show success message with account info
            if 'github_username' in git_config:
                st.success(f"✅ **Ready to commit as:** {git_config['user_name']} ({git_config['user_email']}) to **{git_config['github_username']}/{git_config['github_repo']}**")
            else:
                st.info("ℹ️ **Local repository detected** - commits will be made locally")
    else:
        st.warning("⚠️ **No Git repository found.** Initialize one using the sidebar or navigate to an existing repository.")
    
    # Repository Information Panel
    st.sidebar.subheader("🔧 Repository Information")
    
    if hacker._ensure_git_repo():
        # Get comprehensive repository information
        git_config = hacker.get_git_config()
        repo_info = hacker.get_repository_info()
        commit_stats = hacker.get_commit_stats()
        
        # Account & Repository Info
        st.sidebar.markdown("**📋 Account & Repository:**")
        
        if 'github_username' in git_config:
            st.sidebar.success(f"👤 **GitHub:** {git_config['github_username']}")
            st.sidebar.info(f"📁 **Repo:** {git_config['github_repo']}")
            
            # Repository URL
            if 'remote_url' in git_config and git_config['remote_url'] != "No remote configured":
                repo_url = git_config['remote_url']
                if repo_url.endswith('.git'):
                    repo_url = repo_url[:-4]
                if repo_url.startswith('git@github.com:'):
                    repo_url = repo_url.replace('git@github.com:', 'https://github.com/')
                st.sidebar.markdown(f"🔗 [Open Repository]({repo_url})")
        else:
            st.sidebar.warning("⚠️ No GitHub remote detected")
        
        # Git Configuration
        st.sidebar.markdown("**⚙️ Git Configuration:**")
        
        if git_config.get('user_name') != "Not configured":
            st.sidebar.text(f"👤 {git_config['user_name']}")
            st.sidebar.text(f"📧 {git_config['user_email']}")
        else:
            st.sidebar.error("❌ Git user not configured!")
            st.sidebar.markdown("Run: `git config --global user.name 'Your Name'`")
            st.sidebar.markdown("Run: `git config --global user.email 'your@email.com'`")
        
        # Repository Status
        st.sidebar.markdown("**📊 Repository Status:**")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Branch", git_config.get('current_branch', 'Unknown'))
        with col2:
            if 'error' not in commit_stats:
                st.metric("Commits", commit_stats['total_commits'])
            else:
                st.metric("Commits", "N/A")
        
        # Connection Status
        if git_config.get('remote_accessible'):
            st.sidebar.success("🌐 Remote accessible")
        else:
            st.sidebar.error("🚫 Remote not accessible")
        
        # Uncommitted changes warning
        if git_config.get('has_uncommitted_changes'):
            st.sidebar.warning("⚠️ You have uncommitted changes")
        
        # Script Statistics
        if 'error' not in commit_stats:
            st.sidebar.markdown("**🤖 Script Activity:**")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.metric("Script Commits", commit_stats['script_commits'])
            with col2:
                regular_commits = commit_stats['total_commits'] - commit_stats['script_commits']
                st.metric("Regular Commits", regular_commits)
        
        # Last Commit Info
        if 'last_commit' in git_config:
            last = git_config['last_commit']
            st.sidebar.markdown("**🕒 Last Commit:**")
            st.sidebar.text(f"📅 {last['date']}")
            st.sidebar.text(f"👤 {last['author_name']}")
            st.sidebar.text(f"💬 {last['message'][:30]}...")
        
        # Repository Details (Expandable)
        with st.sidebar.expander("📂 Repository Details"):
            if 'error' not in repo_info:
                st.text(f"📍 Root: {repo_info['repo_root']}")
                st.text(f"📦 Size: {repo_info.get('size_kb', 0)} KB")
                st.text(f"🌿 Branches: {len(repo_info.get('branches', []))}")
                
                if repo_info.get('branches'):
                    st.markdown("**Branches:**")
                    for branch in repo_info['branches'][:5]:  # Show first 5 branches
                        if branch.startswith('remotes/'):
                            continue
                        current = "🔸" if branch == git_config.get('current_branch') else "▫️"
                        st.text(f"{current} {branch}")
                    
                    if len(repo_info['branches']) > 5:
                        st.text(f"... and {len(repo_info['branches']) - 5} more")
            else:
                st.error("Could not get repository details")
        
        # Account Management
        st.sidebar.markdown("---")
        st.sidebar.markdown("**👤 Account Management:**")
        
        # Account switching
        with st.sidebar.expander("🔄 Switch Git Account"):
            # Get available configurations
            available_configs = hacker.get_available_git_configs()
            common_accounts = hacker.get_common_git_accounts()
            
            if available_configs and 'error' not in available_configs:
                st.markdown("**Available Configurations:**")
                for scope, config in available_configs.items():
                    if st.button(f"Use {scope.title()}: {config['name']}", key=f"use_{scope}"):
                        success, message = hacker.set_git_config(
                            config['name'], 
                            config['email'], 
                            'local'  # Always set as local to avoid affecting other repos
                        )
                        if success:
                            st.success(f"✅ Switched to {config['name']}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
            
            if common_accounts:
                st.markdown("**Recent Git History Accounts:**")
                for i, account in enumerate(common_accounts[:5]):  # Show top 5
                    if st.button(f"{account['name']} <{account['email']}>", key=f"history_{i}"):
                        success, message = hacker.set_git_config(
                            account['name'],
                            account['email'],
                            'local'
                        )
                        if success:
                            st.success(f"✅ Switched to {account['name']}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
            
            # Manual account setup
            st.markdown("**Manual Setup:**")
            with st.form("git_config_form"):
                new_name = st.text_input("Git Name", placeholder="Your Name")
                new_email = st.text_input("Git Email", placeholder="your@email.com")
                config_scope = st.selectbox("Scope", ["local", "global"], 
                                          help="Local: This repo only, Global: All repos")
                
                if st.form_submit_button("💾 Set Git Config"):
                    if new_name and new_email:
                        success, message = hacker.set_git_config(new_name, new_email, config_scope)
                        if success:
                            st.success(f"✅ Git config updated!")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("Please fill in both name and email")
        
        # Quick Actions
        st.sidebar.markdown("**🔧 Quick Actions:**")
        
        if st.sidebar.button("🔄 Refresh Repository Info"):
            st.rerun()
        
        if st.sidebar.button("🧪 Test Git Configuration"):
            with st.spinner("Testing configuration..."):
                # Test basic git commands
                test_results = []
                
                # Test git user config
                if git_config.get('user_name') != "Not configured":
                    test_results.append("✅ Git user configured")
                else:
                    test_results.append("❌ Git user not configured")
                
                # Test remote connectivity
                if git_config.get('remote_accessible'):
                    test_results.append("✅ Remote repository accessible")
                else:
                    test_results.append("❌ Remote repository not accessible")
                
                # Test commit ability (dry run)
                success, _ = hacker._run_git_command(['git', 'status'])
                if success:
                    test_results.append("✅ Repository is ready for commits")
                else:
                    test_results.append("❌ Repository has issues")
                
                # Display results
                st.sidebar.markdown("**Test Results:**")
                for result in test_results:
                    st.sidebar.text(result)
        
        # Safety Warnings
        st.sidebar.markdown("---")
        st.sidebar.markdown("**⚠️ Safety Reminders:**")
        st.sidebar.caption("• This tool modifies Git history")
        st.sidebar.caption("• Use private repos for testing")
        st.sidebar.caption("• Always backup important data")
        
    else:
        st.sidebar.error("❌ No git repository found")
        st.sidebar.markdown("**Initialize Repository:**")
        if st.sidebar.button("🚀 Initialize Git Repository"):
            if hacker._init_git_repo():
                st.sidebar.success("Git repository initialized!")
                st.rerun()
            else:
                st.sidebar.error("Failed to initialize git repository")
        
        st.sidebar.markdown("**Or navigate to existing repo:**")
        st.sidebar.caption("Change the repository path above")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Single Commit", 
        "🎲 Random Commits", 
        "🎨 Pattern Creator", 
        "📅 Fill Year", 
        "🔄 Manage Commits",
        "🩺 Troubleshoot"
    ])
    
    with tab1:
        st.header("Make Single Commit")
        st.markdown("Create a commit at specific coordinates on your contribution graph.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_coord = st.slider("Week (X coordinate)", 0, 51, 10)
            y_coord = st.slider("Day (Y coordinate)", 0, 6, 3)
            push_single = st.checkbox("Push immediately", value=True)
        
        with col2:
            # Show target date
            start_date = hacker.get_start_of_year()
            target_date = start_date + datetime.timedelta(weeks=x_coord, days=y_coord)
            st.info(f"Target date: {target_date.strftime('%Y-%m-%d (%A)')}")
            
            if target_date > datetime.datetime.now():
                st.warning("⚠️ This date is in the future!")
        
        if st.button("Make Single Commit", type="primary"):
            if not hacker._ensure_git_repo():
                st.error("No git repository found!")
            else:
                with st.spinner("Creating commit..."):
                    success, message = hacker.mark_commit(x_coord, y_coord, push=push_single)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    with tab2:
        st.header("Generate Random Commits")
        st.markdown("Generate multiple random commits across the past year.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_commits = st.number_input("Number of commits", 1, 1000, 100)
            push_random = st.checkbox("Push all at end", value=True, key="push_random")
            
            # Weekend settings for random commits
            st.markdown("**Weekend Settings:**")
            avoid_weekends = st.checkbox("Avoid weekends", value=True, key="avoid_weekends_random",
                                       help="Reduces likelihood of commits on weekends (Sat/Sun)")
            
            if st.button("Generate Preview", type="secondary"):
                with st.spinner("Generating preview..."):
                    commits_data = hacker.generate_commits_data(num_commits, avoid_weekends)
                    st.session_state.random_commits = commits_data
                    st.success(f"Generated preview with {len(commits_data)} commits")
        
        with col2:
            if st.button("Execute Random Commits", type="primary"):
                if not hacker._ensure_git_repo():
                    st.error("No git repository found!")
                elif 'random_commits' not in st.session_state:
                    st.warning("Generate preview first!")
                else:
                    with st.spinner("Executing commits..."):
                        success, messages = hacker.execute_commits(
                            st.session_state.random_commits, 
                            push_at_end=push_random
                        )
                        
                        # Show results
                        if success:
                            st.success("Commits executed successfully!")
                        else:
                            st.error("Some commits failed")
                        
                        with st.expander("Detailed Results"):
                            for msg in messages:
                                st.text(msg)
        
        # Show preview graph
        if 'random_commits' in st.session_state:
            st.subheader("Preview")
            fig = create_contribution_graph(st.session_state.random_commits)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Pattern Creator")
        st.markdown("Create commits based on custom patterns.")
        
        # Pattern input methods
        pattern_method = st.radio(
            "Pattern Input Method",
            ["Text to Pattern", "Predefined Patterns", "Simple Grid", "JSON Upload"]
        )
        
        if pattern_method == "Text to Pattern":
            st.subheader("Generate Pattern from Text")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                text_input = st.text_input(
                    "Enter text to convert to pattern",
                    value="HELLO",
                    help="Enter text to convert to ASCII art pattern. Supports A-Z, space, !, ?, and ♥"
                )
                
                pattern_width = st.slider("Pattern width (weeks)", 10, 52, 30)
                
                if text_input:
                    pattern = text_to_pattern(text_input, pattern_width)
                    if pattern:
                        st.success(f"Generated pattern: {len(pattern[0])} weeks × {len(pattern)} days")
                    else:
                        st.warning("Could not generate pattern from text")
                        pattern = []
                else:
                    pattern = []
            
            with col2:
                if pattern:
                    fig = create_pattern_preview(pattern)
                    st.plotly_chart(fig, use_container_width=True)
                
        elif pattern_method == "Predefined Patterns":
            st.subheader("Predefined Patterns")
            
            # Fixed predefined patterns (corrected orientation)
            patterns = {
                "Heart": [
                    [0,1,1,0,1,1,0],
                    [1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1],
                    [0,1,1,1,1,1,0],
                    [0,0,1,1,1,0,0],
                    [0,0,0,1,0,0,0],
                    [0,0,0,0,0,0,0]
                ],
                "Smile": [
                    [0,1,1,1,1,1,0],
                    [1,0,0,0,0,0,1],
                    [1,0,1,0,1,0,1],
                    [1,0,0,0,0,0,1],
                    [1,0,1,1,1,0,1],
                    [1,0,0,0,0,0,1],
                    [0,1,1,1,1,1,0]
                ],
                "Cross": [
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [1,1,1,1,1],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0]
                ],
                "Diamond": [
                    [0,0,0,1,0,0,0],
                    [0,0,1,1,1,0,0],
                    [0,1,1,1,1,1,0],
                    [1,1,1,1,1,1,1],
                    [0,1,1,1,1,1,0],
                    [0,0,1,1,1,0,0],
                    [0,0,0,1,0,0,0]
                ],
                "Star": [
                    [0,0,0,1,0,0,0],
                    [0,1,0,1,0,1,0],
                    [1,1,1,1,1,1,1],
                    [0,1,1,1,1,1,0],
                    [0,1,0,1,0,1,0],
                    [1,0,0,1,0,0,1],
                    [0,0,0,0,0,0,0]
                ],
                "Arrow": [
                    [0,0,0,1,0,0,0],
                    [0,0,1,1,1,0,0],
                    [0,1,1,1,1,1,0],
                    [1,1,1,1,1,1,1],
                    [0,0,0,1,0,0,0],
                    [0,0,0,1,0,0,0],
                    [0,0,0,1,0,0,0]
                ]
            }
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                selected_pattern = st.selectbox("Choose Pattern", list(patterns.keys()))
                pattern = patterns[selected_pattern]
                
                if pattern:
                    st.info(f"Pattern size: {len(pattern[0])} weeks × {len(pattern)} days")
            
            with col2:
                if pattern:
                    fig = create_pattern_preview(pattern)
                    st.plotly_chart(fig, use_container_width=True)
                    
        elif pattern_method == "Simple Grid":
            st.subheader("Create Pattern with Interactive Grid")
            
            st.markdown("**Interactive Grid Creator** - Click cells to set commit intensity (0-4)")
            
            # Grid size controls
            col1, col2 = st.columns(2)
            with col1:
                grid_weeks = st.slider("Grid width (weeks)", 5, 20, 10)
            with col2:
                grid_days = st.slider("Grid height (days)", 3, 7, 7)
            
            # Create interactive grid
            pattern = []
            
            # Initialize session state for grid
            for day in range(grid_days):
                for week in range(grid_weeks):
                    key = f"grid_{week}_{day}"
                    if key not in st.session_state:
                        st.session_state[key] = 0
            
            # Create grid UI
            st.markdown("**Grid Pattern:**")
            
            # Create columns for each week
            grid_cols = st.columns(grid_weeks)
            pattern_grid = []
            
            for week in range(grid_weeks):
                week_data = []
                for day in range(grid_days):
                    key = f"grid_{week}_{day}"
                    
                    with grid_cols[week]:
                        value = st.selectbox(
                            f"W{week}D{day}",
                            [0, 1, 2, 3, 4],
                            index=st.session_state[key],
                            key=key,
                            label_visibility="collapsed"
                        )
                        week_data.append(value)
                pattern_grid.append(week_data)
            
            # Transpose for correct orientation (days x weeks)
            pattern = [[pattern_grid[week][day] for week in range(grid_weeks)] for day in range(grid_days)]
            
            # Show preview
            if any(any(row) for row in pattern):
                st.subheader("Grid Preview")
                fig = create_pattern_preview(pattern)
                st.plotly_chart(fig, use_container_width=True)
                
        else:  # JSON Upload
            st.subheader("Upload JSON Pattern")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                pattern_text = st.text_area(
                    "Pattern JSON",
                    placeholder='[[1,0,1,0,1],[0,2,0,2,0],[1,0,3,0,1]]',
                    help="2D array where pattern[day][week] = number of commits",
                    height=150
                )
                
                # JSON validation and preview
                try:
                    if pattern_text.strip():
                        pattern = json.loads(pattern_text)
                        if isinstance(pattern, list) and all(isinstance(row, list) for row in pattern):
                            st.success(f"Valid JSON pattern: {len(pattern[0]) if pattern else 0} weeks × {len(pattern)} days")
                        else:
                            st.error("Pattern must be a 2D array")
                            pattern = []
                    else:
                        pattern = []
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON format: {e}")
                    pattern = []
                    
                # Sample patterns
                st.markdown("**Sample JSON patterns:**")
                sample_patterns = {
                    "Simple Cross": '[[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0]]',
                    "Checkerboard": '[[1,0,1,0,1],[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0]]',
                    "Triangle": '[[0,0,1,0,0],[0,1,1,1,0],[1,1,1,1,1]]'
                }
                
                for name, sample_json in sample_patterns.items():
                    if st.button(f"Load {name}", key=f"sample_{name}"):
                        st.session_state.json_pattern = sample_json
                        st.rerun()
                
                # Load sample if selected
                if hasattr(st.session_state, 'json_pattern'):
                    pattern_text = st.session_state.json_pattern
                    pattern = json.loads(pattern_text)
                    
            with col2:
                if pattern:
                    fig = create_pattern_preview(pattern)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Show pattern execution options
        if pattern and any(any(row) for row in pattern):
            st.markdown("---")
            st.subheader("Execute Pattern")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Generate pattern commits data
                pattern_commits = hacker.create_pattern_commits(pattern)
                st.info(f"Pattern will create **{len(pattern_commits)}** commits")
                
                push_pattern = st.checkbox("Push to remote after creating", value=True, key="push_pattern")
                
                if st.button("🎨 Execute Pattern", type="primary"):
                    if not hacker._ensure_git_repo():
                        st.error("No git repository found!")
                    else:
                        with st.spinner("Creating pattern..."):
                            success, messages = hacker.execute_commits(pattern_commits, push_at_end=push_pattern)
                            
                            if success:
                                st.success("Pattern created successfully!")
                            else:
                                st.error("Some commits failed")
                            
                            with st.expander("Detailed Results"):
                                for msg in messages:
                                    st.text(msg)
            
            with col2:
                # Show final contribution graph preview
                if pattern_commits:
                    st.markdown("**Final Contribution Graph Preview:**")
                    fig = create_contribution_graph(pattern_commits, weeks=max(52, len(pattern[0]) if pattern else 52))
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("Fill Time Period")
        st.markdown("Fill multiple years or a specific time period with random commits.")
        
        # Time period selection
        time_period = st.radio(
            "Select time period to fill:",
            ["Single Year", "Multiple Years", "Custom Period"]
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if time_period == "Single Year":
                years = 1
                st.info("📅 Filling the past 12 months (52 weeks)")
                
            elif time_period == "Multiple Years":
                years = st.slider("Number of years", 1, 5, 2)
                total_weeks = years * 52
                st.info(f"📅 Filling the past {years} years ({total_weeks} weeks)")
                
            else:  # Custom Period
                years = 1
                custom_weeks = st.slider("Number of weeks", 1, 260, 52)  # Up to 5 years
                years_equiv = custom_weeks / 52
                st.info(f"📅 Filling {custom_weeks} weeks (~{years_equiv:.1f} years)")
            
            # Commit parameters
            st.markdown("**Commit Parameters:**")
            min_commits = st.slider("Min commits per day", 0, 5, 0)
            max_commits = st.slider("Max commits per day", 1, 10, 3)
            frequency = st.slider("Commit frequency", 0.0, 1.0, 0.7, 0.1)
            
            # Weekend options
            st.markdown("**Weekend Settings:**")
            reduce_weekends = st.checkbox("Reduce weekend activity", value=True, 
                                        help="Reduces commit frequency on weekends (Sat/Sun) to simulate realistic work patterns")
            if reduce_weekends:
                weekend_factor = st.slider("Weekend frequency multiplier", 0.01, 0.5, 0.05, 0.01,
                                         help="Weekend commits will be: base_frequency × this multiplier")
                st.caption(f"Weekend frequency: {frequency * weekend_factor:.2%} (vs weekday: {frequency:.2%})")
            else:
                weekend_factor = 1.0
            
            # Calculate estimated commits
            if time_period == "Custom Period":
                total_days = custom_weeks * 7
                estimated_commits = int(total_days * frequency * (min_commits + max_commits) / 2)
                st.info(f"📊 Estimated: ~{estimated_commits} commits on ~{int(total_days * frequency)} days")
            else:
                total_days = years * 365
                estimated_commits = int(total_days * frequency * (min_commits + max_commits) / 2)
                st.info(f"📊 Estimated: ~{estimated_commits} commits on ~{int(total_days * frequency)} days")
            
        with col2:
            if st.button("🔍 Generate Preview", type="secondary"):
                with st.spinner("Generating preview..."):
                    if time_period == "Custom Period":
                        # Generate custom period data
                        year_commits = []
                        for x in range(custom_weeks):
                            for y in range(7):   # 7 days
                                # Apply weekend frequency reduction
                                if reduce_weekends:
                                    adjusted_frequency = apply_weekend_frequency(frequency, y, weekend_factor)
                                else:
                                    adjusted_frequency = frequency
                                
                                if random.random() < adjusted_frequency:
                                    num_commits = random.randint(min_commits, max_commits)
                                    for _ in range(num_commits):
                                        start_date = hacker.get_start_of_year(custom_weeks)
                                        target_date = start_date + datetime.timedelta(weeks=x, days=y)
                                        
                                        if target_date <= datetime.datetime.now():
                                            year_commits.append({
                                                'x': x,
                                                'y': y,
                                                'date': target_date,
                                                'date_str': hacker.get_date_string(target_date)
                                            })
                    else:
                        # Generate multi-year data
                        year_commits = hacker.generate_multi_year_commits(
                            years, min_commits, max_commits, frequency, weekend_factor if reduce_weekends else 1.0
                        )
                    
                    st.session_state.year_commits = year_commits
                    st.session_state.fill_weeks = custom_weeks if time_period == "Custom Period" else years * 52
                    st.success(f"✅ Generated preview with **{len(year_commits)}** commits")
            
            if st.button("🚀 Execute Fill", type="primary"):
                if not hacker._ensure_git_repo():
                    st.error("❌ No git repository found!")
                elif 'year_commits' not in st.session_state:
                    st.warning("⚠️ Generate preview first!")
                else:
                    push_fill = st.checkbox("Push to remote after filling", value=True, key="push_fill")
                    
                    if st.button("✅ Confirm Execute", type="primary"):
                        with st.spinner("Filling time period..."):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Execute commits in batches for better performance
                            commits = st.session_state.year_commits
                            batch_size = 50
                            total_batches = len(commits) // batch_size + (1 if len(commits) % batch_size else 0)
                            
                            all_success = True
                            all_messages = []
                            
                            for i in range(0, len(commits), batch_size):
                                batch = commits[i:i+batch_size]
                                batch_num = i // batch_size + 1
                                
                                status_text.text(f"Processing batch {batch_num}/{total_batches}...")
                                
                                success, messages = hacker.execute_commits(batch, push_at_end=False)
                                all_messages.extend(messages)
                                
                                if not success:
                                    all_success = False
                                
                                progress_bar.progress(min(1.0, (i + batch_size) / len(commits)))
                            
                            # Push all at the end if requested
                            if push_fill and any('✅' in msg for msg in all_messages):
                                status_text.text("Pushing to remote...")
                                success, push_msg = hacker._run_git_command(["git", "push"])
                                if success:
                                    all_messages.append("✅ All commits pushed to remote repository")
                                else:
                                    all_messages.append(f"❌ Push failed: {push_msg}")
                            
                            progress_bar.progress(1.0)
                            status_text.text("Complete!")
                            
                            if all_success:
                                st.success("🎉 Time period filled successfully!")
                            else:
                                st.error("⚠️ Some commits failed")
                            
                            with st.expander("📋 Detailed Results"):
                                for msg in all_messages[-20:]:  # Show last 20 messages
                                    st.text(msg)
                                if len(all_messages) > 20:
                                    st.info(f"... and {len(all_messages) - 20} more messages")
        
        # Show preview
        if 'year_commits' in st.session_state:
            st.markdown("---")
            st.subheader("📊 Time Period Preview")
            
            commits = st.session_state.year_commits
            fill_weeks = st.session_state.get('fill_weeks', 52)
            
            # Show statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Commits", len(commits))
            with col2:
                st.metric("Time Span", f"{fill_weeks} weeks")
            with col3:
                if commits:
                    unique_days = len(set((c['x'], c['y']) for c in commits))
                    st.metric("Active Days", unique_days)
                else:
                    st.metric("Active Days", 0)
            with col4:
                if commits:
                    avg_commits = len(commits) / max(1, len(set((c['x'], c['y']) for c in commits)))
                    st.metric("Avg/Day", f"{avg_commits:.1f}")
                else:
                    st.metric("Avg/Day", "0")
            
            # Show contribution graph
            fig = create_contribution_graph(commits, weeks=fill_weeks)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show date range
            if commits:
                dates = [c['date'] for c in commits]
                start_date = min(dates)
                end_date = max(dates)
                st.info(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    with tab5:
        st.header("Manage Commits")
        st.markdown("View and manage commits created by this tool.")
        
        # Show current stats
        stats = hacker.get_commit_stats()
        if "error" not in stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Commits", stats['total_commits'])
            with col2:
                st.metric("Script Commits", stats['script_commits'])
            with col3:
                st.metric("Regular Commits", stats['total_commits'] - stats['script_commits'])
        
        st.subheader("Danger Zone")
        st.markdown("⚠️ **Warning**: These operations will modify your Git history!")
        
        if st.button("🗑️ Revert All Script Commits", type="secondary"):
            st.warning("This will remove all commits created by this script!")
            
            if st.checkbox("I understand this will modify Git history"):
                if st.button("Confirm Revert", type="primary"):
                    # Implementation would go here
                    st.error("Revert functionality not yet implemented in Streamlit version")
    
    with tab6:
        st.header("🩺 GitHub Profile Troubleshooting")
        st.markdown("**Not seeing commits on your GitHub profile?** Use these diagnostic tools to identify the issue.")
        
        # Run diagnostics
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔍 Diagnose Profile Issues", type="primary"):
                with st.spinner("Running diagnostics..."):
                    diagnosis = hacker.diagnose_github_profile_issues()
                    st.session_state.diagnosis = diagnosis
            
            if st.button("📋 Check Recent Commits"):
                with st.spinner("Checking commit authorship..."):
                    commits = hacker.check_commit_authorship()
                    st.session_state.recent_commits = commits
        
        with col2:
            # GitHub profile tips
            st.markdown("**💡 Common Issues & Solutions:**")
            tips = hacker.get_github_profile_tips()
            for tip in tips:
                st.markdown(tip)
        
        # Show diagnosis results
        if 'diagnosis' in st.session_state:
            diagnosis = st.session_state.diagnosis
            
            if 'error' in diagnosis:
                st.error(f"Diagnostic error: {diagnosis['error']}")
            else:
                st.markdown("---")
                st.subheader("🔍 Diagnostic Results")
                
                # Issues (Critical)
                if diagnosis['issues']:
                    st.error("**❌ Critical Issues Found:**")
                    for issue in diagnosis['issues']:
                        st.markdown(f"• {issue}")
                
                # Warnings (Information)
                if diagnosis['warnings']:
                    st.warning("**⚠️ Current Configuration:**")
                    for warning in diagnosis['warnings']:
                        st.markdown(f"• {warning}")
                
                # Suggestions (Solutions)
                if diagnosis['suggestions']:
                    st.info("**💡 Suggested Solutions:**")
                    for suggestion in diagnosis['suggestions']:
                        st.markdown(f"• {suggestion}")
                
                # Quick fixes
                st.markdown("---")
                st.subheader("🔧 Quick Fixes")
                
                git_config = diagnosis.get('git_config', {})
                
                # Email verification
                if git_config.get('user_email') != "Not configured":
                    st.markdown("**📧 Email Verification:**")
                    st.info(f"Your current Git email: **{git_config['user_email']}**")
                    st.markdown("**✅ To verify this email is linked to your GitHub account:**")
                    st.markdown("1. Go to [GitHub Settings → Emails](https://github.com/settings/emails)")
                    st.markdown("2. Check if this email is listed and verified")
                    st.markdown("3. If not, add and verify this email address")
                
                # Repository check
                if 'github_username' in git_config:
                    repo_url = f"https://github.com/{git_config['github_username']}/{git_config['github_repo']}"
                    st.markdown("**🔗 Repository Check:**")
                    st.markdown(f"**Repository:** [{git_config['github_username']}/{git_config['github_repo']}]({repo_url})")
                    st.markdown("**✅ Verify repository settings:**")
                    st.markdown("1. Check if repository is public")
                    st.markdown("2. If private, enable 'Private contributions' in your [GitHub profile settings](https://github.com/settings/profile)")
                
                # Branch check
                current_branch = git_config.get('current_branch', 'unknown')
                if current_branch not in ['main', 'master']:
                    st.markdown("**🌿 Branch Issue:**")
                    st.warning(f"You're on branch '{current_branch}', but GitHub profiles only show commits to the default branch.")
                    st.markdown("**🔧 To fix:**")
                    if st.button("Switch to main branch"):
                        success, output = hacker._run_git_command(['git', 'checkout', 'main'])
                        if not success:
                            success, output = hacker._run_git_command(['git', 'checkout', 'master'])
                        
                        if success:
                            st.success("✅ Switched to main/master branch!")
                            st.rerun()
                        else:
                            st.error(f"❌ Could not switch branch: {output}")
        
        # Show recent commits analysis
        if 'recent_commits' in st.session_state:
            commits = st.session_state.recent_commits
            
            if commits:
                st.markdown("---")
                st.subheader("📋 Recent Commit Analysis")
                
                # Create a dataframe for better display
                import pandas as pd
                df = pd.DataFrame(commits)
                
                # Check for issues
                current_email = hacker.get_git_config().get('user_email', 'Unknown')
                email_issues = []
                
                for commit in commits:
                    if commit['author_email'] != current_email:
                        email_issues.append(f"Commit {commit['hash']}: {commit['author_email']} ≠ {current_email}")
                
                if email_issues:
                    st.error("**❌ Email Mismatch Issues:**")
                    for issue in email_issues:
                        st.markdown(f"• {issue}")
                    st.markdown("**These commits won't appear on your profile because the email doesn't match!**")
                else:
                    st.success("✅ All recent commits use the correct email address!")
                
                # Display commits table
                st.markdown("**Recent Commits:**")
                st.dataframe(df[['hash', 'author_name', 'author_email', 'date', 'message']], use_container_width=True)
            else:
                st.warning("No recent commits found.")
        
        # Additional help section
        st.markdown("---")
        st.subheader("🆘 Still Having Issues?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔍 Manual Checks:**")
            st.markdown("1. **Wait 24 hours** - GitHub can be slow to update")
            st.markdown("2. **Check your GitHub profile** directly")
            st.markdown("3. **Verify repository permissions**")
            st.markdown("4. **Check GitHub's status page**")
        
        with col2:
            st.markdown("**🔗 Helpful Links:**")
            st.markdown("• [GitHub Profile Settings](https://github.com/settings/profile)")
            st.markdown("• [GitHub Email Settings](https://github.com/settings/emails)")
            st.markdown("• [GitHub Contributions Guide](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/managing-contribution-graphs-on-your-profile/why-are-my-contributions-not-showing-up-on-my-profile)")
            st.markdown("• [GitHub Status Page](https://githubstatus.com/)")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Disclaimer**: This tool is for educational purposes only. 
    Use responsibly and do not use to mislead others about your actual coding activity.
    
    **Tips**:
    - Use a private repository for testing
    - Be aware that this modifies your Git history
    - Always backup your repository before using
    """)

if __name__ == "__main__":
    main() 