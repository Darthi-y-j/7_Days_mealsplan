# GitHub Setup Guide

Follow these steps to push your backend to GitHub and deploy it.

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the **+** icon in the top right corner
3. Select **New repository**
4. Name it (e.g., `meal-planner-api`)
5. Choose **Public** or **Private**
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **Create repository**

## Step 2: Initialize Git in Your Backend Folder

Open PowerShell or Command Prompt in your backend directory and run:

```powershell
# Navigate to backend directory
cd "C:\Users\dell\OneDrive\Desktop\Office use\backend"

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Meal Planner API"
```

## Step 3: Connect to GitHub and Push

After creating the repository on GitHub, you'll see a URL like:
`https://github.com/yourusername/meal-planner-api.git`

Run these commands (replace with your actual repository URL):

```powershell
# Add remote repository
git remote add origin https://github.com/yourusername/meal-planner-api.git

# Rename main branch (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

If you get authentication errors, you may need to:
- Use a Personal Access Token instead of password
- Set up SSH keys
- Use GitHub Desktop app

## Step 4: Create .env File Locally

**IMPORTANT:** Before pushing, make sure you have a `.env` file with your API key:

1. Create a file named `.env` in the backend folder
2. Add this line (replace with your actual API key):
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

The `.gitignore` file will prevent this from being pushed to GitHub.

## Step 5: Verify Your Push

1. Go to your GitHub repository page
2. You should see all your files:
   - `main.py`
   - `requirements.txt`
   - `README.md`
   - `food_data/` folder
   - etc.

## Quick Command Reference

```powershell
# Check git status
git status

# See what files will be committed
git status --short

# Add specific file
git add filename.py

# Commit changes
git commit -m "Your commit message"

# Push changes
git push

# Pull latest changes
git pull
```

## Future Updates

Whenever you make changes:

```powershell
git add .
git commit -m "Description of changes"
git push
```

