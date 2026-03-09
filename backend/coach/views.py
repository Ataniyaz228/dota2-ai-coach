from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as http_status

from players.models import Player
from coach.service import generate_analysis, generate_match_analysis, generate_chat_response


@api_view(['POST'])
def coach_analyze(request, account_id):
    """Generate AI coaching analysis for a player."""
    try:
        player = Player.objects.get(account_id=account_id)
    except Player.DoesNotExist:
        return Response({'error': 'Player not found'}, status=http_status.HTTP_404_NOT_FOUND)

    match_limit = int(request.data.get('match_limit', 20))
    result = generate_analysis(player, match_limit)
    return Response(result)


@api_view(['POST'])
def coach_match(request, match_id):
    """Generate AI analysis for a single match."""
    account_id = request.data.get('account_id')
    if not account_id:
        return Response({'error': 'account_id is required'}, status=http_status.HTTP_400_BAD_REQUEST)

    result = generate_match_analysis(match_id, int(account_id))
    return Response(result)


@api_view(['POST'])
def coach_chat(request, account_id):
    """Chat with AI coach — send conversation history."""
    try:
        player = Player.objects.get(account_id=account_id)
    except Player.DoesNotExist:
        return Response({'error': 'Player not found'}, status=http_status.HTTP_404_NOT_FOUND)

    messages = request.data.get('messages', [])
    if not messages:
        return Response({'error': 'messages are required'}, status=http_status.HTTP_400_BAD_REQUEST)

    reply = generate_chat_response(player, messages)
    return Response({'reply': reply})
