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

def execute(cursor, stmt_str, p=[], l=[]):
    stmt = sql.SQL(stmt_str).format(*p)
    print(stmt.as_string(cursor.connection) % tuple(lit.getquoted()
    for lit in l))
    cursor.execute(stmt, l)

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
    print(('-'*43 + '\n%s\n' + '-'*43) % name)

    row = cursor.fetchone()
    while row is not None:
        print(row)
        row = cursor.fetchone()

    execute(cursor, 'COMMIT')
    
def update(cursor, table, index, vals):
    execute(cursor, 'BEGIN')

    parameters = []
    name = table.get_name()
    parameters.append(sql.Identifier(name))
    for key, val in vals.items():
        parameters.append(sql.Identifier(key))
        parameters.append(sql.Literal(val))
    for key, val in index.items():
        parameters.append(sql.Identifier(key))
        parameters.append(sql.Literal(val))
    
    stmt_str = "UPDATE {} SET"
    for i in range(len(vals)):
        if i == 0:
            stmt_str += " {} = NULLIF({}, NULL)"
        else:
            stmt_str += ", {} = NULLIF({}, NULL)"
    stmt_str += " WHERE"
    for i in range(len(index)):
        if i == 0:
            stmt_str += " {} = {}"
        else:
            stmt_str += "AND {} = {}"

    execute(cursor, stmt_str, p=parameters)

    execute(cursor, 'COMMIT')


def insert(cursor, table, vals):
    execute(cursor, 'BEGIN')

    parameters = []
    name = table.get_name()
    parameters.append(sql.Identifier(name))
    parameters += list(map(lambda k : sql.Identifier(str(k)), vals.keys()))
    parameters += list(map(lambda v : sql.Literal(str(v)), vals.values()))

    stmt_str = "INSERT INTO {}"
    for i in range(len(vals)):
        if i == 0:
            stmt_str += " ({}"
        else:
            stmt_str += ", {}"
        if i == len(vals) - 1:
            stmt_str += ")"
    stmt_str += " VALUES"
    for i in range(len(vals)):
        if i == 0:
            stmt_str += " ({}"
        else:
            stmt_str += ", {}"
        if i == len(vals) - 1:
            stmt_str += ")"
    
    execute(cursor, stmt_str, p=parameters)

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
