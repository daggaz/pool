from django.db import models, transaction
from django.db.models import Count, F
from django.db.models.expressions import RawSQL
from trueskill import Rating, rate_1vs1


class PlayerManager(models.Manager):
    def get_queryset(self):
        query = super(PlayerManager, self).get_queryset()
        return query.annotate(
            games_played=Count('games_won', distinct=True) + Count('games_lost', distinct=True),
            pessimistic_mu=F('mu')-(F('sigma')*3),
        ).order_by('-pessimistic_mu', '-games_played')

    def annotate_against(self, other):
        return self.annotate(
            games_won_against=RawSQL(
                """
                    SELECT COUNT(*)
                    FROM pool_game
                    WHERE loser_id = %s AND winner_id = pool_player.id
                """,
                (other.id,)
            ),
            games_lost_against=RawSQL(
                """
                    SELECT COUNT(*)
                    FROM pool_game
                    WHERE winner_id = %s AND loser_id = pool_player.id
                """,
                (other.id,)
            ),
            games_played=RawSQL(
                """
                    SELECT COUNT(*)
                    FROM pool_game
                    WHERE
                      loser_id = %s AND winner_id = pool_player.id OR
                      winner_id = %s AND loser_id = pool_player.id
                """,
                (other.id, other.id,)
            )
        )


class Player(models.Model):
    name = models.CharField(max_length=265, unique=True)
    mu = models.FloatField(null=True)
    sigma = models.FloatField(null=True)

    objects = PlayerManager()

    @property
    def ranking(self):
        if self.mu:
            return Player.objects.filter(mu__gt=self.mu).count() + 1
        return Player.objects.count()

    @property
    def rating(self):
        return Rating(self.mu, self.sigma)

    @rating.setter
    def rating(self, rating):
        self.mu = rating.mu
        self.sigma = rating.sigma

    def __str__(self):
        return self.name


class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(Player, related_name='games_won')
    loser = models.ForeignKey(Player, related_name='games_lost')

    def create_rankings(self):
        winner = self.winner
        loser = self.loser
        winner.rating, loser.rating = rate_1vs1(winner.rating, loser.rating)
        winner_ranking = Ranking(player=winner, game=self)
        winner_ranking.rating = winner.rating
        loser_ranking = Ranking(player=loser, game=self)
        loser_ranking.rating = loser.rating
        with transaction.atomic():
            winner.save()
            loser.save()
            winner_ranking.save()
            loser_ranking.save()

    def save(self, *args, **kwargs):
        created = self.pk is None
        super(Game, self).save(*args, **kwargs)
        if created:
            self.create_rankings()

    class Meta(object):
        ordering = ('created',)


class Ranking(models.Model):
    player = models.ForeignKey(Player, related_name='rankings')
    game = models.ForeignKey(Game, related_name='rankings')
    mu = models.FloatField(null=True)
    sigma = models.FloatField(null=True)

    @property
    def rating(self):
        return Rating(self.mu, self.sigma)

    @rating.setter
    def rating(self, rating):
        self.mu = rating.mu
        self.sigma = rating.sigma

    class Meta(object):
        ordering = ('game__created',)
