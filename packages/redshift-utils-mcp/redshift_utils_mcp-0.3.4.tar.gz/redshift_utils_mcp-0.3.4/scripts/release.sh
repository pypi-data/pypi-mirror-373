#!/bin/bash
set -e

# Release automation script for redshift-utils-mcp
# Usage: ./scripts/release.sh [patch|minor|major]

VERSION_TYPE=${1:-patch}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting release process for redshift-utils-mcp${NC}"
echo -e "${YELLOW}Version bump type: $VERSION_TYPE${NC}"

# Check if we're on the main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${RED}Error: You must be on the main branch to create a release${NC}"
    echo "Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}Error: You have uncommitted changes${NC}"
    echo "Please commit or stash your changes before releasing"
    git status --short
    exit 1
fi

# Make sure we're up to date with remote
echo -e "${YELLOW}Fetching latest changes from remote...${NC}"
git fetch origin main
if [ $(git rev-list HEAD...origin/main --count) -gt 0 ]; then
    echo -e "${RED}Error: Your local branch is not up to date with origin/main${NC}"
    echo "Please pull the latest changes before releasing"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed${NC}"
    echo "Please install uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Check if hatch is available via uv
if ! uv tool list | grep -q hatch; then
    echo -e "${YELLOW}Installing hatch...${NC}"
    uv tool install hatch
fi

# Get current version
CURRENT_VERSION=$(uv run hatch version 2>/dev/null || python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
echo -e "${GREEN}Current version: $CURRENT_VERSION${NC}"

# Bump version
echo -e "${YELLOW}Bumping $VERSION_TYPE version...${NC}"
uv run hatch version $VERSION_TYPE

# Get new version
NEW_VERSION=$(uv run hatch version)
echo -e "${GREEN}New version: $NEW_VERSION${NC}"

# Update changelog if it exists
if [ -f "CHANGELOG.md" ]; then
    echo -e "${YELLOW}Updating CHANGELOG.md...${NC}"
    # Add new version header to changelog
    CHANGELOG_ENTRY="## [$NEW_VERSION] - $(date +%Y-%m-%d)\n\n### Added\n- \n\n### Changed\n- \n\n### Fixed\n- \n\n"
    # Insert after the # Changelog header
    sed -i.bak "/^# Changelog/a\\
\\
$CHANGELOG_ENTRY" CHANGELOG.md
    rm CHANGELOG.md.bak
    echo -e "${GREEN}CHANGELOG.md updated${NC}"
    echo -e "${YELLOW}Please edit CHANGELOG.md to add release notes${NC}"
fi

# Run tests before committing
echo -e "${YELLOW}Running tests...${NC}"
if uv run pytest tests/ -q; then
    echo -e "${GREEN}Tests passed${NC}"
else
    echo -e "${RED}Tests failed! Aborting release${NC}"
    # Revert version change
    git checkout -- pyproject.toml src/redshift_utils_mcp/__init__.py
    exit 1
fi

# Check code formatting
echo -e "${YELLOW}Checking code formatting...${NC}"
if uv run black --check src/ && uv run ruff check src/; then
    echo -e "${GREEN}Code formatting check passed${NC}"
else
    echo -e "${YELLOW}Code formatting issues detected. Fixing...${NC}"
    uv run black src/
    uv run ruff check src/ --fix
fi

# Commit version bump
echo -e "${YELLOW}Committing version bump...${NC}"
git add -A
git commit -m "chore(release): bump version to $NEW_VERSION

- Bumped version from $CURRENT_VERSION to $NEW_VERSION
- Type: $VERSION_TYPE release"

# Create and push tag
echo -e "${YELLOW}Creating tag v$NEW_VERSION...${NC}"
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION

This is a $VERSION_TYPE release.

Changes:
- Version bumped from $CURRENT_VERSION to $NEW_VERSION

See CHANGELOG.md for detailed release notes."

# Push changes
echo -e "${YELLOW}Pushing changes to remote...${NC}"
git push origin main
git push origin "v$NEW_VERSION"

echo -e "${GREEN}✅ Release v$NEW_VERSION created successfully!${NC}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. GitHub Actions will automatically publish to PyPI"
echo "2. Check the Actions tab for the publishing workflow status"
echo "3. Once published, the package will be available at:"
echo "   https://pypi.org/project/redshift-utils-mcp/"
echo "4. Install with: pip install redshift-utils-mcp"
echo ""
echo -e "${YELLOW}Don't forget to:${NC}"
echo "- Update CHANGELOG.md with release notes if needed"
echo "- Create a GitHub release with release notes"
echo "- Announce the release to users if significant changes"