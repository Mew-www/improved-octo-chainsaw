# Import @decorators
from django.views.decorators.http import require_http_methods

# Import responses
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError

# Import utilities
from djproject.prod_settings import MYSQL_LEAGUE_USER, MYSQL_LEAGUE_PW, MYSQL_LEAGUE_DBNAME
import MySQLdb as MDB
import json, time

@require_http_methods(["POST"])
def log(request):

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

  # Parse request
  try:
    inputdata = json.loads(request.body.decode('utf-8'))
  except ValueError:
    return HttpResponseBadRequest("Invalid json")

  # Check event length
  msg = inputdata.get('msg', None)
  etype = inputdata.get('type', None)
  status = inputdata.get('status', None)
  if msg is None or len(msg) > 255:
    return HttpResponseBadRequest("Invalid event msg")
  if etype is None or len(etype) > 255:
    return HttpResponseBadRequest("Invalid event msg")
  if status is None or len(status) > 255:
    return HttpResponseBadRequest("Invalid event status")

  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "INSERT INTO AppLog (IP, Timestamp, EventDescription, EventType, EventStatus)"
      + " VALUES (%s, %s, %s, %s, %s)")
    cursor.execute(escaped_sqlstr, (request.META.get('REMOTE_ADDR'), int(time.time()), msg, etype, status,))
    dbh.commit()
    dbh.close()

  except MDB.Error as e:
    return HttpResponseServerError("MySQLdb Generic Error: " + str(e.args[0]) + ((" " + str(e.args[1])) if len(e.args) > 1 else ""))

  except MDB.IntegrityError as e:
    return HttpResponseServerError("MySQLdb Integrity Error: " + str(e.args[0]) + ((" " + str(e.args[1])) if len(e.args) > 1 else ""))

  return HttpResponse("ok")
