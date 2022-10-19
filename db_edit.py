#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_edit.py
# Author: Drew Curran
# -----------------------------------------------------------------------

import os
import sys
import argparse
from prettytable import PrettyTable as Table_Display
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import AsIs

# -----------------------------------------------------------------------

## TO DO: String parameterization, input commands, cursor scope

class Table:

    def __init__(self, name, index, vals):
        self._name = name
        self._index = index
        self._vals = vals
        self._attributes = {**index, **vals}

    def get_name(self):
        return self._name

    def get_index(self):
        return self._index
    
    def get_vals(self):
        return self._vals

    def get_attributes(self):
        return self._attributes
        
    def drop(self, cursor):
        parameters = []
        parameters.append(sql.Identifier(self._name))

        stmt_str = "DROP TABLE IF EXISTS {}"

        execute(stmt_str, cursor, p=parameters)

    ## ANY WAY TO GET RID OF STRING PARAMETERIZATION?
    def create(self, cursor):
        parameters = []
        literals = []
        parameters.append(sql.Identifier(self._name))
        for key, val in self._attributes.items():
            parameters.append(sql.Identifier(key))
            literals.append(AsIs(val))
        
        stmt_str = "CREATE TABLE {}"
        for i in range(len(self._attributes)):
            if i == 0:
                stmt_str += " ({} %s"
            else:
                stmt_str += ", {} %s"
            if i == len(self._attributes) - 1:
                stmt_str += ")"
        
        execute(stmt_str, cursor, p=parameters, l=literals)

    def insert(self, cursor, vals):
        parameters = []
        parameters.append(sql.Identifier(self._name))
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
        
        execute(stmt_str, cursor, p=parameters)
    
    ## ANY WAY TO GET RID OF STRING PARAMETERIZATION?
    def update(self, cursor, index, vals):
        parameters = []
        literals = []
        parameters.append(sql.Identifier(self._name))
        for key, val in vals.items():
            parameters.append(sql.Identifier(key))
            parameters.append(sql.Literal(val))
            literals.append(AsIs('B') if self._attributes[key] == 'BIT(2)' else AsIs(''))
        for key, val in index.items():
            parameters.append(sql.Identifier(key))
            parameters.append(sql.Literal(val))
            literals.append(AsIs('B') if self._attributes[key] == 'BIT(2)' else AsIs(''))
        
        stmt_str = "UPDATE {} SET"
        for i in range(len(vals)):
            if i == 0:
                stmt_str += " {} = NULLIF(%s{}, NULL)"
            else:
                stmt_str += ", {} = NULLIF(%s{}, NULL)"
        stmt_str += " WHERE"
        for i in range(len(index)):
            if i == 0:
                stmt_str += " {} = %s{}"
            else:
                stmt_str += "AND {} = %s{}"

        execute(stmt_str, cursor, p=parameters, l=literals)   
      
    def delete(self, cursor, index):
        parameters = []
        literals = []
        parameters.append(sql.Identifier(self._name))
        for key, val in index.items():
            parameters.append(sql.Identifier(key))
            parameters.append(sql.Literal(val))
            literals.append(AsIs('B') if self._attributes[key] == 'BIT(2)' else AsIs(''))
        
        stmt_str = "DELETE FROM {} WHERE"
        for i in range(len(index)):
            if i == 0:
                stmt_str += " {} = %s{}"
            else:
                stmt_str += "AND {} = %s{}"

        execute(stmt_str, cursor, p=parameters, l=literals)
    
    def selectAll(self, cursor):
        parameters = []
        parameters.append(sql.Identifier(self._name))

        stmt_str = "SELECT * FROM {}"

        execute(stmt_str, cursor, parameters)
        return self._name, self._attributes

def execute(stmt_str, cursor, p=[], l=[]):
        stmt = sql.SQL(stmt_str).format(*p)
        cursor.execute(stmt, l)
        return stmt.as_string(cursor.connection) % tuple(lit.getquoted()
        for lit in l)

def begin(cursor, transacting):
    if not transacting:
        transacting = True
    execute("BEGIN", cursor)
    
def commit(cursor, transacting):
    if transacting:
        transacting = False
    execute("COMMIT", cursor)
    
def rollback(cursor, transacting):
    if transacting:
        transacting = False
    execute("ROLLBACK", cursor)

