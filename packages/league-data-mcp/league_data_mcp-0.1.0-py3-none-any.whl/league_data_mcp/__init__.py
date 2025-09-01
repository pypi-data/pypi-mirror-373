#!/usr/bin/env python3

import os
from mcp.server.fastmcp import FastMCP
from .utility import Riot_client
from typing import Optional, List
#from dotenv import load_dotenv

#load_dotenv()

# 初始化Fast MCP服务器
mcp = FastMCP("League of Legends MCP Server")

# 初始化Riot API客户端
API = os.getenv("API")
if not API:
    raise ValueError("API environment variable is required")
client = Riot_client(API)

@mcp.tool()
def get_puuid(players: List[dict]):
    """
    Get player's PUUID by their gamename and tagline (supports batch query)
    
    Args:
        players (List[dict]): List of player dicts with 'game_name' and 'tag_line' keys
                e.g., [{"game_name": "Faker", "tag_line": "KR1"}, {"game_name": "Untargetable", "tag_line": "666"}]
        
    Returns:
        List of PUUIDs or None values for failed requests
    """
    return client.get_puuid(players)

@mcp.tool()
def get_match_list(puuid: str, type: Optional[str] = None, count: Optional[str] = None):
    """
    Get a list of match for a player by their PUUID
    
    Args:
        puuid (str): Player's PUUID
        type (str): Optional match type filter (normal, ranked, etc.)
        count (str): Optional number of matches to return
        
    Returns:
        List of match IDs or None if failed
    """
    return client.get_match_list(puuid, match_type=type, count=count)

@mcp.tool()
def get_match_detail(matchId: str):
    """
    Get single match detailed data by match ID
    
    Args:
        matchId (str): Match ID (e.g., NA1_5354690210)
        
    Returns:
        A single match detailed data or None if failed
    """
    return client.get_match(matchId)

@mcp.tool()
def get_match_summary(match_ids: List[str], game_name: str):
    """
    Get match summaries for multiple matches (max 10 matches)
    Returns truncated match data (first 32 lines of JSON) + context around the specified game_name
    
    Args:
        match_ids (List[str]): List of match IDs (e.g., ["NA1_5354690210", "NA1_5354690211"])
        game_name (str): Player's game name to search for additional context
        
    Returns:
        List of truncated match data with game_name context or None values for failed requests
    """
    return client.get_match_summary(match_ids, game_name)

def main() -> None:
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
