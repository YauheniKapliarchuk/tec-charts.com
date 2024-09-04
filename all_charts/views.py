"""Views."""
from django.shortcuts import render
from .graph import get_graphs_hourly, get_generated_ionex_json_url, get_valid_date

from django.shortcuts import render
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

    form = DateForm(request.POST)
    correct_date = form.cleaned_data['selected_date'] if request.method == 'POST' and form.is_valid() else ''

    generated_ionex_json_url = get_generated_ionex_json_url(request.POST.get('selected_satellite', 'CODE'), get_valid_date(correct_date))
              
    context = {
            'context': pictures,
            'selected_date': selected_date,
            'selected_satellite': selected_satellite,
            'generated_ionex_json_url': generated_ionex_json_url
        }
    return render(request, 'home/index.html', context)

def graph_view(request):
    # Get the graph
    # graph = get_graph()

    context = {'context': get_graphs_hourly()}
    return render(request, 'graphs/graph.html', context)


