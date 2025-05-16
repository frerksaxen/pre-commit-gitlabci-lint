# pre-commit-gitlabci-lint

This is a [pre-commit hook](https://pre-commit.com/). It uses the `https://gitlab.com/api/v4/ci/lint` lint endpoint to validate the contents of your `.gitlab-ci.yml` file, but the api v4 url can be adjusted (see below for an example).

## Usage

GitLab Lint API [requires authorization](https://gitlab.com/gitlab-org/gitlab/-/issues/321290).

1. [Create Access Token](https://gitlab.com/-/profile/personal_access_tokens) with `api` scope.
2.1 Set access token value as `GITLAB_TOKEN` environment variable
2.2 Or provide the access token via argument (see example below)

**Warning** Please note the token should not be shared and if leaked can cause significant harm.

With Gitlab version 15.7 onwards, the ci linter api has changed and requires the project id (see [Validate a project's CI configuration](https://docs.gitlab.com/ee/api/lint.html#validate-a-projects-ci-configuration)).
Please specify the full linter url in the args parameter containing the correct project id of the hook (replace ':id' with your project id in the example below).

An example `.pre-commit-config.yaml`:

```yaml
---
repos:
  - repo: https://github.com/frerksaxen/pre-commit-gitlabci-lint
    rev: 1.0.0
    hooks:
      - id: gitlabci-lint
        args:
        # for gitlab version > 15.7
        - "https://custom.gitlab.host.com/api/v4/projects/:id"
        # or for gitlab version < 15.7
        # "https://custom.gitlab.host.com/api/v4"
        # It is recommended to store the Access token in the GITLAB_TOKEN environment variable, but you can also set it via
        - "--token"
        - "Your_Gitlab_Access_Token_Value"
        # Enable dry_run to run pipeline creation simulation. See (https://docs.gitlab.com/api/lint/#validate-sample-cicd-configuration)
        - "--dry_run"
```
