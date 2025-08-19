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

def create_contribution_graph(commits_data: List[Dict]) -> go.Figure:
    """Create a visual representation of the contribution graph"""
    # Create a grid for the contribution graph (52 weeks x 7 days)
    weeks = 52
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
            ["Simple Grid", "JSON Upload", "Predefined Patterns"]
        )
        
        if pattern_method == "Simple Grid":
            st.subheader("Create Pattern with Grid")
            
            # Simple 7x10 grid for pattern creation
            pattern = []
            
            st.markdown("**Click to set commit intensity (0-4):**")
            
            # Create a simple pattern grid
            grid_cols = st.columns(10)
            pattern_grid = []
            
            for week in range(10):  # 10 weeks for simplicity
                week_data = []
                for day in range(7):
                    key = f"grid_{week}_{day}"
                    if key not in st.session_state:
                        st.session_state[key] = 0
                    
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
            
            # Transpose for correct orientation
            pattern = [[pattern_grid[week][day] for week in range(10)] for day in range(7)]
            
        elif pattern_method == "JSON Upload":
            st.subheader("Upload JSON Pattern")
            
            pattern_text = st.text_area(
                "Pattern JSON",
                placeholder='[[1,0,1],[0,2,0],[1,0,1]]',
                help="2D array where pattern[day][week] = number of commits"
            )
            
            try:
                pattern = json.loads(pattern_text) if pattern_text else []
            except json.JSONDecodeError:
                st.error("Invalid JSON format")
                pattern = []
                
        else:  # Predefined patterns
            st.subheader("Predefined Patterns")
            
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
                ]
            }
            
            selected_pattern = st.selectbox("Choose Pattern", list(patterns.keys()))
            pattern = patterns[selected_pattern]
        
        # Show pattern preview and execute
        if pattern:
            col1, col2 = st.columns(2)
            
            with col1:
                # Generate pattern commits data
                pattern_commits = hacker.create_pattern_commits(pattern)
                st.info(f"Pattern will create {len(pattern_commits)} commits")
                
                if st.button("Execute Pattern", type="primary"):
                    if not hacker._ensure_git_repo():
                        st.error("No git repository found!")
                    else:
                        with st.spinner("Creating pattern..."):
                            success, messages = hacker.execute_commits(pattern_commits, push_at_end=True)
                            
                            if success:
                                st.success("Pattern created successfully!")
                            else:
                                st.error("Some commits failed")
                            
                            with st.expander("Detailed Results"):
                                for msg in messages:
                                    st.text(msg)
            
            with col2:
                # Show pattern preview
                if pattern_commits:
                    fig = create_contribution_graph(pattern_commits)
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("Fill Entire Year")
        st.markdown("Fill the entire past year with random commits.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            min_commits = st.slider("Min commits per day", 0, 5, 0)
            max_commits = st.slider("Max commits per day", 1, 10, 3)
            frequency = st.slider("Commit frequency", 0.0, 1.0, 0.7, 0.1)
            
            st.info(f"This will create commits on ~{int(365 * frequency)} days")
            
        with col2:
            if st.button("Generate Year Preview", type="secondary"):
                with st.spinner("Generating year preview..."):
                    # Generate year data
                    year_commits = []
                    for x in range(52):  # 52 weeks
                        for y in range(7):   # 7 days
                            if random.random() < frequency:
                                num_commits = random.randint(min_commits, max_commits)
                                for _ in range(num_commits):
                                    start_date = hacker.get_start_of_year()
                                    target_date = start_date + datetime.timedelta(weeks=x, days=y)
                                    
                                    if target_date <= datetime.datetime.now():
                                        year_commits.append({
                                            'x': x,
                                            'y': y,
                                            'date': target_date,
                                            'date_str': hacker.get_date_string(target_date)
                                        })
                    
                    st.session_state.year_commits = year_commits
                    st.success(f"Generated preview with {len(year_commits)} commits")
            
            if st.button("Execute Year Fill", type="primary"):
                if not hacker._ensure_git_repo():
                    st.error("No git repository found!")
                elif 'year_commits' not in st.session_state:
                    st.warning("Generate preview first!")
                else:
                    with st.spinner("Filling year..."):
                        success, messages = hacker.execute_commits(
                            st.session_state.year_commits, 
                            push_at_end=True
                        )
                        
                        if success:
                            st.success("Year filled successfully!")
                        else:
                            st.error("Some commits failed")
        
        # Show year preview
        if 'year_commits' in st.session_state:
            st.subheader("Year Preview")
            fig = create_contribution_graph(st.session_state.year_commits)
            st.plotly_chart(fig, use_container_width=True)
    
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