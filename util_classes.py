import dbobj
import os
#import sqlite3
import psycopg2
import discord
from discord.ext import commands
from contextlib import contextmanager
from sqlite3 import Error
from datetime import datetime,timezone

# Required fill-in field is on line 159
# Replace the file path with database file location

# Utility classes
# A file with classes that can be used for more than just
# the bot that I have made them for. Enjoy utilizing them
# for both this bot and any other work you may want to add
# them to.
# This file contains:
# - Paged list: contains a list, the contents of which are
#   split into separately iterable pages. Access is limited
#   to the current page of the list but the page can be
#   changed easily.
# - Database utilities: A context manager and a class that
#   uses it to *considerably* streamline the database access
#   and manipulation process, and even auto-close right
#   afterwards.

class PagedList:
  def __init__(self, per_page, contents):
    self.per_page = per_page
    self.contents = []
    self.non_paginated = contents
    self.page = 0
    self.iterator = 0
    self.tmpage = 0
    for i in contents:
      if(self.iterator == self.per_page):
        self.iterator = 0
        self.tmpage += 1
      if(self.iterator == 0):
        self.contents.append([])
      self.contents[tmpage].append(i)
      self.iterator += 1

  def update_contents(self):
    self.contents = []
    self.iterator = 0
    self.tmpage = 0
    for i in self.non_paginated:
      if(self.iterator == self.per_page):
        self.iterator = 0
        self.tmpage += 1
      if(self.iterator == 0):
        self.contents.append([])
      self.contents[tmpage].append(i)
      iterator += 1
    if(self.page >= len(self.contents)):
      self.page = len(self.contents) - 1

  # ~~ Paging Methods ~~ #

  def page_forward(self):
    if(self.page is not len(self.contents) - 1):
      self.page += 1
    return self

  def page_back(self):
    if(self.page is not 0):
      self.page -= 1
    return self

  def goto_page(self,page):
    if(page < len(self.contents) and page >= 0):
      self.page = page
    return self

  # ~~ Basic Sequence Methods ~~ #

  def append(self,item):
    '''Add an item to the end of the paged list, on the final page of the list.'''
    if(len(self.contents[len(self.contents)-1]) == self.per_page):
      self.contents.append([])
    self.contents[len(self.contents)-1].append(item)
    self.non_paginated.append(item)

  def remove(self,item):
    '''Remove the item from the current page, then update with new pagination to account for the missing item.'''
    self.non_paginated.remove(item)
    self.update_contents()

  # ~~ Magic Methods: Sequence Functionality ~~ #
  # Makes instances of this object class subscriptable and
  # iterable, a la a standard list object.

  def __getitem__(self,idx):
    print("Retrieving item at " + str(idx))
    return self.contents[self.page][idx]

  def __setitem__(self,idx,value):
    print("Changing item at " + str(idx))
    self.contents[self.page][idx] = value

  def __delitem__(self,idx):
    print("Deleting item at " + str(idx))
    del self.contents[self.page][idx]

  def __iter__(self):
    return self.contents[self.page].__iter__()

  def __len__(self):
    return len(self.contents[self.page])

  def __reversed__(self):
    self.contents = reversed(self.contents)
    return self

  # ~~ Magic Methods: Comparators ~~ #

  def __eq__(self,other):
    return self.equals(other)

  # Note that these comparators do not fit the same mold
  # as the equality comparator and are based on length as
  # opposed to object value.
  def __gt__(self,other):
    return len(self.non_paginated) > other

  def __lt__(self,other):
    return len(self.non_paginated) < other

  def __ge__(self,other):
    return len(self.non_paginated) >= other

  def __le__(self,other):
    return len(self.non_paginated) <= other

  # ~~ Magic Methods: Operators ~~ #

  def __add__(self,other):
    self.append(other)
    return self

  def __sub__(self,other):
    self.remove(other)
    return self

@contextmanager
def db_open():
  try:
    #conn = sqlite3.connect(file_or_path)
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    yield conn
  except Error as e:
    print(e)
  else:
    conn.commit()
  finally: # close the connection after
    conn.close

