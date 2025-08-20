# 🎨 GitHub Contribution Graph Hacker

Create beautiful patterns and designs in your GitHub contribution graph! This interactive Streamlit web application generates commits to make your contribution graph more active and artistic.

![GitHub Graph Hacker Demo](https://img.shields.io/badge/Status-Ready%20to%20Use-brightgreen)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)

⚠️ **Educational purposes only** - Use responsibly and don't mislead others about your coding activity.

## ✨ Features

- 🎯 **Single Commits & Patterns**: Create individual commits or complex patterns
- 📝 **Text-to-Pattern**: Convert any text into ASCII art patterns
- 🎨 **Predefined Patterns**: Hearts, stars, diamonds, arrows, and more
- 📊 **Multi-Year Generation**: Fill entire years with realistic commit patterns
- 🔧 **Built-in Troubleshooting**: Comprehensive diagnostics and fixes
- 🚀 **Setup Wizard**: Guided setup for first-time users
- 📱 **Interactive UI**: Modern, responsive web interface
- 👥 **Multi-Account Support**: Easy setup for different GitHub accounts

## 🚀 Quick Start (3 Steps!)

### Option 1: Basic Setup
```bash
# 1. Clone or download the files
git clone https://github.com/your-username/repo-name.git
cd repo-name

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run streamlit_app.py
```

### Option 2: Multi-Account Setup (New!)
If you want to use this with a different GitHub account than your main one:

```bash
# 1. Create a new directory for your account
mkdir github-contributions-youraccount
cd github-contributions-youraccount

# 2. Copy the application files
cp path/to/streamlit_app.py .
cp path/to/app.py .
cp path/to/requirements.txt .

# 3. Initialize git repository
git init

# 4. Configure git for your specific account
git config user.name "youraccount"
git config user.email "your-account-email@example.com"

# 5. Create initial commit
echo "# GitHub Contributions for youraccount" > README.md
git add .
git commit -m "Initial commit - GitHub contribution graph hacker"

# 6. Create GitHub repository and connect
# (See detailed instructions below)
```

## 👥 Multi-Account Setup Guide

### Why Use Multi-Account Setup?
- Test patterns safely on a secondary account
- Keep your main account's contribution history clean
- Experiment with different patterns without affecting your primary profile
- Avoid permission issues when copying code to different accounts

### Step-by-Step Multi-Account Setup

#### 1. **Prepare Your Environment**
```bash
# Create dedicated directory
mkdir github-contributions-[ACCOUNT-NAME]
cd github-contributions-[ACCOUNT-NAME]

# Copy application files
cp /path/to/original/streamlit_app.py .
cp /path/to/original/app.py .
cp /path/to/original/requirements.txt .
```

#### 2. **Configure Git for Your Account**
```bash
# Initialize git repository
git init

# CRITICAL: Set the correct email for your target account
git config user.name "your-github-username"
git config user.email "email-associated-with-github-account@example.com"

# Verify configuration
git config --list | grep user
```

#### 3. **Create GitHub Repository**
1. **Switch to your target GitHub account** in your browser
2. **Create a new repository:**
   - Go to https://github.com/new
   - Name: `github-contributions` or `contribution-graph`
   - **Make it PUBLIC** (required for contributions to show on profile)
   - **Don't initialize with README** (we already have files)
3. **Copy the repository URL** for the next step

#### 4. **Connect and Push**
```bash
# Create initial commit
echo "# GitHub Contributions for [ACCOUNT-NAME]" > README.md
git add .
git commit -m "Initial commit - GitHub contribution graph hacker"

# Connect to your GitHub repository
git remote add origin https://github.com/[ACCOUNT-NAME]/[REPO-NAME].git
git branch -M main
git push -u origin main
```

#### 5. **Verify Setup**
```bash
# Run the app from your account-specific directory
streamlit run streamlit_app.py

# In the app, go to "🩺 Troubleshoot" tab to verify:
# - Correct email is configured
# - Repository is accessible
# - Ready to create commits
```

### 🚨 Common Multi-Account Issues & Solutions

#### **Issue: "Permission denied" or "403 error"**
```bash
# Solution: Check your git configuration
git config user.email  # Must match your GitHub account email
git remote -v          # Must point to YOUR repository

# Fix if needed:
git config user.email "correct-email@example.com"
git remote set-url origin https://github.com/YOURUSERNAME/YOURREPO.git
```

#### **Issue: "Commits not showing on profile"**
1. **Email mismatch**: Git email ≠ GitHub account email
   ```bash
   # Check your GitHub emails at: https://github.com/settings/emails
   git config user.email "matching-email@example.com"
   ```

2. **Private repository**: Contributions from private repos don't show by default
   - Make repository public, OR
   - Enable "Private contributions" in GitHub profile settings

3. **Wrong branch**: Commits must be on default branch (main/master)
   ```bash
   git branch --show-current  # Should show "main" or "master"
   ```

#### **Issue: "Repository belongs to different account"**
```bash
# This happens when you copy code without changing remote URL
git remote -v  # Check current remote
git remote set-url origin https://github.com/YOURUSERNAME/YOURREPO.git
```

## 📋 Requirements

- **Python 3.7+** (Check: `python --version`)
- **Git installed** (Check: `git --version`)
- **GitHub account**
- **Internet connection**

### Installing Requirements

**Git Installation:**
- **Windows**: Download from [git-scm.com](https://git-scm.com/)
- **Mac**: `brew install git` or download from [git-scm.com](https://git-scm.com/)
- **Linux**: `sudo apt install git` (Ubuntu/Debian) or equivalent

**Python Dependencies:**
```bash
pip install streamlit plotly pandas
# OR
pip install -r requirements.txt
```

## 🎯 How to Use

### 1. First Run - Setup Wizard
When you first run the app, you'll see a **Setup Wizard** that guides you through:

1. **Git Installation Check** - Verifies Git is installed
2. **Repository Setup** - Auto-detects, uses existing, or creates new repo
3. **Git Configuration** - Sets up your name and email
4. **Completion** - Ready to create patterns!

### 2. Create Your First Pattern
1. **Single Commit**: Test with one commit first
2. **Text Pattern**: Try typing "HI" or your name
3. **Predefined Patterns**: Use hearts, stars, or arrows
4. **Execute**: Click the button and watch the magic happen!

### 3. Check Your GitHub Profile
- Visit `https://github.com/YOUR_USERNAME`
- Look at your contribution graph
- **Wait 2-4 hours** if commits don't appear immediately

## 🧪 Safe Testing

Before making actual commits, you can test the functionality safely:

### Option 1: Use the Built-in Dry Run
1. Open the **🔄 Manage Commits** tab in the web app
2. Use the **Safe Testing Mode** section
3. Click **Test Single Commit (Dry Run)** to see what would happen

### Option 2: Use a Test Repository
```bash
# Create a test repository
mkdir test-github-graph
cd test-github-graph
git init
echo "# Test Repository" > README.md
git add README.md
git commit -m "Initial commit"

# Test the app in this repository
streamlit run streamlit_app.py
```

## 🎨 Pattern Examples

### Text Patterns
```
Input: "HELLO"
Result: ASCII art spelling "HELLO" in your graph
```

### Predefined Patterns
- ❤️ **Heart**: Classic heart shape
- ⭐ **Star**: 5-pointed star
- 💎 **Diamond**: Diamond shape
- ➡️ **Arrow**: Right-pointing arrow
- 😊 **Smile**: Smiley face

### Custom Patterns
Upload JSON files with custom 2D arrays:
```json
{
  "pattern": [
    [1, 0, 1, 0, 1],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 0, 0]
  ]
}
```

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 🚫 "Commits not appearing on my profile"

**Most Common Causes:**
1. **Email Mismatch**: Your Git email ≠ GitHub account email
2. **Wrong Repository**: Committing to someone else's repo
3. **Private Repository**: GitHub doesn't show private repo commits by default
4. **Wrong Branch**: Only commits to the default branch (main/master) count
5. **Recent Commits**: GitHub can take 2-4 hours to update

**Quick Fixes:**
```bash
# Check your Git email
git config user.email

# Set correct email (MUST match your GitHub account!)
git config user.email "your.github.email@example.com"

# Check which repo you're in
git remote -v

# Switch to main branch
git checkout main
```

#### 🔴 "Git not installed" or "Command not found"
- **Windows**: Download from [git-scm.com](https://git-scm.com/)
- **Mac**: Run `brew install git`
- **Linux**: Run `sudo apt install git`

#### 🟡 "Permission denied" or "Authentication failed"
1. **Use HTTPS with token**: `https://TOKEN@github.com/user/repo.git`
2. **Use SSH**: Set up SSH keys in GitHub settings
3. **Use GitHub CLI**: `gh auth login`

#### 🟠 "Repository not found"
- Make sure the repository exists on GitHub
- Check if you have access permissions
- Verify the remote URL: `git remote -v`

### Built-in Diagnostics

The app includes a **🩺 Troubleshoot** tab that automatically checks:
- ✅ Git installation and configuration
- ✅ Repository status and remote access
- ✅ Recent commit authorship
- ✅ Branch and email configuration
- ✅ Common GitHub profile issues

## ⚠️ Important Notes

### Email Configuration
**CRITICAL**: Your Git email MUST match your GitHub account email:

```bash
# Check your GitHub email at: https://github.com/settings/emails
# Set Git email to match:
git config user.email "your.github.email@example.com"
```

### Repository Recommendations
- ✅ **Use your own repository** (not a fork of this tool)
- ✅ **Create a dedicated repo** for contribution patterns
- ✅ **Make it private** if you don't want others to see the pattern code
- ✅ **Use descriptive commit messages**

### GitHub Profile Settings
Make sure your GitHub profile is configured to show contributions:
1. Go to [GitHub Profile Settings](https://github.com/settings/profile)
2. Check "Private contributions" if using private repositories
3. Ensure your email is verified: [Email Settings](https://github.com/settings/emails)

## 🔒 Privacy & Security

### Data Safety
- ✅ **No data collection**: This tool doesn't send data anywhere
- ✅ **Local execution**: Everything runs on your computer
- ✅ **Open source**: You can inspect all the code
- ✅ **No GitHub token required**: Uses your local Git configuration

### Responsible Use
- ⚠️ **Educational purposes only**
- ⚠️ **Don't mislead employers** about your actual coding activity
- ⚠️ **Use private repositories** for testing
- ⚠️ **Be transparent** about generated commits if asked

## 📁 File Structure

```
github-contribution-graph/
├── streamlit_app.py      # Main Streamlit application
├── app.py               # Command-line version
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── commits.json        # Generated commit data (created automatically)
```

## ❓ FAQ

### Q: Will this get me in trouble with GitHub?
A: No, this doesn't violate GitHub's terms of service. You're creating real commits in your own repositories.

### Q: Can employers detect generated commits?
A: Potentially yes. The commits have patterns and timestamps that might look artificial. Use responsibly.

### Q: Do I need a GitHub Pro account?
A: No, this works with free GitHub accounts.

### Q: Can I undo the commits?
A: Yes! Use the "Revert All Script Commits" feature in the Manage Commits tab, or manually reset your Git history.

### Q: Why aren't my commits showing up?
A: Check the troubleshooting section above. Most issues are email configuration or timing related.

### Q: Can I use this on multiple repositories?
A: Yes, just change the repository path in the sidebar.

### Q: How do I set up for multiple GitHub accounts?
A: Follow the "Multi-Account Setup Guide" section above for detailed instructions.

## 🆘 Getting Help

If you're stuck:

1. **Use the built-in troubleshooting** (🩺 tab in the app)
2. **Check this README** for common solutions
3. **Verify your multi-account setup** if using a different GitHub account
4. **Open an issue** on GitHub with:
   - Your operating system
   - Python version (`python --version`)
   - Git version (`git --version`)
   - Error messages
   - Screenshots if helpful

## 🎉 Credits

Created with ❤️ for the developer community.

Special thanks to:
- **Streamlit** for the amazing web app framework
- **Plotly** for beautiful visualizations
- **GitHub** for the contribution graph feature
- **You** for using this tool responsibly!

---

**Remember**: This tool is for educational purposes and artistic expression. Use it responsibly and have fun creating beautiful patterns in your GitHub contribution graph! 🎨✨
