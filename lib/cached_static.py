from djproject.prod_settings import MYSQL_LEAGUE_USER, MYSQL_LEAGUE_PW, MYSQL_LEAGUE_DBNAME
import MySQLdb as MDB

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
Delete all old Champion metadata from cache.
Insert the new in to cache.

args:
champions       = [{id: <int> (not automatic/running), name: <str>, ddragon_key: <str>}, ...]
champion_skills = [{champion: <int>, name: <str>, description: <str>, cooldowns: <str> like "1/2/3", slot: <int> 0..4}, ...]
champion_tips   = [{champion: <int>, vs: <"bool" string>, description: <str>}, ...]
"""
def replace_champion_metadata(champions, champion_skills, champion_tips):
  try:
    cursor, dbh = __get_cursor_and_handle()
    # Delete old data
    cursor.execute("DELETE FROM ChampionTip")
    cursor.execute("DELETE FROM ChampionSkill")
    cursor.execute("DELETE FROM Champion")
    # Prepare query strings
    escaped_champion_sqlstr = (
      "INSERT INTO Champion"
      + " (ID, Name, DdragonKey) VALUES "
      + ",".join(["(%s, %s, %s)" for c in champions])
    )
    escaped_championskill_sqlstr = (
      "INSERT INTO ChampionSkill"
      + " (Champion, Name, Description, CooldownSlashDelimited, Slot) VALUES "
      + ",".join(["(%s, %s, %s, %s, %s)" for c in champion_skills])
    )
    escaped_championtip_sqlstr = (
      "INSERT INTO ChampionTip (Champion, Vs, Description) VALUES "
      + ",".join(["(%s, %s, %s)" for c in champion_tips])
    )
    # Execute queries
    cursor.execute(escaped_champion_sqlstr, tuple(
      [val for sublist in
        [[c['id'], c['name'], c['ddragon_key']] for c in champions]
        for val in sublist]
    ))
    cursor.execute(escaped_championskill_sqlstr, tuple(
      [val for sublist in
        [[s['champion'], s['name'], s['description'], s['cooldowns'], s['slot']] for s in champion_skills]
        for val in sublist]
    ))
    cursor.execute(escaped_championtip_sqlstr, tuple(
      [val for sublist in
        [[t['champion'], t['vs'], t['description']] for t in champion_tips]
        for val in sublist]
    ))
    # Commit all
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
    "data": "Updated Champions' metadata successfully"
  }

"""
...
"""
def replace_item_metadata(items):
  try:
    cursor, dbh = __get_cursor_and_handle()
    # Delete old data
    cursor.execute("DELETE FROM Itemdata")
    # Prepare query strings
    escaped_item_sqlstr = (
      "INSERT INTO Itemdata"
      + " (ItemJSON) VALUES "
      + " (%s)"
    )
    # Execute queries
    cursor.execute(escaped_item_sqlstr, (items,))
    # Commit all
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
    "data": "Updated Items' metadata successfully"
  }

"""
...
"""
def replace_summonerspell_metadata(summonerspells):
  try:
    cursor, dbh = __get_cursor_and_handle()
    # Delete old data
    cursor.execute("DELETE FROM Summonerspelldata")
    # Prepare query strings
    escaped_item_sqlstr = (
      "INSERT INTO Summonerspelldata"
      + " (SummonerspellJSON) VALUES "
      + " (%s)"
    )
    # Execute queries
    cursor.execute(escaped_item_sqlstr, (summonerspells,))
    # Commit all
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
    "data": "Updated Summonerspells' metadata successfully"
  }

"""
List Champions' ID <=> Name  mapping
"""
def list_champion():
  try:
    cursor, dbh = __get_cursor_and_handle()
    cursor.execute("SELECT ID, Name, DdragonKey FROM Champion")
    result = cursor.fetchall()
    if not result:
      return {
        "success": True,
        "data": []
      }
    # Else unpack
    champions = []
    for row in result:
      id, name, ddragon_key = row
      champions.append({"id": id, "name": name, "ddragon_key": ddragon_key})
    dbh.close()

    return {
      "success": True,
      "data": champions
    }

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

"""
...
"""
def list_item():
  try:
    cursor, dbh = __get_cursor_and_handle()
    cursor.execute("SELECT Ver, ItemJSON FROM Itemdata")
    result = cursor.fetchall()
    if not result:
      return {
        "success": True,
        "data": []
      }
    # Else unpack
    ver, items = result[0]
    dbh.close()

    return {
      "success": True,
      "data": items
    }

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

"""
...
"""
def list_summonerspell():
  try:
    cursor, dbh = __get_cursor_and_handle()
    cursor.execute("SELECT Ver, SummonerspellJSON FROM Summonerspelldata")
    result = cursor.fetchall()
    if not result:
      return {
        "success": True,
        "data": []
      }
    # Else unpack
    ver, summonerspells = result[0]
    dbh.close()

    return {
      "success": True,
      "data": summonerspells
    }

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
