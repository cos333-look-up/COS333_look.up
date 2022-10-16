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
    parser.add_argument('table',
    help = 'name of the table edited')
    parser.add_argument('key',
    help = 'primary key of table')
    parser.add_argument('-c', metavar='club',
    help = 'new club name')
    parser.add_argument('-d', metavar='desc',
    help = 'new club description')
    parser.add_argument('-i', metavar='info',
    help = 'new club information shared')
    args = parser.parse_args()
    return args

def editClub(cursor, name, new_vals=[None, None, None]):
    cursor.execute('BEGIN')

    stmt_str = "UPDATE clubs SET name = ISNULL(?, name), "
    stmt_str += "description = ISNULL(?, description), "
    stmt_str += "info_shared = ISNULL(?, info_shared) "
    stmt_str += "WHERE name = ?"
    cursor.execute(stmt_str, 
        [new_vals[0], new_vals[1], new_vals[2], name])

    cursor.execute('COMMIT')
    print('Transaction committed.')


def main():
    input = parse_user_input()

    if len(sys.argv) != 1:
        print('Usage: python ' + sys.argv[0] + "name", file=sys.stderr)
        sys.exit(1)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                if (input.table == 'clubs'):
                    editClub(cursor, input.key,
                        new_vals=[input.c, input.d, input.i])

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# -----------------------------------------------------------------------


if __name__ == '__main__':
    main()
