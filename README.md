# GitHub Contribution Graph Hacker - Streamlit Edition

A modern web application for generating fake commits to make your GitHub contribution graph look more active. This is the Streamlit version of the original Python script, providing an intuitive web interface for all functionality.

## ⚠️ Disclaimer

**This tool is for educational purposes only.** Do not use it to mislead employers, colleagues, or anyone else about your actual coding activity. Always be honest about your contributions and use this tool responsibly.

## 🚀 Features

- **Interactive Web Interface**: Easy-to-use Streamlit web app
- **Multiple Commit Strategies**: 
  - Single commits at specific coordinates
  - Random commit generation
  - Pattern-based commits (hearts, smiles, custom patterns)
  - Fill entire year with commits
- **Visual Preview**: See how your contribution graph will look before committing
- **Real-time Feedback**: Progress tracking and detailed results
- **Repository Management**: View commit statistics and manage generated commits
- **Git Integration**: Seamless integration with Git repositories

## 📋 Requirements

- Python 3.6 or higher
- Git installed and configured
- A GitHub repository (preferably private for testing)

## 🛠️ Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd github-contribution-hacker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## 📖 Usage Guide

### Getting Started

1. **Set up your repository**: Make sure you're in a Git repository or initialize one using the app
2. **Configure settings**: Use the sidebar to set repository path and data file name
3. **Choose your strategy**: Select from the available tabs based on what you want to accomplish

### Available Features

#### 🎯 Single Commit
- Create individual commits at specific coordinates
- Choose week (X) and day (Y) coordinates
- See the target date before committing

#### 🎲 Random Commits
- Generate multiple random commits across the past year
- Set the number of commits (1-1000)
- Preview before executing
- Visual contribution graph preview

#### 🎨 Pattern Creator
- **Simple Grid**: Interactive 10x7 grid for creating patterns
- **JSON Upload**: Upload custom patterns in JSON format
- **Predefined Patterns**: Choose from heart, smile, or cross patterns
- Real-time pattern preview

#### 📅 Fill Year
- Fill the entire past year with commits
- Configurable commit frequency (0-100%)
- Set minimum and maximum commits per day
- Preview before execution

#### 🔄 Manage Commits
- View repository statistics
- See total commits vs script-generated commits
- Manage and potentially revert generated commits

### Pattern Format

For custom patterns, use a 2D JSON array where:
- `pattern[day][week] = number_of_commits`
- Days: 0-6 (Monday to Sunday)
- Weeks: 0-51 (past 52 weeks)

Example:
```json
[
  [1,0,1,0,1],
  [0,1,0,1,0],
  [1,0,1,0,1]
]
```

## 🔧 Technical Details

### How It Works

1. **Date Calculation**: Calculates target dates based on GitHub's contribution graph coordinate system
2. **Backdated Commits**: Uses Git's `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` environment variables
3. **Data Tracking**: Stores commit metadata in a JSON file for tracking
4. **Git Integration**: Automatically handles staging, committing, and pushing

### File Structure

- `streamlit_app.py`: Main Streamlit application
- `app.py`: Original command-line version
- `requirements.txt`: Python dependencies
- `data.json`: Generated commit metadata (created automatically)

## 🛡️ Safety Tips

1. **Use a private repository** for testing to avoid affecting your public profile
2. **Backup your repository** before using the tool
3. **Understand Git history implications** - this tool modifies your commit history
4. **Test with small numbers** before generating large amounts of commits
5. **Be aware of GitHub's terms of service**

## 🤝 Contributing

This is an educational project. If you have suggestions for improvements or find bugs, feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is for educational purposes. Use responsibly and ethically.

## 🔗 Related

- Original inspiration from various GitHub contribution graph manipulation tutorials
- Built with [Streamlit](https://streamlit.io/) for the web interface
- Uses [Plotly](https://plotly.com/) for interactive visualizations

## 🆘 Troubleshooting

### Common Issues

**"No git repository found"**
- Make sure you're in a directory with a Git repository
- Use the "Initialize Git Repository" button in the sidebar
- Check that Git is installed and accessible from command line

**"Failed to push"**
- Ensure you have a remote repository configured (`git remote -v`)
- Check your Git credentials and permissions
- Make sure you have push access to the repository

**"Commits not showing on GitHub"**
- It may take a few minutes for GitHub to update the contribution graph
- Ensure commits are actually pushed to the remote repository
- Check that the email in your Git config matches your GitHub account

**Performance Issues**
- Reduce the number of commits for better performance
- Use the preview feature before executing large batches
- Consider running smaller batches if you encounter timeouts

---

**Remember**: This tool is for educational purposes only. Always be honest about your actual contributions and coding activity. 