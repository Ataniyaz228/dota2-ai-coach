"""
AI Coach service — aggregates player data and generates LLM-based analysis.
"""

import os
import logging
from openai import OpenAI

from matches.models import Match, PlayerMatch, PlayerHeroStats
from matches.items import format_items_for_llm, format_purchase_log_for_llm
from players.models import Player

logger = logging.getLogger(__name__)


def get_llm_client():
    return OpenAI(
        base_url=os.getenv('LLM_BASE_URL', 'http://127.0.0.1:8045/v1'),
        api_key=os.getenv('LLM_API_KEY', 'sk-no-key'),
    )


def _call_llm(messages: list, temperature: float = 0.7, max_tokens: int = 2000) -> str:
    """Shared LLM call wrapper with error handling."""
    try:
        client = get_llm_client()
        model = os.getenv('LLM_MODEL', 'gemini-3.1-pro-high')
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return f"Ошибка при обращении к AI: {str(e)}"


# ─── Data Aggregators ─────────────────────────────────

def aggregate_player_data(player: Player, match_limit: int = 20) -> dict:
    """Build a structured data summary from recent matches for the LLM."""
    recent_matches = list(
        PlayerMatch.objects
        .filter(player=player)
        .select_related('match', 'hero')
        .order_by('-match__start_time')[:match_limit]
    )

    if not recent_matches:
        return None

    total = len(recent_matches)
    wins = sum(1 for m in recent_matches if m.win)
    losses = total - wins

    avg_kills = sum(m.kills for m in recent_matches) / total
    avg_deaths = sum(m.deaths for m in recent_matches) / total
    avg_assists = sum(m.assists for m in recent_matches) / total
    avg_gpm = sum(m.gold_per_min for m in recent_matches) / total
    avg_xpm = sum(m.xp_per_min for m in recent_matches) / total
    avg_last_hits = sum(m.last_hits for m in recent_matches) / total
    avg_hero_damage = sum(m.hero_damage for m in recent_matches) / total
    avg_tower_damage = sum(m.tower_damage for m in recent_matches) / total

    match_details = []
    for pm in recent_matches:
        hero_name = pm.hero.localized_name if pm.hero else 'Unknown'
        match_details.append({
            'hero': hero_name,
            'result': 'WIN' if pm.win else 'LOSS',
            'kda': f'{pm.kills}/{pm.deaths}/{pm.assists}',
            'gpm': pm.gold_per_min,
            'xpm': pm.xp_per_min,
            'last_hits': pm.last_hits,
            'hero_damage': pm.hero_damage,
            'tower_damage': pm.tower_damage,
            'duration': pm.match.duration_display if pm.match else '?',
        })

    hero_stats = list(
        PlayerHeroStats.objects
        .filter(player=player, games_played__gte=2)
        .select_related('hero')
        .order_by('-games_played')[:10]
    )

    hero_pool = []
    for hs in hero_stats:
        hero_pool.append({
            'hero': hs.hero.localized_name,
            'games': hs.games_played,
            'winrate': f'{hs.winrate * 100:.0f}%',
            'avg_kda': f'{hs.avg_kda:.1f}',
            'avg_gpm': f'{hs.avg_gpm:.0f}',
        })

    max_losing_streak = 0
    current_streak = 0
    for m in recent_matches:
        if not m.win:
            current_streak += 1
            max_losing_streak = max(max_losing_streak, current_streak)
        else:
            current_streak = 0

    high_death_games = sum(1 for m in recent_matches if m.deaths >= 8)
    low_cs_games = sum(1 for m in recent_matches if m.last_hits < 100 and m.match.duration_seconds > 1800)

    return {
        'player_name': player.personaname or 'Unknown',
        'rank_tier': player.rank_tier,
        'total_analyzed': total,
        'wins': wins, 'losses': losses,
        'winrate': f'{wins / total * 100:.1f}%',
        'averages': {
            'kills': round(avg_kills, 1), 'deaths': round(avg_deaths, 1),
            'assists': round(avg_assists, 1), 'gpm': round(avg_gpm),
            'xpm': round(avg_xpm), 'last_hits': round(avg_last_hits),
            'hero_damage': round(avg_hero_damage), 'tower_damage': round(avg_tower_damage),
        },
        'patterns': {
            'max_losing_streak': max_losing_streak,
            'high_death_games': high_death_games,
            'low_cs_games': low_cs_games,
            'most_played_hero': hero_pool[0]['hero'] if hero_pool else 'N/A',
        },
        'hero_pool': hero_pool,
        'recent_matches': match_details,
    }


