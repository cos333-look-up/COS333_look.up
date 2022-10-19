#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_editor.py
# Author: Drew Curran
# -----------------------------------------------------------------------

import os
from db_edit import Table
import argparse
#from psycopg2 import connect
#from psycopg2 import cursor
import psycopg2
from psycopg2 import sql

# -----------------------------------------------------------------------

class TableEditor:

    def __init__(self, tables, cursor, transacting):
        self._tables = tables
        self._cursor = cursor
        self._transacting = transacting

    def execute(self, table, function, stmt_str, p=[], l=[]):
        table = self._tables.get(table)
        stmt, parameters, literals = function(table)
        stmt = sql.SQL(stmt_str).format(*p)
        cursor.execute(stmt, l)
        return stmt.as_string(cursor.connection) % tuple(lit.getquoted()
        for lit in l)

    def begin(self):
        stmt_str = "BEGIN"
        if not transacting:
            transacting = True
        return stmt_str
        
    def commit(self):
        stmt_str = "COMMIT"
        if transacting:
            transacting = False
        return stmt_str
        
    def rollback(self):
        stmt_str = "ROLLBACK"
        if transacting:
            transacting = False
        return stmt_str

    def display(name, attributes):
        data = fetchAll(cursor)
        table = Table_Display()
        table.title = name
        table.field_names = attributes.keys()
        table.add_rows(data)
        print(table)

    def fetchAll(cursor):
        rows = []
        row = cursor.fetchone()
        rows.append(row)
        while row is not None:
            row = cursor.fetchone()
            rows.append(row)
        return rows[:-1]

def sample(cursor, tables, transacting):
    stmt_str = begin(transacting)
    execute(cursor, stmt_str)
    clubs = tables[0]
    clubs.drop()
    clubs.create()
    clubs.insert({'clubid':1, 
                'name':'Women\'s Club Lacrosse',
                'description':'Free for all to join!', 
                'info_shared':'11'})
    clubs.insert({'clubid':2, 
                'name':'Cloister',
                'description':'Official Cloister Club Page', 
                'info_shared':'10'})
    clubs.insert({'clubid':3, 
                'name':'Asian-American Students Association',
                'description':'Welcome!', 
                'info_shared':'01'})
    clubs.insert({'clubid':4, 
                'name':'Cannon',
                'description':'Cannon Homepage!', 
                'info_shared':'00'})
    name, attributes = clubs.selectAll()
    display(name, attributes)
    
    clubmembers = tables[1]
    clubmembers.drop()
    clubmembers.create()
    clubmembers.insert({'clubid':2, 
                'netid':'bm18',
                'is_moderator':True})
    clubmembers.insert({'clubid':2, 
                'netid':'denisac',
                'is_moderator':False})
    clubmembers.insert({'clubid':2, 
                'netid':'pmt2',
                'is_moderator':True})
    clubmembers.insert({'clubid':3, 
                'netid':'evanwang',
                'is_moderator':False})
    name, attributes = clubmembers.selectAll()
    display(name, attributes)

    users = tables[2]
    users.drop()
    users.create()
    users.insert({'netid':'denisac', 
                'is_admin':False,
                'first_name':'Drew',
                'last_name':'Curran', 
                'photo':'Placeholder',
                'phone':'+17037329370',
                'instagram':'drewcurran17', 
                'snapchat':None
                })
    users.insert({'netid':'dh37', 
                'is_admin':True,
                'first_name':'Daniel',
                'last_name':'Hu', 
                'photo':None,
                'phone':None,
                'instagram':None, 
                'snapchat':None
                })
    users.insert({'netid':'gleising', 
                'is_admin':True,
                'first_name':None,
                'last_name':None, 
                'photo':None,
                'phone':None,
                'instagram':None, 
                'snapchat':None
                })
    users.insert({'netid':'evanwang', 
                'is_admin':True,
                'first_name':'Evan',
                'last_name':'Wang', 
                'photo':'Placeholder',
                'phone':None,
                'instagram':None, 
                'snapchat':None
                })
    users.insert({'netid':'rc38', 
                'is_admin':True,
                'first_name':'Richard',
                'last_name':'Cheng', 
                'photo':None,
                'phone':'+13142952690',
                'instagram':None, 
                'snapchat':None
                })
    name, attributes = users.selectAll()
    display(name, attributes)

    creationreqs = tables[3]
    creationreqs.drop()
    creationreqs.create()
    creationreqs.insert({'name':'Club Tennis', 
                'netid':'denisac',
                'description':'Official club',
                'info_shared':'11'
                })
    creationreqs.insert({'name':'Basketball Group', 
                'netid':'dh37',
                'description':'Group to play pickup basketball',
                'info_shared':'10'
                })
    name, attributes = creationreqs.selectAll()
    display(name, attributes)
    
    joinreqs = tables[4]
    joinreqs.drop()
    joinreqs.create()
    joinreqs.insert({'clubid':2, 
                'netid':'jasonsun',
                })
    joinreqs.insert({'clubid':1, 
                'netid':'aleshire',
                })      
    joinreqs.insert({'clubid':2, 
                'netid':'arobang',
                })
    name, attributes = joinreqs.selectAll()
    display(name, attributes)
    commit(transacting)

