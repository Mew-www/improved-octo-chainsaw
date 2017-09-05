from djproject.prod_settings import MYSQL_LEAGUE_USER, MYSQL_LEAGUE_PW, MYSQL_LEAGUE_DBNAME
import MySQLdb as MDB
import json

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

"""
Add match to cache db
"""
def add_match_details(match_id, region, jsondump):
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "INSERT INTO MatchDetails (MatchId, Region, Content)"
      + " VALUES (%s, (SELECT ID FROM Region WHERE Name=%s), %s)")
    cursor.execute(escaped_sqlstr, (match_id, region, jsondump))
    dbh.commit()
    dbh.close()

  except MDB.Error as e:
    return {
      "success": False,
      "data": "MySQLdb Generic Error: " + str(e.args[0]) + ((" " + str(e.args[1])) if len(e.args) > 1 else "")
    }

  except MDB.IntegrityError as e:
    return {
      "success": False,
      "data": "MySQLdb Integrity Error: " + str(e.args[0]) + ((" " + str(e.args[1])) if len(e.args) > 1 else "")
    }

  return {
    "success": True,
    "data": "Saved matchdata successfully"
  }

"""
Add timeline to cache db
"""
def add_match_timeline(match_id, region, jsondump):
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "INSERT INTO MatchTimeline (MatchId, Region, Content)"
      + " VALUES (%s, (SELECT ID FROM Region WHERE Name=%s), %s)")
    cursor.execute(escaped_sqlstr, (match_id, region, jsondump))
    dbh.commit()
    dbh.close()

  except MDB.Error as e:
    return {
      "success": False,
      "data": "MySQLdb Generic Error: " + str(e.args[0]) + ((" " + str(e.args[1])) if len(e.args) > 1 else "")
    }

  except MDB.IntegrityError as e:
    return {
      "success": False,
      "data": "MySQLdb Integrity Error: " + str(e.args[0]) + ((" " + str(e.args[1])) if len(e.args) > 1 else "")
    }

  return {
    "success": True,
    "data": "Saved matchdata successfully"
  }

"""
Get match record
"""
def get_match_details(match_id, region):
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "SELECT Content"
      + " FROM MatchDetails"
      + " WHERE MatchId = %s AND Region = (SELECT ID FROM Region WHERE Name=%s)")
    cursor.execute(escaped_sqlstr, (match_id, region))
    result = cursor.fetchone()
    if not result:
      return {
        "success": True,
        "data": None # Not found
      }
    # Else unpack
    content = result[0]
    dbh.close()

  except MDB.Error as e:
    return {
      "success": False,
      "data": "MySQLdb Generic Error: " + str(e.args[0]) + ((" " + str(e.args[1])) if len(e.args) > 1 else "")
    }

  except MDB.IntegrityError as e:
    return {
      "success": False,
      "data": "MySQLdb Integrity Error: " + str(e.args[0]) + ((" " + str(e.args[1])) if len(e.args) > 1 else "")
    }

  return {
    "success": True,
    "data": json.loads(content)
  }

"""
Get timeline record
"""
def get_match_timeline(match_id, region):
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "SELECT Content"
      + " FROM MatchTimeline"
      + " WHERE MatchId = %s AND Region = (SELECT ID FROM Region WHERE Name=%s)")
    cursor.execute(escaped_sqlstr, (match_id, region))
    result = cursor.fetchone()
    if not result:
      return {
        "success": True,
        "data": None # Not found
      }
    # Else unpack
    content = result[0]
    dbh.close()

  except MDB.Error as e:
    return {
      "success": False,
      "data": "MySQLdb Generic Error: " + str(e.args[0]) + ((" " + str(e.args[1])) if len(e.args) > 1 else "")
    }

  except MDB.IntegrityError as e:
    return {
      "success": False,
      "data": "MySQLdb Integrity Error: " + str(e.args[0]) + ((" " + str(e.args[1])) if len(e.args) > 1 else "")
    }

  return {
    "success": True,
    "data": json.loads(content)
  }
