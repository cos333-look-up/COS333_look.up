#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_edit.py
# Author: Drew Curran
# -----------------------------------------------------------------------

import sys
import argparse
from psycopg2 import sql
from psycopg2.extensions import AsIs
import json

# -----------------------------------------------------------------------

## ANY WAY TO GET RID OF STRING PARAMETERIZATION? THEN NO NEED TO RETURN DICTIONARY
## CAN FUNCTIONS BE CALLED AS VARIABLES WITH DIFFERENT PARAMETERS? THEN NO NEED TO PASS **kwargs TO EVERYTHING
## ANY WAY TO CALL table.command() WITH MORE GENERALITY?

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
        
    def drop(self, **_):
        parameters = []
        parameters.append(sql.Identifier(self._name))

        stmt_str = "DROP TABLE IF EXISTS {}"

        return {'stmt_str':stmt_str, 'parameters':parameters}

    def create(self, **_):
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
        
        return {'stmt_str':stmt_str, 'parameters':parameters, 'literals':literals}

    def insert(self, **kwargs):
        values = kwargs.get('values')
        if values is None:
            raise Exception("Values dictionary is None")
        parameters = []
        parameters.append(sql.Identifier(self._name))
        parameters += list(map(lambda k : sql.Identifier(str(k)), values.keys()))
        parameters += list(map(lambda v : sql.Literal(str(v)), values.values()))

        stmt_str = "INSERT INTO {}"
        for i in range(len(values)):
            if i == 0:
                stmt_str += " ({}"
            else:
                stmt_str += ", {}"
            if i == len(values) - 1:
                stmt_str += ")"
        stmt_str += " VALUES"
        for i in range(len(values)):
            if i == 0:
                stmt_str += " ({}"
            else:
                stmt_str += ", {}"
            if i == len(values) - 1:
                stmt_str += ")"
        
        return {'stmt_str':stmt_str, 'parameters':parameters}
    
    def update(self, **kwargs):
        values = kwargs.get('values')
        indices = kwargs.get('indices')
        if values is None or indices is None:
            raise Exception("Values or Indices dictionary is None")
        parameters = []
        literals = []
        parameters.append(sql.Identifier(self._name))
        for key, val in values.items():
            parameters.append(sql.Identifier(key))
            parameters.append(sql.Literal(val))
            literals.append(AsIs('B') if self._attributes[key] == 'BIT(2)' else AsIs(''))
        for key, val in indices.items():
            parameters.append(sql.Identifier(key))
            parameters.append(sql.Literal(val))
            literals.append(AsIs('B') if self._attributes[key] == 'BIT(2)' else AsIs(''))
        
        stmt_str = "UPDATE {} SET"
        for i in range(len(values)):
            if i == 0:
                stmt_str += " {} = NULLIF(%s{}, NULL)"
            else:
                stmt_str += ", {} = NULLIF(%s{}, NULL)"
        stmt_str += " WHERE"
        for i in range(len(indices)):
            if i == 0:
                stmt_str += " {} = %s{}"
            else:
                stmt_str += "AND {} = %s{}"

        return {'stmt_str':stmt_str, 'parameters':parameters, 'literals':literals}
    
    def delete(self, **kwargs):
        indices = kwargs.get('indices')
        if indices is None:
            raise Exception("Indices dictionary is None")
        parameters = []
        literals = []
        parameters.append(sql.Identifier(self._name))
        for key, val in indices.items():
            parameters.append(sql.Identifier(key))
            parameters.append(sql.Literal(val))
            literals.append(AsIs('B') if self._attributes[key] == 'BIT(2)' else AsIs(''))
        
        stmt_str = "DELETE FROM {} WHERE"
        for i in range(len(indices)):
            if i == 0:
                stmt_str += " {} = %s{}"
            else:
                stmt_str += "AND {} = %s{}"

        return {'stmt_str':stmt_str, 'parameters':parameters, 'literals':literals}
    
    def select_all(self, **_):
        parameters = []
        parameters.append(sql.Identifier(self._name))

        stmt_str = "SELECT * FROM {}"

        return {'stmt_str':stmt_str, 'parameters':parameters}

    def freeform(self, **kwargs):
        stmt_str = kwargs.get('stmt_str')
        parameters = []
        parameters.append(sql.Identifier(self._name))
        literals = []
        return {'stmt_str':stmt_str, 'parameters':parameters, 'literals':literals}

