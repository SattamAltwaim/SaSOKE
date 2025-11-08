#!/bin/bash
# Script to push SaSOKE to your GitHub account

echo "=== SaSOKE GitHub Push Script ==="
echo ""
echo "Before running this script:"
echo "1. Create new repo 'SaSOKE' at https://github.com/new"
echo "2. Don't initialize with README"
echo "3. Copy your GitHub username"
echo ""
read -p "Enter your GitHub username: " USERNAME
echo ""

# Remove old remote
echo "Removing old remote..."
git remote remove origin 2>/dev/null

# Add new remote
echo "Adding new remote: https://github.com/$USERNAME/SaSOKE.git"
git remote add origin "https://github.com/$USERNAME/SaSOKE.git"

# Show status
echo ""
echo "Current branch:"
git branch --show-current

# Push
echo ""
echo "Pushing to GitHub..."
git push -u origin $(git branch --show-current)

echo ""
echo "=== Done! ==="
echo ""
echo "Next steps:"
echo "1. Verify at: https://github.com/$USERNAME/SaSOKE"
echo "2. Update notebooks: Replace YOUR_USERNAME with $USERNAME"
echo "3. Upload data to Google Drive: /MyDrive/SOKE_data/"
echo "4. Open Colab and run notebooks"
echo ""
echo "See GITHUB_SETUP_INSTRUCTIONS.md for details"

