# CI/CD Automation System

This directory contains the complete CI/CD automation system for the Sleepr Fantasy Football application, including GitHub Actions workflows, release management, and deployment automation.

## 🚀 Features

### GitHub Actions Workflows

#### Continuous Integration (`ci.yml`)
- **Multi-language testing**: Go API, Python Analytics, React Frontend
- **Code quality**: Linting, security scanning, dependency checks
- **Docker image building**: Automated container builds
- **Coverage reporting**: Codecov integration
- **Parallel execution**: Fast feedback on pull requests

#### Continuous Deployment (`cd.yml`)
- **Automated staging deployment**: On main branch merges
- **Production deployment**: On release tag creation
- **Container registry**: GitHub Container Registry integration
- **Database migrations**: Automated schema updates
- **Performance testing**: Load testing with Artillery

#### Security Scanning (`security.yml`)
- **Dependency vulnerability scanning**: Go, Python, Node.js
- **Container security**: Trivy scanning
- **Static code analysis**: CodeQL integration
- **License compliance**: Automated license checking
- **Scheduled scans**: Daily security audits

### Release Management

#### Automated Release Script (`release.sh`)
```bash
# Create a new release
./scripts/cicd/release.sh v1.2.3

# Dry run (preview changes)
./scripts/cicd/release.sh --dry-run v1.2.4

# Skip tests (not recommended)
./scripts/cicd/release.sh --skip-tests v1.2.5
```

**Features:**
- Semantic versioning validation
- Automated release notes generation
- Comprehensive testing before release
- Docker image building and validation
- Git tag creation and GitHub release

#### CI/CD Environment Setup (`setup-cicd.sh`)
```bash
# Setup CI/CD environment
./scripts/cicd/setup-cicd.sh
```

**Features:**
- Environment configuration generation
- GitHub branch protection rules
- CODEOWNERS file creation
- Deployment documentation
- Secret validation

## 🔧 GitHub Actions Configuration

### Required Secrets
Set these in your GitHub repository settings (Settings → Secrets and variables → Actions):

#### Development
- `DEVELOPMENT_DATABASE_URL`
- `DEVELOPMENT_JWT_SECRET`

#### Staging
- `STAGING_DATABASE_URL`
- `STAGING_JWT_SECRET`
- `STAGING_SENTRY_DSN` (optional)

#### Production
- `PRODUCTION_DATABASE_URL`
- `PRODUCTION_JWT_SECRET`
- `PRODUCTION_SENTRY_DSN` (optional)

### Environment Variables
```yaml
GO_VERSION: '1.21'
NODE_VERSION: '18'
PYTHON_VERSION: '3.11'
REGISTRY: ghcr.io
```

## 🚦 Workflow Triggers

### Pull Requests
- Run full CI pipeline
- Security scanning
- Code quality checks
- Build validation

### Main Branch
- Deploy to staging
- Run integration tests
- Database migrations

### Release Tags
- Deploy to production
- Create GitHub release
- Build and push production images
- Performance testing

### Scheduled
- Daily security scans
- Dependency updates
- License compliance checks

## 📊 Monitoring & Observability

### CI/CD Metrics
- **Build success rate**: Track deployment reliability
- **Test coverage**: Maintain code quality standards
- **Security scan results**: Monitor vulnerability trends
- **Performance benchmarks**: Ensure application performance

### Alerts
- Build failures
- Security vulnerabilities
- Test coverage drops
- Performance regressions

## 🔄 Deployment Pipeline

### Staging Deployment
1. Code merged to main branch
2. CI pipeline passes
3. Automatic deployment to staging
4. Integration tests run
5. Notification sent

### Production Deployment
1. Release tag created (manual or automated)
2. Full CI pipeline validation
3. Production deployment
4. Health checks
5. Rollback on failure

## 🛡️ Security Features

### Code Scanning
- **Go**: gosec for security vulnerabilities
- **Python**: bandit and safety for security issues
- **JavaScript/TypeScript**: npm audit for dependencies
- **Containers**: Trivy for image vulnerabilities

### Supply Chain Security
- Dependency vulnerability scanning
- License compliance checking
- Container base image scanning
- Secret detection

## 📈 Performance Optimization

### Build Optimization
- **Docker layer caching**: Reduce build times
- **Parallel job execution**: Faster feedback
- **Conditional job execution**: Skip unnecessary steps
- **Artifact reuse**: Share build outputs

### Test Optimization
- **Parallel test execution**: Faster test runs
- **Test result caching**: Skip unchanged tests
- **Coverage reporting**: Track test effectiveness

## 🔍 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check workflow logs
gh run list --workflow=ci.yml
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id>
```

#### Secret Issues
```bash
# List repository secrets
gh secret list

# Set a secret
gh secret set SECRET_NAME --body "secret-value"
```

#### Permission Issues
```bash
# Check repository permissions
gh auth status
gh repo view --json permissions
```

## 📚 Best Practices

### Branch Protection
- Require status checks
- Require pull request reviews
- Restrict force pushes
- Require up-to-date branches

### Release Management
- Use semantic versioning
- Generate automated release notes
- Tag releases consistently
- Test thoroughly before release

### Security
- Scan dependencies regularly
- Keep secrets secure
- Monitor for vulnerabilities
- Update dependencies promptly

## 🚀 Getting Started

1. **Setup CI/CD environment**:
   ```bash
   ./scripts/cicd/setup-cicd.sh
   ```

2. **Configure GitHub secrets** in repository settings

3. **Test the pipeline** with a pull request

4. **Create your first release**:
   ```bash
   ./scripts/cicd/release.sh v1.0.0
   ```

## 🔗 Integration

### With Monitoring System
- Pipeline metrics exported to Prometheus
- Grafana dashboards for CI/CD visibility
- Alerts for build failures and security issues

### With Deployment System
- Automated deployment after successful builds
- Health checks and rollback capabilities
- Environment-specific configurations

### With Analytics System
- Build and deployment metrics
- Performance trend analysis
- Quality metrics tracking

This CI/CD system provides a robust, secure, and automated pipeline for the Sleepr Fantasy Football application, ensuring high-quality deployments and maintaining security standards.
