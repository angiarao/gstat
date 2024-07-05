#!/usr/bin/env python
import argparse
import csv
import datetime
from github import Github

def get_parser():
    parser = argparse.ArgumentParser(description="Get stats of a Github repository")
    parser.add_argument("--repos_list_path", help="Path to the repository info")
    parser.add_argument("--users_path", help="Path to the user info")
    parser.add_argument("--since", default=30, type=int, help="Get stats for last X days")
    parser.add_argument("--token", help="Github token")
    parser.add_argument("--output_path", help="Path to the output file")
    return parser

def get_repo(repo_path):
    """
    Get the Github repo names.
    """
    with open(repo_path, 'r') as f:
        repos = [line.strip() for line in f]
    return repos

def get_users(users_path):
    """
    Get the Github users.
    """
    with open(users_path, 'r') as f:
        users = [line.strip() for line in f]
    return users

def get_pulls(repos, users, since, git_client: Github):
    """
    Get the stats of the Github repositories.
    """
    print("Collecting Pull Request stats...")
    prs_map = {}
    since_dt = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=since)
    for user in users:
        prs_map.setdefault(user, {
            "opened": 0,
            "merged": 0
        })
    for repo in repos:
        repo = git_client.get_repo(repo)
        for user in users:
            issues = repo.get_issues(
                since=since_dt,
                state='all',
                creator=user,
                sort='created',
                direction='desc',
            )
            for issue in issues:
                if issue.pull_request:
                    if issue.state == "closed" and issue.closed_at is not None:
                        prs_map[user]["merged"] += 1
                    else:
                        prs_map[user]["opened"] += 1
    return prs_map

def get_comments(repos, users, since, git_client: Github):
    """
    Get the number of comments each user made.
    """
    print("Collecting Pull Request Comments stats...")
    comments_map = {}
    since_dt = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=since)
    for user in users:
        comments_map.setdefault(user, 0)
    for repo in repos:
        repo = git_client.get_repo(repo)
        comments = repo.get_pulls_review_comments(sort='created', direction='desc', since=since_dt)
        for comment in comments:
            if comment.user.login in users:
                comments_map[comment.user.login] += 1
    return comments_map


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    repos = get_repo(args.repos_list_path)
    users = get_users(args.users_path)
    git_client = Github(args.token)
    print("Getting stats for the following repositories: ", repos)
    print("Getting stats for the following users: ", users)
    pulls = get_pulls(repos, users, args.since, git_client)
    comments = get_comments(repos, users, args.since, git_client)
    with open(args.output_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["User", "Opened PRs", "Merged PRs", "Comments"])
        for user in users:
            writer.writerow([user, pulls[user]["opened"], pulls[user]["merged"], comments[user]])



