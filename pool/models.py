from django.db import models
from django.db.models import Count
from trueskill import Rating, rate_1vs1


class PlayerManager(models.Manager):
    def get_queryset(self):
        query = super(PlayerManager, self).get_queryset()
        return query.annotate(
            games_played=Count('games_won', distinct=True) + Count('games_lost', distinct=True)
        ).order_by('-mu', '-games_played')


class Player(models.Model):
    name = models.CharField(max_length=265, unique=True)
    mu = models.FloatField(null=True)
    sigma = models.FloatField(null=True)

    objects = PlayerManager()

    @property
    def ranking(self):
        return Player.objects.filter(mu__gt=self.mu).count() + 1

    @property
    def rating(self):#
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

    def save(self, *args, **kwargs):
        super(Game, self).save(*args, **kwargs)
        winner = self.winner
        loser = self.loser
        winner.rating, loser.rating = rate_1vs1(winner.rating, loser.rating)
        winner.save()
        loser.save()
