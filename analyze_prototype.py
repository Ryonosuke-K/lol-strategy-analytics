import os
import time
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==========================================
# CONFIGURATION & SECURITY
# ==========================================

API_KEY = os.environ.get("RIOT_API_KEY")

# Region Settings
REGION = "jp1"
ROUTING = "asia"

BASE_URL_REGION = f"https://{REGION}.api.riotgames.com"
BASE_URL_ROUTE = f"https://{ROUTING}.api.riotgames.com"

# ==========================================
# UTILITY: RATE LIMIT HANDLER
# ==========================================

def safe_request(url):
    if not API_KEY:
        print("[Error] RIOT_API_KEY environment variable is not set.")
        return None

    headers = {"X-Riot-Token": API_KEY}

    while True:
        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 10))
                print(f"[Limit] Rate limit hit. Sleeping for {retry_after} seconds...")
                time.sleep(retry_after)
                continue 
            else:
                print(f"[Error] Status: {response.status_code} | URL: {url}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"[Network Error] {e}. Retrying in 5 seconds...")
            time.sleep(5)

# ==========================================
# CORE LOGIC: DATA PIPELINE PROTOTYPE
# ==========================================

def run_analysis_pipeline():
    print("--- Starting LoL Analysis Pipeline Prototype ---")
    
    # ---------------------------------------------------------
    # STEP 1: Fetch High-ELO Players & Extract PUUID directly
    # ---------------------------------------------------------
    print("\n[Step 1] Fetching Challenger League data...")
    url_challenger = f"{BASE_URL_REGION}/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
    league_data = safe_request(url_challenger)
    
    if not league_data: return

    # Sort by LP
    top_players = sorted(league_data['entries'], key=lambda x: x['leaguePoints'], reverse=True)
    
    # ターゲット選定（1位のプレイヤー）
    target_player = top_players[0]

    # ★修正: summonerIdを経由せず、直接 'puuid' を取得します
    if 'puuid' not in target_player:
        print("[Error] Unexpected API response: 'puuid' key is missing.")
        print(f"Debug Keys: {target_player.keys()}")
        return

    puuid = target_player['puuid']
    lp = target_player['leaguePoints']
    
    # 名前はAPIから消えたため、ログにはPUUIDの一部を表示します
    print(f"-> Target Found (1st Place): {lp} LP")
    print(f"-> PUUID Extracted directly: {puuid}")

    # (Step 2 was 'Resolve Name to PUUID', which is now skipped!)

    # ---------------------------------------------------------
    # STEP 3: Fetch Recent Match IDs
    # ---------------------------------------------------------
    print("\n[Step 2] Fetching recent Match IDs using PUUID...")
    # Get last 5 matches
    url_matches = f"{BASE_URL_ROUTE}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=5"
    match_ids = safe_request(url_matches)
    
    if not match_ids: 
        print("No match IDs found (Player might be inactive recently).")
        return
    print(f"-> Retrieved {len(match_ids)} matches.")

    # ---------------------------------------------------------
    # STEP 4: Analyze a Single Match
    # ---------------------------------------------------------
    target_match_id = match_ids[0]
    print(f"\n[Step 3] Deep Analysis of Match: {target_match_id}")
    url_match_detail = f"{BASE_URL_ROUTE}/lol/match/v5/matches/{target_match_id}"
    match_detail = safe_request(url_match_detail)

    if not match_detail: return

    info = match_detail['info']
    
    # --- DEMONSTRATION FOR ANALYSIS 1: OBJECTIVE VALUE ---
    print("\n  [Analysis 1: Objectives (Dragon vs Grubs)]")
    for team in info['teams']:
        team_id = "Blue" if team['teamId'] == 100 else "Red"
        dragons = team['objectives']['dragon']['kills']
        horde = team['objectives']['horde']['kills'] # 'horde' = Void Grubs
        win_status = "WIN" if team['win'] else "LOSS"
        print(f"   - {team_id} Team: Dragons={dragons}, Grubs={horde} -> {win_status}")

    # --- DEMONSTRATION FOR ANALYSIS 3: PREDICTION (DRAFT) ---
    print("\n  [Analysis 3: Win Prediction (Draft Data)]")
    print("   -> Extracting pre-game features (Example):")
    # Show first 2 players
    for p in info['participants'][:2]: 
        print(f"   - Champion: {p['championName']} (ID: {p['championId']}) | Role: {p['teamPosition']}")

    # --- DEMONSTRATION FOR ANALYSIS 2: CLIMBER TRAITS ---
    print("\n  [Analysis 2: Climber Traits (Behavior)]")
    try:
        # 自分のPUUIDと一致する参加者を探す
        target_participant = [p for p in info['participants'] if p['puuid'] == puuid][0]
        print(f"   - Target Player Stats for this game:")
        print(f"     Vision Score: {target_participant['visionScore']}")
        print(f"     Control Wards Bought: {target_participant['visionWardsBoughtInGame']}")
        print(f"     Deaths: {target_participant['deaths']}")
    except IndexError:
        print("   - Target player not found in this match (Arena mode or data mismatch).")

    print("\n--- Pipeline Prototype Finished Successfully ---")
    print("Ready for deployment to Cloud Server with Production Key.")

if __name__ == "__main__":
    if not API_KEY:
        print("FATAL ERROR: Please set 'RIOT_API_KEY' environment variable.")
    else:
        run_analysis_pipeline()