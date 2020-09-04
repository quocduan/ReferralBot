#      -- Database Object Definitions --
# This python file defines certain statements
# that align with the database tables associ-
# -ated with this project. It basically makes
# the most easily templated SQL statements to
# manipulate these tables with relative ease.
# Certain other common statements can not be
# included as they require more complexity and
# therefore do not fit in with the templated
# format these classes take. These classes are
# primarily used in association with the met-
# -hods in the 'database.py' file of this
# project.


class servers:
  sql_create = '''CREATE TABLE IF NOT EXISTS servers (
  id integer PRIMARY KEY,
  prefix text);'''
  sql_insert = '''INSERT INTO servers(id,prefix)
  VALUES(%s,%s)'''
  sql_update = '''UPDATE servers
  SET prefix = %s
  WHERE id = %s'''
  fields = ("id","prefix")
  table_name = "servers"

class scores:
  sql_create = '''CREATE TABLE IF NOT EXISTS scores (
  user_id integer PRIMARY KEY,
  score integer);'''
  sql_insert = '''INSERT INTO scores(user_id,score)
  VALUES(%s,%s)'''
  sql_update = '''UPDATE scores
  SET score = %s
  WHERE user_id = %s'''
  fields = ("user_id","score")
  table_name = "scores"

class user_link:
  sql_create = '''CREATE TABLE user_link (
  source integer PRIMARY KEY,
  target integer);'''
  sql_insert = '''INSERT INTO user_link(source,target)
  VALUES(%s,%s)'''
  sql_update = '''UPDATE user_link
  SET target = %s
  WHERE source = %s'''
  fields = ("source","target")
  table_name = "user_link"

# Add your other things here with the same data structure to make them work with the built-in
# database system in util_classes.py