def display(cursor, name, attributes):
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
    begin(cursor, transacting)
    clubs = tables[0]
    clubs.drop(cursor)
    clubs.create(cursor)
    clubs.insert(cursor,
                {'clubid':1, 
                'name':'Women\'s Club Lacrosse',
                'description':'Free for all to join!', 
                'info_shared':'11'})
    clubs.insert(cursor,
                {'clubid':2, 
                'name':'Cloister',
                'description':'Official Cloister Club Page', 
                'info_shared':'10'})
    clubs.insert(cursor,
                {'clubid':3, 
                'name':'Asian-American Students Association',
                'description':'Welcome!', 
                'info_shared':'01'})
    clubs.insert(cursor,
                {'clubid':4, 
                'name':'Cannon',
                'description':'Cannon Homepage!', 
                'info_shared':'00'})
    name, attributes = clubs.selectAll(cursor)
    display(cursor, name, attributes)
    
    clubmembers = tables[1]
    clubmembers.drop(cursor)
    clubmembers.create(cursor)
    clubmembers.insert(cursor,
                {'clubid':2, 
                'netid':'bm18',
                'is_moderator':True})
    clubmembers.insert(cursor,
                {'clubid':2, 
                'netid':'denisac',
                'is_moderator':False})
    clubmembers.insert(cursor,
                {'clubid':2, 
                'netid':'pmt2',
                'is_moderator':True})
    clubmembers.insert(cursor,
                {'clubid':3, 
                'netid':'evanwang',
                'is_moderator':False})
    name, attributes = clubmembers.selectAll(cursor)
    display(cursor, name, attributes)

    users = tables[2]
    users.drop(cursor)
    users.create(cursor)
    users.insert(cursor,
                {'netid':'denisac', 
                'is_admin':False,
                'first_name':'Drew',
                'last_name':'Curran', 
                'photo':'Placeholder',
                'phone':'+17037329370',
                'instagram':'drewcurran17', 
                'snapchat':None
                })
    users.insert(cursor,
                {'netid':'dh37', 
                'is_admin':True,
                'first_name':'Daniel',
                'last_name':'Hu', 
                'photo':None,
                'phone':None,
                'instagram':None, 
                'snapchat':None
                })
    users.insert(cursor,
                {'netid':'gleising', 
                'is_admin':True,
                'first_name':None,
                'last_name':None, 
                'photo':None,
                'phone':None,
                'instagram':None, 
                'snapchat':None
                })
    users.insert(cursor,
                {'netid':'evanwang', 
                'is_admin':True,
                'first_name':'Evan',
                'last_name':'Wang', 
                'photo':'Placeholder',
                'phone':None,
                'instagram':None, 
                'snapchat':None
                })
    users.insert(cursor,
                {'netid':'rc38', 
                'is_admin':True,
                'first_name':'Richard',
                'last_name':'Cheng', 
                'photo':None,
                'phone':'+13142952690',
                'instagram':None, 
                'snapchat':None
                })
    name, attributes = users.selectAll(cursor)
    display(cursor, name, attributes)

    creationreqs = tables[3]
    creationreqs.drop(cursor)
    creationreqs.create(cursor)
    creationreqs.insert(cursor,
                {'name':'Club Tennis', 
                'netid':'denisac',
                'description':'Official club',
                'info_shared':'11'
                })
    creationreqs.insert(cursor,
                {'name':'Basketball Group', 
                'netid':'dh37',
                'description':'Group to play pickup basketball',
                'info_shared':'10'
                })
    name, attributes = creationreqs.selectAll(cursor)
    display(cursor, name, attributes)
    
    joinreqs = tables[4]
    joinreqs.drop(cursor)
    joinreqs.create(cursor)
    joinreqs.insert(cursor,
                {'clubid':2, 
                'netid':'jasonsun',
                })
    joinreqs.insert(cursor,
                {'clubid':1, 
                'netid':'aleshire',
                })      
    joinreqs.insert(cursor,
                {'clubid':2, 
                'netid':'arobang',
                })
    name, attributes = joinreqs.selectAll(cursor)
    display(cursor, name, attributes)
    commit(cursor, transacting)

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
    execs = ["DROP", "CREATE", "INSERT", "UPDATE", "DELETE"]
    transacting = False

    try:
        with open(user_input.db_url) as f:
            os.environ.update(line.strip().split('=', 1) for line in f)
        db_url = os.getenv('ELEPHANTSQL_URL')
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