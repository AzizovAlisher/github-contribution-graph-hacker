#!/usr/bin/env python3
"""
GitHub Contribution Graph Hack - Python Version
Based on the JavaScript implementation from the video by Fenrir

This script generates fake commits to make your GitHub contribution graph look more active.
Educational purposes only - do not use to mislead employers or others.

Usage:
    python github_hack.py [options]

Requirements:
    - Git installed and configured
    - Python 3.6+
    - A GitHub repository (preferably private)
"""

import datetime
import json
import os
import subprocess
import random
import time
import argparse
from typing import Optional, List, Tuple

class GitHubHacker:
    def __init__(self, repo_path: str = ".", data_file: str = "data.json"):
        """
        Initialize the GitHub Contribution Graph Hacker

        Args:
            repo_path: Path to the git repository
            data_file: Name of the JSON file to store commit data
        """
        self.repo_path = repo_path
        self.data_file = data_file
        self.data_path = os.path.join(repo_path, data_file)

        # Ensure we're in a git repository
        self._ensure_git_repo()

    def _ensure_git_repo(self):
        """Ensure we're in a git repository"""
        try:
            subprocess.run(["git", "status"], 
                         cwd=self.repo_path, 
                         check=True, 
                         capture_output=True)
        except subprocess.CalledProcessError:
            # Initialize git repo if it doesn't exist
            subprocess.run(["git", "init"], cwd=self.repo_path, check=True)
            print("Initialized new git repository")

    def _run_git_command(self, command: List[str]) -> str:
        """Run a git command and return the output"""
        try:
            result = subprocess.run(
                command, 
                cwd=self.repo_path, 
                check=True, 
                capture_output=True, 
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {' '.join(command)}")
            print(f"Error: {e.stderr}")
            raise

    def get_date_string(self, date: datetime.datetime) -> str:
        """
        Convert datetime to the format GitHub stores internally
        Equivalent to moment.format() in the original JavaScript
        """
        return date.strftime("%Y-%m-%d %H:%M:%S")

    def write_data_to_file(self, commit_data: dict, callback: Optional[callable] = None):
        """
        Write commit data to JSON file
        Equivalent to json.writeFile in the original JavaScript

        Args:
            commit_data: Dictionary containing commit information
            callback: Optional callback function to execute after writing
        """
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

            print(f"Data written to {self.data_file}: {commit_data['date']}")

            # Execute callback if provided
            if callback:
                callback()

        except Exception as e:
            print(f"Error writing to file: {e}")
            raise

    def add_commit_and_push(self, date: datetime.datetime, push: bool = True):
        """
        Add, commit, and optionally push changes
        Equivalent to simple-git operations in the original JavaScript

        Args:
            date: The date for the commit
            push: Whether to push to remote repository
        """
        try:
            # Add files to staging
            self._run_git_command(["git", "add", self.data_file])

            # Create commit message
            commit_message = f"Commit for {self.get_date_string(date)}"

            # Set environment variables for backdating the commit
            env = os.environ.copy()
            date_str = date.strftime("%Y-%m-%d %H:%M:%S")
            env['GIT_AUTHOR_DATE'] = date_str
            env['GIT_COMMITTER_DATE'] = date_str

            # Commit with backdated timestamp
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_path,
                env=env,
                check=True,
                capture_output=True
            )

            print(f"Committed: {commit_message}")

            # Push if requested
            if push:
                self._run_git_command(["git", "push"])
                print("Pushed to remote repository")

        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
            # Don't raise here, as we might want to continue with other commits

    def make_commit_yesterday(self):
        """
        Make a commit for yesterday
        Demonstrates date manipulation equivalent to moment.subtract()
        """
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

        commit_data = {
            'date': self.get_date_string(yesterday)
        }

        def commit_callback():
            self.add_commit_and_push(yesterday, push=False)

        self.write_data_to_file(commit_data, commit_callback)

    def get_start_of_year(self, weeks_back: int = 52) -> datetime.datetime:
        """
        Get the start date for generating commits (equivalent to setting up the coordinate system)

        Args:
            weeks_back: How many weeks back to start from
        """
        today = datetime.datetime.now()
        start_date = today - datetime.timedelta(weeks=weeks_back)
        # Align to start of week (Sunday) - GitHub's contribution graph starts on Sunday
        days_since_sunday = (start_date.weekday() + 1) % 7
        start_date = start_date - datetime.timedelta(days=days_since_sunday)
        return start_date

    def mark_commit(self, x: int, y: int, push: bool = False):
        """
        Make a commit at specific X,Y coordinates on the contribution graph
        Equivalent to the markCommit function in the original JavaScript

        Args:
            x: Week offset (0-52, horizontal position)
            y: Day offset (0-6, vertical position, 0=Sunday, 1=Monday, ..., 6=Saturday)
            push: Whether to push after commit
        """
        start_date = self.get_start_of_year()

        # Calculate the target date
        target_date = start_date + datetime.timedelta(weeks=x, days=y)

        # Don't commit in the future
        if target_date > datetime.datetime.now():
            print(f"Skipping future date: {target_date}")
            return

        commit_data = {
            'date': self.get_date_string(target_date),
            'x': x,
            'y': y
        }

        def commit_callback():
            self.add_commit_and_push(target_date, push=push)

        self.write_data_to_file(commit_data, commit_callback)
        print(f"Marked commit at ({x}, {y}) on {target_date.strftime('%Y-%m-%d')}")

    def generate_random_commits(self, num_commits: int = 100, push_at_end: bool = True):
        """
        Generate random commits across the past year
        Equivalent to the random commit generation in the original JavaScript

        Args:
            num_commits: Number of commits to generate
            push_at_end: Whether to push all commits at the end
        """
        print(f"Generating {num_commits} random commits...")

        for i in range(num_commits):
            # Random X coordinate (0-52 weeks)
            x = random.randint(0, 51)
            # Random Y coordinate (0-6 days)
            y = random.randint(0, 6)

            # Make the commit
            self.mark_commit(x, y, push=False)

            # Small delay to avoid overwhelming git
            time.sleep(0.1)

            if i % 10 == 0:
                print(f"Generated {i}/{num_commits} commits...")

        # Push all commits at the end if requested
        if push_at_end:
            try:
                self._run_git_command(["git", "push"])
                print("Pushed all commits to remote repository")
            except:
                print("Failed to push. Make sure you have a remote repository configured.")

    def create_pattern(self, pattern: List[List[int]]):
        """
        Create commits based on a 2D pattern

        Args:
            pattern: 2D list where pattern[y][x] represents number of commits for that position
        """
        print("Creating pattern...")

        for y, row in enumerate(pattern):
            for x, num_commits in enumerate(row):
                if num_commits > 0:
                    for _ in range(num_commits):
                        self.mark_commit(x, y, push=False)
                        time.sleep(0.05)  # Small delay

        # Push all commits at the end
        try:
            self._run_git_command(["git", "push"])
            print("Pattern created and pushed to remote repository")
        except:
            print("Pattern created but failed to push. Make sure you have a remote repository configured.")

    def fill_random_year(self, min_commits: int = 0, max_commits: int = 3, frequency: float = 0.7):
        """
        Fill the entire past year with random commits

        Args:
            min_commits: Minimum commits per day
            max_commits: Maximum commits per day
            frequency: Probability of making commits on any given day (0.0 to 1.0)
        """
        print(f"Filling past year with random commits (frequency: {frequency*100}%)...")

        for x in range(52):  # 52 weeks
            for y in range(7):   # 7 days
                # Random chance of making commits this day
                if random.random() < frequency:
                    num_commits = random.randint(min_commits, max_commits)
                    for _ in range(num_commits):
                        self.mark_commit(x, y, push=False)
                        time.sleep(0.02)

        # Push all commits
        try:
            self._run_git_command(["git", "push"])
            print("Year filled and pushed to remote repository")
        except:
            print("Year filled but failed to push. Make sure you have a remote repository configured.")

    def revert_all_commits(self):
        """
        Revert all commits created by this script
        WARNING: This is destructive and will modify Git history
        """
        print("WARNING: This will revert all commits with 'GitHub hack commit' or 'Commit for' messages!")
        print("This will also remove any commits with backdated timestamps.")
        confirm = input("Are you sure you want to continue? (yes/no): ")
        
        if confirm.lower() not in ['yes', 'y']:
            print("Operation cancelled.")
            return
            
        try:
            # Get total commit count
            total_commits = self._run_git_command(['git', 'rev-list', '--count', 'HEAD']).strip()
            print(f"Total commits in repository: {total_commits}")
            
            # Find commits by message patterns (more comprehensive)
            patterns = [
                '--grep=GitHub hack commit',
                '--grep=Commit for 20',  # Catches "Commit for 2024-..." etc
                '--grep=hack commit'
            ]
            
            all_commits = set()
            for pattern in patterns:
                try:
                    commits = self._run_git_command(['git', 'log', pattern, '--pretty=format:%H'])
                    if commits.strip():
                        all_commits.update(commits.strip().split('\n'))
                except:
                    continue
            
            # Remove empty strings
            all_commits = [c for c in all_commits if c.strip()]
            
            if not all_commits:
                print("No commits found to revert.")
                return
                
            print(f"Found {len(all_commits)} commits to revert...")
            
            # Alternative approach: reset to initial commit if we have many commits
            if len(all_commits) > 100:
                print("Large number of commits detected. Resetting to initial commit...")
                # Find the first commit (initial commit)
                try:
                    first_commit = self._run_git_command(['git', 'rev-list', '--max-parents=0', 'HEAD']).strip()
                    if first_commit:
                        self._run_git_command(['git', 'reset', '--hard', first_commit])
                        self._run_git_command(['git', 'push', '--force', 'origin', 'main'])
                        print("Successfully reset to initial commit!")
                        return
                except:
                    pass
            
            # Original method for smaller numbers of commits
            if all_commits:
                oldest_commit = all_commits[-1]
                try:
                    parent_commit = self._run_git_command(['git', 'rev-parse', f'{oldest_commit}^'])
                    self._run_git_command(['git', 'reset', '--hard', parent_commit])
                    self._run_git_command(['git', 'push', '--force', 'origin', 'main'])
                    print(f"Successfully reverted {len(all_commits)} commits!")
                except:
                    print("Could not find parent commit. Repository may be in an inconsistent state.")
                    print("Try manually resetting to a known good commit.")
                
        except Exception as e:
            print(f"Error during revert: {e}")
            print("You may need to manually clean up the repository.")
            print("Try: git reset --hard <commit-hash> && git push --force origin main")

