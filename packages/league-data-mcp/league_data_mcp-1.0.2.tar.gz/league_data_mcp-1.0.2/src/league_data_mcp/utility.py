import json
import requests
from typing import Optional, Dict, Any, List

class Riot_client:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": api_token
        }

    def get_puuid(self, players: List[Dict[str, str]]) -> List[Optional[str]]:
        """
        Get PUUIDs for players
        Args:
            players: List of dicts with 'game_name' and 'tag_line' keys
                    e.g., [{"game_name": "Faker", "tag_line": "KR1"}, {"game_name": "Untargetable", "tag_line": "666"}]
        Returns: List of PUUIDs (None for failed requests)
        """
        results = []
        for player in players:
            game_name = player.get("game_name")
            tag_line = player.get("tag_line")
            
            if not game_name or not tag_line:
                results.append(None)
                continue
                
            url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
            
            try:
                response = requests.get(url, headers=self.base_headers)
                
                if response.status_code == 200:
                    data = response.json()
                    results.append(data.get("puuid"))
                else:
                    print(f"API Error {response.status_code}: {response.text}")
                    results.append(None)
                    
            except Exception as e:
                print(f"Request failed: {e}")
                results.append(None)
                
        return results

    def get_match_list(self, puuid: str, match_type: Optional[str] = None, count: Optional[str] = None) -> Optional[List[str]]:
        url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        
        params = {}
        if match_type:
            params["type"] = match_type
        if count:
            params["count"] = int(count) if isinstance(count, str) else count
        params["start"] = 0
        
        try:
            response = requests.get(url, headers=self.base_headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
        
        try:
            response = requests.get(url, headers=self.base_headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def get_match_summary(self, match_ids: List[str], game_name: str) -> Optional[List[Dict[str, Any]]]:
        if len(match_ids) > 10:
            match_ids = match_ids[:10]
            
        results = []
        for match_id in match_ids:
            data = self.get_match(match_id)
            
            if data is None:
                results.append(None)
                continue
                
            json_str = json.dumps(data, indent=2)
            lines = json_str.split('\n')
            
            # Get first 32 lines
            truncated_lines = lines[:32]
            
            # Search for game_name and collect context separately
            game_name_context = []
            for i, line in enumerate(lines):
                if game_name.lower() in line.lower():
                    # Get ±100 lines around the game_name
                    start_idx = max(0, i - 150)
                    end_idx = min(len(lines), i + 150)
                    game_name_context = lines[start_idx:end_idx]
                    break
            
            truncated_json_str = '\n'.join(truncated_lines)
            
            try:
                # Try to parse the first 32 lines as JSON
                truncated_data = json.loads(truncated_json_str + '\n}' if not truncated_json_str.endswith('}') else truncated_json_str)
                # Add game_name context as a separate field
                if game_name_context:
                    truncated_data["game_name_context"] = game_name_context
                results.append(truncated_data)
            except json.JSONDecodeError:
                truncated_data = {
                    "metadata": data.get("metadata", {}),
                    "info": {
                        "gameCreation": data.get("info", {}).get("gameCreation"),
                        "gameDuration": data.get("info", {}).get("gameDuration"),
                        "gameId": data.get("info", {}).get("gameId"),
                        "gameMode": data.get("info", {}).get("gameMode"),
                    }
                }
                truncated_data["game_name"] = f"{game_name}"
                if game_name_context:
                    truncated_data["game_name_context"] = game_name_context
                results.append(truncated_data)
                
        return results