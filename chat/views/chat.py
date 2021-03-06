from __future__ import unicode_literals

from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET'])
def semantize(request, dataset_id):
    return render(request, 'chatbot_semantize.html', {'dataset_id': dataset_id})


@require_http_methods(['GET'])
def chatbot_form(request):
    return render(request, 'chatbot_form.html')
