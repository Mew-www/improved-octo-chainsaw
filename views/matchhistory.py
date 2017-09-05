from djproject.prod_settings import CURRENT_SEASON

# Import @decorators
from django.views.decorators.http import require_http_methods

# Import responses
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

# Import abstractions
from league.lib.cached_region import list_region
from league.lib import riotapi

# Import utilities
import json, time

# Import cache (memcached)
from django.core.cache import cache

@require_http_methods(["GET"])
def get_past_ranked_soloduo_matchids(request):

  # Fetch arguments
  region     = request.GET.get("region", None)
  account_id = request.GET.get("account_id", None)
  if (region is None or
      account_id is None):
    return HttpResponseBadRequest("Missing arg region/account_id in querystring")

  # Validate arguments
  region_query = list_region()
  if not region_query['success']:
    return HttpResponseServerError(region_query['data'])

  if region.upper() not in region_query['data']:
    return HttpResponseBadRequest("Invalid or unsupported region.")

  if not account_id.isdigit():
    return HttpResponseBadRequest("Invalid account id")

  # (check cache) If context is "current game lookup", as account data isn't going to change mid-match
  in_match_id = request.GET.get("inmatch", None)
  if in_match_id is not None:
    datajson = cache.get('soloq_history_by_accountid'+account_id+'in_match'+in_match_id, None)
    if datajson:
      return HttpResponse(datajson)

  # (GET) List of past games up to maxcount
  r = riotapi.get(riotapi.platform(region)
      + "/lol/match/v3/matchlists/by-account/"+account_id
      + "?queue=420"
      + "&season="+str(CURRENT_SEASON), method="match/v3/matchlist", region=region)
  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 404:
    return HttpResponseNotFound("No matching account was found.")
  if r['status'] == 200:
    history_matches = r['data']
  else:
    return HttpResponseServerError(json.dumps(r))

  # https://developer.riotgames.com/api-methods/#match-v3/GET_getMatchlist
  datajson = json.dumps(history_matches)

  # (save to cache) If context is "current game lookup", as game history isn't going to change mid-match
  in_match_id = request.GET.get("inmatch", None)
  if in_match_id is not None:
    cache.set('soloq_history_by_accountid'+account_id+'in_match'+in_match_id, datajson, 30*60) # 30 minutes

  return HttpResponse(datajson)

@require_http_methods(["GET"])
def get_past_ranked_flex_matchids(request):

  # Fetch arguments
  region     = request.GET.get("region", None)
  account_id = request.GET.get("account_id", None)
  if (region is None or
      account_id is None):
    return HttpResponseBadRequest("Missing arg region/account_id in querystring")

  # Validate arguments
  region_query = list_region()
  if not region_query['success']:
    return HttpResponseServerError(region_query['data'])

  if region.upper() not in region_query['data']:
    return HttpResponseBadRequest("Invalid or unsupported region.")

  if not account_id.isdigit():
    return HttpResponseBadRequest("Invalid account id")

  # (check cache) If context is "current game lookup", as account data isn't going to change mid-match
  in_match_id = request.GET.get("inmatch", None)
  if in_match_id is not None:
    datajson = cache.get('flexq_history_by_accountid'+account_id+'in_match'+in_match_id, None)
    if datajson:
      return HttpResponse(datajson)

  # (GET) List of past games up to maxcount
  r = riotapi.get(riotapi.platform(region)
      + "/lol/match/v3/matchlists/by-account/"+account_id
      + "?queue=440"
      + "&season="+str(CURRENT_SEASON), method="match/v3/matchlist", region=region)
  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 404:
    return HttpResponseNotFound("No matching account was found.")
  if r['status'] == 200: 
    history_matches = r['data']
  else:
    return HttpResponseServerError(json.dumps(r))

  # https://developer.riotgames.com/api-methods/#match-v3/GET_getMatchlist
  datajson = json.dumps(history_matches)

  # (save to cache) If context is "current game lookup", as game history isn't going to change mid-match
  in_match_id = request.GET.get("inmatch", None)
  if in_match_id is not None:
    cache.set('flexq_history_by_accountid'+account_id+'in_match'+in_match_id, datajson, 30*60) # 30 minutes

  return HttpResponse(datajson)

@require_http_methods(["GET"])
def get_past_ranked_flex_soloduo_matchids(request):

  # Fetch arguments
  region     = request.GET.get("region", None)
  account_id = request.GET.get("account_id", None)
  if (region is None or
      account_id is None):
    return HttpResponseBadRequest("Missing arg region/account_id in querystring")

  # Validate arguments
  region_query = list_region()
  if not region_query['success']:
    return HttpResponseServerError(region_query['data'])

  if region.upper() not in region_query['data']:
    return HttpResponseBadRequest("Invalid or unsupported region.")

  if not account_id.isdigit():
    return HttpResponseBadRequest("Invalid account id")

  # (check cache) If context is "current game lookup", as account data isn't going to change mid-match
  in_match_id = request.GET.get("inmatch", None)
  if in_match_id is not None:
    datajson = cache.get('soloandflexq_history_by_accountid'+account_id+'in_match'+in_match_id, None)
    if datajson:
      return HttpResponse(datajson)

  # (GET) List of past games up to maxcount
  r = riotapi.get(riotapi.platform(region)
      + "/lol/match/v3/matchlists/by-account/"+account_id
      + "?queue=420&queue=440"
      + "&season="+str(CURRENT_SEASON), method="match/v3/matchlist", region=region)
  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 404:
    return HttpResponseNotFound("No matching account was found.")
  if r['status'] == 200: 
    history_matches = r['data']
  else:
    return HttpResponseServerError(json.dumps(r))

  # https://developer.riotgames.com/api-methods/#match-v3/GET_getMatchlist
  datajson = json.dumps(history_matches)

  # (save to cache) If context is "current game lookup", as game history isn't going to change mid-match
  in_match_id = request.GET.get("inmatch", None)
  if in_match_id is not None:
    cache.set('soloandflexq_history_by_accountid'+account_id+'in_match'+in_match_id, datajson, 30*60) # 30 minutes

  return HttpResponse(datajson)
