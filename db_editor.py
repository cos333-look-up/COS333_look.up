#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_editor.py
# Author: Drew Curran
# -----------------------------------------------------------------------

from re import L
import sys
import os
import argparse
#from psycopg2 import connect
#from psycopg2 import cursor
import psycopg2
from psycopg2.extensions import AsIs
from psycopg2 import sql
from db_edit import Table
from prettytable import PrettyTable as TableDisplay

# -----------------------------------------------------------------------

## ANY WAY TO GET RID OF STRING PARAMETERIZATION? THEN NO NEED TO RETURN DICTIONARY
## CAN FUNCTIONS BE CALLED AS VARIABLES WITH DIFFERENT PARAMETERS? THEN NO NEED TO PASS **kwargs TO EVERYTHING
## ANY WAY TO CALL table.command() WITH MORE GENERALITY?

class TableEditor:

    def __init__(self, cursor, tables):
        self._cursor = cursor
        self._tables = tables
        self._current_table = -1
        self._transacting = False
        self._queue = []

    def get_tables(self):
        return self._tables

    def get_current_table(self):
        return self._tables[self._current_table]

    def set_current_table(self, index):
        self._current_table = index

    def get_transacting(self):
        return self._transacting

    def get_queue(self):
        return self._queue

    def enqueue(self, function, **kwargs):
        parameters = []
        literals = []
        values = kwargs.get('values', [])
        indices = kwargs.get('indices', [])
        table = self._tables[self._current_table]
        action = getattr(table, function.__name__)
        result = action(values=values, indices=indices)
        stmt_str = result['stmt_str']
        if 'parameters' in result:
            parameters = result['parameters']
        if 'literals' in result:
            literals = result['literals']
        arguments = [stmt_str, parameters, literals]
        self._queue.append(arguments)
        return arguments

    def execute_queue(self):
        statements = ""
        while self._queue:
            query = self._queue.pop(0)
            
            stmt_str = self.execute(query)
            
            statements += stmt_str

        return statements

    def execute(self, query):
        try:
            stmt_str = query[0]
            stmt = sql.SQL(stmt_str)
        except:
            pass
        
        try:
            parameters = query[1]
            stmt = stmt.format(*parameters)
            if type(parameters) == list:
                for i in range(len(parameters)):
                    p = parameters[i]
                    p = p._wrapped
                    if (type(parameters[i]) == sql.Identifier):
                        p = ', '.join(p)
                    parameters[i] = p
            stmt_str = stmt_str.format(*parameters)
        except:
            pass
        
        try:
            literals = query[2]
            self._cursor.execute(stmt, literals)
            if type(literals) == list:
                for i in range(len(literals)):
                    l = literals[i]
                    if (type(parameters[i]) == sql.Literal):
                        l = l.getquoted()
                    literals[i] = l
                literals = tuple(literals)
            
            stmt_str = stmt_str % literals
        except:
            pass

        return stmt_str + "\n"

    def begin(self):
        stmt_str = "BEGIN"
        if not self._transacting:
            self._transacting = True
        return self.execute([stmt_str])
        
    def commit(self):
        stmt_str = "COMMIT"
        if self._transacting:
            self._transacting = False
        return self.execute([stmt_str])
        
    def rollback(self):
        stmt_str = "ROLLBACK"
        if self._transacting:
            self._transacting = False
        return self.execute([stmt_str])

    def display(self, name, attributes, data):
        table_display = TableDisplay()
        table_display.title = name
        table_display.field_names = attributes.keys()
        table_display.add_rows(data)
        return table_display

    def fetch_all(self):
        rows = []
        row = self._cursor.fetchone()
        rows.append(row)
        while row is not None:
            row = self._cursor.fetchone()
            rows.append(row)
        return rows[:-1]

