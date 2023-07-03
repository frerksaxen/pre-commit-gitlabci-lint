from typing import List
import argparse
import json
import os

import urllib.error
from urllib.request import Request, urlopen


token_env_key = "GITLAB_TOKEN"

parser = argparse.ArgumentParser()
parser.add_argument("url", nargs="?", default="https://gitlab.com/api/v4/ci/lint")
parser.add_argument(
    "--token",
    default=os.getenv(token_env_key),
    help=(
        "GitLab personal access token. "
        "As default the value of {} environmental variable is used.".format(
            token_env_key
        )
    ),
)


def print_messages(messages: List[str]):
    print("=======")
    for msg in messages:
        print(msg)
    print("=======")


def main(argv=None):
    args = parser.parse_args(argv)
    url = args.url
    token = args.token

    rv = 0
    try:
        with open(".gitlab-ci.yml", "r") as f:
            data = json.dumps({"content": f.read()})
    except (FileNotFoundError, PermissionError):
        print("Cannot open .gitlab-ci.yml")
        rv = 1
    else:
        # url = urljoin(base_url, "/api/v4/ci/lint")
        msg_using_linter = "Using linter: " + url
        headers = {
            "Content-Type": "application/json",
            "Content-Length": len(data),
        }
        if token:
            headers["PRIVATE-TOKEN"] = token
            msg_using_linter += " with token " + len(token) * "*"
        print(msg_using_linter)
        try:
            request = Request(
                url,
                data.encode("utf-8"),
                headers=headers,
            )
            response = urlopen(request)
            lint_output = json.loads(response.read())

            if "status" in lint_output:
                # Gitlab version < 15.7
                if not lint_output["status"] == "valid":
                    print_messages(lint_output["errors"])
                    rv = 1
                elif lint_output["warnings"]:
                    print_messages(lint_output["warnings"])
            elif "valid" in lint_output:
                # Gitlab version > 15.7
                if not lint_output["valid"]:
                    print_messages(lint_output["errors"])
                    rv = 1
                elif lint_output["warnings"]:
                    print_messages(lint_output["warnings"])
            else:
                # Gitlab changed its output again?
                print(
                    "Unknown gitlab response. Did gitlab update the ci linter response again?"
                )
                rv = 1
        except urllib.error.URLError as exc:
            print("Error connecting to Gitlab: " + str(exc))
            if (
                not token
                and isinstance(exc, urllib.error.HTTPError)
                and exc.code == 401
            ):
                print(
                    "The lint endpoint requires authentication."
                    "Please set {} environment variable".format(token_env_key)
                )
            rv = 1
    return rv


if __name__ == "__main__":
    exit(main())
