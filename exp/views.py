from django.shortcuts import redirect, render
from django.http import HttpResponse
from exp.models import Experiment
from exp.forms import ModelOrganismForm, DescriptorMapInline


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


def updateOrganism(request):
    
    if request.method == 'POST':
        print(request.POST)
        form = DescriptorMapInline(request.POST)
        if form.is_valid():
            form.save()
            return redirect('exp-all')
        else:
            return HttpResponse('An Error ocurred:(')
    
    form = DescriptorMapInline()
    context = {'form': form}
    return render(request, 'exp/updateOrganism.html', context)