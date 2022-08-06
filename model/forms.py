from django import forms
from django.db import models


class Instruments(models.TextChoices):
    PIANO = "pno", "piano"
    GUITAR = "gtr", "guitar"
    TRUMPET = "trp", "trumpet"


class MusicModels(models.TextChoices):
    MAESTRO = "mst", "maestro"
    MOZART = "mzt", "mozart" 
    ANIME = "anm", "anime"
    BACH = "bch", "bach"
    LOFI = "lof", "lofi"


class BackgroundMusic(models.TextChoices):
    RAIN = "Rain", "Rain"
    STORM = "Storm", "Storm"
    THUNDER = "Thunder", "Thunder"


class CreateSongs(forms.Form):
    number_of_songs = forms.IntegerField()
    song_length = forms.DecimalField()
    background_music = forms.ChoiceField(
        choices=BackgroundMusic.choices,
    )
    instrument = forms.ChoiceField(
        choices=Instruments.choices,
    )
    # get a music file from the user
    music_model = forms.ChoiceField(
        choices=MusicModels.choices,
    )

