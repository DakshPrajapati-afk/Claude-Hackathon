# Git Workflow - Quick Reference Guide

## 📍 Important: Always Work in the Correct Directory

```bash
cd /Users/nikhil01/Desktop/Poly_Prediction_Tool/Claude-Hackathon
```

**NOT** the parent directory! All Git commands must be run from inside `Claude-Hackathon/`.

---

## 🔄 Daily Workflow

### 1. Start Your Work Session

```bash
# Navigate to project
cd /Users/nikhil01/Desktop/Poly_Prediction_Tool/Claude-Hackathon

# Pull latest changes from team
git pull origin data-nikhil

# Check what branch you're on
git branch
# Should show: * data-nikhil
```

### 2. Make Your Changes

- Edit code files
- Test your changes
- Make sure everything works

### 3. Check What Changed

```bash
git status
```

This shows:
- 🔴 **Red files** = Modified but not staged
- 🟢 **Green files** = Staged and ready to commit
- ⚪ **Untracked files** = New files not in Git yet

### 4. Add Your Changes

```bash
# Add all changes
git add .

# OR add specific files
git add backend/app.py
git add frontend/src/App.js
```

### 5. Commit Your Changes

```bash
git commit -m "Brief description of what you changed"
```

**Good commit messages:**
- ✅ "Added hybrid confidence scoring system"
- ✅ "Fixed 404 error on favicon endpoint"
- ✅ "Updated UI with data quality metrics"

**Bad commit messages:**
- ❌ "Changes"
- ❌ "Fixed stuff"
- ❌ "Update"

### 6. Push to GitHub

```bash
git push origin data-nikhil
```

**If you get an error** saying "non-fast-forward":

```bash
# Pull first (syncs with remote)
git pull origin data-nikhil

# Then push again
git push origin data-nikhil
```

---

## 🆕 Setting Up on a New Computer

### Step 1: Clone the Repository

```bash
# Navigate to where you want the project
cd ~/Desktop

# Clone from GitHub
git clone https://github.com/DakshPrajapati-afk/Claude-Hackathon.git

# Enter the directory
cd Claude-Hackathon

# Switch to your branch
git checkout data-nikhil
```

### Step 2: Set Up Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
nano .env
```

Add your API keys to `.env`:
```
ANTHROPIC_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
GOOGLE_CSE_ID=your_cse_id_here
```

### Step 3: Set Up Frontend

```bash
cd ../frontend

# Install dependencies
npm install
```

### Step 4: Run the Application

**Terminal 1:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2:**
```bash
cd frontend
npm start
```

---

## 🔍 Useful Git Commands

### Check Status
```bash
git status                  # See what changed
git log --oneline          # See recent commits
git branch                 # See current branch
```

### Undo Changes

```bash
# Undo changes to a specific file (before committing)
git restore backend/app.py

# Unstage a file (keep changes, just unstage)
git restore --staged backend/app.py

# Discard ALL local changes (dangerous!)
git reset --hard HEAD
```

### View Differences

```bash
# See what changed in files
git diff

# See what's staged for commit
git diff --cached
```

### Remote Information

```bash
# See remote repository URL
git remote -v

# See remote branches
git branch -r
```

---

## 📤 Complete Push Workflow (Copy-Paste)

```bash
# Navigate to project
cd /Users/nikhil01/Desktop/Poly_Prediction_Tool/Claude-Hackathon

# Pull latest changes
git pull origin data-nikhil

# Check what changed
git status

# Add all changes
git add .

# Commit with message
git commit -m "Your descriptive message here"

# Push to GitHub
git push origin data-nikhil
```

---

## ⚠️ Common Mistakes to Avoid

### ❌ Don't Work in Parent Directory

**Wrong:**
```bash
cd /Users/nikhil01/Desktop/Poly_Prediction_Tool
git add .  # This won't work correctly!
```

**Right:**
```bash
cd /Users/nikhil01/Desktop/Poly_Prediction_Tool/Claude-Hackathon
git add .  # ✅ Correct!
```

### ❌ Don't Commit Sensitive Files

Never commit:
- `.env` (API keys) - Already in .gitignore ✅
- `venv/` (virtual environment) - Already in .gitignore ✅
- `node_modules/` (NPM packages) - Already in .gitignore ✅
- `predictions.db` (database) - Already in .gitignore ✅

### ❌ Don't Force Push

**Dangerous command (avoid):**
```bash
git push --force  # Can overwrite team's work!
```

**Safe alternative:**
```bash
git pull origin data-nikhil  # Sync first
git push origin data-nikhil  # Then push
```

---

## 🤝 Working with a Team

### Before You Start Working

```bash
git pull origin data-nikhil
```

This gets the latest changes from your teammates.

### If Someone Else Pushed

When you try to push and get "rejected":

```bash
# Pull their changes
git pull origin data-nikhil

# Git will try to auto-merge
# If successful, push your changes
git push origin data-nikhil
```

### If There Are Conflicts

Git will tell you which files have conflicts. Open them and look for:

```python
<<<<<<< HEAD
Your code
=======
Their code
>>>>>>> branch-name
```

1. Decide which code to keep (or combine both)
2. Remove the `<<<<<<<`, `=======`, `>>>>>>>` markers
3. Save the file
4. Add and commit:

```bash
git add conflicted-file.py
git commit -m "Resolved merge conflict"
git push origin data-nikhil
```

---

## 📊 What Was Just Pushed

Your recent push included:

✅ **Backend Changes:**
- Hybrid confidence scoring system
- Reddit API removed
- Enhanced data quality calculations
- New data sources integration
- Better error handling

✅ **Frontend Changes:**
- Modern UI with glassmorphism
- Data quality metrics display
- Definitive prediction banners
- Improved animations

✅ **Documentation:**
- 13 new markdown guides
- Setup instructions
- Confidence scoring explanations
- Git workflow guide

✅ **Configuration:**
- Updated `.gitignore`
- Removed database from tracking
- Added comprehensive setup guide

---

## 🎯 Quick Commands Reference

| Task | Command |
|------|---------|
| See what changed | `git status` |
| Add all changes | `git add .` |
| Commit changes | `git commit -m "message"` |
| Push to GitHub | `git push origin data-nikhil` |
| Pull from GitHub | `git pull origin data-nikhil` |
| See commit history | `git log --oneline` |
| Undo file changes | `git restore filename` |
| Switch branch | `git checkout branch-name` |

---

## ✅ Success Checklist

After pushing, verify on GitHub:

1. Go to: https://github.com/DakshPrajapati-afk/Claude-Hackathon
2. Switch to `data-nikhil` branch
3. You should see your latest commit
4. Check that new files appear
5. Verify `.env` is NOT visible (it's secret!)

---

## 🆘 If Something Goes Wrong

### "Not a git repository"
```bash
# Make sure you're in the right directory
cd /Users/nikhil01/Desktop/Poly_Prediction_Tool/Claude-Hackathon
git status
```

### "Permission denied"
```bash
# Make sure you're authenticated with GitHub
# You may need to set up SSH keys or use a personal access token
```

### "Changes not staged"
```bash
# You forgot to add files
git add .
git commit -m "Your message"
```

### "Merge conflict"
```bash
# Open conflicted files, fix them, then:
git add .
git commit -m "Resolved conflicts"
git push origin data-nikhil
```

---

## 📚 Learn More

- [Git Official Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Visualizing Git](https://git-school.github.io/visualizing-git/)

---

**Remember:** Always work in `/Claude-Hackathon/` directory, not the parent! 🎯

