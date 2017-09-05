from djproject.prod_settings import MYSQL_LEAGUE_USER, MYSQL_LEAGUE_PW, MYSQL_LEAGUE_DBNAME, Q_A_DAILY_QUOTA, Q_A_UNANSWERED_QUOTA
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

def check_question_quota(ip_address):
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "SELECT Answer"
      + " FROM QA"
      + " WHERE IP = %s AND Timestamp < %s")
    cursor.execute(escaped_sqlstr, ( ip_address, (int(time.time())-(60*60*24)) ))
    result = cursor.fetchall()
    if not result:
      return {
        "success": True,
        "data": True # No questions done prior to now, quota ok
      }
    # Else unpack
    if len(result) >= Q_A_DAILY_QUOTA:
      return {
        "success": True,
        "data": False # Daily quota exceeded
      }
    unanswered = [hit for hit in result if hit[0] == None]
    if len(unanswered) >= Q_A_UNANSWERED_QUOTA:
      return {
        "success": True,
        "data": False # Unanswered quota exceeded
      }
    # Else
    return {
      "success": True,
      "data": True # Both daily quota and unanswered quota ok
    }
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

def add_question(question, ip_address):
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "INSERT INTO QA (IP, Timestamp, Question)"
      + " VALUES (%s, %s, %s)")
    cursor.execute(escaped_sqlstr, (ip_address, int(time.time()), question))
    dbh.commit()
    question_id = cursor.lastrowid
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
    "data": question_id
  }

def add_answer(question_id, answer):
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "UPDATE QA SET"
      + " Answer = %s,"
      + " AnswerCreated = (CASE WHEN AnswerCreated IS NULL THEN %s ELSE AnswerCreated),"
      + " AnswerLastModified = %s"
      + " WHERE ID = %s"
    cursor.execute(escaped_sqlstr, (answer, int(time.time()), int(time.time()), question_id))
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
    "data": True
  }

def question_was_opened(question_id):
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "UPDATE QA SET"
      + " TimesOpened = TimesOpened+1"
      + " WHERE ID = %s"
    cursor.execute(escaped_sqlstr, (answer, int(time.time()), int(time.time()), question_id))
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
    "data": True
  }

def list_answered_questions():
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "SELECT ID, Timestamp, Question, TimesOpened"
      + " FROM QA"
      + " WHERE Answer IS NOT NULL AND Disapproved != 1")
    cursor.execute(escaped_sqlstr)
    result = cursor.fetchall()
    if not result:
      return {
        "success": True,
        "data": [] # Empty set
      }
    # Else unpack
    answered_questions = [
      {
        'id': record[0],
        'time_asked': record[1],
        'question': record[2],
        'times_viewed': record[3]
      }
      for record in result
    ]
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
    "data": answered_questions
  }

def get_answer(question_id):
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "SELECT Answer, AnswerCreated, AnswerLastModified"
      + " FROM QA"
      + " WHERE ID = %s AND Answer IS NOT NULL AND Disapproved != 1")
    cursor.execute(escaped_sqlstr, (question_id))
    result = cursor.fetchone()
    if not result:
      return {
        "success": True,
        "data": None # 404
      }
    # Else unpack
    answer = {
      'answer': result[0][0],
      'time_answered': result[0][1],
      'time_answer_updated': result[0][2]
    }
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
    "data": answer
  }

def list_all_questions_and_answers():
  try:
    cursor, dbh = __get_cursor_and_handle()
    escaped_sqlstr = (
      "SELECT ID, IP, Timestamp, Question, Disapproved,"
      + " Answer, AnswerCreated, AnswerLastModified,"
      + " TimesOpened, LastTimeOpened"
      + " FROM QA")
    cursor.execute(escaped_sqlstr, (match_id, region))
    result = cursor.fetchall()
    if not result:
      return {
        "success": True,
        "data": [] # Empty set
      }
    # Else unpack
    all_questions = [
      {
        'id': record[0],
        'ip_address': record[1],
        'time_asked': record[2],
        'question': record[3],
        'disapproved': record[4],
        'answer': record[5],
        'time_answered': record[6],
        'time_answer_updated': record[7],
        'times_viewed': record[8],
        'time_last_viewed': record[9],
      }
      for record in result
    ]
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
    "data": all_questions
  }

