#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_edit.py
# Author: Drew Curran
# -----------------------------------------------------------------------

import sys
import argparse
from psycopg2 import sql
from psycopg2.extensions import AsIs

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

    def command_string(self, stmt_str, **kwargs):
        parameters = list(map(lambda x : x._wrapped, kwargs.get('parameters')))
        literals = kwargs.get('literals')
        if parameters:
            stmt_str = stmt_str.format(*parameters)
        if literals:
            stmt_str = stmt_str % tuple(*literals)
        return stmt_str
        
    def drop(self, **kwargs):
        parameters = []
        parameters.append(sql.Identifier(self._name))

        stmt_str = "DROP TABLE IF EXISTS {}"

        return {'stmt_str':stmt_str, 'parameters':parameters}

    def create(self, **kwargs):
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
        if values or indices is None:
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
    
    def select_all(self, **kwargs):
        parameters = []
        parameters.append(sql.Identifier(self._name))

        stmt_str = "SELECT * FROM {}"

        return {'stmt_str':stmt_str, 'parameters':parameters}

    def freeform(self, stmt_str, **kwargs):
        parameters = kwargs.get('parameters')
        literals = kwargs.get('literals')
        return {'stmt_str':stmt_str, 'parameters':parameters, 'literals':literals}

def parse_user_input(commands, tables):
    parser = argparse.ArgumentParser(allow_abbrev = False,
    description = 'Database edit statements')
    parser.add_argument('-v', '--values', type = dict,
    help = 'values given as arguments for the command')
    parser.add_argument('-i', '--indices', type = dict,
    help = 'indices given as arguments for the command')
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
    command = commands[user_input.command_num]
    table = tables[user_input.table_num]
    values = user_input.values
    indices = user_input.indices
    print("Command: " + command.__name__)
    print("Table: " + table.get_name())
    print("Values: " + str(values))
    print("Indices: " + str(indices))

    try:
        action = getattr(table, command.__name__)
        result = action(indices=indices, values=values)
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
        print(table.command_string(stmt_str, parameters=parameters, literals=literals))
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()