def main():
    parser = argparse.ArgumentParser(description='GitHub Contribution Graph Hacker')
    parser.add_argument('--repo-path', default='.', help='Path to git repository')
    parser.add_argument('--data-file', default='data.json', help='JSON data file name')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Yesterday command
    subparsers.add_parser('yesterday', help='Make a commit for yesterday')

    # Specific commit command
    coord_parser = subparsers.add_parser('commit', help='Make commit at specific coordinates')
    coord_parser.add_argument('x', type=int, help='Week coordinate (0-52)')
    coord_parser.add_argument('y', type=int, help='Day coordinate (0-6)')

    # Random commits command
    random_parser = subparsers.add_parser('random', help='Generate random commits')
    random_parser.add_argument('--count', type=int, default=100, help='Number of commits')

    # Fill year command
    fill_parser = subparsers.add_parser('fill', help='Fill entire year with commits')
    fill_parser.add_argument('--min-commits', type=int, default=0, help='Min commits per day')
    fill_parser.add_argument('--max-commits', type=int, default=3, help='Max commits per day')
    fill_parser.add_argument('--frequency', type=float, default=0.7, help='Commit frequency (0.0-1.0)')

    # Pattern command
    pattern_parser = subparsers.add_parser('pattern', help='Create pattern from file')
    pattern_parser.add_argument('file', help='Pattern file (JSON format)')
    
    # Revert command
    subparsers.add_parser('revert', help='Revert all commits created by this script')

    args = parser.parse_args()

    # Create hacker instance
    hacker = GitHubHacker(args.repo_path, args.data_file)

    if args.command == 'yesterday':
        hacker.make_commit_yesterday()
    elif args.command == 'commit':
        hacker.mark_commit(args.x, args.y, push=True)
    elif args.command == 'random':
        hacker.generate_random_commits(args.count)
    elif args.command == 'fill':
        hacker.fill_random_year(args.min_commits, args.max_commits, args.frequency)
    elif args.command == 'pattern':
        with open(args.file, 'r') as f:
            pattern = json.load(f)
        hacker.create_pattern(pattern)
    elif args.command == 'revert':
        hacker.revert_all_commits()
    else:
        # Default behavior - demonstrate basic functionality
        print("GitHub Contribution Graph Hacker - Python Version")
        print("\nDemo: Creating a few sample commits...")

        # Make a commit for yesterday
        hacker.make_commit_yesterday()

        # Make a specific coordinate commit
        hacker.mark_commit(10, 3)

        # Generate a few random commits
        hacker.generate_random_commits(10, push_at_end=True)

        print("\nDemo completed! Check your contribution graph in a few minutes.")
        print("\nUsage examples:")
        print("  python github_hack.py yesterday")
        print("  python github_hack.py commit 5 2")  
        print("  python github_hack.py random --count 50")
        print("  python github_hack.py fill --frequency 0.8")
        print("  python github_hack.py revert")

if __name__ == "__main__":
    main()
