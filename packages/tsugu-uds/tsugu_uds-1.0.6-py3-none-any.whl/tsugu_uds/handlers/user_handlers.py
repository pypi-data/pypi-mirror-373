"""User-related request handlers."""

import json
import random
import string
import httpx
from typing import Dict, Any, Optional

from ..database import DatabaseManager, verify_code_cache


class Config:
    def __init__(self):
        self._i_s = {0: "jp", 1: "en", 2: "tw", 3: "cn", 4: "kr"}
        self._s_i = {"jp": 0, "en": 1, "tw": 2, "cn": 3, "kr": 4}
        self.proxy = ''


config = Config()


def server_id_2_server_name(index: int) -> Optional[str]:
    """Convert server ID to server name."""
    return config._i_s.get(index)


def get_bestdori_player(player_id: str, server: int, proxy: str = "") -> Optional[Dict[str, Any]]:
    """Get player information from Bestdori API."""
    # 获取服务器名
    server_s_name = server_id_2_server_name(server)
    if not server_s_name:
        return None
    
    # 构建 URL
    url = f'https://bestdori.com/api/player/{server_s_name}/{player_id}?mode=2'
    
    try:
        # 设置代理
        proxy_url = None
        if proxy:
            proxy_url = proxy
        
        http = httpx.Client(proxy=proxy_url)
        
        # 发送请求
        response = http.get(url, timeout=120)
        
        # 检查响应的状态码是否为 200
        if response.status_code == 200:
            # 解析 JSON 响应数据
            data = response.json()
            return data
        else:
            return None
    except Exception:
        return None


def get_user_data_handler(db_manager: DatabaseManager, platform: str, user_id: str) -> Dict[str, Any]:
    """Handle get user data request."""
    try:
        user_data = db_manager.get_user_data(platform, user_id)
        
        if not user_data:
            # Create new user with defaults
            user_data = db_manager.create_user(platform, user_id)
        
        # Format response to match original API
        response_data = {
            "userId": user_data["userId"],
            "platform": user_data["platform"],
            "mainServer": user_data["mainServer"],
            "displayedServerList": user_data["displayedServerList"],
            "shareRoomNumber": user_data["shareRoomNumber"],
            "userPlayerIndex": user_data["userPlayerIndex"],
            "userPlayerList": user_data["userPlayerList"],
        }
        
        return {
            "status": "success",
            "data": response_data
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Error getting user data: {str(e)}"
        }


def change_user_data_handler(db_manager: DatabaseManager, platform: str, user_id: str, update: Dict[str, Any]) -> Dict[str, Any]:
    """Handle change user data request."""
    try:
        # Check if user exists
        user_data = db_manager.get_user_data(platform, user_id)
        if not user_data:
            return {
                "status": "failed",
                "message": "User not found"
            }
        
        # Validate and update user data
        success = db_manager.update_user(platform, user_id, update)
        
        if success:
            # Get updated user data
            updated_user = db_manager.get_user_data(platform, user_id)
            if not updated_user:
                return {
                    "status": "failed",
                    "message": "Failed to retrieve updated user data"
                }
            
            response_data = {
                "userId": updated_user["userId"],
                "platform": updated_user["platform"],
                "mainServer": updated_user["mainServer"],
                "displayedServerList": updated_user["displayedServerList"],
                "shareRoomNumber": updated_user["shareRoomNumber"],
                "userPlayerIndex": updated_user["userPlayerIndex"],
                "userPlayerList": updated_user["userPlayerList"],
            }
            
            return {
                "status": "success",
                "data": response_data
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to update user data"
            }
            
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Error updating user data: {str(e)}"
        }


def generate_verify_code() -> str:
    while True:
        verify_code = random.randint(10000, 99999)
        verify_code_str = str(verify_code)
        banned = ['64', '89', '250', '1226', '817']
        if not any(b in verify_code_str for b in banned):
            return verify_code_str


def bind_player_request_handler(db_manager: DatabaseManager, platform: str, user_id: str, direct_unbind: bool = False) -> Dict[str, Any]:
    """Handle bind player request."""
    try:
        # Check if user exists
        user_data = db_manager.get_user_data(platform, user_id)
        if not user_data:
            return {
                "status": "failed",
                "data": "未找到用户"
            }
        
        # Generate verification code
        code = generate_verify_code()
        
        # Store in cache with the same key format as old code
        cache_key = f"{platform}_{user_id}"
        verify_code_cache[cache_key] = code
        
        response = {
            "status": "success",
            "data": {
                "verifyCode": code
            }
        }
        
        # Only add extra field if direct_unbind is enabled (affects unbind only)
        if direct_unbind:
            response["extra"] = "safe_mode"
        
        return response
        
    except Exception as e:
        return {
            "status": "failed",
            "data": f"Error generating verification code: {str(e)}"
        }


