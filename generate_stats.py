import os
import sys
import math
import json
import requests

USERNAME = "Imtiaz-Ali17314"
TOKEN = os.getenv("GITHUB_TOKEN")

headers = {}
if TOKEN:
    headers["Authorization"] = f"token {TOKEN}"

def fetch_data():
    try:
        # Fetch user profile data
        user_url = f"https://api.github.com/users/{USERNAME}"
        user_res = requests.get(user_url, headers=headers, timeout=5)
        if user_res.status_code != 200:
            print(f"Error fetching user: {user_res.status_code}")
            return None
        user_data = user_res.json()

        # Fetch repositories (up to 100)
        repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
        repos_res = requests.get(repos_url, headers=headers, timeout=5)
        if repos_res.status_code != 200:
            print(f"Error fetching repos: {repos_res.status_code}")
            return None
        repos = repos_res.json()

        # Aggregate metrics
        total_stars = 0
        total_forks = 0
        languages = {}

        # Limit language API calls to top 8 active repos to prevent hitting rate limits locally
        active_repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:8]

        for repo in repos:
            if repo.get("fork"):
                continue
            total_stars += repo.get("stargazers_count", 0)
            total_forks += repo.get("forks_count", 0)

        for repo in active_repos:
            if repo.get("fork"):
                continue
            lang_url = repo.get("languages_url")
            if lang_url:
                try:
                    lang_res = requests.get(lang_url, headers=headers, timeout=3)
                    if lang_res.status_code == 200:
                        repo_langs = lang_res.json()
                        for lang, bytes_count in repo_langs.items():
                            languages[lang] = languages.get(lang, 0) + bytes_count
                except Exception as e:
                    print(f"Skipping language fetch for {repo.get('name')}: {e}")

        # Default languages fallback if empty
        if not languages:
            languages = {"JavaScript": 650000, "PHP": 420000, "Vue": 250000, "HTML": 90000}

        return {
            "name": user_data.get("name") or USERNAME,
            "followers": user_data.get("followers", 0),
            "public_repos": user_data.get("public_repos", 0),
            "stars": total_stars,
            "forks": total_forks,
            "languages": languages
        }
    except Exception as e:
        print(f"Exception during fetch: {e}")
        return None

