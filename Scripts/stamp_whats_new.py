#!/usr/bin/env python3
"""
stamp_whats_new.py
Automates stamping of release notes and What's New items on every InkSync Pro build.
Executed during GitHub Actions CI workflow prior to xcodegen project generation.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""

def main():
    build_number = os.environ.get("BUILD_NUMBER") or (sys.argv[1] if len(sys.argv) > 1 else "")
    short_sha = os.environ.get("SHORT_SHA") or (sys.argv[2] if len(sys.argv) > 2 else "")
    
    if not build_number:
        build_number = run_cmd(["git", "rev-list", "--count", "HEAD"]) or "Dev"
    if not short_sha:
        short_sha = run_cmd(["git", "rev-parse", "--short", "HEAD"]) or "local"
        
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    target_json = os.path.join(repo_root, "ComicToPDF", "ComicToPDF", "Resources", "WhatsNew.json")
    os.makedirs(os.path.dirname(target_json), exist_ok=True)
    
    # Load existing releases if available
    releases = []
    if os.path.exists(target_json):
        try:
            with open(target_json, "r", encoding="utf-8") as f:
                releases = json.load(f)
        except Exception as e:
            print(f"Warning: could not parse existing WhatsNew.json: {e}")
            releases = []
            
    # Check if this build number already exists
    existing_idx = None
    for i, r in enumerate(releases):
        if str(r.get("buildNumber")) == str(build_number) or (short_sha != "local" and r.get("commitSHA") == short_sha):
            existing_idx = i
            break
            
    # Extract recent commit information
    latest_subject = run_cmd(["git", "log", "-1", "--pretty=%s"]) or "Continuous Performance & Feature Updates"
    raw_log = run_cmd(["git", "log", "-5", "--pretty=%s%n%b%n---COMMIT---"])
    
    # Check for dedicated WHATS_NEW.md
    whats_new_md = os.path.join(repo_root, "WHATS_NEW.md")
    custom_title = ""
    custom_subtitle = ""
    custom_features = []
    
    if os.path.exists(whats_new_md):
        try:
            with open(whats_new_md, "r", encoding="utf-8") as f:
                content = f.read().strip()
            lines = content.splitlines()
            for line in lines:
                line = line.strip()
                if line.startswith("# "):
                    custom_title = line[2:].strip()
                elif line.startswith("## ") and not custom_subtitle:
                    custom_subtitle = line[3:].strip()
                elif line.startswith("- ") or line.startswith("* "):
                    bullet = line[2:].strip()
                    if ":" in bullet:
                        t, d = bullet.split(":", 1)
                        clean_t = t.strip().replace("**", "").replace("*", "")
                        clean_d = d.strip().replace("**", "").replace("*", "")
                        custom_features.append({
                            "icon": "sparkles",
                            "colorHex": "orange",
                            "title": clean_t,
                            "description": clean_d,
                            "category": "Update"
                        })
                    else:
                        clean_b = bullet.replace("**", "").replace("*", "")
                        custom_features.append({
                            "icon": "checkmark.circle.fill",
                            "colorHex": "green",
                            "title": clean_b[:30],
                            "description": clean_b,
                            "category": "Update"
                        })
        except Exception as e:
            print(f"Warning: could not parse WHATS_NEW.md: {e}")

    now_month_year = datetime.now().strftime("%B %Y")
    
    if custom_features:
        new_release = {
            "buildNumber": str(build_number),
            "commitSHA": str(short_sha),
            "version": "1.0.1",
            "releaseDate": now_month_year,
            "title": custom_title or f"Build {build_number} Updates",
            "subtitle": custom_subtitle or latest_subject,
            "features": custom_features
        }
    else:
        # Generate features from git history
        features = []
        commit_entries = [c.strip() for c in raw_log.split("---COMMIT---") if c.strip()]
        
        seen_titles = set()
        for entry in commit_entries:
            lines = [l.strip() for l in entry.splitlines() if l.strip()]
            if not lines:
                continue
            subj = lines[0]
            desc = " ".join(lines[1:]) if len(lines) > 1 else subj
            
            # Categorize icon and color
            cat = "Update"
            icon = "sparkles"
            color = "orange"
            
            lower_subj = subj.lower()
            if "fix" in lower_subj:
                cat = "Fix"
                icon = "wrench.and.screwdriver"
                color = "blue"
            elif "feat" in lower_subj or "add" in lower_subj:
                cat = "Feature"
                icon = "star.fill"
                color = "orange"
            elif "reader" in lower_subj or "pdf" in lower_subj or "epub" in lower_subj:
                cat = "Reader"
                icon = "book.fill"
                color = "cyan"
            elif "note" in lower_subj or "study" in lower_subj or "cornell" in lower_subj:
                cat = "Study"
                icon = "text.book.closed.fill"
                color = "purple"
            elif "perf" in lower_subj or "speed" in lower_subj:
                cat = "Performance"
                icon = "bolt.fill"
                color = "green"
                
            clean_title = subj.replace("feat:", "").replace("fix:", "").replace("perf:", "").strip()
            clean_title = clean_title[0].upper() + clean_title[1:] if clean_title else "System Update"
            
            if clean_title not in seen_titles:
                seen_titles.add(clean_title)
                features.append({
                    "icon": icon,
                    "colorHex": color,
                    "title": clean_title[:45],
                    "description": desc[:160],
                    "category": cat
                })
                
        if not features:
            features = [
                {
                    "icon": "sparkles",
                    "colorHex": "orange",
                    "title": "Continuous Refinement",
                    "description": latest_subject,
                    "category": "System"
                }
            ]
            
        new_release = {
            "buildNumber": str(build_number),
            "commitSHA": str(short_sha),
            "version": "1.0.1",
            "releaseDate": now_month_year,
            "title": f"Build {build_number} Updates",
            "subtitle": latest_subject,
            "features": features[:6] # Top 6 features max
        }
        
    if existing_idx is not None:
        releases[existing_idx] = new_release
    else:
        releases.insert(0, new_release)
        
    with open(target_json, "w", encoding="utf-8") as f:
        json.dump(releases, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully stamped WhatsNew.json for Build {build_number} ({short_sha})")
    
    # Also write latest_release_notes.md for GitHub release description
    notes_file = os.path.join(repo_root, "latest_release_notes.md")
    with open(notes_file, "w", encoding="utf-8") as f:
        f.write(f"### What's New in Build {build_number} ({short_sha})\n\n")
        f.write(f"**{new_release['title']}**\n\n")
        if new_release.get('subtitle'):
            f.write(f"*{new_release['subtitle']}*\n\n")
        for feat in new_release['features']:
            f.write(f"- **[{feat['category']}] {feat['title']}**: {feat['description']}\n")
    print(f"Wrote latest_release_notes.md")

if __name__ == "__main__":
    main()
