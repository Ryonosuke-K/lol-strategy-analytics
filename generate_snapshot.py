import json
import os
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("RIOT_API_KEY")
REGION = "jp1"
ROUTING = "asia"
QUEUE = "RANKED_SOLO_5x5"

BASE_REGION = f"https://{REGION}.api.riotgames.com"
BASE_ROUTE = f"https://{ROUTING}.api.riotgames.com"
HEADERS = {"X-Riot-Token": API_KEY} if API_KEY else {}


def safe_get(url, max_retries=5):
    if not API_KEY:
        raise RuntimeError("RIOT_API_KEY is not set.")

    for _ in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
        except requests.RequestException:
            time.sleep(2)
            continue

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "2"))
            time.sleep(max(retry_after, 1))
            continue

        if response.status_code in {500, 502, 503, 504}:
            time.sleep(2)
            continue

        raise RuntimeError(f"Request failed: {response.status_code} {url}")

    raise RuntimeError(f"Request exceeded retries: {url}")


def win_rate(wins, total):
    if total == 0:
        return None
    return round((wins / total) * 100.0, 2)


def collect_snapshot(target_players=12, matches_per_player=3):
    league_url = f"{BASE_REGION}/lol/league/v4/challengerleagues/by-queue/{QUEUE}"
    league_data = safe_get(league_url)

    entries = sorted(
        league_data.get("entries", []),
        key=lambda x: x.get("leaguePoints", 0),
        reverse=True,
    )
    selected = entries[:target_players]
    player_puuids = {p["puuid"] for p in selected if p.get("puuid")}

    match_ids = []
    for puuid in player_puuids:
        ids_url = (
            f"{BASE_ROUTE}/lol/match/v5/matches/by-puuid/{puuid}/ids"
            f"?start=0&count={matches_per_player}"
        )
        ids = safe_get(ids_url)
        match_ids.extend(ids)

    unique_match_ids = list(dict.fromkeys(match_ids))

    team_3grub_1dragon = {"wins": 0, "total": 0}
    team_2dragon_1grub = {"wins": 0, "total": 0}
    climber_metrics = {
        "matches": 0,
        "vision_score_sum": 0,
        "control_wards_sum": 0,
        "deaths_sum": 0,
        "wins": 0,
    }

    for match_id in unique_match_ids:
        match_url = f"{BASE_ROUTE}/lol/match/v5/matches/{match_id}"
        match = safe_get(match_url)
        info = match.get("info", {})

        for team in info.get("teams", []):
            dragons = team.get("objectives", {}).get("dragon", {}).get("kills", 0)
            grubs = team.get("objectives", {}).get("horde", {}).get("kills", 0)
            team_win = bool(team.get("win", False))

            if grubs >= 3 and dragons <= 1:
                team_3grub_1dragon["total"] += 1
                if team_win:
                    team_3grub_1dragon["wins"] += 1

            if dragons >= 2 and grubs <= 1:
                team_2dragon_1grub["total"] += 1
                if team_win:
                    team_2dragon_1grub["wins"] += 1

        for p in info.get("participants", []):
            if p.get("puuid") not in player_puuids:
                continue

            climber_metrics["matches"] += 1
            climber_metrics["vision_score_sum"] += p.get("visionScore", 0)
            climber_metrics["control_wards_sum"] += p.get(
                "visionWardsBoughtInGame", 0
            )
            climber_metrics["deaths_sum"] += p.get("deaths", 0)
            if p.get("win"):
                climber_metrics["wins"] += 1

    m = climber_metrics["matches"]
    snapshot = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "region": REGION,
        "routing": ROUTING,
        "generation_config": {
            "queue": QUEUE,
            "target_players": target_players,
            "matches_per_player": matches_per_player,
        },
        "sample": {
            "challenger_players": len(player_puuids),
            "matches_analyzed": len(unique_match_ids),
            "player_match_rows": m,
        },
        "match_id_preview": unique_match_ids[:15],
        "objective_value": {
            "three_grubs_one_or_less_dragon": {
                "wins": team_3grub_1dragon["wins"],
                "total": team_3grub_1dragon["total"],
                "win_rate_percent": win_rate(
                    team_3grub_1dragon["wins"], team_3grub_1dragon["total"]
                ),
            },
            "two_or_more_dragons_one_or_less_grub": {
                "wins": team_2dragon_1grub["wins"],
                "total": team_2dragon_1grub["total"],
                "win_rate_percent": win_rate(
                    team_2dragon_1grub["wins"], team_2dragon_1grub["total"]
                ),
            },
        },
        "climber_traits": {
            "win_rate_percent": win_rate(climber_metrics["wins"], m),
            "avg_vision_score": round(climber_metrics["vision_score_sum"] / m, 2)
            if m
            else None,
            "avg_control_wards_bought": round(climber_metrics["control_wards_sum"] / m, 2)
            if m
            else None,
            "avg_deaths": round(climber_metrics["deaths_sum"] / m, 2) if m else None,
        },
    }
    return snapshot


def to_markdown(snapshot):
    a = snapshot["objective_value"]["three_grubs_one_or_less_dragon"]
    b = snapshot["objective_value"]["two_or_more_dragons_one_or_less_grub"]
    c = snapshot["climber_traits"]
    s = snapshot["sample"]

    return (
        "# Live API Snapshot\n\n"
        f"- Generated at (UTC): {snapshot['generated_at_utc']}\n"
        f"- Region: {snapshot['region']} / Routing: {snapshot['routing']}\n"
        f"- Challenger players sampled: {s['challenger_players']}\n"
        f"- Matches analyzed: {s['matches_analyzed']}\n"
        f"- Player-match rows: {s['player_match_rows']}\n\n"
        "## Objective Value (Team-level)\n\n"
        "| Segment | Wins | Total | Win Rate |\n"
        "|---|---:|---:|---:|\n"
        f"| 3+ Grubs and <=1 Dragon | {a['wins']} | {a['total']} | {a['win_rate_percent']}% |\n"
        f"| >=2 Dragons and <=1 Grub | {b['wins']} | {b['total']} | {b['win_rate_percent']}% |\n\n"
        "## High-ELO Climber Traits (Sample)\n\n"
        f"- Win rate: {c['win_rate_percent']}%\n"
        f"- Avg vision score: {c['avg_vision_score']}\n"
        f"- Avg control wards bought: {c['avg_control_wards_bought']}\n"
        f"- Avg deaths: {c['avg_deaths']}\n"
    )


def main():
    snapshot = collect_snapshot()

    os.makedirs("docs/data", exist_ok=True)
    json_path = os.path.join("docs", "data", "live-snapshot.json")
    root_json_path = os.path.join("docs", "live-snapshot.json")
    md_path = os.path.join("docs", "data", "live-snapshot.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    with open(root_json_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(to_markdown(snapshot))

    print(f"Wrote {json_path}")
    print(f"Wrote {root_json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
