# Import configs
from djproject.prod_settings import MYSQL_LEAGUE_USER, MYSQL_LEAGUE_PW, MYSQL_LEAGUE_DBNAME
from djproject.prod_settings import RIOT_APIKEY
from djproject.prod_settings import LOG_PATH

# Import DatabaseConnector (for [persistent] cache DB)
import MySQLdb as MDB

# Import cache (memcached)
from django.core.cache import cache

# Import utils
import time, requests, json

def __get_cursor_and_handle():
  dbh = MDB.connect(
    host="localhost",
    user=MYSQL_LEAGUE_USER,
    passwd=MYSQL_LEAGUE_PW,
    db=MYSQL_LEAGUE_DBNAME,
    use_unicode=True,
    charset="utf8"
  )
  dbc = dbh.cursor()
  dbh.set_character_set('utf8')
  dbc.execute('SET NAMES utf8;')
  dbc.execute('SET CHARACTER SET utf8;')
  dbc.execute('SET character_set_connection=utf8;')
  return dbc, dbh

def compare_ratelimits_to_requesthistory(ratelimits, requesthistory):
  epoch_now = int(time.time())
  for rl in ratelimits:
    max_requests_in_timeframe   = int(rl[0])
    timeframe_size              = int(rl[1])
    ratelimited_timeframe_start = epoch_now - timeframe_size
    requests_done_in_timeframe  = list(filter(lambda timestamp: timestamp >= ratelimited_timeframe_start, requesthistory))
    # Compare done requests to permitted amount of requests
    if len(requests_done_in_timeframe) >= max_requests_in_timeframe: # Greater-than, in case if ratelimit lowers by time
      return True, timeframe_size-(epoch_now-requests_done_in_timeframe[-1]) # timeframe_size - time between now and last request caught in timeframe
  # Else, if all checks
  return False, None # False as in "ratelimit not exceeded"

def headers_to_normal_dict(headers_obj):
  return {key:val for key,val in headers_obj.items()}

"""
Standard regional RIOT API platform prefixes
"""
def platform(region):
  if region.upper() == "EUW":
    return "https://euw1.api.riotgames.com"
  if region.upper() == "EUNE":
    return "https://eun1.api.riotgames.com"
  raise ValueError('Undefined region<=>platform mapping')

