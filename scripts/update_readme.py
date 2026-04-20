import os
import re
import requests
from datetime import datetime

USERNAME = "MuhammadAliRaza-DevSecOps"
README_FILE = "README.md"
TOKEN = os.getenv("PROFILE_GH_TOKEN") or os.getenv("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

def get(url):
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()

def format_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d %b %Y")
    except Exception:
        return date_str

def fetch_repos():
    repos = get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated")
    repos = [r for r in repos if not r.get("fork")]
    repos.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return repos

def fetch_events():
    return get(f"https://api.github.com/users/{USERNAME}/events/public?per_page=100")

def fetch_starred():
    return get(f"https://api.github.com/users/{USERNAME}/starred?per_page=20")

def build_recent_repos_section(repos):
    if not repos:
        return "- No repositories found."
    lines = []
    for repo in repos[:6]:
        lines.append(
            f"- 📦 **[{repo['name']}]({repo['html_url']})**  \n"
            f"  🔹 {repo.get('description') or 'No description added yet.'}  \n"
            f"  🔹 Language: `{repo.get('language') or 'Not specified'}` | Updated: `{format_date(repo.get('updated_at', ''))}`"
        )
    return "\n\n".join(lines)

def build_latest_commits_section(events):
    lines = []
    commit_events = [e for e in events if e.get("type") == "PushEvent"]
    for event in commit_events[:5]:
        repo = event["repo"]["name"]
        created = format_date(event["created_at"])
        commits = event.get("payload", {}).get("commits", [])
        if commits:
            first = commits[0].get("message", "Commit updated")
            lines.append(
                f"- 📝 **{repo}**  \n"
                f"  🔹 Latest commit: `{first[:90]}`  \n"
                f"  🔹 Date: `{created}`"
            )
    return "\n\n".join(lines) if lines else "- No recent commit activity found."

def build_starred_section(starred):
    if not starred:
        return "- No recently starred repositories found."
    lines = []
    for repo in starred[:5]:
        lines.append(
            f"- ⭐ **[{repo['full_name']}]({repo['html_url']})**  \n"
            f"  🔹 {repo.get('description') or 'No description available.'}"
        )
    return "\n\n".join(lines)

def build_repo_insights_section(repos):
    total = len(repos)
    latest = repos[0]["name"] if repos else "No repositories"
    most_starred = max(repos, key=lambda x: x.get("stargazers_count", 0))["name"] if repos else "No repositories"

    langs = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            langs[lang] = langs.get(lang, 0) + 1
    sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:5]
    lang_text = ", ".join([f"`{lang}` ({count})" for lang, count in sorted_langs]) if sorted_langs else "No languages found"

    return (
        f"- 📦 Total Public Repositories: **{total}**\n"
        f"- 🆕 Recently Updated Repository: **{latest}**\n"
        f"- ⭐ Most Starred Repository: **{most_starred}**\n"
        f"- 🧠 Main Languages Used: {lang_text}"
    )

def build_blog_posts_section():
    return "- ✍️ Blog posts coming soon.\n- 📰 Project write-ups and learning notes will be added here."

def replace_section(content, start_marker, end_marker, new_content):
    pattern = re.compile(
        rf"({re.escape(start_marker)})(.*)({re.escape(end_marker)})",
        re.DOTALL
    )
    replacement = rf"\1\n{new_content}\n\3"
    return pattern.sub(replacement, content)

def main():
    repos = fetch_repos()
    events = fetch_events()
    starred = fetch_starred()

    recent_repos = build_recent_repos_section(repos)
    latest_commits = build_latest_commits_section(events)
    starred_repos = build_starred_section(starred)
    repo_insights = build_repo_insights_section(repos)
    blog_posts = build_blog_posts_section()

    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_section(content, "<!-- START_RECENT_REPOS -->", "<!-- END_RECENT_REPOS -->", recent_repos)
    content = replace_section(content, "<!-- START_LATEST_COMMITS -->", "<!-- END_LATEST_COMMITS -->", latest_commits)
    content = replace_section(content, "<!-- START_STARRED_REPOS -->", "<!-- END_STARRED_REPOS -->", starred_repos)
    content = replace_section(content, "<!-- START_REPO_INSIGHTS -->", "<!-- END_REPO_INSIGHTS -->", repo_insights)
    content = replace_section(content, "<!-- START_BLOG_POSTS -->", "<!-- END_BLOG_POSTS -->", blog_posts)

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
