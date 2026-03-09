"""
Item constants utility — fetches and caches Dota 2 item data from OpenDota.
"""

import requests
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

OPENDOTA_ITEMS_URL = "https://api.opendota.com/api/constants/items"


@lru_cache(maxsize=1)
def get_item_map() -> dict:
    """
    Fetch item constants from OpenDota API.
    Returns a dict: {item_id: {"name": "...", "dname": "...", "cost": ...}, ...}
    Cached for the lifetime of the process.
    """
    try:
        resp = requests.get(OPENDOTA_ITEMS_URL, timeout=10)
        resp.raise_for_status()
        raw = resp.json()  # {item_name: {id: X, dname: ..., cost: ...}, ...}

        # Invert: {id: {name, dname, cost, img}}
        item_map = {}
        for key, data in raw.items():
            item_id = data.get("id")
            if item_id is not None:
                item_map[item_id] = {
                    "name": key,
                    "dname": data.get("dname", key),
                    "cost": data.get("cost", 0),
                    "img": f"https://cdn.cloudflare.steamstatic.com{data['img']}" if data.get("img") else None,
                }
        return item_map
    except Exception as e:
        logger.error(f"Failed to fetch item constants: {e}")
        return {}


def resolve_items_final(items_final: dict) -> list:
    """
    Convert items_final dict ({slot_0: 147, slot_1: 0, ...})
    into a list of resolved item dicts.
    """
    if not items_final:
        return []

    item_map = get_item_map()
    result = []
    for slot in range(6):
        item_id = items_final.get(f"slot_{slot}", 0)
        if item_id and item_id in item_map:
            info = item_map[item_id]
            result.append({
                "slot": slot,
                "id": item_id,
                "name": info["dname"],
                "cost": info["cost"],
                "img": info["img"],
            })
    # Also check backpack slots (slot_6..8) and neutral (slot_9)
    for slot in range(6, 10):
        key = f"slot_{slot}" if slot < 9 else "slot_9"
        item_id = items_final.get(key, 0)
        if item_id and item_id in item_map:
            info = item_map[item_id]
            label = "neutral" if slot == 9 else "backpack"
            result.append({
                "slot": slot,
                "id": item_id,
                "name": info["dname"],
                "cost": info["cost"],
                "img": info["img"],
                "type": label,
            })
    return result


def resolve_purchase_log(purchase_log: list) -> list:
    """
    Enrich purchase_log entries with display names.
    """
    if not purchase_log:
        return []

    item_map = get_item_map()
    # Build name-based lookup
    name_lookup = {v["name"]: v for v in item_map.values()}

    result = []
    for entry in purchase_log:
        key = entry.get("key", "")
        time = entry.get("time", 0)
        info = name_lookup.get(key, {})
        result.append({
            "time": time,
            "key": key,
            "name": info.get("dname", key),
            "cost": info.get("cost", 0),
        })
    return result


def format_items_for_llm(items_final: dict) -> str:
    """Format item build as a simple text string for the AI coach."""
    resolved = resolve_items_final(items_final)
    if not resolved:
        return "Нет данных"
    
    main_items = [i for i in resolved if i.get("type") not in ("backpack", "neutral")]
    backpack = [i for i in resolved if i.get("type") == "backpack"]
    neutral = [i for i in resolved if i.get("type") == "neutral"]
    
    parts = []
    if main_items:
        parts.append("Предметы: " + ", ".join(f"{i['name']} ({i['cost']}g)" for i in main_items))
    if backpack:
        parts.append("Рюкзак: " + ", ".join(i['name'] for i in backpack))
    if neutral:
        parts.append("Нейтральный: " + neutral[0]['name'])
    
    return " | ".join(parts)


def format_purchase_log_for_llm(purchase_log: list, min_cost: int = 500) -> str:
    """
    Format the purchase log for the AI coach, filtering out cheap items (like tangos/wards)
    to save context tokens. Formats as '[MM:SS] Item Name'.
    """
    if not purchase_log:
        return "Тайминги недоступны (нет реплея)"
        
    resolved_log = resolve_purchase_log(purchase_log)
    
    # Filter items that cost less than min_cost, and format the time
    significant_items = []
    for item in resolved_log:
        cost = item.get("cost", 0)
        # Some items might have cost 0 in the api but are significant (like Aghs Blessing from Roshan),
        # but usually we want to filter out < 500g items.
        if cost >= min_cost or ("recipe" not in item.get("key", "").lower() and cost == 0 and item.get("key") != "tpscroll"):
            time_sec = item.get("time", 0)
            if time_sec < 0:
                time_str = f"-{-time_sec//60:02d}:{-time_sec%60:02d}"
            else:
                time_str = f"{time_sec//60:02d}:{time_sec%60:02d}"
                
            significant_items.append(f"[{time_str}] {item.get('name', item.get('key'))}")
            
    if not significant_items:
        return "Значимых покупок не зафиксировано (возможно, баг парсинга)"
        
    return " -> ".join(significant_items)