def parse_user_input():
    parser = argparse.ArgumentParser(allow_abbrev = False,
    description = 'Database editor')
    parser.add_argument('-s', '--sample', action='store_true',
    help = 'run the sample')
    parser.add_argument('-i', '--input', action='store_true',
    help = 'give commands as input')
    parser.add_argument('db_url',
    help = 'the file holding the url of the database')
    args = parser.parse_args()
    return args

def main():
    user_input = parse_user_input()
    command = ""
    
    clubs = Table('clubs',
                {'clubid':'INTEGER'}, 
                {'name':'TEXT', 'description':'TEXT', 'info_shared':'BIT(2)'})
    clubmembers = Table('clubmembers',
                {'clubid':'INTEGER', 'netid':'TEXT'},
                {'is_moderator':'BOOL'})
    users = Table('users',
                {'netid':'TEXT'},
                {'is_admin':'BOOL', 'first_name':'TEXT', 
                'last_name':'TEXT', 'photo':'TEXT', 'phone':'TEXT', 
                'instagram':'TEXT', 'snapchat':'TEXT'})
    creationreqs = Table('creationreqs',
                {'name':'TEXT', 'netid':'TEXT'},
                {'description':'TEXT', 'info_shared':'BIT(2)'})
    joinreqs = Table('joinreqs',
                {'clubid':'INTEGER', 'netid':'TEXT'},
                {})
    tables = [clubs, clubmembers, users, creationreqs, joinreqs]
    execs = ["DROP", "CREATE", "INSERT", "UPDATE", "DELETE", "CHANGE ALL INSTANCES"]
    transacting = False

    env_vars = []
    
    try:
        with open(user_input.db_url) as f:
            for line in f:
                assignment = line.strip().split('=', 1)
                env_vars.append(assignment[0])
                os.environ.update(assignment)
        db_url = os.getenv(env_vars[0])
        with psycopg2.connect(db_url) as connection:
            with connection.cursor() as cursor:
                if user_input.sample:
                    sample(cursor, tables, transacting)
                if user_input.input:
                    print("Enter q to quit.")
                    while True:
                        prompt = ""
                        for i in range(len(tables)):
                            prompt += str(i) + ": " + tables[i].get_name() + " "
                        print(prompt)
                        command = input()
                        if (command=='q'):
                            break
                        table = tables[int(command)]
                        
                        prompt = ""
                        for i in range(len(tables)):
                            prompt += str(i) + ": " + execs[i] + " "
                        print(prompt)
                        command = input()
                        if (command=='q'):
                            break
                        exec = execs[int(command)]

                        


    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()