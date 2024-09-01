"""Views."""
from django.shortcuts import render
from .graph import get_graphs_hourly

from django.shortcuts import render
from django.http import HttpResponse
from .forms import DateForm

def index(request):
    selected_date = None
    selected_satellite = 'CODE'

    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            selected_satellite = request.POST.get('selected_satellite')
            print('Selected satellite: ', selected_satellite)
            selected_date = form.cleaned_data['selected_date']
            pictures = get_graphs_hourly(selected_date, selected_satellite)
        else:
            pictures = []
    else:
        pictures = get_graphs_hourly(selected_date)
              
    context = {
            'context': pictures,
            'selected_date': selected_date,
            'selected_satellite': selected_satellite
        }
    return render(request, 'home/index.html', context)

def graph_view(request):
    # Get the graph
    # graph = get_graph()

    context = {'context': get_graphs_hourly()}
    return render(request, 'graphs/graph.html', context)


