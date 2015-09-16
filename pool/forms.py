from django import forms
from django.forms.models import modelform_factory
from pool.models import Player, Game


PlayerForm = modelform_factory(Player, fields=['name'])


class GameForm(forms.Form):
    winner = forms.ModelChoiceField(required=True, queryset=Player.objects.all())
    loser = forms.ModelChoiceField(required=True, queryset=Player.objects.all())

    def clean(self):
        cleaned_data = super(GameForm, self).clean()
        if cleaned_data.get('winner') == cleaned_data.get('loser'):
            raise forms.ValidationError("Stop playing with yourself...")
