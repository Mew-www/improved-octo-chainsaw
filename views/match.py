# Import @decorators
from django.views.decorators.http import require_http_methods

# Import responses
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

# Import abstractions
from league.lib.cached_region import list_region
from league.lib.cached_match import add_match_details, add_match_timeline, get_match_details, get_match_timeline
from league.lib import riotapi

# Import utilities
import json

@require_http_methods(["GET"])
def get_single_match(request):

  # Fetch arguments
  match_id = request.GET.get("match_id", None)
  region   = request.GET.get("region", None)
  if (match_id is None or
      region is None):
    return HttpResponseBadRequest("Missing arg match_id/region in querystring")

  # Validate arguments
  region_query = list_region()
  if not region_query['success']:
    return HttpResponseServerError(region_query['data'])

  if region.upper() not in region_query['data']:
    return HttpResponseBadRequest("Invalid or unsupported region.")

  if not match_id.isdigit():
    return HttpResponseBadRequest("Invalid match id.")

  # Check if match data exists in cache
  find_query = get_match_details(match_id, region.upper())
  if not find_query['success']:
    return HttpResponseServerError(find_query['data'])
  elif find_query['data'] is None:
    # Didn't exist so fetch
    r = riotapi.get(riotapi.platform(region)
                    + "/lol/match/v3/matches/"+match_id)

    if not r['success']:
      return HttpResponseServerError(json.dumps(r))
    if r['status'] == 404:
      return HttpResponseNotFound("No matching match was found.")
    if r['status'] == 200:
      # On success add it to cache and return
      update_query = add_match_details(match_id, region.upper(), json.dumps(r['data']))
      return HttpResponse(json.dumps(r['data'], indent=4))
    else:
      return HttpResponseServerError(json.dumps(r))
  else:
    # Matchdata existed in cache so return it, it's not gonna need update anyway since it's a singular old match
    return HttpResponse(json.dumps(find_query['data'], indent=4))

@require_http_methods(["GET"])
def get_single_timeline(request):

  # Fetch arguments
  match_id = request.GET.get("match_id", None)
  region   = request.GET.get("region", None)
  if (match_id is None or
      region is None):
    return HttpResponseBadRequest("Missing arg match_id/region in querystring")

  # Validate arguments
  region_query = list_region()
  if not region_query['success']:
    return HttpResponseServerError(region_query['data'])

  if region.upper() not in region_query['data']:
    return HttpResponseBadRequest("Invalid or unsupported region.")

  if not match_id.isdigit():
    return HttpResponseBadRequest("Invalid match id.")

  # Check if match-timeline exists in cache
  find_query = get_match_timeline(match_id, region.upper())
  if not find_query['success']:
    return HttpResponseServerError(find_query['data'])
  elif find_query['data'] is None:
    # Didn't exist so fetch
    r = riotapi.get(riotapi.platform(region)
                    + "/lol/match/v3/timelines/by-match/"+match_id)

    if not r['success']:
      return HttpResponseServerError(json.dumps(r))
    if r['status'] == 404:
      return HttpResponseNotFound("No matching match was found.")
    if r['status'] == 200:
      # On success add it to cache and return
      update_query = add_match_timeline(match_id, region.upper(), json.dumps(r['data']))
      return HttpResponse(json.dumps(r['data'], indent=4))
    else:
      return HttpResponseServerError(json.dumps(r))
  else:
    # Match-timeline existed in cache so return it, it's not gonna need update anyway since it's from a singular old match
    return HttpResponse(json.dumps(find_query['data'], indent=4))
