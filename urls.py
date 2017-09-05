from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from .views.templating import render_template

from .views import static          # Static gamefile data
from .views import images          # Icons
from .views import summoner        # Generic account data
from .views import rankings        # Rank by queuetype
from .views import championmastery # Champion masteries
from .views import spectator       # Current game
from .views import match           # Single (historic) game
from .views import matchhistory    # Match identifiers
from .views.explorer import SeenEntityView, FailedRequestsView
from .views import logging

urlpatterns = [

  url(r'^api/', include([

    url(r'^static/', include([
      url(r'^champions$',              static.list_champions),                     # no args
      url(r'^champions/refresh$',      static.refresh_all_champion_metadata),      # no args
      url(r'^items$',                  static.all_items),                          # no args
      url(r'^items/refresh$',          static.refresh_all_item_metadata),          # no args
      url(r'^summonerspells$',         static.all_summonerspells),                 # no args
      url(r'^summonerspells/refresh$', static.refresh_all_summonerspell_metadata), # no args

      url(r'assets/', include([
        url(r'item_icons/(?P<icon_filename>\w+\.png)$',              images.get_item_icon),
        url(r'profile_icons/(?P<icon_id>\w+).png$',                  images.get_profile_icon),
        url(r'champion_squares/(?P<champion_name>\w+).png$',         images.get_champion_square),
        url(r'summonerspell_icons/(?P<summonerspell_name>\w+).png$', images.get_summonerspell_icon),
      ])),
    ])),

    url(r'^player/', include([
      url(r'^basic_data_by_name$', summoner.get_by_name), # args GET[region] & GET[name] <-- start of ClientSide stuff since name <=> ID may be changed
      url(r'^basic_data_by_id$',   summoner.get_by_id),   # args GET[region] & GET[account_id]

      # All at once (if available) [soloq & flex5v5 & flex3v3] rankings
      url(r'^rankings$', rankings.get_all_uptodate), # args GET[region] & GET[summoner_id]

      # Champion mastery points
      url(r'^championmasteries$',  championmastery.get_all_uptodate),   # args GET[region] & GET[summoner_id]

      # Current game
      url(r'^current_game$', spectator.get_current_gameinfo), # args GET[region] & GET[summoner_id]
      url(r'^deprecated_api_current_game$', spectator.get_odd_api_current_gameinfo), # args GET[region] & GET[summoner_id]

      # Match IDs of past games
      url(r'^history/solo/preview$',          matchhistory.get_past_ranked_soloduo_matchids),      # args GET[region] & GET[account_id]
      url(r'^history/flex/preview$',          matchhistory.get_past_ranked_flex_matchids),         # args GET[region] & GET[account_id]
      url(r'^history/solo_and_flex/preview$', matchhistory.get_past_ranked_flex_soloduo_matchids), # args GET[region] & GET[account_id]

    ])),

    # Match details
    url(r'^match/details$',  match.get_single_match),    # args GET[region] & GET[match_id]
    url(r'^match/timeline$', match.get_single_timeline), # args GET[region] & GET[match_id]

    # Explorer API
    url(r'^explorer/', include([
      url(r'^seen_people$',     csrf_exempt(SeenEntityView.as_view(filename='traversed_people.json'))),
      url(r'^seen_matches$',    csrf_exempt(SeenEntityView.as_view(filename='traversed_matches.json'))),
      url(r'^seen_timelines$',  csrf_exempt(SeenEntityView.as_view(filename='traversed_timelines.json'))),
      url(r'^failed_requests$', csrf_exempt(FailedRequestsView.as_view(filename='failed_requests.json')))
    ])),

    # Logging
    url(r'^log$', csrf_exempt(logging.log)),

  ])),

  # Last (by default) render a given (app based) template name
  url(r'^(?P<template_name>\w+)/$', render_template),
]
