from model.forms import CreateSongs
from django.shortcuts import render
from model.class_engine import utils


def generate_page(request):

    results = False
    songs_created = []

    if request.method == "POST":
        form = CreateSongs(request.POST, request.FILES)
        song_form = form.save(commit=False)
        print(f"number of songs: {song_form.number_of_songs}")
        print(f"song length: {song_form.song_length}")
        print(f"background music: {song_form.background_music}")
        print(f"instrument: {song_form.instrument}")
        print(f"music model: {song_form.music_model}")

        utils.generate_songs(song_form.music_model, song_form.instrument, song_form.background_music, song_form.number_of_songs)
        results = True

    return render(request, 'generate/generate_page.html', {'generate_form': CreateSongs, 'songs_created': songs_created, 'results': results})