def generate_svg(stats):
    if not stats:
        # Fallback stats in case of rate-limiting or errors
        stats = {
            "name": USERNAME,
            "followers": 18,
            "public_repos": 20,
            "stars": 15,
            "forks": 6,
            "languages": {"JavaScript": 650000, "PHP": 420000, "Vue": 250000, "HTML": 90000}
        }

    # Process languages
    sorted_langs = sorted(stats["languages"].items(), key=lambda x: x[1], reverse=True)
    total_bytes = sum(stats["languages"].values()) or 1
    
    top_langs = []
    colors = ["#00f2fe", "#7f00ff", "#ff007f", "#39ff14"] # Neon Cyan, Purple, Pink, Green
    
    for idx, (lang, bytes_count) in enumerate(sorted_langs[:4]):
        pct = (bytes_count / total_bytes) * 100
        top_langs.append({
            "name": lang,
            "bytes": bytes_count,
            "percentage": pct,
            "color": colors[idx % len(colors)]
        })

    # While we need at least 4 languages to render concentric rings, handle cases with fewer
    while len(top_langs) < 4:
        top_langs.append({
            "name": "N/A",
            "bytes": 0,
            "percentage": 0,
            "color": "#1f2d3d"
        })

    # Ring Circumferences (C = 2 * pi * r)
    r_vals = [60, 45, 30, 15]
    c_vals = [2 * math.pi * r for r in r_vals]
    
    ring_dasharrays = []
    for idx, lang in enumerate(top_langs):
        c = c_vals[idx]
        pct = lang["percentage"]
        fill_len = (pct / 100) * c
        empty_len = c - fill_len
        ring_dasharrays.append(f"{fill_len:.2f}, {empty_len:.2f}")

    # Generate custom SVG
    svg = f"""<svg viewBox="0 0 800 320" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Glow Filters -->
    <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <filter id="glow-purple" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- Pattern Background -->
    <pattern id="grid-stats" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1f2d3d" stroke-width="0.8" opacity="0.2" />
    </pattern>

    <!-- Linear Gradients -->
    <linearGradient id="grad-cyber" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00f2fe" />
      <stop offset="100%" stop-color="#7f00ff" />
    </linearGradient>
  </defs>

  <style>
    @keyframes spin-cw {{
      from {{ transform: rotate(0deg); }}
      to {{ transform: rotate(360deg); }}
    }}
    @keyframes spin-ccw {{
      from {{ transform: rotate(360deg); }}
      to {{ transform: rotate(0deg); }}
    }}
    @keyframes pulse-light {{
      0%, 100% {{ opacity: 0.4; }}
      50% {{ opacity: 1; }}
    }}
    @keyframes text-scramble {{
      0% {{ opacity: 0.7; }}
      50% {{ opacity: 1; }}
    }}

    .bg-main {{ fill: #0b0f19; }}
    .bg-grid {{ fill: url(#grid-stats); }}
    .rot-cw {{
      animation: spin-cw 15s linear infinite;
      transform-origin: 650px 160px;
    }}
    .rot-ccw {{
      animation: spin-ccw 10s linear infinite;
      transform-origin: 650px 160px;
    }}
    .pulse-status {{
      animation: pulse-light 2.5s ease-in-out infinite;
    }}
  </style>

  <!-- Backgrounds -->
  <rect width="100%" height="100%" class="bg-main" rx="10" />
  <rect width="100%" height="100%" class="bg-grid" rx="10" />

  <!-- Outer Cyber-HUD Borders -->
  <rect x="10" y="10" width="780" height="300" fill="none" stroke="#1f2d3d" stroke-width="1.5" rx="6" />
  <rect x="15" y="15" width="770" height="290" fill="none" stroke="#00f2fe" stroke-width="1" opacity="0.15" rx="4" />

  <!-- Corner Graphic Accents -->
  <path d="M 10 30 L 10 10 L 30 10" fill="none" stroke="#00f2fe" stroke-width="2.5" />
  <path d="M 790 30 L 790 10 L 770 10" fill="none" stroke="#00f2fe" stroke-width="2.5" />
  <path d="M 10 290 L 10 310 L 30 310" fill="none" stroke="#00f2fe" stroke-width="2.5" />
  <path d="M 790 290 L 790 310 L 770 310" fill="none" stroke="#00f2fe" stroke-width="2.5" />

  <!-- Panel Title -->
  <text x="35" y="42" fill="#00f2fe" font-family="'Fira Code', monospace" font-size="13" font-weight="bold" letter-spacing="1">📡 METRICS::GITHUB_TELEMETRY_CORE</text>
  <circle cx="20" cy="37" r="4" fill="#00f2fe" class="pulse-status" />

  <!-- Divider -->
  <line x1="435" y1="30" x2="435" y2="290" stroke="#1f2d3d" stroke-width="1.5" />

  <!-- ================= SECTION 1: SYSTEM METRICS (Left Console) ================= -->
  <g transform="translate(35, 70)">
    <!-- Metrics Terminal Display -->
    <rect width="365" height="215" fill="#090d16" stroke="#1f2d3d" stroke-width="1" rx="4" />
    <rect width="365" height="20" fill="#111827" stroke="#1f2d3d" stroke-width="1" rx="2" />
    <text x="15" y="14" fill="#8892b0" font-family="'Fira Code', monospace" font-size="9">> telemetry_uplink.sh</text>

    <!-- Terminal Readings -->
    <g font-family="'Fira Code', monospace" font-size="11" fill="#c9d1d9" transform="translate(20, 45)">
      <!-- Line 1: Profile Host -->
      <text x="0" y="0" fill="#8892b0">> HOST_NODE:</text>
      <text x="180" y="0" fill="#00f2fe" font-weight="bold">{stats["name"].upper()}</text>

      <!-- Line 2: Public Repos -->
      <text x="0" y="25" fill="#8892b0">> SYS_REPOSITORIES:</text>
      <text x="180" y="25" fill="#c9d1d9" font-weight="bold">{stats["public_repos"]} Active</text>

      <!-- Line 3: System Followers -->
      <text x="0" y="50" fill="#8892b0">> NEURAL_FOLLOWERS:</text>
      <text x="180" y="50" fill="#c9d1d9" font-weight="bold">{stats["followers"]} nodes</text>

      <!-- Line 4: System Stars -->
      <text x="0" y="75" fill="#8892b0">> CORE_STARS:</text>
      <text x="180" y="75" fill="#ff007f" font-weight="bold" filter="url(#glow-purple)">★ {stats["stars"]}</text>

      <!-- Line 5: System Forks -->
      <text x="0" y="100" fill="#8892b0">> ACTIVE_FORKS:</text>
      <text x="180" y="100" fill="#c9d1d9" font-weight="bold">⚙ {stats["forks"]}</text>

      <!-- Line 6: Decryption Key -->
      <text x="0" y="125" fill="#8892b0">> SHA256_HASH:</text>
      <text x="180" y="125" fill="#39ff14" font-size="10" class="pulse-status">0xFA7E90B1E2</text>

      <!-- Connection Status Beacon -->
      <g transform="translate(0, 145)">
        <rect width="325" height="20" fill="#111827" stroke="#00f2fe" stroke-width="0.8" rx="2" />
        <circle cx="15" cy="10" r="4.5" fill="#39ff14" class="pulse-status" />
        <text x="30" y="14" fill="#39ff14" font-size="9" font-weight="bold">GATEWAY_UPLINK::SECURE_AND_SYNCHRONIZED</text>
      </g>
    </g>
  </g>

  <!-- ================= SECTION 2: CONCENTRIC LANGUAGE CORE (Right) ================= -->
  
  <!-- concentric language rings -->
  <g class="rot-cw">
    <circle cx="650" cy="160" r="60" fill="none" stroke="#1f2d3d" stroke-width="4.5" />
    <circle cx="650" cy="160" r="60" fill="none" stroke="{top_langs[0]["color"]}" stroke-width="4.5" stroke-dasharray="{ring_dasharrays[0]}" stroke-linecap="round" />
  </g>
  <g class="rot-ccw">
    <circle cx="650" cy="160" r="45" fill="none" stroke="#1f2d3d" stroke-width="4.5" />
    <circle cx="650" cy="160" r="45" fill="none" stroke="{top_langs[1]["color"]}" stroke-width="4.5" stroke-dasharray="{ring_dasharrays[1]}" stroke-linecap="round" />
  </g>
  <g class="rot-cw">
    <circle cx="650" cy="160" r="30" fill="none" stroke="#1f2d3d" stroke-width="4.5" />
    <circle cx="650" cy="160" r="30" fill="none" stroke="{top_langs[2]["color"]}" stroke-width="4.5" stroke-dasharray="{ring_dasharrays[2]}" stroke-linecap="round" />
  </g>
  <g class="rot-ccw">
    <circle cx="650" cy="160" r="15" fill="none" stroke="#1f2d3d" stroke-width="4.5" />
    <circle cx="650" cy="160" r="15" fill="none" stroke="{top_langs[3]["color"]}" stroke-width="4.5" stroke-dasharray="{ring_dasharrays[3]}" stroke-linecap="round" />
  </g>

  <!-- Concentric core center -->
  <circle cx="650" cy="160" r="5" fill="#00f2fe" class="pulse-status" />

  <!-- Language Key Labels (Center) -->
  <g transform="translate(460, 75)" font-family="'Fira Code', monospace" font-size="10">
    <!-- Language 1 -->
    <g transform="translate(0, 0)">
      <rect width="10" height="10" fill="{top_langs[0]["color"]}" rx="2" />
      <text x="18" y="9" fill="#c9d1d9" font-weight="bold">{top_langs[0]["name"]}</text>
      <text x="110" y="9" fill="#8892b0">{top_langs[0]["percentage"]:.1f}%</text>
    </g>
    <!-- Language 2 -->
    <g transform="translate(0, 30)">
      <rect width="10" height="10" fill="{top_langs[1]["color"]}" rx="2" />
      <text x="18" y="9" fill="#c9d1d9" font-weight="bold">{top_langs[1]["name"]}</text>
      <text x="110" y="9" fill="#8892b0">{top_langs[1]["percentage"]:.1f}%</text>
    </g>
    <!-- Language 3 -->
    <g transform="translate(0, 60)">
      <rect width="10" height="10" fill="{top_langs[2]["color"]}" rx="2" />
      <text x="18" y="9" fill="#c9d1d9" font-weight="bold">{top_langs[2]["name"]}</text>
      <text x="110" y="9" fill="#8892b0">{top_langs[2]["percentage"]:.1f}%</text>
    </g>
    <!-- Language 4 -->
    <g transform="translate(0, 90)">
      <rect width="10" height="10" fill="{top_langs[3]["color"]}" rx="2" />
      <text x="18" y="9" fill="#c9d1d9" font-weight="bold">{top_langs[3]["name"]}</text>
      <text x="110" y="9" fill="#8892b0">{top_langs[3]["percentage"]:.1f}%</text>
    </g>

    <!-- Sum of All Runtimes -->
    <g transform="translate(0, 125)">
      <line x1="0" y1="0" x2="150" y2="0" stroke="#1f2d3d" stroke-width="1" />
      <text x="0" y="15" fill="#8892b0">TOTAL_CODE_MASS:</text>
      <text x="0" y="30" fill="#00f2fe" font-weight="bold" font-size="11">{(total_bytes / 1024 / 1024):.2f} MB OF DATA</text>
    </g>
  </g>

</svg>
"""
    return svg

def main():
    print("Fetching active GitHub telemetry data...")
    stats = fetch_data()
    
    print("Generating animated SVG stats schematic...")
    svg_content = generate_svg(stats)
    
    output_path = "github_stats.svg"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"Success! Telemetry statistics updated and saved to {output_path}")

if __name__ == "__main__":
    main()
