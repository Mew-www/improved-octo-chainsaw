# Import @decorators
from django.views.decorators.http import require_http_methods

# Import responses
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

# Import abstractions
from league.lib.cached_static import replace_champion_metadata, replace_item_metadata, replace_summonerspell_metadata
from league.lib.cached_static import list_champion, list_item, list_summonerspell
from league.lib import riotapi

# Import utilities
import json

"""
  Returns array of {"id": id, "name": name} -objects
"""
@require_http_methods(["GET"])
def list_champions(request):
  # Just list all champion <=> ID mappings
  champions_query = list_champion()
  if not champions_query['success']:
    return HttpResponseServerError(champions_query['data'])
  return JsonResponse(champions_query['data'], safe=False) # We return an array of dicts

"""
  Returns array of { ... } -objects
"""
@require_http_methods(["GET"])
def all_items(request):
  # List all items along with their metadata
  items_query = list_item()
  if not items_query['success']:
    return HttpResponseServerError(items_query['data'])
  return JsonResponse(json.loads(items_query['data']))

"""
  Returns array of { ... } -objects
"""
@require_http_methods(["GET"])
def all_summonerspells(request):
  # List summonerspells' basic data + range + cooldown
  summspell_query = list_summonerspell()
  if not summspell_query['success']:
    return HttpResponseServerError(summspell_query['data'])
  return JsonResponse(json.loads(summspell_query['data']))

@require_http_methods(["GET"])
def refresh_all_champion_metadata(request):

  # (GET) dump of all Champion metadata from STATIC API
  r = riotapi.get(riotapi.platform("EUW")
      +"/lol/static-data/v3/champions"
      + "?champListData=allytips"
      + "&champListData=enemytips"
      + "&champListData=passive"
      + "&champListData=spells", is_static=True)
  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 200:
    championdata = r['data']
  else:
    return HttpResponseServerError(json.dumps(r))

  # Re-structure dataset
  champions       = []
  champion_skills = []
  champion_tips   = []

  for champion_key in championdata['data']:
    champion = championdata['data'][champion_key]

    # Add champion <=> ID mapping
    champions.append({
      "id":   champion['id'],
      "name": champion['name'],
      "ddragon_key": champion['key']
    })
    # Add passive skill
    champion_skills.append({
      "champion":    champion['id'],
      "name":        champion['passive']['name'],
      "description": champion['passive']['description'],
      "cooldowns":   "-1", # this is argueable but meh...
      "slot":        0
    })
    # Add QWER
    champion_skills.extend([
      {
        "champion":    champion['id'],
        "name":        skill['name'],
        "description": skill['description'],
        "cooldowns":   "/".join(map(lambda n: str(n), skill['cooldown'])),
        "slot":        (i+1)
      } for i, skill in enumerate(champion['spells'])])
    # Add tips "for"
    champion_tips.extend([
      {
        "champion":    champion['id'],
        "vs":          "FALSE",
        "description": tip
      } for tip in champion['allytips']])
    # Add tips "against"
    champion_tips.extend([
      {
        "champion":    champion['id'],
        "vs":          "TRUE",
        "description": tip
      } for tip in champion['enemytips']])

  # Update Champion basedata to/in cache
  update_query = replace_champion_metadata(champions, champion_skills, champion_tips)
  if not update_query['success']:
    return HttpResponseServerError(update_query['data'])
  else:
    pass # Successfully updated

  return JsonResponse({"success": True, "data": "Successfully updated all Champion metadata"})

@require_http_methods(["GET"])
def refresh_all_item_metadata(request):

  # (GET) dump of SELECTED Items' metadata from STATIC API
  r = riotapi.get(riotapi.platform("EUW")
      + "/lol/static-data/v3/items"
      + "?itemListData=from"
      + "&itemListData=into"
      + "&itemListData=gold"
      + "&itemListData=image"
      + "&itemListData=stats", is_static=True)
  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 200:
    itemdata = r['data']
  else:
    return HttpResponseServerError(json.dumps(r))

  # Update Itemdata to/in cache
  items_by_key = itemdata['data']
  for k in items_by_key:
    items_by_key[k]["ddragon_key"] = items_by_key[k]['image']['full']
    del items_by_key[k]['image']

  update_query = replace_item_metadata(json.dumps(items_by_key))
  if not update_query['success']:
    return HttpResponseServerError(update_query['data'])
  else:
    pass # Successfully updated

  return JsonResponse({"success": True, "data": "Successfully updated all Item metadata"})

@require_http_methods(["GET"])
def refresh_all_summonerspell_metadata(request):

  # (GET) dump of SELECTED summonerspell metadata from STATIC API
  r = riotapi.get(riotapi.platform("EUW")
      + "/lol/static-data/v3/summoner-spells"
      + "?spellListData=range"
      + "&spellListData=cooldown", is_static=True)
  if not r['success']:
    return HttpResponseServerError(json.dumps(r))
  if r['status'] == 200:
    itemdata = r['data']
  else:
    return HttpResponseServerError(json.dumps(r))

  # Update Summonerspells' data to/in cache
  update_query = replace_summonerspell_metadata(json.dumps(r['data']['data']))
  if not update_query['success']:
    return HttpResponseServerError(update_query['data'])
  else:
    pass # Successfully updated

  return JsonResponse({"success": True, "data": "Successfully updated all Summonerspell metadata"})