class database:
  def repair_table(table):
    with db_open() as conn:
      c = conn.cursor()
      c.execute(table.sql_create)
  # Insert a row in the specified table.
  def insert_row(table, data):
    with db_open() as conn:
      c = conn.cursor()
      c.execute(table.sql_insert,data)

  # Update a row in the specified table.
  def update_data(table, data):
    with db_open() as conn:
      c = conn.cursor()
      c.execute(table.sql_update,data)

  # Select a list of objects using the specified SQL statement.
  def select_many(table, **kwargs):
    statement = "SELECT * FROM " + table.table_name + " "
    data = ()
    select_all = kwargs.get("select_all",False)
    if not select_all:
      notfirst = False
      statement += "WHERE "
      for key, value in kwargs.items():
        if(str(key) in table.fields):
          if(notfirst):
            statement = statement + "AND "
          else:
            notfirst = True
          if(type(value) is list or type(value) is tuple):
            statement = statement + "(" + str(key) + "= %s "
            data = data + (value[0],)
            for idx in range(len(value)-1):
              statement = statement + "OR " + str(key) + "= %s "
              data = data + (value[idx+1],)
            statement = statement[:-1] + ") "
          else:
            statement = statement + str(key) + "= %s "
            data = data + (value,)
      # if the code didn't request anything, return nothing.
      if(len(statement) == 19 + len(table.table_name)):
        print("This is not going to go well. Nothing was added to the statement!")
        return []
    order_by = kwargs.get("ORDER_BY")
    order_desc = kwargs.get("ORDER_DESC",False)
    if order_by:
      if str(order_by) in table.fields:
        statement += "ORDER BY %s "
        statement += "DESC " if order_desc else "ASC "
        column_idx = table.fields.index(str(order_by))+1
        data = data + (column_idx,)
    # but trim the trailing space off
    statement = statement[:-1]
    with db_open() as conn:
      c = conn.cursor()
      c.execute(statement, data)
      return c.fetchall()

  # Select a single object using the specified SQL statement.
  def select_one(table, **kwargs):
    statement = "SELECT * FROM " + table.table_name + " WHERE "
    data = ()
    notfirst = False
    for key, value in kwargs.items():
      if(str(key) in table.fields):
        if(notfirst):
          statement = statement + "AND "
        else:
          notfirst = True
        if(type(value) is list or type(value) is tuple):
          statement = statement + "(" + str(key) + "=%s "
          data = data + (value[0],)
          for idx in range(len(value)-1):
            statement = statement + "OR " + str(key) + "=%s "
            data = data + (value[idx+1],)
          statement = statement[:-1] + ") "
        else:
          statement = statement + str(key) + "=%s "
          data = data + (value,)
    if(len(statement) == 19 + len(table.table_name)):
      print("This is not going to go well. Nothing was added to the statement!")
      return []
    statement = statement[:-1]
    print(statement)
    with db_open() as conn:
      c = conn.cursor()
      c.execute(statement, data)
      return c.fetchone()

  def select_all(table):
    statement = "SELECT * FROM " + table.table_name
    with db_open() as conn:
      c = conn.cursor()
      c.execute(statement)
      return c.fetchall()

  # Delete one or more objects from the database using the specified SQL statement.
  def delete_data(statement, data):
    if("DELETE" in statement):
      with db_open() as conn:
        c = conn.cursor()
        c.execute(statement, data)
    else:
      print("Statement must be a 'DELETE' statement.")

  def test_delete(table,**kwargs):
    statement = "DELETE FROM " + table.table_name + " WHERE "
    data = ()
    notfirst = False
    for key, value in kwargs.items():
      if(str(key) in table.fields):
        if(notfirst):
          statement = statement + "AND "
        else:
          notfirst = True
        if(type(value) is list or type(value) is tuple):
          statement = statement + "(" + str(key) + "=%s "
          data = data + (value[0],)
          for idx in range(len(value)-1):
            statement = statement + "OR " + str(key) + "=%s "
            data = data + (value[idx+1],)
          statement = statement[:-1] + ") "
        else:
          statement = statement + str(key) + "=%s "
          data = data + (value,)
    if(len(statement) == 18 + len(table.table_name)):
      print("This is not going to go well. Nothing was added to the statement!")
      return []
    statement = statement[:-1]
    print(statement)
    with db_open() as conn:
      c = conn.cursor()
      c.execute(statement, data)
