from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from players.models import Player
from players.serializers import PlayerSerializer, LinkAccountSerializer
from players.tasks import sync_player_data


@api_view(['POST'])
def link_account(request):
    """Link a Dota 2 account_id — creates player record and starts sync."""
    serializer = LinkAccountSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    account_id = serializer.validated_data['account_id']

    player, created = Player.objects.get_or_create(
        account_id=account_id,
        defaults={'sync_status': Player.SyncStatus.PENDING}
    )

    if created or player.sync_status == Player.SyncStatus.ERROR:
        player.sync_status = Player.SyncStatus.PENDING
        player.save(update_fields=['sync_status'])
        sync_player_data.delay(account_id)

    return Response(
        PlayerSerializer(player).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(['GET'])
def get_player(request, account_id):
    """Get player profile and sync status."""
    try:
        player = Player.objects.get(account_id=account_id)
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found. Link the account first.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(PlayerSerializer(player).data)


@api_view(['POST'])
def trigger_sync(request, account_id):
    """Manually trigger a data sync for a player."""
    try:
        player = Player.objects.get(account_id=account_id)
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if player.sync_status == Player.SyncStatus.SYNCING:
        return Response(
            {'message': 'Sync already in progress', 'sync_status': 'syncing'},
            status=status.HTTP_202_ACCEPTED,
        )

    player.sync_status = Player.SyncStatus.SYNCING
    player.save(update_fields=['sync_status'])
    sync_player_data.delay(account_id)

    return Response(
        {'message': 'Sync started', 'sync_status': 'syncing'},
        status=status.HTTP_202_ACCEPTED,
    )
