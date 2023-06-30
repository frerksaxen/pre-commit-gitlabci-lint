# pre-commit-gitlabci-lint

This is a [pre-commit hook](https://pre-commit.com/). Uses the `https://gitlab.com/api/v4/ci/lint` lint endpoint to validate the contents of your `.gitlab-ci.yml` file, but this can be overridden, see below.

## Usage

GitLab Lint API [requires authorization](https://gitlab.com/gitlab-org/gitlab/-/issues/321290).
1. [Create Access Token](https://gitlab.com/-/profile/personal_access_tokens) with `api` scope.
2. Set access token value as `GITLAB_TOKEN` environment variable

**Warning** Please note the token should not be shared and if leaked can cause significant harm.

An example `.pre-commit-config.yaml`:

```yaml
---
repos:
  - repo: https://github.com/frerksaxen/pre-commit-gitlabci-lint
    rev: 1.0
    hooks:
      - id: gitlabci-lint
      # args: ["https://custom.gitlab.host.com/api/v4/projects/:id/ci/lint"]

