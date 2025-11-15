# 🔒 GitHub Repository Setup for giacomo (giack-hack)

## Step 1: Add giacomo as Collaborator

1. Go to: https://github.com/miradebs98/Investor_voice_agent/settings/access
2. Click **"Add people"** button
3. Enter GitHub username: **giack-hack**
4. Select permission level: **Write** (allows pushing to branches)
5. Click **"Add giack-hack to this repository"**

## Step 2: Protect the Main Branch

1. Go to: https://github.com/miradebs98/Investor_voice_agent/settings/branches
2. Under **"Branch protection rules"**, click **"Add rule"**
3. In **"Branch name pattern"**, enter: **main**
4. Enable these settings:
   - ✅ **"Require pull request reviews before merging"**
     - Set **"Required number of approvals"** to: **1**
     - ✅ **"Require review from Code Owners"** (optional)
   - ✅ **"Require status checks to pass before merging"** (optional)
   - ✅ **"Require conversation resolution before merging"** (optional)
   - ✅ **"Do not allow bypassing the above settings"** (recommended)
5. Click **"Create"**

## Step 3: Allow giacomo to Push to His Branch

The `giacomo` branch is NOT protected, so giacomo can:
- ✅ Push directly to `giacomo` branch
- ✅ Create new branches
- ❌ Cannot push directly to `main` (requires PR + approval)

## Result

✅ **giacomo can:**
- Clone the repository
- Push to `giacomo` branch freely
- Create new branches
- Open pull requests

❌ **giacomo cannot:**
- Push directly to `main` branch
- Merge to `main` without your approval

## Workflow

1. giacomo works on `giacomo` branch
2. When ready, he creates a Pull Request: `giacomo` → `main`
3. You review the PR
4. You approve and merge (or request changes)

---

**Repository URL:** https://github.com/miradebs98/Investor_voice_agent