def command_string(stmt_str, **kwargs):
    parameters = kwargs.get('parameters')
    if parameters:
        if type(parameters) == list:
            for i in range(len(parameters)):
                p = parameters[i]
                p = p._wrapped
                if (type(parameters[i]) == sql.Identifier):
                    p = ', '.join(p)
                parameters[i] = p
        stmt_str = stmt_str.format(*parameters)
    literals = kwargs.get('literals')
    if literals:
        if type(literals) == list:
            for i in range(len(literals)):
                l = literals[i]
                if (type(parameters[i]) == sql.Literal):
                    l = l.getquoted()
                literals[i] = l
            literals = tuple(literals)
        stmt_str = stmt_str % literals
    return stmt_str

def parse_user_input(commands, tables):
    parser = argparse.ArgumentParser(allow_abbrev = False,
    formatter_class=argparse.RawTextHelpFormatter,
    description = '\n'.join(tables[i].get_name() + ": " + ' '.join(attributes for attributes in tables[i].get_attributes()) for i in range(len(tables))))
    parser.add_argument('-v', '--values', type = json.loads,
    help = 'values given as arguments for the command')
    parser.add_argument('-i', '--indices', type = json.loads,
    help = 'indices given as arguments for the command')
    parser.add_argument('-s', '--stmt_str', type = str, nargs = '*',
    help = 'statement given for a free statement')
    parser.add_argument('command_num', type = int,
    help = ' '.join(str(i) + ": " + commands[i].__name__ for i in range(len(commands))))
    parser.add_argument('table_num', type = int,
    help = ' '.join(str(i) + ": " + tables[i].get_name() for i in range(len(tables))))
    user_input = parser.parse_args()
    return user_input

def main():
    commands = [Table.drop, Table.create, Table.insert, Table.update,
    Table.delete, Table.select_all, Table.freeform]
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
    user_input = parse_user_input(commands, tables)
    command_num = user_input.command_num
    table_num = user_input.table_num
    stmt_str = user_input.stmt_str
    values = user_input.values
    indices = user_input.indices
    if command_num is not None:
        command = commands[command_num]
        command_name = command.__name__
        print("Command: %s (%s)" % (command_num, command_name))
    if table_num is not None:
        table = tables[table_num]
        table_name = table.get_name()
        print("Table: %s (%s)" % (table_num, table_name))
    if stmt_str is not None:
        stmt_str = " ".join(stmt_str)
        print("Statement: %s" % (stmt_str))
    if values:
        print("Values: " + str(values))
    if indices:
        print("Indices: " + str(indices))

    '''
    Example Command Line
    > py db_edit.py 0 0
    Command: 0 (drop)
    Table: 0 (clubs)
    DROP TABLE IF EXISTS clubs

    > py db_edit.py 1 3
    Command: 1 (create)
    Table: 3 (creationreqs)
    CREATE TABLE creationreqs (name TEXT, netid TEXT, description TEXT, info_shared BIT(2))

    > py db_edit.py 2 2 -v "{\"netid\":\"denisac\", \"is_admin\":\"False\"}"
    Command: 2 (insert)
    Table: 2 (users)
    Values: {'netid': 'denisac', 'is_admin': 'False'}
    INSERT INTO users (netid, is_admin) VALUES (denisac, False)

    > py db_edit.py 3 0 -v {\"clubid\":4} -i {\"info_shared\":\"10\"}
    >py db_edit.py 3 0 -v {\"clubid\":4} -i {\"info_shared\":\"10\"}
    Command: 3 (update)
    Table: 0 (clubs)
    Values: {'clubid': 4}
    Indices: {'info_shared': '10'}
    UPDATE clubs SET clubid = NULLIF(4, NULL) WHERE info_shared = B10

    > py db_edit.py 4 4 -i {"""clubid""":4}
    py db_edit.py 4 4 -i {"""clubid""":4}
    Command: 4 (delete)
    Table: 4 (joinreqs)
    Indices: {'clubid': 4}
    DELETE FROM joinreqs WHERE clubid = 4

    > py db_edit.py 5 1
    Command: 5 (select_all)
    Table: 1 (clubmembers)
    SELECT * FROM clubmembers

    py db_edit.py 6 2 -s SELECT * FROM {}
    Command: 6 (freeform)
    Table: 2 (users)
    Statement: SELECT * FROM {}
    SELECT * FROM users
    '''

    try:
        action = getattr(table, command.__name__)
        result = action(stmt_str=stmt_str, values=values, indices=indices)
        if 'stmt_str' in result:
            stmt_str = result['stmt_str']
        else:
            stmt_str = None
        if 'parameters' in result:
            parameters = result['parameters']
        else:
            parameters = []
        if 'literals' in result:
            literals = result['literals']
        else:
            literals = []
        print(command_string(stmt_str, parameters=parameters, literals=literals))
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()