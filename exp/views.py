from django.shortcuts import redirect, render
from exp.models import Experiment

# Create your views here.

def home(request):
    return render(request, 'main.html')


def allExperiments(request):
    
    experiments = Experiment.objects.all()
    
    context = {'experiments': experiments}

    return render(request, 'exp/allExperiments.html', context)


def singeExperiment(request, pk):
    
    try:
        experiment = Experiment.objects.get(id=pk)
    except:
        return redirect('exp-home')
    
    context = {'experiment': experiment}
    
    return render(request, 'exp/singleExperiment.html', context) 