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

class Table:

    def __init__(self, name, index, vals, cursor):
        self._name = name
        self._index = index
        self._vals = vals
        self._attributes = {**index, **vals}
        self._cursor = cursor
        self._transacting = False

    def get_name(self):
        return self._name

    def get_index(self):
        return self._index
    
    def get_vals(self):
        return self._vals

    def get_attributes(self):
        return self._attributes
    
    def get_transacting(self):
        return self._transacting

    def execute(self, stmt_str, p=[], l=[]):
        stmt = sql.SQL(stmt_str).format(*p)
        self._cursor.execute(stmt, l)
        return stmt.as_string(self._cursor.connection) % tuple(lit.getquoted()
        for lit in l)
    
    def begin(self):
        if not self._transacting:
            return self.execute("BEGIN")
        return None
    
    def commit(self):
        if self._transacting:
            return self.execute("COMMIT")
        return None
    
    def commit(self):
        if self._transacting:
            return self.execute("ROLLBACK")
        return None
        
    def drop(self):
        parameters = []
        parameters.append(sql.Identifier(self._name))

        stmt_str = "DROP TABLE IF EXISTS {}"

        self.execute(stmt_str, p=parameters)

    def create(self):
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
        
        self.execute(stmt_str, p=parameters, l=literals)

    def selectAll(self):
        parameters = []
        parameters.append(sql.Identifier(self._name))

        stmt_str = "SELECT * FROM {}"

        self.execute(stmt_str, parameters)
        return self._name, self._attributes
        
    def update(self, index, vals):
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

        self.execute(stmt_str, p=parameters, l=literals)

    def insert(self, vals):
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
        
        self.execute(stmt_str, p=parameters)
        
    def delete(self, index):
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

        self.execute(stmt_str, p=parameters, l=literals)

def display(name, attributes, cursor):
    data = fetch(cursor)
    table = Table_Display()
    table.title = name
    table.field_names = attributes.keys()
    table.add_rows(data)
    print(table)

def fetch(cursor):
    rows = []
    row = cursor.fetchone()
    rows.append(row)
    while row is not None:
        row = cursor.fetchone()
        rows.append(row)
    return rows[:-1]

def sample(cursor):
    clubs = Table('clubs',
                {'clubid':'INTEGER'}, 
                {'name':'TEXT', 'description':'TEXT', 'info_shared':'BIT(2)'},
                cursor)
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
    display(name, attributes, cursor)
    
    clubmembers = Table('clubmembers',
                {'clubid':'INTEGER', 'netid':'TEXT'},
                {'is_moderator':'BOOL'},
                cursor)
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
    display(name, attributes, cursor)

    users = Table('users',
                {'netid':'TEXT'},
                {'is_admin':'BOOL', 'first_name':'TEXT', 
                'last_name':'TEXT', 'photo':'TEXT', 'phone':'TEXT', 
                'instagram':'TEXT', 'snapchat':'TEXT'},
                cursor)
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
    display(name, attributes, cursor)

    creationreqs = Table('creationreqs',
                {'name':'TEXT', 'netid':'TEXT'},
                {'description':'TEXT', 'info_shared':'BIT(2)'},
                cursor)
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
    display(name, attributes, cursor)
    
    joinreqs = Table('joinreqs',
                {'clubid':'INTEGER', 'netid':'TEXT'},
                {},
                cursor)
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
    display(name, attributes, cursor)

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
    input = parse_user_input()

    try:
        with open(input.db_url) as f:
            os.environ.update(line.strip().split('=', 1) for line in f)
        db_url = os.getenv('ELEPHANTSQL_URL')
        with psycopg2.connect(db_url) as connection:
            with connection.cursor() as cursor:
                if input.sample:
                    sample(cursor)
                if input.input:
                    while 

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()