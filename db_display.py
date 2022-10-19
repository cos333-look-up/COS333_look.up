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