def bind_player_verification_handler(
    db_manager: DatabaseManager, 
    platform: str, 
    user_id: str, 
    server: int, 
    player_id: str, 
    binding_action: str,
    direct_unbind: bool = False,
    proxy: str = ""
) -> Dict[str, Any]:
    """Handle bind player verification."""
    try:
        # Check if user exists
        user_data = db_manager.get_user_data(platform, user_id)
        if not user_data:
            return {
                "status": "failed", 
                "data": "未找到用户"
            }
        
        # Check verification code (using old key format)
        cache_key = f"{platform}_{user_id}"
        verify_code = verify_code_cache.get(cache_key)
        if not verify_code or verify_code == "":
            return {
                "status": "failed", 
                "data": "请先发送绑定/解除绑定请求"
            }
        
        # Get current player list
        current_players = user_data["userPlayerList"].copy()
        
        if binding_action == "bind":
            # Check if already bound
            for player in current_players:
                if player.get("playerId") == player_id and player.get("server") == server:
                    return {
                        "status": "failed", 
                        "data": "该记录已绑定"
                    }
            
            # Bestdori API verification (always required for binding)
            # 获取玩家信息
            profile = get_bestdori_player(player_id, server, proxy)
            
            if profile is None:
                return {
                    "status": "failed", 
                    "data": "无法获取玩家信息，请检查网络连接"
                }
            
            if profile.get("data", {}).get("profile") is None or profile.get("data", {}).get("profile") == {}:
                return {
                    "status": "failed", 
                    "data": "未找到玩家，请检查玩家ID是否正确或服务器是否对应"
                }
            
            introduction = profile.get("data", {}).get("profile", {}).get("introduction", "")
            deck_name = profile.get("data", {}).get("profile", {}).get("mainUserDeck", {}).get("deckName", "")
            
            if verify_code != introduction and verify_code != deck_name:
                return {
                    "status": "failed", 
                    "data": f"验证失败，该账号的评论与当前使用的乐队编队名称分别为：{introduction}，{deck_name}，都与验证码不匹配，请重试"
                }
            
            # Add new player binding
            new_player = {
                "playerId": player_id,
                "server": server
            }
            current_players.append(new_player)
            
            # Update database
            updates = {"userPlayerList": current_players}
            success = db_manager.update_user(platform, user_id, updates)
            
            if success:
                # Clear verification code after successful binding
                del verify_code_cache[cache_key]
                return {
                    "status": "success", 
                    "data": "绑定成功"
                }
            else:
                return {
                    "status": "failed", 
                    "data": "数据库更新失败"
                }
                
        elif binding_action == "unbind":
            # Check if bound
            found = False
            for player in current_players:
                if player.get("playerId") == player_id and player.get("server") == server:
                    found = True
                    break
            
            if not found:
                return {
                    "status": "failed", 
                    "data": "该记录未绑定"
                }
            
            # Bestdori API verification for unbind (skip in direct_unbind)
            if not direct_unbind:
                # 获取玩家信息进行验证
                profile = get_bestdori_player(player_id, server, proxy)
                
                if profile is None:
                    return {
                        "status": "failed", 
                        "data": "无法获取玩家信息，请检查网络连接"
                    }

                if profile.get("data", {}).get("profile") is None or profile.get("data", {}).get("profile") == {}:
                    return {
                        "status": "failed", 
                        "data": "未找到玩家，请检查玩家ID是否正确"
                    }
                
                introduction = profile.get("data", {}).get("profile", {}).get("introduction", "")
                deck_name = profile.get("data", {}).get("profile", {}).get("mainUserDeck", {}).get("deckName", "")
                
                if verify_code != introduction and verify_code != deck_name:
                    return {
                        "status": "failed", 
                        "data": f"验证失败，该账号的评论与当前使用的乐队编队名称分别为：{introduction}，{deck_name}，都与验证码不匹配，请重试"
                    }
            else:
                # In direct_unbind, skip verification entirely
                pass
            
            # Remove binding
            for player in current_players:
                if player.get("playerId") == player_id and player.get("server") == server:
                    current_players.remove(player)
                    break
            
            # Update database
            updates = {"userPlayerList": current_players}
            success = db_manager.update_user(platform, user_id, updates)
            
            if success:
                # Clear verification code after successful unbinding
                del verify_code_cache[cache_key]
                return {
                    "status": "success", 
                    "data": "解绑成功"
                }
            else:
                return {
                    "status": "failed", 
                    "data": "数据库更新失败"
                }
        else:
            return {
                "status": "failed", 
                "data": "绑定模式只能是 bind 或 unbind"
            }
            
    except Exception as e:
        return {
            "status": "failed",
            "data": f"Error verifying player binding: {str(e)}"
        }
