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
List available regions
"""
def list_region():
  try:
    cursor, dbh = __get_cursor_and_handle()
    cursor.execute("SELECT Name FROM Region")
    result = cursor.fetchall()
    if not result:
      return {
        "success": True,
        "data": [] # None found
      }
    # Else unpack
    regions = [r[0] for r in result]
    dbh.close()
    return {
      "success": True,
      "data": regions
    }

  except MDB.Error as e:
    return {
      "success": False,
      "data": "MySQLdb Generic Error %d: %s" % (e.args[0],e.args[1])
    }

  except MDB.IntegrityError as e:
    return {
      "success": False,
      "data": "MySQLdb IntegrityError %d: %s" % (e.args[0],e.args[1])
    }
