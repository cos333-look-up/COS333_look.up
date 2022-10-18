#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_edit.py
# Author: Drew Curran
# -----------------------------------------------------------------------

import os
import sys
import psycopg2
from psycopg2 import sql
import db_table

# -----------------------------------------------------------------------

def format_val(val):
    if val is not None and type(val)==str:
        val = str(val).replace("'", "''")
        val = "'" + val + "'"
    return val

def drop(cursor, table):
    cursor.execute('BEGIN')
    
    name = table.get_name()
    parameters = tuple()
    stmt_str = "DROP TABLE IF EXISTS {table}"
    stmt = sql.SQL(stmt_str).format(table=sql.Identifier(name))
    cursor.execute(stmt, parameters)

    cursor.execute('COMMIT')

def create(cursor, table):
    cursor.execute('BEGIN')

    name = table.get_name()
    attributes = table.get_attributes()
    var_type = []
    i = 0
    for key, val in attributes.items():
        if i < 2:
            var_type.append(key)
            var_type.append(val)
            i += 1
    stmt_str = "CREATE TABLE {}"
    for i in range(2):
        if i == 0:
            stmt_str += " ({} {}"
        else:
            stmt_str += ", {} {}"
        if i == len(attributes) - 1:
            stmt_str += ")"
    parameters = [sql.Identifier(name)] + list(map(sql.Identifier, var_type))
    stmt_str = "{} "*len(parameters)
    print(stmt_str)
    print(parameters)
    stmt = sql.SQL(stmt_str).format(tuple(parameters))
    print("here")
    print(stmt)
    cursor.execute(stmt)

    cursor.execute('COMMIT')

def select(cursor, table, selection="*"):
    name = table.get_name()
    parameters = tuple()
    stmt_str = "SELECT " + selection + " FROM " + name
    cursor.execute(stmt_str, parameters)

def display(cursor, table):
    name = table.get_name()
    print('-'*43 + '\n' + name + '\n' + '-'*43)

    select(cursor, table)

    row = cursor.fetchone()
    while row is not None:
        print(row)
        row = cursor.fetchone()
    
def update(cursor, table, index, vals):
    cursor.execute('BEGIN')

    name = table.get_name()
    keys = table.get_attributes().keys()
    
    attr_vals = {}
    for key in keys:
        print("here")
        try:
            attr_val = vals[key]
        except:
            continue
        attr_vals[key] = attr_val
    index_vals = {}
    for key in keys:
        try:
            index_val = index[key]
        except:
            continue
        index_vals[key] = index_val
    parameters = tuple(attr_vals.values()) + tuple(index_vals.values())
    print(parameters)
    stmt_str = ""
    i = 0
    for key in attr_vals.keys():
        if i == 0:
            stmt_str += "UPDATE " + name + " SET"
            stmt_str += " " + key + " = NULLIF(%s, NULL)"
            i += 1
        else:
            stmt_str += ", " + key + " = NULLIF(%s, NULL)"
    i = 0
    for key in index_vals.keys():
        if i == 0:
            stmt_str += " WHERE " + key + " = %s"
        else:
            stmt_str += " AND " + key + " = %s"
    if (len(stmt_str) > 0):
        cursor.execute(stmt_str, parameters)

    cursor.execute('COMMIT')


def insert(cursor, table, vals):
    name = table.get_name()
    keys = table.get_attributes().keys()
    vars = []
    var_vals = []
    for key in keys:
        try:
            val = vals[key]
        except:
            pass
        vars.append(key)
        var_vals.append(val)
    parameters = tuple(var_vals)
    stmt_str = "INSERT INTO " + name + " ("
    for i in range(len(vars)):
        if i == 0:
            stmt_str += vars[i]
        else:
            stmt_str += ", " + vars[i]
    stmt_str += ") VALUES ("
    for i in range(len(var_vals)):
        if i == 0:
            stmt_str += "%s"
        else:
            stmt_str += ", %s"
    stmt_str += ")"
    cursor.execute(stmt_str, parameters)

    cursor.execute('COMMIT')
    
def delete(cursor, table, index):
    name = table.get_name()
    keys = table.get_attributes().keys()
    index_vals = []
    for key in keys():
        try:
            index_val = format_val(index[key])
            index_vals.append(key, index_val)
        except:
            pass
    parameters = tuple(index_vals)
    stmt_str = "DELETE FROM " + name
    for i in range(len(index_vals)):
        if i == 0:
            stmt_str += " WHERE %s = %s"
        else:
            stmt_str += " AND %s = %s"
    cursor.execute(stmt_str, parameters)

    cursor.execute('COMMIT')

def main():
    clubs = db_table.Table('clubs', {'clubid':'INTEGER'}, 
    {'name':'TEXT', 'description':'TEXT', 'info_shared':'BIT(2)'})
    
    try:
        database_url = os.getenv('DATABASE_URL')
        with psycopg2.connect(database_url) as connection:
            with connection.cursor() as cursor:
                drop(cursor, clubs)
                create(cursor, clubs)
                insert(cursor, clubs, {'clubid':1, 
                'name':'Women\'s Club Lacrosse',
                'description':'Free for all to join!', 
                'info_shared':'11'})
                display(cursor, clubs)

                update(cursor, clubs,
                {'name':'Women\'s Club Lacrosse'}, {'clubid':8,
                'info_shared':'00'
                })
                display(cursor, clubs)

                # display(cursor, clubs)
                # delete(cursor, clubs, {'clubid':'1', 
                # 'name':'Women\'s Club Lacrosse'})
                # display(cursor, clubs)

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# -----------------------------------------------------------------------

if __name__ == '__main__':
    main()
