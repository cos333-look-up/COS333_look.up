#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_edit.py
# Author: Drew Curran
# -----------------------------------------------------------------------

import os
import sys
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

    def displayAll(self):
        self.selectAll()
        print(('-'*43 + '\n%s\n' + '-'*43) % self._name)

        row = self._cursor.fetchone()
        while row is not None:
            print(row)
            row = self._cursor.fetchone()
        
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
                clubs = Table('clubs', {'clubid':'INTEGER'}, 
                {'name':'TEXT', 'description':'TEXT', 'info_shared':'BIT(2)'},
                cursor)

                clubs.drop()
                clubs.create()
                clubs.insert({'clubid':1, 
                'name':'Women\'s Club Lacrosse',
                'description':'Free for all to join!', 
                'info_shared':'11'})
                clubs.displayAll()

                clubs.update({'name':'Women\'s Club Lacrosse'},
                {'clubid':8, 'info_shared':'00'})
                clubs.displayAll()

                clubs.delete({'clubid':8, 
                'name':'Women\'s Club Lacrosse'})
                clubs.displayAll()

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# -----------------------------------------------------------------------

if __name__ == '__main__':
    main()
