# Contributing Guide

## Quick Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the project in development mode
pip install -e ".[dev]"
```

## Development Commands

```bash
check                     # Run all checks (format, lint, tests)
check --fix               # Auto-fix issues and run all checks
check --fast              # Format + lint only (skip tests)

gen-models                # Generate models from API spec
```

## Workflow

1. **Before committing:** Run `check --fix` to auto-fix issues
2. **During development:** Use `check --fast` for quick validation
3. **Update models:** Run `gen-models` when API changes

## Release Process

### GitHub Actions Release

1. Go to the **Actions** tab in GitHub
2. Select the **Release** workflow
3. Click **Run workflow** and choose:
   - **Version type**: `patch` (default), `minor`, or `major`
   - **Dry run**: Test the release process without publishing

The workflow will automatically:

- ✅ Run all tests, linting, and formatting checks (reuses existing test workflow)
- 🔄 Generate fresh models from the API spec
- 📈 Increment the version using Hatch
- 📦 Build the package
- 🚀 Upload to PyPI
- 🏷️ Create a Git tag and GitHub release
- 📋 Provide detailed summary with links

### Required Repository Secrets

Configure these secrets in your GitHub repository settings:

- `PYPI_API_TOKEN`: Token for https://pypi.org/ (production releases)
- `CODECOV_TOKEN`: Token for Codecov uploads (used by CI test workflow)
- `RELEASE_BOT_APP_ID`: GitHub App ID used to create tags/releases
- `RELEASE_BOT_PRIVATE_KEY`: GitHub App private key (PEM) for the release bot

### Getting API Tokens

1. **PyPI**: Go to https://pypi.org/manage/account/token/
2. Create a token with upload permissions
3. Add the token to your repository secrets

## Auto-Release (OpenAPI changes)

When the backend OpenAPI spec changes, the SDK can auto-release a new version.

- Trigger: a `repository_dispatch` event with type `openapi-updated`
- Detect job: fetches the provided `spec_url` (or defaults to `https://api.amigo.ai/v1/openapi.json`), normalizes and compares against `specs/openapi-baseline.json`
- If changed: invokes the release workflow with `version_type=minor` and passes `spec_url` (supports `dry_run`)
- Release workflow: regenerates models, bumps version, builds, publishes to PyPI, pushes tag, and creates a GitHub release

Manual trigger example (repository_dispatch):

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/repos/<OWNER>/<REPO>/dispatches \
  -d '{
    "event_type": "openapi-updated",
    "client_payload": {
      "spec_url": "https://api.amigo.ai/v1/openapi.json",
      "dry_run": true
    }
  }'
```

Notes:

- The baseline file `specs/openapi-baseline.json` is created on first run and updated as part of the release workflow.
- Ensure the secrets listed above are configured so the workflow can push tags, create releases, and publish to PyPI.

### Manual trigger using GitHub CLI (gh)

Requires `gh` authenticated with a token that can dispatch events on the SDK repos.

```bash
# Values that mirror the workflow
OWNER="amigo-ai"
BACKEND_REPO="$OWNER/backend"
COMMIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo manual-test)"
RUN_ID="$(date +%s)"  # stand-in for GitHub Actions run_id

for repo in amigo-typescript-sdk amigo-python-sdk; do
  echo "Notifying $repo..."
  gh api "repos/$OWNER/$repo/dispatches" \
    --method POST \
    --header 'Accept: application/vnd.github+json' \
    --input - <<EOF || echo "⚠️  Failed to notify $repo"
{
  "event_type": "openapi-updated",
  "client_payload": {
    "spec_url": "https://api.amigo.ai/v1/openapi.json",
    "commit_sha": "$COMMIT_SHA",
    "backend_repo": "$BACKEND_REPO",
    "backend_run_id": "$RUN_ID"
  }
}
EOF
done
```

## IDE Setup (VS Code)

Install extensions:

- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

## Troubleshooting

- **Command not found:** Activate virtual environment with `source .venv/bin/activate`
- **Linting failures:** Run `check --fix` to auto-fix issues
- **Model import errors:** Run `gen-models` to regenerate models
- **Release failures:** Check API tokens are configured in repository secrets and try a dry run first
