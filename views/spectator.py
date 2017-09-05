# Import @decorators
from django.views.decorators.http import require_http_methods

# Import responses
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

# Import abstractions
from league.lib.cached_region import list_region
from league.lib import riotapi

# Import utilities
import json

@require_http_methods(["GET"])
def get_current_gameinfo(request):

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

  # (GET) Current gameinfo
  r = riotapi.get(riotapi.platform(region)
      + "/lol/spectator/v3/active-games/by-summoner/"+summoner_id, method="spectator/v3", region=region)

  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 404:
    return HttpResponseNotFound("Summoner not currently in a spectateable game")
  if r['status'] == 200:
    gameinfo = r['data']
    return HttpResponse(json.dumps(r['data']))
  else:
    return HttpResponseServerError(json.dumps(r))

@require_http_methods(["GET"])
def get_odd_api_current_gameinfo(request):

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

  region_to_p = {"EUW": "EUW1", "EUNE": "EUN1"}
  platform    = region_to_p[region.upper()] if (region.upper() in region_to_p) else None
  if platform is None:
    return HttpResponseServerError("Undefined platform for given region")

  if not summoner_id.isdigit():
    return HttpResponseBadRequest("Invalid summoner id")

  # (GET) Current gameinfo
  r = riotapi.get("https://"+region.lower()+".api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/"+platform+"/"+summoner_id, method="odd-api", region=region)
  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 404:
    return HttpResponseNotFound("Summoner not currently in a spectateable game")
  if r['status'] == 200:
    gameinfo = r['data']
    return HttpResponse(json.dumps(r['data']))
  else:
    return HttpResponseServerError(json.dumps(r))
