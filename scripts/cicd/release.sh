#!/bin/bash
# Release Management Script for Sleepr Fantasy Football App

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CURRENT_VERSION=""
NEW_VERSION=""
RELEASE_NOTES=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    if ! command -v gh &> /dev/null; then
        missing_deps+=("gh (GitHub CLI)")
    fi
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Please install the missing dependencies and try again."
        exit 1
    fi
    
    log_success "All dependencies are installed"
}

# Get current version from git tags
get_current_version() {
    CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    log_info "Current version: $CURRENT_VERSION"
}

# Validate semantic version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Invalid version format: $version"
        log_info "Version must follow semantic versioning: vX.Y.Z (e.g., v1.2.3)"
        return 1
    fi
    return 0
}

# Generate release notes
generate_release_notes() {
    log_info "Generating release notes..."
    
    local last_tag=""
    if git describe --tags --abbrev=0 &> /dev/null; then
        last_tag=$(git describe --tags --abbrev=0)
        RELEASE_NOTES=$(git log --pretty=format:"- %s" "$last_tag"..HEAD)
    else
        RELEASE_NOTES=$(git log --pretty=format:"- %s")
    fi
    
    if [ -z "$RELEASE_NOTES" ]; then
        RELEASE_NOTES="- Initial release"
    fi
    
    log_info "Generated release notes:"
    echo "$RELEASE_NOTES"
}

# Run tests before release
run_tests() {
    log_info "Running tests before release..."
    
    # Run Go tests
    if [ -d "$PROJECT_ROOT/api" ]; then
        log_info "Running Go API tests..."
        cd "$PROJECT_ROOT/api"
        go test ./... || {
            log_error "Go tests failed"
            return 1
        }
    fi
    
    # Run Python tests
    if [ -d "$PROJECT_ROOT/analytics" ]; then
        log_info "Running Python analytics tests..."
        cd "$PROJECT_ROOT/analytics"
        if [ -f "requirements.txt" ]; then
            python -m pip install -r requirements.txt &> /dev/null
        fi
        python -m pytest . || {
            log_error "Python tests failed"
            return 1
        }
    fi
    
    # Run Frontend tests
    if [ -d "$PROJECT_ROOT/web/frontend" ]; then
        log_info "Running Frontend tests..."
        cd "$PROJECT_ROOT/web/frontend"
        if [ -f "package.json" ]; then
            npm test -- --watchAll=false || {
                log_error "Frontend tests failed"
                return 1
            }
        fi
    fi
    
    cd "$PROJECT_ROOT"
    log_success "All tests passed"
}

# Build and test Docker images
build_and_test_images() {
    log_info "Building and testing Docker images..."
    
    # Build API image
    if [ -f "$PROJECT_ROOT/api/Dockerfile" ]; then
        log_info "Building API Docker image..."
        docker build -t sleepr-api:$NEW_VERSION "$PROJECT_ROOT/api" || {
            log_error "Failed to build API Docker image"
            return 1
        }
    fi
    
    # Build Analytics image
    if [ -f "$PROJECT_ROOT/analytics/Dockerfile" ]; then
        log_info "Building Analytics Docker image..."
        docker build -t sleepr-analytics:$NEW_VERSION "$PROJECT_ROOT/analytics" || {
            log_error "Failed to build Analytics Docker image"
            return 1
        }
    fi
    
    # Build Frontend image
    if [ -f "$PROJECT_ROOT/web/frontend/Dockerfile" ]; then
        log_info "Building Frontend Docker image..."
        docker build -t sleepr-frontend:$NEW_VERSION "$PROJECT_ROOT/web/frontend" || {
            log_error "Failed to build Frontend Docker image"
            return 1
        }
    fi
    
    log_success "All Docker images built successfully"
}

# Create and push git tag
create_git_tag() {
    log_info "Creating git tag $NEW_VERSION..."
    
    # Ensure we're on main branch
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        log_error "Not on main branch. Current branch: $current_branch"
        log_info "Please switch to main branch before creating a release"
        return 1
    fi
    
    # Ensure working directory is clean
    if [ -n "$(git status --porcelain)" ]; then
        log_error "Working directory is not clean. Please commit or stash changes."
        return 1
    fi
    
    # Create annotated tag
    git tag -a "$NEW_VERSION" -m "Release $NEW_VERSION

$RELEASE_NOTES"
    
    # Push tag to remote
    git push origin "$NEW_VERSION"
    
    log_success "Git tag $NEW_VERSION created and pushed"
}

# Create GitHub release
create_github_release() {
    log_info "Creating GitHub release..."
    
    gh release create "$NEW_VERSION" \
        --title "Release $NEW_VERSION" \
        --notes "$RELEASE_NOTES" \
        --latest
    
    log_success "GitHub release created: $NEW_VERSION"
}

# Main release function
perform_release() {
    log_info "Starting release process for version $NEW_VERSION..."
    
    generate_release_notes
    run_tests
    build_and_test_images
    create_git_tag
    create_github_release
    
    log_success "Release $NEW_VERSION completed successfully!"
    log_info "Release URL: https://github.com/$(gh repo view --json owner,name -q '.owner.login + \"/\" + .name')/releases/tag/$NEW_VERSION"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS] <version>"
    echo ""
    echo "Create a new release for the Sleepr Fantasy Football application"
    echo ""
    echo "Arguments:"
    echo "  <version>        New version number (e.g., v1.2.3)"
    echo ""
    echo "Options:"
    echo "  -h, --help       Show this help message"
    echo "  -n, --dry-run    Show what would be done without making changes"
    echo "  --skip-tests     Skip running tests (not recommended)"
    echo "  --skip-build     Skip building Docker images"
    echo ""
    echo "Examples:"
    echo "  $0 v1.0.0                    # Create release v1.0.0"
    echo "  $0 --dry-run v1.0.1          # Dry run for v1.0.1"
    echo "  $0 --skip-tests v1.0.2       # Skip tests (not recommended)"
    echo ""
}

# Parse command line arguments
parse_args() {
    local dry_run=false
    local skip_tests=false
    local skip_build=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -n|--dry-run)
                dry_run=true
                shift
                ;;
            --skip-tests)
                skip_tests=true
                shift
                ;;
            --skip-build)
                skip_build=true
                shift
                ;;
            v[0-9]*.[0-9]*.[0-9]*)
                NEW_VERSION=$1
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    if [ -z "$NEW_VERSION" ]; then
        log_error "Version argument is required"
        show_usage
        exit 1
    fi
    
    if ! validate_version "$NEW_VERSION"; then
        exit 1
    fi
    
    if [ "$dry_run" = true ]; then
        log_info "DRY RUN MODE - No changes will be made"
        log_info "Would create release: $NEW_VERSION"
        generate_release_notes
        exit 0
    fi
    
    # Set flags for skipping steps
    if [ "$skip_tests" = true ]; then
        log_warning "Skipping tests - this is not recommended for production releases"
    fi
    
    if [ "$skip_build" = true ]; then
        log_warning "Skipping Docker image builds"
    fi
}

# Main execution
main() {
    cd "$PROJECT_ROOT"
    
    parse_args "$@"
    check_dependencies
    get_current_version
    
    log_info "Creating release $NEW_VERSION (current: $CURRENT_VERSION)"
    
    # Confirm with user
    read -p "Continue with release? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Release cancelled"
        exit 0
    fi
    
    perform_release
}

# Run main function with all arguments
main "$@"
