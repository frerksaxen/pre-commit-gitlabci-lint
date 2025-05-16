from typing import List
import argparse
import json
import os
import urllib.error
import urllib.request

import git


def print_messages(messages: List[str]):
    print("=======")
    for msg in messages:
        print(msg)
    print("=======")


def urlerr(err, token: str, token_env_key: str):
    print("Error connecting to Gitlab: " + str(err))
    if not token and isinstance(err, urllib.error.HTTPError) and err.code == 401:
        print(
            "The lint endpoint requires authentication."
            "Please set {} environment variable".format(token_env_key)
        )


def add_ref():
    repo = git.Repo(".")
    try:
        repo.git.ls_remote(
            "--exit-code", "--heads", "origin", f"refs/heads/{repo.active_branch.name}"
        )
    except git.exc.GitCommandError:
        # No ref possible, because the local branch name does not exist remotely. Use default branch instead.
        return {}
    # The remote branch exists and thus, the ci is validated within the context of to the active branch
    return {"ref": repo.active_branch.name}


def add_dry_run(args):
    if args.dry_run:
        return {"dry_run": True} | add_ref()
    else:
        return {}


def main(argv=None):
    token_env_key = "GITLAB_TOKEN"
    default_ci_config_path = ".gitlab-ci.yml"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        nargs="?",
        default="https://gitlab.com/api/v4",
        help="Gitlab api endpoint to validate the contents of your .gitlab-ci.yml file. Default %(default)s",
        type=str,
    )
    parser.add_argument(
        "--token",
        default=os.getenv(token_env_key),
        help=f"GitLab personal access token. By default the environmental variable {token_env_key} is used.",
        type=str,
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="""
            Run pipeline creation simulation (true) or only do static check (false).
            If set to true, the ref parameter of the ci lint argument (https://docs.gitlab.com/api/lint/) is set to the current branch (if it already exists on origin).
            Default %(default)s""",
    )
    args = parser.parse_args(argv)

    # Set endpoint url
    url = args.url
    if url.endswith("/"):
        url = url.rstrip("/")
    lint_ext = "/ci/lint"
    if url.endswith(lint_ext):
        url = url.rstrip(lint_ext)

    # Set header for the curl command
    headers = {
        "Content-Type": "application/json",
    }
    if args.token:
        headers["PRIVATE-TOKEN"] = args.token

    # Try to get the default ci config path from the gitlab api.
    # Otherwise fall back to default
    try:
        response = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
        project_info = json.loads(response.read())
        if "ci_config_path" in project_info and project_info["ci_config_path"]:
            ci_config_path = project_info["ci_config_path"]
        else:
            # Use the default path for the gitlab-ci.yml file
            ci_config_path = default_ci_config_path
    except urllib.error.URLError:
        ci_config_path = default_ci_config_path

    # Prepare the data field for the curl command
    try:
        with open(ci_config_path, "r") as f:
            data = {"content": f.read()}
    except (FileNotFoundError, PermissionError):
        print(f"Cannot open {ci_config_path}")
        return 11

    # Add optional dry_run
    data |= add_dry_run(args)
    # Convert to json
    data = json.dumps(data).encode("utf-8")

    # Prepare header for curl
    url += lint_ext
    headers["Content-Length"] = len(data)
    msg_using_linter = "Using linter: " + url
    if args.token:
        msg_using_linter += " with token " + len(args.token) * "*"
    print(msg_using_linter)

    # curl request to gitlab and interpret response
    try:
        request = urllib.request.Request(
            url=url,
            data=data,
            headers=headers,
        )
        response = urllib.request.urlopen(request)
        lint_output = json.loads(response.read())

        if "status" in lint_output:
            # Gitlab version < 15.7
            if not lint_output["status"] == "valid":
                print_messages(lint_output["errors"])
                return 1
            elif lint_output["warnings"]:
                print_messages(lint_output["warnings"])
        elif "valid" in lint_output:
            # Gitlab version > 15.7
            if not lint_output["valid"]:
                print_messages(lint_output["errors"])
                return 2
            elif lint_output["warnings"]:
                print_messages(lint_output["warnings"])
        else:
            # Gitlab changed its output again?
            print(
                "Unknown gitlab response. Did gitlab update the ci linter response again?"
            )
            return 3
    except urllib.error.URLError as err:
        urlerr(err, args.token, token_env_key)
        return 12
    return 0


if __name__ == "__main__":
    exit(main())
