from django.db import models
from django.forms import ModelForm
from model.models import SongFile


class Instruments(models.TextChoices):
    PIANO = "piano", "piano"
    GUITAR = "guitar", "guitar"
    TRUMPET = "trumpet", "trumpet"


class MusicModels(models.TextChoices):
    MAESTRO = "maestro", "maestro"
    MOZART = "mozart", "mozart" 
    ANIME = "anime", "anime"
    BACH = "bach", "bach"
    LOFI = "lofi", "lofi"


class BackgroundMusic(models.TextChoices):
    RAIN = "Rain", "Rain"
    STORM = "Storm", "Storm"
    THUNDER = "Thunder", "Thunder"


class CreateSongs(ModelForm):
    class Meta:
        model = SongFile
        exclude = ['generated_file']
        fields = '__all__'
