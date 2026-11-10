import json
import os
import urllib.parse
import urllib.request
import xml.sax.saxutils
from datetime import datetime, timedelta, timezone

OWNER = os.environ.get("OWNER", "Phillipe17Macedo")
TOKEN = os.environ["GH_TOKEN"]
COLORS = {"TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3776ab", "Java": "#b07219", "CSS": "#563d7c", "HTML": "#e34c26", "PHP": "#4f5d95", "C++": "#f34b21", "Kotlin": "#a97bff", "Blade": "#f7523f"}

def api(path):
    request = urllib.request.Request("https://api.github.com" + path, headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request) as response:
        return json.load(response)

def search_total(query):
    return api("/search/issues?" + urllib.parse.urlencode({"q": query}))["total_count"]

def esc(value):
    return xml.sax.saxutils.escape(str(value))

profile = api(f"/users/{OWNER}")
repos = api(f"/users/{OWNER}/repos?per_page=100&sort=updated")
languages = {}
stars = sum(repo["stargazers_count"] for repo in repos)
for repo in repos:
    for language, amount in api(f"/repos/{OWNER}/{repo['name']}/languages").items():
        languages[language] = languages.get(language, 0) + amount
languages = sorted(languages.items(), key=lambda item: item[1], reverse=True)[:8]
language_total = sum(amount for _, amount in languages)
cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).date().isoformat()
commits = api(f"/search/commits?q={urllib.parse.quote(f'author:{OWNER} committer-date:{cutoff}..{datetime.now(timezone.utc).date().isoformat()}')}")["total_count"]
prs = search_total(f"author:{OWNER} is:pr")
issues = search_total(f"author:{OWNER} is:issue")
rows = []
for index, (language, amount) in enumerate(languages[:8]):
    column = 0 if index < 4 else 1
    row = index if index < 4 else index - 4
    x = 533 + column * 139
    y = 111 + row * 26
    percent = amount / language_total * 100
    rows.append(f'<circle cx="{x}" cy="{y-4}" r="5" fill="{COLORS.get(language, "#8be9fd")}"/><text x="{x+11}" y="{y}">{esc(language)} {percent:.2f}%</text>')
segments = []
offset = 528
for language, amount in languages[:5]:
    width = 238 * amount / language_total
    segments.append(f'<rect x="{offset:.2f}" y="78" width="{width:.2f}" height="8" fill="{COLORS.get(language, "#8be9fd")}"/>')
    offset += width
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="220" viewBox="0 0 800 220" role="img"><title>{esc(OWNER)} GitHub Stats</title><rect width="800" height="220" fill="#0d1117"/><rect x="18" y="20" width="479" height="198" rx="6" fill="#0d1117" stroke="#c9d1d9"/><rect x="512" y="20" width="270" height="198" rx="6" fill="#0d1117" stroke="#c9d1d9"/><text x="44" y="57" fill="#00b8e6" font-family="Arial,sans-serif" font-size="19" font-weight="700">{esc(OWNER)}'s GitHub Stats</text><g fill="#f0f6fc" font-family="Arial,sans-serif" font-size="14" font-weight="700"><text x="69" y="90">☆</text><text x="91" y="90">Total Stars Earned:</text><text x="268" y="90">{stars}</text><text x="68" y="116">↻</text><text x="91" y="116">Total Commits (last year):</text><text x="268" y="116">{commits}</text><text x="69" y="142">♧</text><text x="91" y="142">Total PRs:</text><text x="268" y="142">{prs}</text><text x="69" y="168">ⓘ</text><text x="91" y="168">Total Issues:</text><text x="268" y="168">{issues}</text><text x="69" y="194">▣</text><text x="91" y="194">Contributed to (last year):</text><text x="268" y="194">{profile["public_repos"]}</text></g><circle cx="411" cy="132" r="41" fill="none" stroke="#164e63" stroke-width="7"/><circle cx="411" cy="132" r="41" fill="none" stroke="#00a8d6" stroke-width="7" stroke-dasharray="190 258" stroke-linecap="round" transform="rotate(-90 411 132)"/><text x="392" y="140" fill="#f0f6fc" font-family="Arial,sans-serif" font-size="25" font-weight="700">B+</text><text x="528" y="57" fill="#00b8e6" font-family="Arial,sans-serif" font-size="19" font-weight="700">Most Used Languages</text>{''.join(segments)}<g font-family="Arial,sans-serif" font-size="11" fill="#f0f6fc">{''.join(rows)}</g></svg>'''
open("stats.svg", "w", encoding="utf-8").write(svg)
