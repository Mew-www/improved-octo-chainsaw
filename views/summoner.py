# Import @decorators
from django.views.decorators.http import require_http_methods

# Import responses
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

# Import abstractions
from league.lib.cached_region import list_region
from league.lib import riotapi

# Import utilities
import json, re, base64

# Import cache
from django.core.cache import cache

@require_http_methods(["GET"])
def get_by_name(request):

  # Fetch arguments
  region = request.GET.get("region", None)
  name   = request.GET.get("name", None)
  if (name is None or
      region is None):
    return HttpResponseBadRequest("Missing arg name/region in querystring")

  # Validate arguments
  region_query = list_region()
  if not region_query['success']:
    return HttpResponseServerError(region_query['data'])

  if region.upper() not in region_query['data']:
    return HttpResponseBadRequest("Invalid or unsupported region.")

  if (len(name) < 3 or
      len(name) > 16):
    return HttpResponseBadRequest("Invalid summoner name.")

  # (check cache) If context is "current game lookup", as account data isn't going to change mid-match
  in_match_id = request.GET.get("inmatch", None)
  if in_match_id is not None:
    datajson = cache.get('summoner_by_name'+base64.b64encode(name.encode('utf-8')).decode('utf-8')+'in_match'+in_match_id, None)
    if datajson:
      return HttpResponse(datajson)

  # (GET) Summoner basedata
  r = riotapi.get(riotapi.platform(region)
                  + "/lol/summoner/v3/summoners/by-name/"+name.lower())
  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 404:
    return HttpResponseNotFound("Summoner not found.")
  if r['status'] == 200:
    summoner = r['data']
  else:
    return HttpResponseServerError(json.dumps(r))

  # https://developer.riotgames.com/api-methods/#summoner-v3/GET_getBySummonerName
  datajson = json.dumps({
    "id": summoner['id'],
    "name": summoner['name'],
    "icon": summoner['profileIconId'],
    "account": summoner['accountId'],
    "level": summoner['summonerLevel']
  })

  # (save to cache) If context is "current game lookup", as account data isn't going to change mid-match
  in_match_id = request.GET.get("inmatch", None)
  if in_match_id is not None:
    cache.set('summoner_by_name'+base64.b64encode(name.encode('utf-8')).decode('utf-8')+'in_match'+in_match_id, datajson, 30*60) # 30 minutes

  return HttpResponse(datajson)

def get_by_id(request):

  # Fetch arguments
  region     = request.GET.get("region", None)
  account_id = request.GET.get("account_id", None)
  if (account_id is None or
      region is None):
    return HttpResponseBadRequest("Missing arg account_id/region in querystring")

  # Validate arguments
  region_query = list_region()
  if not region_query['success']:
    return HttpResponseServerError(region_query['data'])

  if region.upper() not in region_query['data']:
    return HttpResponseBadRequest("Invalid or unsupported region.")

  if not account_id.isdigit():
    return HttpResponseBadRequest("Invalid account id")

  # (GET) Summoner basedata
  r = riotapi.get(riotapi.platform(region)
                  + "/lol/summoner/v3/summoners/by-account/"+account_id)
  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 404:
    return HttpResponseNotFound("Summoner not found.")
  if r['status'] == 200:
    summoner = r['data']
  else:
    return HttpResponseServerError(json.dumps(r))

  # https://developer.riotgames.com/api-methods/#summoner-v3/GET_getByAccountId
  datajson = json.dumps({
    "id": summoner['id'],
    "name": summoner['name'],
    "icon": summoner['profileIconId'],
    "account": summoner['accountId'],
    "level": summoner['summonerLevel']
  })

  return HttpResponse(datajson)
