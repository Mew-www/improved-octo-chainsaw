from djproject.prod_settings import DATADRAGON_DAILY_VERSION_FILEPATH, DATADRAGON_STATIC_FOLDERPATH
from league.lib import riotapi
import os, json, time, requests, datetime

# Check (maximum once-a-24h) if ddragon version is up to date
def should_check_version():
  if not os.path.isfile(DATADRAGON_DAILY_VERSION_FILEPATH):
    return True
  with open(DATADRAGON_DAILY_VERSION_FILEPATH, 'r') as fh:
    ddragon_metadata = json.load(fh)
  if ddragon_metadata['epoch_sec_timestamp']+(60*60*24) < time.time():
    return True
  return False

def update_version():
  r = riotapi.get("https://euw1.api.riotgames.com/lol/static-data/v3/versions", is_static=True)
  if not r['success']:
    return False
  newest_euw_version = r['data'][0]
  with open(DATADRAGON_DAILY_VERSION_FILEPATH, 'w') as fh:
    json.dump({
      'epoch_sec_timestamp': time.time(),
      'version': newest_euw_version
    }, fh)
  return True

def last_modified(resource_type):
  def check_mtime(request, **kwargs):
    if resource_type == 'profile_icon':
      filepath = os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'profile_icons', str(kwargs['icon_id'])+'.png')
    elif resource_type == 'item_icon':
      filepath = os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'item_icons', str(kwargs['icon_filename']))
    elif resource_type == 'champion_square':
      filepath = os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'champion_squares', str(kwargs['champion_name'])+'.png')
    elif resource_type == 'summonerspell_icon':
      filepath = os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'summonerspell_icons', str(kwargs['summonerspell_name'])+'.png')
    else:
      raise ValueError('Invalid resource type in Last-Modified check')
    if not os.path.isfile(filepath):
      return datetime.datetime.now()
    return datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
  return check_mtime

# Error => False, Success => True
def cache_profile_icon(icon_id):
  if should_check_version():
    version_updated = update_version()
    if not version_updated:
      return False
  # Get current version (kinda redundant but, meh)
  with open(DATADRAGON_DAILY_VERSION_FILEPATH, 'r') as fh:
    ddragon_metadata = json.load(fh)
  current_version = ddragon_metadata['version']
  # Fetch the file
  r = requests.get("http://ddragon.leagueoflegends.com/cdn/"+str(current_version)+"/img/profileicon/"+str(icon_id)+".png", stream=True)
  if r.status_code != 200:
    return False
  with open(os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'profile_icons', str(icon_id)+'.png'), 'wb') as fh:
    for chunk in r:
      fh.write(chunk)
  return True

# Error => False, Success => True
def cache_item_icon(icon_filename):
  if should_check_version():
    version_updated = update_version()
    if not version_updated:
      return False
  # Get current version (kinda redundant but, meh)
  with open(DATADRAGON_DAILY_VERSION_FILEPATH, 'r') as fh:
    ddragon_metadata = json.load(fh)
  current_version = ddragon_metadata['version']
  # Fetch the file
  r = requests.get("http://ddragon.leagueoflegends.com/cdn/"+str(current_version)+"/img/item/"+icon_filename, stream=True)
  if r.status_code != 200:
    return False
  with open(os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'item_icons', icon_filename), 'wb') as fh:
    for chunk in r:
      fh.write(chunk)
  return True

# Error => False, Success => True
def cache_champion_square(champion_name):
  if should_check_version():
    version_updated = update_version()
    if not version_updated:
      return False
  # Get current version (kinda redundant but, meh)
  with open(DATADRAGON_DAILY_VERSION_FILEPATH, 'r') as fh:
    ddragon_metadata = json.load(fh)
  current_version = ddragon_metadata['version']
  # Fetch the file
  r = requests.get("http://ddragon.leagueoflegends.com/cdn/"+str(current_version)+"/img/champion/"+champion_name+".png", stream=True)
  if r.status_code != 200:
    return False
  with open(os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'champion_squares', champion_name+'.png'), 'wb') as fh:
    for chunk in r:
      fh.write(chunk)
  return True

# Error => False, Success => True
def cache_summonerspell_icon(summonerspell_name):
  if should_check_version():
    version_updated = update_version()
    if not version_updated:
      return False
  # Get current version (kinda redundant but, meh)
  with open(DATADRAGON_DAILY_VERSION_FILEPATH, 'r') as fh:
    ddragon_metadata = json.load(fh)
  current_version = ddragon_metadata['version']
  # Fetch the file
  r = requests.get("http://ddragon.leagueoflegends.com/cdn/"+str(current_version)+"/img/spell/"+summonerspell_name+".png", stream=True)
  if r.status_code != 200:
    return False
  with open(os.path.join(DATADRAGON_STATIC_FOLDERPATH, 'summonerspell_icons', summonerspell_name+'.png'), 'wb') as fh:
    for chunk in r:
      fh.write(chunk)
  return True
