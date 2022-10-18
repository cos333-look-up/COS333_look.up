#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_edit.py
# Author: Drew Curran
# -----------------------------------------------------------------------

import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import AsIs
import db_table

# -----------------------------------------------------------------------

def format_val(val):
    if val is not None and type(val)==str:
        val = str(val).replace("'", "''")
        val = "'" + val + "'"
    return val

def execute(cursor, stmt_str, p=[], l=[]):
    stmt = sql.SQL(stmt_str).format(*p)
    cursor.execute(stmt, l)
    return stmt.as_string(cursor.connection) % tuple(lit.getquoted() 
    for lit in l)

def drop(cursor, table):
    execute(cursor, 'BEGIN')

    parameters = []
    name = table.get_name()
    parameters.append(sql.Identifier(name))
    stmt_str = "DROP TABLE IF EXISTS {}"
    execute(cursor, stmt_str, p=parameters)

    execute(cursor, 'COMMIT')

def create(cursor, table):
    execute(cursor, 'BEGIN')

    parameters = []
    literals = []
    name = table.get_name()
    parameters.append(sql.Identifier(name))    
    attributes = table.get_attributes()
    for key, val in attributes.items():
        parameters.append(sql.Identifier(key))
        literals.append(AsIs(val))
    stmt_str = "CREATE TABLE {}"
    for i in range(len(attributes)):
        if i == 0:
            stmt_str += " ({} %s"
        else:
            stmt_str += ", {} %s"
        if i == len(attributes) - 1:
            stmt_str += ")"
    execute(cursor, stmt_str, p=parameters, l=literals)

    execute(cursor, 'COMMIT')

def selectAll(cursor, table):
    # execute(cursor, 'BEGIN')

    parameters = []
    name = table.get_name()
    parameters.append(sql.Identifier(name))
    stmt_str = "SELECT * FROM {}"
    execute(cursor, stmt_str, parameters)

    # execute(cursor, 'COMMIT')

def display(cursor, table):
    execute(cursor, 'BEGIN')
    
    selectAll(cursor, table)

    name = table.get_name()
    print('-'*43 + '\n%s\n' + '-'*43 % name)
    row = cursor.fetchone()
    while row is not None:
        print(row)
        row = cursor.fetchone()

    execute(cursor, 'COMMIT')
    
def update(cursor, table, index, vals):
    cursor.execute('BEGIN')

    name = table.get_name()
    keys = table.get_attributes().keys()
    
    attr_vals = {}
    for key in keys:
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
    execute(cursor, 'BEGIN')

    parameters = []
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

    for i in range(len(vars)):
        if i == 0:
            stmt_str += "INSERT INTO {} ({}"
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

    execute(cursor, 'COMMIT')
    
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

    if len(sys.argv) != 2:
        print('usage: python %s db_url' % sys.argv[0],
            file=sys.stderr)
        sys.exit(1)
    db_file = sys.argv[1]

    try:
        with open(db_file) as f:
            os.environ.update(line.strip().split('=', 1) for line in f)
        db_url = os.getenv('ELEPHANTSQL_URL')
        with psycopg2.connect(db_url) as connection:
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