def aggregate_match_data(match_id: int, account_id: int) -> dict:
    """Build a structured data summary for a single match."""
    try:
        match = Match.objects.get(match_id=match_id)
    except Match.DoesNotExist:
        return None

    all_players = list(
        PlayerMatch.objects
        .filter(match=match)
        .select_related('hero', 'player')
        .order_by('player_slot')
    )

    # Find our player
    our_pm = None
    for pm in all_players:
        if pm.player and pm.player.account_id == account_id:
            our_pm = pm
            break

    if not our_pm:
        return None

    teammates = [pm for pm in all_players if pm.is_radiant == our_pm.is_radiant and pm != our_pm]
    enemies = [pm for pm in all_players if pm.is_radiant != our_pm.is_radiant]

    def _player_line(pm):
        hero = pm.hero.localized_name if pm.hero else '?'
        items = format_items_for_llm(pm.items_final)
        return f"{hero} KDA:{pm.kills}/{pm.deaths}/{pm.assists} GPM:{pm.gold_per_min} LH:{pm.last_hits} DMG:{pm.hero_damage} | {items}"

    return {
        'match_id': match.match_id,
        'result': 'WIN' if our_pm.win else 'LOSS',
        'duration': match.duration_display,
        'our_hero': our_pm.hero.localized_name if our_pm.hero else '?',
        'our_stats': {
            'kills': our_pm.kills, 'deaths': our_pm.deaths, 'assists': our_pm.assists,
            'gpm': our_pm.gold_per_min, 'xpm': our_pm.xp_per_min,
            'last_hits': our_pm.last_hits, 'denies': our_pm.denies,
            'hero_damage': our_pm.hero_damage, 'tower_damage': our_pm.tower_damage,
            'hero_healing': our_pm.hero_healing,
        },
        'teammates': [_player_line(pm) for pm in teammates],
        'enemies': [_player_line(pm) for pm in enemies],
        'score': f"{match.radiant_score} : {match.dire_score}",
        'our_items': format_items_for_llm(our_pm.items_final),
        'our_timings': format_purchase_log_for_llm(our_pm.purchase_log),
    }


# ─── System Prompts ───────────────────────────────────

SYSTEM_PROMPT = """Ты — AI-тренер по Dota 2 (DotaCoach.AI). Тебе предоставлена статистика последних матчей игрока.

Твоя задача — дать КОНКРЕТНЫЙ, ПРАКТИЧЕСКИЙ анализ на русском языке. НЕ пиши общие советы типа "играй лучше" или "коммуницируй с тимой".

Основывайся ТОЛЬКО на предоставленных данных. Структура ответа:

## Общая оценка
Краткая (2-3 предложения) оценка текущей формы игрока.

## Сильные стороны
Конкретные метрики, в которых игрок хорош (со ссылками на числа).

## Проблемные зоны
Конкретные слабости с числами. Например: "Средняя смертность 7.2 — это высоко для вашего ранга".

## Рекомендации
3-5 конкретных, выполнимых советов. Каждый совет должен ссылаться на конкретную метрику из данных.

## Герои
Анализ пула героев: на ком стоит фокусироваться, а кого лучше избегать, основываясь на винрейте и KDA.

Формат: чистый Markdown с заголовками ##, списками (- ), и **жирным** текстом. Будь лаконичен, точен, профессионален."""

MATCH_SYSTEM_PROMPT = """Ты — AI-тренер по Dota 2 (DotaCoach.AI). Тебе предоставлены данные одного конкретного матча.

Твоя задача — дать КОНКРЕТНЫЙ разбор этого матча на русском языке. Структура:

## Результат
Краткое резюме матча (1-2 предложения).

## Перформанс игрока
Оценка игры игрока: что он сделал хорошо, где ошибся. Со ссылками на конкретные числа.

## Предметы и Тайминги
Оцени итоговый билд и порядок покупки (если тайминги доступны). Опирайся на время (например, "Blink на 15:00 — это неплохо"). Если билд неоптимальный или тайминги завалены — предложи лучшее решение.

## Сравнение с командой
Как игрок выглядел на фоне тиммейтов (GPM, урон, KDA).

## Что улучшить
2-3 конкретных совета по этому конкретному матчу.

Формат: чистый Markdown с заголовками ##, списками (- ), и **жирным** текстом. Будь лаконичен и по делу."""

CHAT_SYSTEM_PROMPT = """Ты — AI-тренер по Dota 2 (DotaCoach.AI). Ты ведешь диалог с игроком. У тебя есть контекст его статистики.

Правила:
- Отвечай на русском языке
- Будь конкретным — ссылайся на числа из контекста
- Если вопрос не связан с Dota 2, вежливо перенаправь разговор
- Формат: Markdown с **жирным**, списками (- ), заголовками (##)
- Будь профессиональным, но дружелюбным"""


