import os
import glob
import subprocess
from pydub import AudioSegment



def midi_to_wav():
    # midi to wav
    env = os.environ.copy()
    for midi in glob.glob("midi_generated_generated/*.mid"):
        file_name = midi[:-4].split('/')[1]
        print(file_name)
        subprocess.run(f"echo {file_name}", shell=True, env=env)
        subprocess.run(f'timidity "{midi}" -Ow -o "wav_generated/{file_name}.wav"', shell=True, env=env)



def background_merger():
    # merge background music
    songs = []
    for melody in glob.glob("wav_generated/*"):
        piano = AudioSegment.from_file(melody, format="wav")
        songs.append(piano + 10)   # increase volume by 6DB

    # drum = AudioSegment.from_file("SFX/drum.wav", format="wav")
    rain = AudioSegment.from_file("SFX/rain.wav", format="wav")

    count = 0
    for song in songs:
        # overlayDrum = song.overlay(drum, position=0)
        overlayRain = song.overlay(rain, position=0)
        overlayRain.export("Lo-Fi{id}.mp3".format(id = count), format="mp3")
        count += 1
