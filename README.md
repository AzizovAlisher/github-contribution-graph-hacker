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

## 🚀 Quick Start (3 Steps!)

### Option 1: Fork & Use (Recommended)
```bash
# 1. Fork this repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/github-contribution-graph.git
cd github-contribution-graph

# 3. Run the app
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Option 2: Download & Use
```bash
# 1. Download the repository
curl -L -o github-graph-hacker.zip https://github.com/YOUR_USERNAME/github-contribution-graph/archive/main.zip
unzip github-graph-hacker.zip
cd github-contribution-graph-main

# 2. Install & run
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Option 3: Copy Files
1. Copy `streamlit_app.py` and `requirements.txt` to your desired folder
2. Run the commands above

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

## 🛠️ Setup Options

### Automatic Setup (Recommended)
The app includes a **Setup Wizard** that:
- ✅ Checks if Git is installed
- ✅ Auto-detects existing repositories
- ✅ Creates new repositories if needed
- ✅ Configures Git with your information
- ✅ Validates everything works

### Manual Setup
If you prefer manual setup:

```bash
# 1. Create a new repository
mkdir my-contribution-graph
cd my-contribution-graph
git init

# 2. Configure Git (IMPORTANT: Use your GitHub email!)
git config user.name "Your Name"
git config user.email "your.github.email@example.com"

# 3. Create initial commit
echo "# My Contribution Graph" > README.md
git add README.md
git commit -m "Initial commit"

# 4. Connect to GitHub (optional but recommended)
git remote add origin https://github.com/YOUR_USERNAME/my-contribution-graph.git
git push -u origin main
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
├── streamlit_app.py      # Main application
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── commits.json         # Generated commit data (created automatically)
```

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
git clone https://github.com/YOUR_USERNAME/github-contribution-graph.git
cd github-contribution-graph
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ❓ FAQ

### Q: Will this get me in trouble with GitHub?
A: No, this doesn't violate GitHub's terms of service. You're creating real commits in your own repositories.

### Q: Can employers detect generated commits?
A: Potentially yes. The commits have patterns and timestamps that might look artificial. Use responsibly.

### Q: Do I need a GitHub Pro account?
A: No, this works with free GitHub accounts.

### Q: Can I undo the commits?
A: Yes! Use the "Reverse Commits" feature in the app, or manually reset your Git history.

### Q: Why aren't my commits showing up?
A: Check the troubleshooting section above. Most issues are email configuration or timing related.

### Q: Can I use this on multiple repositories?
A: Yes, just change the repository path in the sidebar.

## 🆘 Getting Help

If you're stuck:

1. **Use the built-in troubleshooting** (🩺 tab in the app)
2. **Check this README** for common solutions
3. **Open an issue** on GitHub with:
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