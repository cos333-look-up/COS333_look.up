#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_edit.py
# Author: Drew Curran
# -----------------------------------------------------------------------

import os
import sys
import psycopg2
import argparse
import db_table

# -----------------------------------------------------------------------

def parse_user_input():
    parser = argparse.ArgumentParser(allow_abbrev=False,
    description='Database editor')
    return args

def format_string(val):
    if val is not None:
        val = str(val).replace("'", "''")
        val = "'" + val + "'"
    else:
        val = "NULL"
    return val

def pad_input(list, padding, val=None):
    diff = padding - len(list)
    if diff < 0:
        raise AttributeError("List length is too long.")
    return list + [val] * diff

def drop(cursor, table):
    cursor.execute('BEGIN')
    name = table.get_name()
    "DROP TABLE IF EXISTS %s" + self._name

def create(self):
    stmt_str = "CREATE TABLE " + self._name + " "
    var_types = []
    for var, type in self._attributes.items():
        var_types.append(var + " " + type)
    stmt_str += "(" + ", ".join(var_types) + ")"
    return stmt_str

def select(self, selection="*"):
    return "SELECT " + selection + " FROM " + self._name
    
def update(self, index, vals):
    stmt_str = "UPDATE clubs SET "
    for key in self._attributes.keys():
        try:
            val = self.format_string(vals[key])
            stmt_str += key + " = COALESCE(" + val + ", " + key + ") "
        except:
            pass
    stmt_str += "WHERE "
    first = True
    for key in self._attributes.keys():
        try:
            if first:
                val = self.format_string(index[key])
                stmt_str += key + " = " + val + " "
                first = False
            else:
                val = self.format_string(index[key])
                stmt_str += "AND " + key + " = " + val + " "
        except:
            pass
    return stmt_str

def insert(self, vals):
    stmt_str = "INSERT INTO " + self._name  + " "
    stmt_str += "(" + ", ".join(self._attributes.keys()) + ") "
    stmt_str += "VALUES "
    var_vals = []
    for key in self._attributes.keys():
        try:
            val = self.format_string(vals[key])
        except:
            pass
        var_vals.append(val)
    stmt_str += "(" + ", ".join(var_vals) + ")"
    return stmt_str
    
def delete(self, index):
    stmt_str = "DELETE FROM clubs WHERE "
    first = True
    for key in self._attributes.keys():
        try:
            if first:
                val = self.format_string(index[key])
                stmt_str += key + " = " + val + " "
                first = False
            else:
                val = self.format_string(index[key])
                stmt_str += "AND " + key + " = " + val + " "
        except:
            pass
    return stmt_str

def main():
    input = parse_user_input()
    
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                if (input.t == 'clubs'):
                    updateClub(cursor, input.k, 
                    new_vals=pad_input(input.n, 3))

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# -----------------------------------------------------------------------

if __name__ == '__main__':
    main()
