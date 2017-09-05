from django.http import JsonResponse, HttpResponse, HttpResponseServerError
from django.views import View

from djproject.prod_settings import BASE_DIR

import os, json

class SeenEntityView(View):
  filename = ''

  def get(self, request):
    filepath = os.path.join(BASE_DIR, 'league', self.filename)
    if not os.path.isfile(filepath):
      return JsonResponse([], safe=False)
    with open(filepath, 'r') as fh:
      return JsonResponse(json.load(fh), safe=False)

  def post(self, request):
    filepath = os.path.join(BASE_DIR, 'league', self.filename)
    new = json.loads(request.body.decode('utf-8'))
    old = [] if not os.path.isfile(filepath) else json.load(open(filepath, 'r'))
    old_and_new = list(set(old+new)) # Parse duplicates off
    with open(filepath, 'w') as fh:
      json.dump(old_and_new, fh)
    return HttpResponse('')


class FailedRequestsView(View):
  filename = ''

  def get(self, request):
    filepath = os.path.join(BASE_DIR, 'league', self.filename)
    if not os.path.isfile(filepath):
      return JsonResponse([], safe=False)
    with open(filepath, 'r') as fh:
      return JsonResponse(json.load(fh), safe=False)

  def post(self, request):
    filepath = os.path.join(BASE_DIR, 'league', self.filename)
    new = json.loads(request.body.decode('utf-8'))
    old = [] if not os.path.isfile(filepath) else json.load(open(filepath, 'r'))
    old_and_new = old+new
    with open(filepath, 'w') as fh:
      json.dump(old_and_new, fh)
    return HttpResponse('')
