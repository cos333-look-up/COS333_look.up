#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_edit.py
# Author: Drew Curran
# -----------------------------------------------------------------------

import os
import sys
import psycopg2
import argparse

# -----------------------------------------------------------------------

def parse_user_input():
    parser = argparse.ArgumentParser(allow_abbrev = False,
    description = 'Database editor')
    parser.add_argument('-t', metavar='table',
    help = 'name of the table edited')
    parser.add_argument('-k', metavar='key',
    help = 'primary key of table')
    parser.add_argument('-n', metavar='new',
    help = 'new values', nargs='*')
    args = parser.parse_args()
    return args

def pad_input(list, padding, val=None):
    diff = padding - len(list)
    if diff < 0:
        raise AttributeError("List length is too long.")
    return list + [val] * diff

def replace_wild_cards(arg):
    if arg is not None:
        arg = str(arg).replace("\\", "\\\\")
        arg = str(arg).replace("_", "\\_")
        arg = str(arg).replace("%", "\\%")
    return arg

def updateClub(cursor, clubid, vals=[None, None, None]):
    cursor.execute('BEGIN')

    stmt_str = "UPDATE clubs SET name = COALESCE(%s, name), "
    stmt_str += "description = COALESCE(%s, description), "
    stmt_str += "info_shared = COALESCE(%s, info_shared) "
    stmt_str += "WHERE clubid = %s"
    parameters = vals + [clubid]
    cursor.execute(stmt_str, parameters)

    cursor.execute('COMMIT')
    print('Transaction committed.')

def addClub(cursor, vals=[None, None, None]):
    cursor.execute('BEGIN')

    cursor.execute("SELECT MAX(clubid) FROM clubs")
    clubid = cursor.fetchone() + 1

    stmt_str = "INSERT INTO clubs "
    stmt_str += "(clubid, name, description, info_shared) "
    stmt_str += "VALUES (%s, %s, %s, %s)"
    parameters = [clubid] + vals
    cursor.execute(stmt_str, parameters)

    cursor.execute('COMMIT')
    print('Transaction committed.')

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
