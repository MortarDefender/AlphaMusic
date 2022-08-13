from model.forms import CreateSongs
from django.shortcuts import render
# from model.class_engine import generator, utils


def generate_page(request):

    results = False

    if request.method == "POST":
        form = CreateSongs(request.POST, request.FILES)
        song_form = form.save(commit=False)
        print(f"number of songs: {song_form.number_of_songs}")
        print(f"song length: {song_form.song_length}")
        print(f"background music: {song_form.background_music}")
        print(f"instrument: {song_form.instrument}")
        print(f"music model: {song_form.music_model}")

        # generator.AlphaGenerate(input_notes_file_name="123 notes 123").create(song_form.number_of_songs)
        # utils.background_merger()
        results = True


    return render(request, 'generate/generate_page.html', {'generate_form': CreateSongs, 'results': results})
