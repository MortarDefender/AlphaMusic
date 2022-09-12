from django.db import models
from django.forms import ModelForm
from model.models import SongFile


class Instruments(models.TextChoices):
    PIANO = "piano", "piano"
    GUITAR = "guitar", "guitar"
    TRUMPET = "trumpet", "trumpet"


class MusicModels(models.TextChoices):
    MAESTRO7 = "maestro_2017", "maestro_2017"
    MAESTRO8 = "maestro_2018", "maestro_2018"
    MOZART = "mozart", "mozart" 
    ANIME = "anime", "anime"
    BACH = "bach", "bach"
    LOFI = "lofi", "lofi"


class BackgroundMusic(models.TextChoices):
    RAIN = "rain", "rain"
    STORM = "storm", "storm"
    THUNDER = "thunder", "thunder"


class CreateSongs(ModelForm):
    class Meta:
        model = SongFile
        exclude = ['generated_file']
        fields = '__all__'
