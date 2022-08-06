from model.forms import CreateSongs
from django.shortcuts import render


def generate_page(request):
    return render(request, 'generate/generate_page.html', {'generate_form': CreateSongs})
