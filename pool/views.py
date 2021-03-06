from django.http import HttpResponseRedirect
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from pool.forms import PlayerForm, GameForm
from pool.models import Game, Player


def home(request):
    player_form = PlayerForm()
    game_form = GameForm()

    if request.method == 'POST':
        print request.POST
        if 'player' in request.POST:
            player_form = PlayerForm(request.POST)
            if player_form.is_valid():
                player_form.save()
                return HttpResponseRedirect('/')

        if 'game' in request.POST:
            game_form = GameForm(request.POST)
            if game_form.is_valid():
                Game.objects.create(
                    winner=game_form.cleaned_data['winner'],
                    loser=game_form.cleaned_data['loser'],
                )
                return HttpResponseRedirect('/')

    players = Player.objects.all()
    matrix = []
    for player in players:
        matrix.append((
            player,
            Player.objects.annotate_against(player),
        ))

    return render(request, 'pool/home.html', {
        'players': players,
        'player_form': player_form,
        'game_form': game_form,
        'matrix': matrix,
    })


def player(request, id):
    player = get_object_or_404(Player, pk=id)
    others = Player.objects.annotate_against(player).exclude(pk=player.pk)
    return render(request, 'pool/player.html', {
        'player': player,
        'games': Game.objects.filter(
            Q(winner=player) | Q(loser=player)
        ).order_by('created'),
        'others': others,
    })
