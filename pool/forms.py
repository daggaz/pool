from django import forms
from django.forms.models import modelform_factory
from pool.models import Player, Game


PlayerForm = modelform_factory(Player, fields=['name'])


class GameForm(forms.Form):
    winner = forms.ModelChoiceField(queryset=Player.objects.all())
    loser = forms.ModelChoiceField(queryset=Player.objects.all())

    def clean(self):
        cleaned_data = super(GameForm, self).clean()
        if cleaned_data['winner'] == cleaned_data['loser']:
            raise forms.ValidationError("Stop playing with yourself...")
