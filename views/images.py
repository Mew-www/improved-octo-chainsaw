# Import @decorators
from django.views.decorators.http import condition, require_http_methods

# Import responses
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

# Import settings (hidden_static_files)
from djproject.prod_settings import DATADRAGON_STATIC_FOLDERPATH

# Import abstractions
from league.lib import ddragon

# Import utilities
import os

@condition(last_modified_func=ddragon.last_modified('profile_icon'))
@require_http_methods(["GET"])
def get_profile_icon(request, icon_id):

  supposed_filepath = os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'profile_icons', str(icon_id)+'.png')
  if not os.path.isfile(supposed_filepath):
    caching_successful = ddragon.cache_profile_icon(icon_id)
    if not caching_successful:
      return HttpResponseNotFound("Something went wrong, sorry but no can help.")
  image = open(supposed_filepath, 'rb').read()
  return HttpResponse(image, content_type='image/png')

@condition(last_modified_func=ddragon.last_modified('item_icon'))
@require_http_methods(["GET"])
def get_item_icon(request, icon_filename):

  supposed_filepath = os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'item_icons', icon_filename)
  if not os.path.isfile(supposed_filepath):
    caching_successful = ddragon.cache_item_icon(icon_filename)
    if not caching_successful:
      return HttpResponseNotFound("Something went wrong, sorry but no can help.")
  image = open(supposed_filepath, 'rb').read()
  return HttpResponse(image, content_type='image/png')

@condition(last_modified_func=ddragon.last_modified('champion_square'))
@require_http_methods(["GET"])
def get_champion_square(request, champion_name):

  supposed_filepath = os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'champion_squares', champion_name+'.png')
  if not os.path.isfile(supposed_filepath):
    caching_successful = ddragon.cache_champion_square(champion_name)
    if not caching_successful:
      return HttpResponseNotFound("Something went wrong, sorry but no can help.")
  image = open(supposed_filepath, 'rb').read()
  return HttpResponse(image, content_type='image/png')

@condition(last_modified_func=ddragon.last_modified('summonerspell_icon'))
@require_http_methods(["GET"])
def get_summonerspell_icon(request, summonerspell_name):

  supposed_filepath = os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'summonerspell_icons', summonerspell_name+'.png')
  if not os.path.isfile(supposed_filepath):
    caching_successful = ddragon.cache_summonerspell_icon(summonerspell_name)
    if not caching_successful:
      return HttpResponseNotFound("Something went wrong, sorry but no can help.")
  image = open(supposed_filepath, 'rb').read()
  return HttpResponse(image, content_type='image/png')