# ─── Analysis Functions ─────────────────────────────

def generate_analysis(player: Player, match_limit: int = 20) -> dict:
    """Full player analysis."""
    data = aggregate_player_data(player, match_limit)
    if not data:
        return {'analysis': 'Недостаточно данных для анализа. Синхронизируйте матчи.', 'data_summary': None}

    user_message = f"""Проанализируй статистику игрока:

Игрок: {data['player_name']}
Ранг: {data['rank_tier'] or 'Не определён'}
Матчей проанализировано: {data['total_analyzed']}
Винрейт: {data['winrate']} ({data['wins']}W / {data['losses']}L)

Средние показатели:
- KDA: {data['averages']['kills']}/{data['averages']['deaths']}/{data['averages']['assists']}
- GPM: {data['averages']['gpm']}
- XPM: {data['averages']['xpm']}
- Last Hits: {data['averages']['last_hits']}
- Hero Damage: {data['averages']['hero_damage']}
- Tower Damage: {data['averages']['tower_damage']}

Паттерны:
- Макс. серия поражений: {data['patterns']['max_losing_streak']}
- Матчей с 8+ смертями: {data['patterns']['high_death_games']} из {data['total_analyzed']}
- Матчей с низким фармом (< 100 LH за 30+ мин): {data['patterns']['low_cs_games']}

Пул героев (топ):
""" + '\n'.join(
        f"- {h['hero']}: {h['games']} игр, WR {h['winrate']}, KDA {h['avg_kda']}, GPM {h['avg_gpm']}"
        for h in data['hero_pool']
    ) + f"""

Последние {len(data['recent_matches'])} матчей:
""" + '\n'.join(
        f"- {m['hero']} [{m['result']}] KDA:{m['kda']} GPM:{m['gpm']} LH:{m['last_hits']} DMG:{m['hero_damage']} ({m['duration']})"
        for m in data['recent_matches']
    )

    analysis_text = _call_llm([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ])

    return {
        'analysis': analysis_text,
        'data_summary': {
            'winrate': data['winrate'],
            'avg_kda': f"{data['averages']['kills']}/{data['averages']['deaths']}/{data['averages']['assists']}",
            'avg_gpm': data['averages']['gpm'],
            'matches_analyzed': data['total_analyzed'],
        },
    }


def generate_match_analysis(match_id: int, account_id: int) -> dict:
    """Single match analysis."""
    data = aggregate_match_data(match_id, account_id)
    if not data:
        return {'analysis': 'Матч не найден или нет данных игрока в этом матче.'}

    s = data['our_stats']
    user_message = f"""Разбери этот конкретный матч:

Match ID: {data['match_id']}
Результат: {data['result']}
Длительность: {data['duration']}
Счёт: {data['score']}

Герой игрока: {data['our_hero']}
- KDA: {s['kills']}/{s['deaths']}/{s['assists']}
- GPM: {s['gpm']}, XPM: {s['xpm']}
- Last Hits: {s['last_hits']}, Denies: {s['denies']}
- Урон по героям: {s['hero_damage']}, по строениям: {s['tower_damage']}
- Hero Healing: {s['hero_healing']}
- Итоговый билд: {data['our_items']}
- Тайминги покупок: {data['our_timings']}

Тиммейты:
""" + '\n'.join(f"- {t}" for t in data['teammates']) + """

Противники:
""" + '\n'.join(f"- {e}" for e in data['enemies'])

    analysis_text = _call_llm([
        {"role": "system", "content": MATCH_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ])

    return {'analysis': analysis_text, 'match_id': data['match_id']}


def generate_chat_response(player: Player, messages: list) -> str:
    """Chat with the coach — maintain conversation history."""
    data = aggregate_player_data(player, 20)

    context = "Контекст отсутствует — данных нет."
    if data:
        context = f"""Контекст игрока (для справки):
Игрок: {data['player_name']}, Ранг: {data['rank_tier'] or '?'}
Винрейт: {data['winrate']} ({data['total_analyzed']} матчей)
Средний KDA: {data['averages']['kills']}/{data['averages']['deaths']}/{data['averages']['assists']}
Средний GPM: {data['averages']['gpm']}, XPM: {data['averages']['xpm']}
Топ-герой: {data['patterns']['most_played_hero']}"""

    llm_messages = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT + "\n\n" + context},
    ]
    # Add conversation history
    for msg in messages:
        llm_messages.append({"role": msg["role"], "content": msg["content"]})

    return _call_llm(llm_messages)