"""
Wrapper to check Rate Limiting then create HTTP GET request to RIOT public API
"""
def get(url, method=None, region=None, is_static=False):

  # EITHER static is True, OR both method and region must exist
  if is_static == False and (method is None or region is None):
    return {
      "success": False,
      "status": 500,
      "data": "Server error. Invalid rate-limit args given to riotapi->get function."
    }

  try:
    # (Database Session Open)
    cursor, dbh = __get_cursor_and_handle()

    # (Database Query) LOCK RequestHistory TABLE to prevent (previously occuring) race condition (Unavoidable by merely using transactions)
    cursor.execute("LOCK TABLES RequestHistory WRITE")
    dbh.commit()

    if is_static:

      ######################
      # STATIC RATE LIMIT(S)
      ######################

      current_STATIC_ratelimits = cache.get('RL_STATIC', [[900001, 10]]) # EITHER get current rate limits from memory OR set default
      highest_STATIC_ratelimit = max(map(lambda rl: rl[0], current_STATIC_ratelimits))

      # (Database Query) FETCH RequestHistory
      cursor.execute("SELECT Timestamp FROM RequestHistory"
        + " WHERE IsStatic=TRUE"
        + " ORDER BY Timestamp DESC"
        + " LIMIT " + str(highest_STATIC_ratelimit))
      timestamps = map(lambda row: row[0], cursor.fetchall()) # Only timestamp column -> row[0]

      # COMPARE request history to rate limits
      rl_exceeded, retry_after = compare_ratelimits_to_requesthistory(current_STATIC_ratelimits, timestamps)
      if rl_exceeded:
          # (Database Query) No more database queries since quota full => UNLOCK (release) TABLE
          cursor.execute("UNLOCK TABLES")
          dbh.commit()
          # (Database Session Close)
          dbh.close()
          return {
            "success": False,
            "status": 418,
            "data": {'Retry-After': retry_after}
          }

    else: # if not a static API call

      ###################
      # APP RATE LIMIT(S)
      ###################

      current_APP_ratelimits = cache.get('RL_APP', [[900001, 10]])
      highest_APP_ratelimit = max(map(lambda rl: rl[0], current_APP_ratelimits))

      # (Database Query) FETCH RequestHistory
      cursor.execute("SELECT Timestamp FROM RequestHistory"
        + " WHERE IsStatic=FALSE AND Region=%s"
        + " ORDER BY Timestamp DESC"
        + " LIMIT " + str(highest_APP_ratelimit), (region, ))
      timestamps = map(lambda row: row[0], cursor.fetchall()) # Only timestamp column -> row[0]

      # COMPARE request history to rate limits
      rl_exceeded, retry_after = compare_ratelimits_to_requesthistory(current_APP_ratelimits, timestamps)
      if rl_exceeded:
        # (Database Query) No more database queries since quota full => UNLOCK (release) TABLE
        cursor.execute("UNLOCK TABLES")
        dbh.commit()
        # (Database Session Close)
        dbh.close()
        return {
          "success": False,
          "status": 418,
          "data": {'Retry-After': retry_after}
        }

      ######################
      # METHOD RATE LIMIT(S)
      ######################

      current_METHOD_ratelimits = cache.get('RL_METHOD_'+method, [[900001, 10]])
      highest_METHOD_ratelimit = max(map(lambda rl: rl[0], current_METHOD_ratelimits))

      # (Database Query) FETCH RequestHistory
      cursor.execute("SELECT Timestamp FROM RequestHistory"
        + " WHERE IsStatic=FALSE AND Region=%s AND Method=%s"
        + " ORDER BY Timestamp DESC"
        + " LIMIT " + str(highest_METHOD_ratelimit), (region, method))
      timestamps = map(lambda row: row[0], cursor.fetchall()) # Only timestamp column -> row[0]

      # COMPARE request history to rate limits
      rl_exceeded, retry_after = compare_ratelimits_to_requesthistory(current_METHOD_ratelimits, timestamps)
      if rl_exceeded:
        # (Database Query) No more database queries since quota full => UNLOCK (release) TABLE
        cursor.execute("UNLOCK TABLES")
        dbh.commit()
        # (Database Session Close)
        dbh.close()
        return {
          "success": False,
          "status": 418,
          "data": {'Retry-After': retry_after}
        }

    # If all rate-limit checks passed...

    ##############################################
    # UPDATING REQUEST HISTORY (prior API request)
    ##############################################

    # (Database Query) UPDATE the to-be-used key-use to RequestHistory (so we can release table lock)
    escaped_sqlstr = ("INSERT INTO RequestHistory (RequestURL, Timestamp, IsStatic, Region, Method)"
      + " VALUES (%s, %s, %s, %s, %s)")
    val_static = "TRUE" if is_static else "FALSE"
    val_region = region if region is not None else "NULL"
    val_method = method if method is not None else "NULL"
    cursor.execute(escaped_sqlstr, (url, int(time.time()), val_static, val_region, val_method))
    dbh.commit()

    # (Database Query) UNLOCK (release) TABLE
    cursor.execute("UNLOCK TABLES")
    dbh.commit()
    # (Database Session Close)
    dbh.close()

    # (GET) response from RIOT public API
    apikey_postfix = ("?api_key="+RIOT_APIKEY) if not "?" in url else ("&api_key="+RIOT_APIKEY)
    resp = requests.get(url + apikey_postfix)

    ############################################
    # UPDATING RATE LIMIT(S) (after API request)
    ############################################

    if resp.status_code != 200:
      # Log the error
      with open(LOG_PATH, 'a') as fh:
        fh.write('[%s UTC+0] API request returned non-200.\n' % time.strftime('%H:%M (%Ss) %d/%m/%Y', time.gmtime()))
        json.dump({
          'status_code': resp.status_code,
          'content': resp.text[0:100], # Limit this in case something like... massive, youknow, "too big", comes around.
          'headers': headers_to_normal_dict(resp.headers)
        }, fh)
        fh.write('\n\n')
    else:
      if is_static:
        # Update static-ratelimit
        static_rl = resp.headers.get('X-Method-Rate-Limit', None)
        if static_rl is not None:
          received_limits = list(map(lambda textual_rl: textual_rl.split(':'), static_rl.split(',')))
          old_limits = cache.get('RL_STATIC', None)
          if old_limits is None or json.dumps(sorted(old_limits, key=lambda x: x[1])) != json.dumps(sorted(received_limits, key=lambda x: x[1])):
            cache.set('RL_STATIC', received_limits, None) # Timeout = None = cache forever
            with open(LOG_PATH, 'a') as fh:
              fh.write('[%s UTC+0] Updated static-API cache-rate-limit since found a new one.\n' % time.strftime('%H:%M (%Ss) %d/%m/%Y', time.gmtime()))
              fh.write('Old rate limit: ' + (json.dumps(sorted(old_limits, key=lambda x: x[1])) if old_limits else 'None') + '\n')
              fh.write('New rate limit: ' + json.dumps(sorted(received_limits, key=lambda x: x[1])) + '\n')
              json.dump({
                'status_code': resp.status_code,
                'content': resp.text[0:100], # Limit this in case something like... massive, youknow, "too big", comes around.
                'headers': headers_to_normal_dict(resp.headers)
              }, fh)
              fh.write('\n\n')
        else:
          with open(LOG_PATH, 'a') as fh:
            fh.write('[%s UTC+0] A static-API request did not return method ratelimit, using defaults still.\n' % time.strftime('%H:%M (%Ss) %d/%m/%Y', time.gmtime()))
            json.dump({
              'status_code': resp.status_code,
              'content': resp.text[0:100], # Limit this in case something like... massive, youknow, "too big", comes around.
              'headers': headers_to_normal_dict(resp.headers)
            }, fh)
            fh.write('\n\n')
      else:
        # Update app-ratelimit
        app_rl = resp.headers.get('X-App-Rate-Limit', None)
        if app_rl is not None:
          received_limits = list(map(lambda textual_rl: textual_rl.split(':'), app_rl.split(',')))
          old_limits = cache.get('RL_APP', None)
          if old_limits is None or json.dumps(sorted(old_limits, key=lambda x: x[1])) != json.dumps(sorted(received_limits, key=lambda x: x[1])):
            cache.set('RL_APP', received_limits, None) # Timeout = None = cache forever
            with open(LOG_PATH, 'a') as fh:
              fh.write('[%s UTC+0] Updated app cache-rate-limit since found a new one.\n' % time.strftime('%H:%M (%Ss) %d/%m/%Y', time.gmtime()))
              fh.write('Old rate limit: ' + (json.dumps(sorted(old_limits, key=lambda x: x[1])) if old_limits else 'None') + '\n')
              fh.write('New rate limit: ' + json.dumps(sorted(received_limits, key=lambda x: x[1])) + '\n')
              json.dump({
                'status_code': resp.status_code,
                'content': resp.text[0:100], # Limit this in case something like... massive, youknow, "too big", comes around.
                'headers': headers_to_normal_dict(resp.headers)
              }, fh)
              fh.write('\n\n')
        else:
          with open(LOG_PATH, 'a') as fh:
            fh.write('[%s UTC+0] A NON-static-API request did not return app ratelimit, using defaults still.\n' % time.strftime('%H:%M (%Ss) %d/%m/%Y', time.gmtime()))
            json.dump({
              'status_code': resp.status_code,
              'content': resp.text[0:100], # Limit this in case something like... massive, youknow, "too big", comes around.
              'headers': headers_to_normal_dict(resp.headers)
            }, fh)
            fh.write('\n\n')
        # Update method-ratelimit
        method_rl = resp.headers.get('X-Method-Rate-Limit', None)
        if method_rl is not None:
          received_limits = list(map(lambda textual_rl: textual_rl.split(':'), method_rl.split(',')))
          old_limits = cache.get('RL_METHOD_', None)
          if old_limits is None or json.dumps(sorted(old_limits, key=lambda x: x[1])) != json.dumps(sorted(received_limits, key=lambda x: x[1])):
            cache.set('RL_METHOD_'+method, received_limits, None) # Timeout = None = cache forever
            with open(LOG_PATH, 'a') as fh:
              fh.write('[%s UTC+0] Updated method cache-rate-limit since found a new one.\n' % time.strftime('%H:%M (%Ss) %d/%m/%Y', time.gmtime()))
              fh.write('Old rate limit: ' + (json.dumps(sorted(old_limits, key=lambda x: x[1])) if old_limits else 'None') + '\n')
              fh.write('New rate limit: ' + json.dumps(sorted(received_limits, key=lambda x: x[1])) + '\n')
              json.dump({
                'status_code': resp.status_code,
                'content': resp.text[0:100], # Limit this in case something like... massive, youknow, "too big", comes around.
                'headers': headers_to_normal_dict(resp.headers)
              }, fh)
              fh.write('\n\n')
        else:
          with open(LOG_PATH, 'a') as fh:
            fh.write('[%s UTC+0] A NON-static-API request did not return method ratelimit, using defaults still.\n' % time.strftime('%H:%M (%Ss) %d/%m/%Y', time.gmtime()))
            json.dump({
              'status_code': resp.status_code,
              'content': resp.text[0:100], # Limit this in case something like... massive, youknow, "too big", comes around.
              'headers': headers_to_normal_dict(resp.headers)
            }, fh)
            fh.write('\n\n')

    try:
        data = resp.json()
    except ValueError:
        data = resp.text
    return {
      "success": True,
      "status": resp.status_code,
      "data": data
    }

  except MDB.Error as e:
    return {
      "success": False,
      "status": 500,
      "data": "MySQLdb Generic Error" #"MySQLdb Generic Error: %s" % (e.args[0])
    }

  except MDB.IntegrityError as e:
    return {
      "success": False,
      "status": 500,
      "data": "MySQLdb Integrity Error" #"MySQLdb IntegrityError: %s" % (e.args[0])
    }