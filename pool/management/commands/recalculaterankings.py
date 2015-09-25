from django.core.management.base import BaseCommand

from pool.models import Player, Game, Ranking


class Command(BaseCommand):
    help = 'Resets and recalculates player rankings'

    def handle(self, *args, **options):
        # Clear data
        for player in Player.objects.all():
            player.mu = None
            player.sigma = None
            player.save()

        Ranking.objects.all().delete()

        # Repopulate
        for game in Game.objects.all():
            game.create_rankings()
