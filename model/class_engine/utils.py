import os
import subprocess
from pydub import AudioSegment
from glob import glob as search
from model.class_engine import generator


PATH = "model//class_engine"

def midi_to_wav():
    """ convert midi to wav format """
    output_path = None
    env = os.environ.copy()
    for midi in search(f"{PATH}//output/*.mid"):
        file_name = midi.split("/")[-1].split(".")[0]

        if output_path is None:
            output_path = get_files_location(file_name)

        subprocess.run(f"echo {file_name}", shell=True, env=env)
        subprocess.run(f'timidity "/app//model//class_engine//output//{file_name}.mid" -Ow -o "/app//model//class_engine//wav_generated//{file_name}.wav"', shell=True, env=env)
        # subprocess.run(f'timidity "/app//model//class_engine//output//{file_name}.mid" -Ow -o "{output_path}//{file_name}.wav"', shell=True, env=env)

    # cp /app//model//class_engine//wav_generated//{file_name}.wav /app//static//anime//piano//rain//{file_name}.wav


def get_files_location(file_name):
    music_model, instrument, background_music, _, _ = file_name.split("-")

    return f"/app//static//files//{music_model}//{instrument}//{background_music}"


def background_merger(background_song_name="rain"):
    """ merge all the songs with a background noise """
    songs = []
    for melody in search(f"{PATH}//wav_generated/*.*"):
        piano = AudioSegment.from_file(melody, format="wav")
        file_name = melody.split("/")[-1].split(".")[0]
        songs.append((piano + 10, file_name))   # increase volume by 6DB

    rain = AudioSegment.from_file(f"{PATH}//background_music//{background_song_name}.wav", format="wav")

    count = 0
    for song, file_name in songs:
        overlayRain = song.overlay(rain, position=0)
        overlayRain.export(f"{file_name}.mp3", format="mp3")
        count += 1


def delete_all_songs(song_list=None, dir="wav_generated"):
    """ delete all files from a directory """
    search_list = song_list if song_list is not None else search(f"{PATH}//{dir}//*.*")  # *.wav / *.mp3

    for song in search_list:
        os.remove(song)


def generate_songs(music_model, instrument, background_music, number_of_songs):
    songs_created = generator.AlphaGenerate(
                        model_name=music_model,
                        instrument_name=instrument,
                        file_name=f"{music_model}-{instrument}-{background_music}"
                    ).create(number_of_songs)
    midi_to_wav()
    background_merger(background_music)
    # delete_all_songs(song_list=[item[0] for item in songs_created])
