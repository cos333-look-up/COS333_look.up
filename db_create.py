#!/usr/bin/env python

#-----------------------------------------------------------------------
# db_create.py
# Author: Drew Curran
#-----------------------------------------------------------------------

import os
import sys
import psycopg2

#-----------------------------------------------------------------------

def main():

    if len(sys.argv) != 1:
        print('Usage: python create.py', file=sys.stderr)
        sys.exit(1)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS clubs")
                cursor.execute("CREATE TABLE clubs "
                    + "(name TEXT, description TEXT, "
                    + "info_shared INTEGER)")
                cursor.execute("INSERT INTO clubs "
                    + "(name, description, info_shared) "
                    + "VALUES ('Womens Club Lacrosse', "
                    + "'Free for all to join!', 3)")
                cursor.execute("INSERT INTO clubs "
                    + "(name, description, info_shared) "
                    + "VALUES ('Cloister', "
                    + "'Official Cloister Club Page', 2)")
                cursor.execute("INSERT INTO clubs "
                    + "(name, description, info_shared) "
                    + "VALUES ('Asian-American Students Association', "
                    + "'Welcome!', 1)")
                cursor.execute("INSERT INTO clubs "
                    + "(name, description, info_shared) "
                    + "VALUES ('Cannon', "
                    + "'Cannon Homepage', 0)")    

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS clubmembers")
                cursor.execute("CREATE TABLE clubmembers "
                    + "(name TEXT, netid TEXT, is_moderator INTEGER)")
                cursor.execute("INSERT INTO clubmembers "
                    + "(name, netid, is_moderator) "
                    + "VALUES ('Cloister', 'bm18', 1)")
                cursor.execute("INSERT INTO clubmembers "
                    + "(name, netid, is_moderator) "
                    + "VALUES ('Cloister', 'denisac', 0)")
                cursor.execute("INSERT INTO clubmembers "
                    + "(name, netid, is_moderator) "
                    + "VALUES ('Cloister', 'pmt2', 1)")
                cursor.execute("INSERT INTO clubmembers "
                    + "(name, netid, is_moderator) "
                    + "VALUES ('Asian-American Students Association', "
                    + "'evanwang', 0)")

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS users")
                cursor.execute("CREATE TABLE users "
                    + "(netid TEXT, is_admin INTEGER, first_name TEXT, "
                    + "last_name TEXT, photo TEXT, phone TEXT, "
                    + "instagram TEXT, snapchat TEXT)")
                cursor.execute("INSERT INTO users "
                    + "(netid, is_admin, first_name, last_name, photo, "
                    + "phone, instagram, snapchat) VALUES "
                    + "('denisac', 1, 'Drew', 'Curran', 'Placeholder', "
                    + "'+17037329370', 'drewcurran17', NULL)")
                cursor.execute("INSERT INTO users "
                    + "(netid, is_admin, first_name, last_name, photo, "
                    + "phone, instagram, snapchat) VALUES "
                    + "('dh37', 1, 'Daniel', 'Hu', NULL, "
                    + "NULL, NULL, NULL)")
                cursor.execute("INSERT INTO users "
                    + "(netid, is_admin, first_name, last_name, photo, "
                    + "phone, instagram, snapchat) VALUES "
                    + "('gleising', 1, NULL, NULL, NULL, "
                    + "NULL, NULL, NULL)")
                cursor.execute("INSERT INTO users "
                    + "(netid, is_admin, first_name, last_name, photo, "
                    + "phone, instagram, snapchat) VALUES "
                    + "('evanwang', 1, 'Evan', 'Wang', 'Placeholder', "
                    + "NULL, NULL, NULL)")
                cursor.execute("INSERT INTO users "
                    + "(netid, is_admin, first_name, last_name, photo, "
                    + "phone, instagram, snapchat) VALUES "
                    + "('rc38', 1, 'Richard', 'Cheng', NULL, "
                    + "'+13142952690', NULL, NULL)")

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS creationreqs")
                cursor.execute("CREATE TABLE creationreqs "
                    + "(name TEXT, netid TEXT, reason TEXT, "
                    + "info_shared INTEGER)")
                cursor.execute("INSERT INTO creationreqs "
                    + "(name, netid, reason, info_shared) VALUES "
                    + "('Club Tennis', 'denisac', 'Official club', 3)")
                cursor.execute("INSERT INTO creationreqs "
                    + "(name, netid, reason, info_shared) VALUES "
                    + "('Basketball Group', 'dh37', "
                    + "'Group to play pickup basketball', 2)")

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS joinreqs")
                cursor.execute("CREATE TABLE joinreqs "
                    + "(name TEXT, netid TEXT)")
                cursor.execute("INSERT INTO joinreqs (name, netid) "
                    + "VALUES ('Cloister', 'jasonsun')")
                cursor.execute("INSERT INTO joinreqs (name, netid) "
                    + "VALUES ('Womens Club Lacrosse', 'aleshire')")
                cursor.execute("INSERT INTO joinreqs (name, netid) "
                    + "VALUES ('Cloister', 'arobang')")

                #-------------------------------------------------------

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
