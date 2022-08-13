from os import path
from django.db import models


def upload_to_function(instance, filename):
    return path.join('files', str(instance.music_model), str(instance.instrument), str(instance.background_music), path.basename(filename))


class BackgroundMusic(models.TextChoices):
    RAIN = "rain", "rain"
    STORM = "storm", "storm"
    THUNDER = "thunder", "thunder"


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


class SongFile(models.Model):
    number_of_songs = models.IntegerField()
    song_length = models.FloatField()
    # get a music file from the user
    background_music = models.CharField(
        max_length=7,
        choices=BackgroundMusic.choices,
        default=BackgroundMusic.RAIN,
    )
    instrument = models.CharField(
        max_length=7,
        choices=Instruments.choices,
        default=Instruments.PIANO,
    )
    music_model = models.CharField(
        max_length=7,
        choices=MusicModels.choices,
        default=MusicModels.MAESTRO,
    )
    generated_file = models.FileField(upload_to=upload_to_function)

    def __str__(self):
        return f"{path.basename(self.file.name)}"
