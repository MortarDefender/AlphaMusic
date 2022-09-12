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
    ANIME = "anime", "anime"
    MAESTRO7 = "maestro_2017", "maestro_2017"
    MAESTRO8 = "maestro_2018", "maestro_2018"
    BACH = "beethoven", "beethoven"
    MOZART = "mozart", "mozart" 
    LOFI = "lofi", "lofi"


class SongFile(models.Model):
    number_of_songs = models.IntegerField()
    song_length = models.FloatField()
    background_music = models.CharField(
        max_length=20,
        choices=BackgroundMusic.choices,
        default=BackgroundMusic.RAIN,
    )
    instrument = models.CharField(
        max_length=20,
        choices=Instruments.choices,
        default=Instruments.PIANO,
    )
    music_model = models.CharField(
        max_length=20,
        choices=MusicModels.choices,
        default=MusicModels.ANIME,
    )
    generated_file = models.FileField(upload_to=upload_to_function)

    def __str__(self):
        return f"{path.basename(self.file.name)}"
