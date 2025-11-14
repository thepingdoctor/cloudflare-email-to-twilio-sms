#!/bin/bash
# Gitignore Cleanup Script
# This script removes tracked files that should be ignored
# Run with: bash cleanup-gitignore.sh

set -e

echo "=================================================="
echo "Gitignore Cleanup Script"
echo "=================================================="
echo ""
echo "This script will:"
echo "1. Remove backup files from git tracking"
echo "2. Optionally delete backup files from filesystem"
echo "3. Update .gitignore with recommended patterns"
echo "4. Verify changes"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# List of backup files to remove from tracking
BACKUP_FILES=(
    "README.md.backup-20251113-221653"
    "src/services/twilio-service.ts.backup-20251113-221637"
    "src/utils/logger.ts.backup-20251113-222601"
    "src/worker/index.ts.backup-20251113-221653"
    "src/worker/index.ts.backup-20251113-222601"
    "streamlit-app/app.py.backup-20251113-221646"
    "streamlit-app/app.py.backup-20251113-221653"
    "streamlit-app/components/input_form.py.backup-20251113-221639"
    "streamlit-app/components/input_form.py.backup-20251113-221645"
    "streamlit-app/generators/code_generator.py.backup-20251113-221645"
    "streamlit-app/templates/config/.env.example.j2.backup-20251113-221653"
    "streamlit-app/templates/email-worker/index.ts.j2.backup-20251113-221639"
)

echo -e "${YELLOW}Step 1: Remove backup files from git tracking${NC}"
echo "Found ${#BACKUP_FILES[@]} backup files to remove from tracking"
echo ""

for file in "${BACKUP_FILES[@]}"; do
    if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
        echo "Removing from tracking: $file"
        git rm --cached "$file"
    else
        echo "Not tracked (skipping): $file"
    fi
done

echo ""
echo -e "${GREEN}✓ Backup files removed from git tracking${NC}"
echo ""

# Ask about deleting physical files
echo -e "${YELLOW}Step 2: Delete backup files from filesystem?${NC}"
read -p "Do you want to delete backup files from the filesystem? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deleting backup files..."
    find . -name "*.backup-*" -type f -delete
    echo -e "${GREEN}✓ Backup files deleted${NC}"
else
    echo "Keeping backup files on filesystem"
fi

echo ""

# Ask about poetry.lock
echo -e "${YELLOW}Step 3: Handle poetry.lock file${NC}"
echo "Current recommendation: KEEP poetry.lock tracked for reproducible deployments"
echo ""
read -p "Do you want to remove poetry.lock from tracking? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing poetry.lock from tracking..."
    git rm --cached streamlit-app/poetry.lock
    echo -e "${GREEN}✓ poetry.lock removed from tracking${NC}"
    echo -e "${YELLOW}Note: You should uncomment the poetry.lock line in .gitignore${NC}"
else
    echo "Keeping poetry.lock tracked"
fi

echo ""

# Update .gitignore
echo -e "${YELLOW}Step 4: Update .gitignore${NC}"
if [ -f "docs/.gitignore.recommended" ]; then
    read -p "Replace current .gitignore with recommended version? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Backup current .gitignore
        cp .gitignore .gitignore.backup-$(date +%Y%m%d-%H%M%S)
        # Replace with recommended
        cp docs/.gitignore.recommended .gitignore
        echo -e "${GREEN}✓ .gitignore updated (backup created)${NC}"
    else
        echo "Keeping current .gitignore"
        echo "You can manually review docs/.gitignore.recommended"
    fi
else
    echo -e "${RED}Warning: docs/.gitignore.recommended not found${NC}"
    echo "Skipping .gitignore update"
fi

echo ""

# Verification
echo -e "${YELLOW}Step 5: Verification${NC}"
echo ""

echo "Files currently ignored (sample):"
git status --ignored | head -20
echo ""

echo "Checking for accidentally ignored source files..."
IGNORED_SOURCE=$(git ls-files --others --ignored --exclude-standard | grep -E "\.(py|ts|js|json)$" | grep -v node_modules | head -10)
if [ -z "$IGNORED_SOURCE" ]; then
    echo -e "${GREEN}✓ No source files accidentally ignored${NC}"
else
    echo -e "${RED}Warning: Some source files may be ignored:${NC}"
    echo "$IGNORED_SOURCE"
fi

echo ""
echo "Files staged for commit:"
git status --short
echo ""

# Final summary
echo "=================================================="
echo -e "${GREEN}Cleanup Complete!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Review staged changes: git status"
echo "2. Commit changes: git commit -m 'chore: update .gitignore and remove tracked artifacts'"
echo "3. Push changes: git push"
echo ""
echo "Verification commands:"
echo "  - Check ignored files: git status --ignored"
echo "  - Verify pattern: git check-ignore -v <file>"
echo "  - Test .gitignore: echo 'test' > test.backup-123 && git status"
echo ""
