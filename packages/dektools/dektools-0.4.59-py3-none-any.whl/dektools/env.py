import os


def is_on_cicd():
    return bool(
        os.getenv("GITHUB_ACTIONS") or
        os.getenv("TRAVIS") or
        os.getenv("CIRCLECI") or
        os.getenv("GITLAB_CI") or
        os.getenv("JENKINS_URL")
    )
