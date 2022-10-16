#!/usr/bin/env python

#-----------------------------------------------------------------------
# db_display.py
# Author: Drew Curran
#-----------------------------------------------------------------------

import os
import sys
import psycopg2

#-----------------------------------------------------------------------

def main():

    if len(sys.argv) != 1:
        print('Usage: python display.py', file=sys.stderr)
        sys.exit(1)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                print('-------------------------------------------')
                print('clubs')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM clubs")
                row = cursor.fetchone()
                while row is not None:
                    print(row)
                    row = cursor.fetchone()

                print('-------------------------------------------')
                print('clubmembers')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM clubmembers")
                row = cursor.fetchone()
                while row is not None:
                    print(row)
                    row = cursor.fetchone()

                print('-------------------------------------------')
                print('users')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM users")
                row = cursor.fetchone()
                while row is not None:
                    print(row)
                    row = cursor.fetchone()

                print('-------------------------------------------')
                print('creationreqs')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM creationreqs")
                row = cursor.fetchone()
                while row is not None:
                    print(row)
                    row = cursor.fetchone()

                print('-------------------------------------------')
                print('joinreqs')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM joinreqs")
                row = cursor.fetchone()
                while row is not None:
                    print(row)
                    row = cursor.fetchone()

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
