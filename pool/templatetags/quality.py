from django import template
from trueskill import quality_1vs1


register = template.Library()


@register.simple_tag
def quality(player_1, player_2):
    return int(quality_1vs1(player_1.rating, player_2.rating)*100)