def sample(editor):
    editor.begin()

    # clubs
    editor.set_current_table(0)
    table = editor.get_current_table()

    editor.enqueue(Table.drop)
    editor.enqueue(Table.create)
    editor.execute_queue()
    
    editor.enqueue(Table.insert,
                values = {'clubid':1, 
                'name':'Women\'s Club Lacrosse',
                'description':'Free for all to join!', 
                'info_shared':'11'})
    editor.enqueue(Table.insert,
                values = {'clubid':2, 
                'name':'Cloister',
                'description':'Official Cloister Club Page', 
                'info_shared':'10'})
    editor.enqueue(Table.insert,
                values = {'clubid':3, 
                'name':'Asian-American Students Association',
                'description':'Welcome!', 
                'info_shared':'01'})
    editor.enqueue(Table.insert,
                values = {'clubid':4, 
                'name':'Cannon',
                'description':'Cannon Homepage!', 
                'info_shared':'00'})
    editor.execute_queue()

    editor.enqueue(Table.select_all)
    editor.execute_queue()

    print(editor.display(table.get_name(), table.get_attributes(), editor.fetch_all()))

    # clubmembers
    editor.set_current_table(1)
    table = editor.get_current_table()
    editor.enqueue(Table.drop)
    editor.enqueue(Table.create)
    editor.execute_queue()
    editor.enqueue(Table.insert,
                values = {'clubid':2, 
                'netid':'bm18',
                'is_moderator':True})
    editor.enqueue(Table.insert,
                values = {'clubid':2, 
                'netid':'denisac',
                'is_moderator':False})
    editor.enqueue(Table.insert,
                values = {'clubid':2, 
                'netid':'pmt2',
                'is_moderator':True})
    editor.enqueue(Table.insert,
                values = {'clubid':3, 
                'netid':'evanwang',
                'is_moderator':False})
    editor.execute_queue()
    editor.enqueue(Table.select_all)
    editor.execute_queue()
    print(editor.display(table.get_name(), table.get_attributes(), editor.fetch_all()))

    # users
    editor.set_current_table(2)
    table = editor.get_current_table()
    editor.enqueue(Table.drop)
    editor.enqueue(Table.create)
    editor.execute_queue()
    editor.enqueue(Table.insert,
                values = {'netid':'denisac', 
                'is_admin':False,
                'first_name':'Drew',
                'last_name':'Curran', 
                'photo':'Placeholder',
                'phone':'+17037329370',
                'instagram':'drewcurran17', 
                'snapchat':None
                })
    editor.enqueue(Table.insert,
                values = {'netid':'dh37', 
                'is_admin':True,
                'first_name':'Daniel',
                'last_name':'Hu', 
                'photo':None,
                'phone':None,
                'instagram':None, 
                'snapchat':None
                })
    editor.enqueue(Table.insert,
                values = {'netid':'gleising', 
                'is_admin':True,
                'first_name':None,
                'last_name':None, 
                'photo':None,
                'phone':None,
                'instagram':None, 
                'snapchat':None
                })
    editor.enqueue(Table.insert,
                values = {'netid':'evanwang', 
                'is_admin':True,
                'first_name':'Evan',
                'last_name':'Wang', 
                'photo':'Placeholder',
                'phone':None,
                'instagram':None, 
                'snapchat':None
                })
    editor.enqueue(Table.insert,
                values = {'netid':'rc38', 
                'is_admin':True,
                'first_name':'Richard',
                'last_name':'Cheng', 
                'photo':None,
                'phone':'+13142952690',
                'instagram':None, 
                'snapchat':None
                })
    editor.execute_queue()
    editor.enqueue(Table.select_all)
    editor.execute_queue()
    print(editor.display(table.get_name(), table.get_attributes(), editor.fetch_all()))

    # creationreqs
    editor.set_current_table(3)
    table = editor.get_current_table()
    editor.enqueue(Table.drop)
    editor.enqueue(Table.create)
    editor.execute_queue()
    editor.enqueue(Table.insert,
                values = {'name':'Club Tennis', 
                'netid':'denisac',
                'description':'Official club',
                'info_shared':'11'
                })
    editor.enqueue(Table.insert,
                values = {'name':'Basketball Group', 
                'netid':'dh37',
                'description':'Group to play pickup basketball',
                'info_shared':'10'
                })
    editor.execute_queue()
    editor.enqueue(Table.select_all)
    editor.execute_queue()
    print(editor.display(table.get_name(), table.get_attributes(), editor.fetch_all()))
    
    # joinreqs
    editor.set_current_table(4)
    table = editor.get_current_table()
    editor.enqueue(Table.drop)
    editor.enqueue(Table.create)
    editor.execute_queue()
    editor.enqueue(Table.insert,
                values = {'clubid':2, 
                'netid':'jasonsun',
                })
    editor.enqueue(Table.insert,
                values = {'clubid':1, 
                'netid':'aleshire',
                })      
    editor.enqueue(Table.insert,
                values = {'clubid':2, 
                'netid':'arobang',
                })
    editor.execute_queue()
    editor.enqueue(Table.select_all)
    editor.execute_queue()
    print(editor.display(table.get_name(), table.get_attributes(), editor.fetch_all()))

    editor.commit()

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

    command = ""
    env_vars = []
    
    try:
        '''
        with open(user_input.db_url) as f:
            for line in f:
                assignment = line.strip().split('=', 1)
                print(assignment)
                env_vars.append(assignment[0])
                print("here")
                os.environ.update(line.strip().split('=', 1))
                print("here")
                db_url = os.getenv(env_vars[0])
        '''
        
        with open(user_input.db_url) as f:
            os.environ.update(line.strip().split('=', 1) for line in f)
        db_url = os.getenv('ELEPHANTSQL_URL')
        with psycopg2.connect(db_url) as connection:
            with connection.cursor() as cursor:
                editor = TableEditor(cursor, tables)
                if user_input.sample:
                    sample(editor)
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