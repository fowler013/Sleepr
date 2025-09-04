#!/bin/bash
# Environment Setup and Validation Script for CI/CD

set -euo pipefail

# Configuration
ENVIRONMENTS=("development" "staging" "production")
REQUIRED_SECRETS=("DATABASE_URL" "JWT_SECRET" "SLEEPER_API_URL")
OPTIONAL_SECRETS=("SENTRY_DSN" "SLACK_WEBHOOK_URL" "EMAIL_CONFIG")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Validate GitHub Actions secrets
validate_secrets() {
    local env=$1
    log_info "Validating secrets for $env environment..."
    
    local missing_secrets=()
    
    for secret in "${REQUIRED_SECRETS[@]}"; do
        local secret_name="${env^^}_${secret}"
        if ! gh secret list | grep -q "$secret_name"; then
            missing_secrets+=("$secret_name")
        fi
    done
    
    if [ ${#missing_secrets[@]} -ne 0 ]; then
        log_error "Missing required secrets for $env:"
        printf '%s\n' "${missing_secrets[@]}"
        return 1
    fi
    
    log_success "All required secrets present for $env"
}

# Setup GitHub environments
setup_github_environments() {
    log_info "Setting up GitHub environments..."
    
    for env in "${ENVIRONMENTS[@]}"; do
        log_info "Setting up $env environment..."
        
        # Create environment (this requires GitHub CLI with appropriate permissions)
        gh api repos/:owner/:repo/environments/$env -X PUT \
            --field wait_timer=0 \
            --field reviewers='[]' \
            --field deployment_branch_policy='{"protected_branches":false,"custom_branch_policies":true}' \
            2>/dev/null || log_warning "Could not create $env environment (may already exist)"
        
        # Validate secrets
        validate_secrets "$env" || log_warning "Secrets validation failed for $env"
    done
}

# Generate environment-specific configuration
generate_env_configs() {
    log_info "Generating environment configurations..."
    
    # Development environment
    cat > .env.development << EOF
# Development Environment Configuration
NODE_ENV=development
PORT=8080
DATABASE_URL=postgres://sleepr_dev:password@localhost:5432/sleepr_dev
JWT_SECRET=dev-secret-key-change-in-production
SLEEPER_API_URL=https://api.sleeper.app
ANALYTICS_API_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=debug
ENABLE_SWAGGER=true
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
EOF

    # Staging environment
    cat > .env.staging << EOF
# Staging Environment Configuration
NODE_ENV=staging
PORT=8080
DATABASE_URL=\${STAGING_DATABASE_URL}
JWT_SECRET=\${STAGING_JWT_SECRET}
SLEEPER_API_URL=https://api.sleeper.app
ANALYTICS_API_URL=http://analytics:8001
FRONTEND_URL=https://staging.sleepr.app
LOG_LEVEL=info
ENABLE_SWAGGER=true
CORS_ORIGINS=https://staging.sleepr.app
SENTRY_DSN=\${STAGING_SENTRY_DSN}
EOF

    # Production environment
    cat > .env.production << EOF
# Production Environment Configuration
NODE_ENV=production
PORT=8080
DATABASE_URL=\${PRODUCTION_DATABASE_URL}
JWT_SECRET=\${PRODUCTION_JWT_SECRET}
SLEEPER_API_URL=https://api.sleeper.app
ANALYTICS_API_URL=http://analytics:8001
FRONTEND_URL=https://sleepr.app
LOG_LEVEL=warn
ENABLE_SWAGGER=false
CORS_ORIGINS=https://sleepr.app
SENTRY_DSN=\${PRODUCTION_SENTRY_DSN}
EOF

    log_success "Environment configurations generated"
}

# Validate CI/CD pipeline configuration
validate_pipeline() {
    log_info "Validating CI/CD pipeline configuration..."
    
    # Check if GitHub Actions workflow files exist
    local workflows_dir=".github/workflows"
    local required_workflows=("ci.yml" "cd.yml" "security.yml")
    
    for workflow in "${required_workflows[@]}"; do
        if [ ! -f "$workflows_dir/$workflow" ]; then
            log_error "Missing workflow file: $workflows_dir/$workflow"
            return 1
        fi
    done
    
    # Validate workflow syntax (basic YAML check)
    for workflow in "${required_workflows[@]}"; do
        if ! python -c "import yaml; yaml.safe_load(open('$workflows_dir/$workflow'))" 2>/dev/null; then
            log_error "Invalid YAML syntax in $workflows_dir/$workflow"
            return 1
        fi
    done
    
    log_success "All workflow files are valid"
}

# Setup branch protection rules
setup_branch_protection() {
    log_info "Setting up branch protection rules..."
    
    # Protect main branch
    gh api repos/:owner/:repo/branches/main/protection -X PUT --input - << EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Test Go API",
      "Test Python Analytics",
      "Test React Frontend",
      "Lint and Code Quality",
      "Security Scan",
      "Build Docker Images"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

    log_success "Branch protection rules configured"
}

# Create CODEOWNERS file
create_codeowners() {
    log_info "Creating CODEOWNERS file..."
    
    cat > .github/CODEOWNERS << EOF
# Global owners
* @fowler013

# API code
/api/ @fowler013

# Analytics code
/analytics/ @fowler013

# Frontend code
/web/ @fowler013

# Infrastructure and deployment
/deployment/ @fowler013
/monitoring/ @fowler013
/.github/ @fowler013
/scripts/ @fowler013

# Documentation
*.md @fowler013
/docs/ @fowler013
EOF

    log_success "CODEOWNERS file created"
}

# Generate deployment documentation
generate_deployment_docs() {
    log_info "Generating deployment documentation..."
    
    cat > docs/DEPLOYMENT.md << EOF
# Deployment Guide

This document describes the deployment process for the Sleepr Fantasy Football application.

## Environments

### Development
- **URL**: http://localhost:3000
- **Database**: Local PostgreSQL
- **Purpose**: Local development and testing

### Staging
- **URL**: https://staging.sleepr.app
- **Database**: Staging PostgreSQL instance
- **Purpose**: Integration testing and feature validation

### Production
- **URL**: https://sleepr.app
- **Database**: Production PostgreSQL instance
- **Purpose**: Live application serving users

## Deployment Process

### Automatic Deployments

1. **Staging**: Automatically deployed when code is merged to \`main\` branch
2. **Production**: Automatically deployed when a new release tag is created

### Manual Deployments

#### Using GitHub Actions
1. Go to the Actions tab in the GitHub repository
2. Select the "Continuous Deployment" workflow
3. Click "Run workflow" and select the environment

#### Using CLI Scripts
\`\`\`bash
# Release a new version
./scripts/cicd/release.sh v1.2.3

# Deploy to specific environment
./deployment/deploy.sh staging
./deployment/deploy.sh production
\`\`\`

## Environment Variables

### Required Secrets
- \`DATABASE_URL\`: PostgreSQL connection string
- \`JWT_SECRET\`: Secret key for JWT token signing
- \`SLEEPER_API_URL\`: Sleeper API base URL

### Optional Secrets
- \`SENTRY_DSN\`: Error tracking configuration
- \`SLACK_WEBHOOK_URL\`: Slack notifications
- \`EMAIL_CONFIG\`: Email service configuration

## Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **AlertManager**: http://localhost:9093

## Rollback Procedures

### Automatic Rollback
Failed deployments will automatically rollback to the previous stable version.

### Manual Rollback
\`\`\`bash
# Rollback to previous release
gh release list
./deployment/deploy.sh production --rollback v1.2.2
\`\`\`

## Troubleshooting

### Common Issues
1. **Database Migration Failures**: Check migration logs and database connectivity
2. **Container Start Failures**: Verify environment variables and resource limits
3. **Health Check Failures**: Check application logs and dependencies

### Log Locations
- Application logs: \`kubectl logs -f deployment/sleepr-api\`
- Database logs: \`kubectl logs -f deployment/postgresql\`
- Monitoring logs: \`kubectl logs -f deployment/prometheus\`
EOF

    log_success "Deployment documentation generated"
}

# Main function
main() {
    log_info "Setting up CI/CD environment for Sleepr Fantasy Football App"
    
    # Check if we're in a git repository
    if [ ! -d ".git" ]; then
        log_error "This script must be run from the root of the git repository"
        exit 1
    fi
    
    # Check if GitHub CLI is authenticated
    if ! gh auth status &>/dev/null; then
        log_error "GitHub CLI is not authenticated. Run 'gh auth login' first."
        exit 1
    fi
    
    # Create necessary directories
    mkdir -p docs .github
    
    # Run setup functions
    generate_env_configs
    validate_pipeline
    create_codeowners
    generate_deployment_docs
    
    # Optional: Setup GitHub-specific configurations (requires appropriate permissions)
    read -p "Setup GitHub environments and branch protection? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_github_environments
        setup_branch_protection
    fi
    
    log_success "CI/CD environment setup complete!"
    log_info "Next steps:"
    log_info "1. Review and commit the generated configuration files"
    log_info "2. Set up required secrets in GitHub repository settings"
    log_info "3. Test the CI/CD pipeline with a pull request"
    log_info "4. Create your first release with: ./scripts/cicd/release.sh v1.0.0"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Setup CI/CD environment for Sleepr Fantasy Football application"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo ""
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Run main function
main
