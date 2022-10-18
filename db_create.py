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
        print('Usage: python ' + sys.argv[0], file=sys.stderr)
        sys.exit(1)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS clubs")
                cursor.execute("CREATE TABLE clubs "
                    + "(clubid INTEGER, name TEXT, description TEXT, "
                    + "info_shared BIT(2))")
                cursor.execute("INSERT INTO clubs "
                    + "(clubid, name, description, info_shared) "
                    + "VALUES ('1', 'Women\'\'s Club Lacrosse', "
                    + "'Free for all to join!', '11')")
                cursor.execute("INSERT INTO clubs "
                    + "(clubid, name, description, info_shared) "
                    + "VALUES (2, 'Cloister', "
                    + "'Official Cloister Club Page', B'10')")
                cursor.execute("INSERT INTO clubs "
                    + "(clubid, name, description, info_shared) "
                    + "VALUES (3, 'Asian-American Students Association', "
                    + "'Welcome!', B'01')")
                cursor.execute("INSERT INTO clubs "
                    + "(clubid, name, description, info_shared) "
                    + "VALUES (4, 'Cannon', "
                    + "'Cannon Homepage', B'00')")    

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS clubmembers")
                cursor.execute("CREATE TABLE clubmembers "
                    + "(clubid INTEGER, netid TEXT, is_moderator BOOL)")
                cursor.execute("INSERT INTO clubmembers "
                    + "(clubid, netid, is_moderator) "
                    + "VALUES (2, 'bm18', true)")
                cursor.execute("INSERT INTO clubmembers "
                    + "(clubid, netid, is_moderator) "
                    + "VALUES (2, 'denisac', false)")
                cursor.execute("INSERT INTO clubmembers "
                    + "(clubid, netid, is_moderator) "
                    + "VALUES (2, 'pmt2', true)")
                cursor.execute("INSERT INTO clubmembers "
                    + "(clubid, netid, is_moderator) "
                    + "VALUES (3, 'evanwang', false)")

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS users")
                cursor.execute("CREATE TABLE users "
                    + "(netid TEXT, is_admin BOOL, first_name TEXT, "
                    + "last_name TEXT, photo TEXT, phone TEXT, "
                    + "instagram TEXT, snapchat TEXT)")
                cursor.execute("INSERT INTO users "
                    + "(netid, is_admin, first_name, last_name, photo, "
                    + "phone, instagram, snapchat) VALUES "
                    + "('denisac', false, 'Drew', 'Curran', 'Placeholder', "
                    + "'+17037329370', 'drewcurran17', NULL)")
                cursor.execute("INSERT INTO users "
                    + "(netid, is_admin, first_name, last_name, photo, "
                    + "phone, instagram, snapchat) VALUES "
                    + "('dh37', true, 'Daniel', 'Hu', NULL, "
                    + "NULL, NULL, NULL)")
                cursor.execute("INSERT INTO users "
                    + "(netid, is_admin, first_name, last_name, photo, "
                    + "phone, instagram, snapchat) VALUES "
                    + "('gleising', true, NULL, NULL, NULL, "
                    + "NULL, NULL, NULL)")
                cursor.execute("INSERT INTO users "
                    + "(netid, is_admin, first_name, last_name, photo, "
                    + "phone, instagram, snapchat) VALUES "
                    + "('evanwang', true, 'Evan', 'Wang', 'Placeholder', "
                    + "NULL, NULL, NULL)")
                cursor.execute("INSERT INTO users "
                    + "(netid, is_admin, first_name, last_name, photo, "
                    + "phone, instagram, snapchat) VALUES "
                    + "('rc38', true, 'Richard', 'Cheng', NULL, "
                    + "'+13142952690', NULL, NULL)")

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS creationreqs")
                cursor.execute("CREATE TABLE creationreqs "
                    + "(name TEXT, netid TEXT, reason TEXT, "
                    + "info_shared BIT(2))")
                cursor.execute("INSERT INTO creationreqs "
                    + "(name, netid, reason, info_shared) VALUES "
                    + "('Club Tennis', 'denisac', 'Official club', "
                    + "B'11')")
                cursor.execute("INSERT INTO creationreqs "
                    + "(name, netid, reason, info_shared) VALUES "
                    + "('Basketball Group', 'dh37', "
                    + "'Group to play pickup basketball', B'10')")

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS joinreqs")
                cursor.execute("CREATE TABLE joinreqs "
                    + "(clubid INTEGER, netid TEXT)")
                cursor.execute("INSERT INTO joinreqs (clubid, netid) "
                    + "VALUES (2, 'jasonsun')")
                cursor.execute("INSERT INTO joinreqs (clubid, netid) "
                    + "VALUES (1, 'aleshire')")
                cursor.execute("INSERT INTO joinreqs (clubid, netid) "
                    + "VALUES (2, 'arobang')")

                #-------------------------------------------------------

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
