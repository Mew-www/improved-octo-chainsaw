from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import HttpResponse

from django.template import loader, TemplateDoesNotExist

@require_http_methods(['GET'])
def render_template(request, template_name):
  try:
    return render(request, "league/templates/"+template_name+".html")
  except TemplateDoesNotExist:
    return render(request, "league/templates/base/404.html")
