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
            # Add files to staging
            success, output = self._run_git_command(["git", "add", self.data_file])
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
    
    def generate_multi_year_commits(self, years: int, min_commits: int = 0, max_commits: int = 3, frequency: float = 0.7) -> List[Dict]:
        """Generate commits data for multiple years"""
        commits_data = []
        weeks_per_year = 52
        total_weeks = years * weeks_per_year
        
        for x in range(total_weeks):
            for y in range(7):   # 7 days
                if random.random() < frequency:
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

    def generate_commits_data(self, num_commits: int = 100) -> List[Dict]:
        """Generate commit data without actually making commits"""
        commits_data = []
        
        for i in range(num_commits):
            # Random X coordinate (0-51 weeks)
            x = random.randint(0, 51)
            # Random Y coordinate (0-6 days)
            y = random.randint(0, 6)
            
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
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=grid,
        colorscale='Greens',
        showscale=True,
        hoverongaps=False,
        hovertemplate='Week: %{x}<br>Day: %{y}<br>Commits: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title="GitHub Contribution Graph Preview",
        xaxis_title="Weeks",
        yaxis_title="Days of Week",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(7)),
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        ),
        height=300
    )
    
    return fig

def create_pattern_preview(pattern: List[List[int]]) -> go.Figure:
    """Create a visual preview of a pattern"""
    if not pattern or not pattern[0]:
        return go.Figure()
    
    # Create heatmap for pattern preview
    fig = go.Figure(data=go.Heatmap(
        z=pattern,
        colorscale='Greens',
        showscale=True,
        hoverongaps=False,
        hovertemplate='Week: %{x}<br>Day: %{y}<br>Commits: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Pattern Preview",
        xaxis_title="Weeks",
        yaxis_title="Days of Week",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(7)),
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
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
            [0,0,0,0,0]
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
    data_file = st.sidebar.text_input(
        "Data File Name",
        value="data.json",
        help="Name of the JSON file to store commit data"
    )
    
    # Initialize hacker
    hacker = StreamlitGitHubHacker(repo_path, data_file)
    
    # Check git repository status
    st.sidebar.subheader("Repository Status")
    if hacker._ensure_git_repo():
        st.sidebar.success("✅ Git repository detected")
        
        # Get repository stats
        stats = hacker.get_commit_stats()
        if "error" not in stats:
            st.sidebar.info(f"Total commits: {stats['total_commits']}")
            st.sidebar.info(f"Script commits: {stats['script_commits']}")
        else:
            st.sidebar.warning(f"Could not get stats: {stats['error']}")
    else:
        st.sidebar.error("❌ No git repository found")
        if st.sidebar.button("Initialize Git Repository"):
            if hacker._init_git_repo():
                st.sidebar.success("Git repository initialized!")
                st.rerun()
            else:
                st.sidebar.error("Failed to initialize git repository")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Single Commit", 
        "🎲 Random Commits", 
        "🎨 Pattern Creator", 
        "📅 Fill Year", 
        "🔄 Manage Commits"
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
            
            if st.button("Generate Preview", type="secondary"):
                with st.spinner("Generating preview..."):
                    commits_data = hacker.generate_commits_data(num_commits)
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
                                if random.random() < frequency:
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
                            years, min_commits, max_commits, frequency
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