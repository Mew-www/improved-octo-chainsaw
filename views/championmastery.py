# Import @decorators
from django.views.decorators.http import require_http_methods

# Import responses
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

# Import abstractions
from league.lib.cached_region   import list_region
from league.lib import riotapi

# Import utilities
import json, re

@require_http_methods(["GET"])
def get_all_uptodate(request):

  # Fetch arguments
  region      = request.GET.get("region", None)
  summoner_id = request.GET.get("summoner_id", None)
  if (region is None or
      summoner_id is None):
    return HttpResponseBadRequest("Missing arg region/summoner_id in querystring")

  # Validate arguments
  region_query = list_region()
  if not region_query['success']:
    return HttpResponseServerError(region_query['data'])

  if region.upper() not in region_query['data']:
    return HttpResponseBadRequest("Invalid or unsupported region.")

  if not summoner_id.isdigit():
    return HttpResponseBadRequest("Invalid summoner id")

  # (GET) Summoner championmasteries
  r = riotapi.get(riotapi.platform(region)
      + "/lol/champion-mastery/v3/champion-masteries/by-summoner/"+summoner_id, method="championmastery/v3", region=region)
  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 404:
    return HttpResponseNotFound("Summoner not found.")
  if r['status'] == 200:
    masteries = r['data']
  else:
    return HttpResponseServerError(json.dumps(r))

  # https://developer.riotgames.com/api-methods/#champion-mastery-v3/GET_getChampionMastery
  return HttpResponse(json.dumps(masteries))
