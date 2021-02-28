import json

from django.shortcuts import render
from django.http import JsonResponse
# from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

from .models import Card

from .CopenMed_Reasoner.reasonerCOSS_0003 import Reasoner0003, Reasoner0003Viewer

# Create your views here.

def retrieve_reasoner(request, viewer=True):
    """Setup the instance to the Reasoner and to the ReasonerViewer to be used in this session"""
    reasoner = request.session.get('reasoner', Reasoner0003())
    if viewer:
        reasoner_viewer = Reasoner0003Viewer(reasoner)
        return reasoner, reasoner_viewer
    else:
        return reasoner

def store_reasoner_session(request, reasoner):
    """Store reasoner in session to be used later by a request"""
    request.session['reasoner'] = reasoner
    return request

def visor(request):
    all_cards = Card.objects.order_by('family')
    template_name = 'Home.html'
    all_families = list(Card.objects.values_list('family', flat=True).distinct())
    context = {
        'get_families': all_families,
        'get_cards': all_cards
    }
    # FIXME: Descomentar estas dos lineas cuando empecemos a probar el razonador
    # reasoner = retrieve_reasoner(request, viewer=False)
    # request = store_reasoner_session(request, reasoner)
    return render(request, template_name, context)
    # return render(request, template_name)

def get_links(request):
    item = request.GET.get('items', None).strip()
    link = {
        'item_link': list(Card.objects.filter(entity=item).values_list('resources', flat=True))
    }
    return JsonResponse(link)
