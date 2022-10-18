#!/usr/bin/env python

#-----------------------------------------------------------------------
# db_structure.py
# Author: Drew Curran
#-----------------------------------------------------------------------

class DataStructure:

    def __init__(self, name, attributes):
        self._name = name
        self._attributes = attributes

    def drop(self):
        return "DROP TABLE IF EXISTS " + self._name

    def create(self):
        stmt_str = "CREATE TABLE " + self._name + " "
        stmt_str += "(" + ", ".join(self.get_var_types()) + ")"
        return stmt_str

    def select(self, selection="*"):
        return "SELECT " + selection + " FROM " + self._name
    
    def update(self):
        pass

    def insert(self, vals):
        stmt_str = "INSERT INTO " + self._name  + " "
        stmt_str += "(" + ", ".join(self._attributes.keys()) + ") "
        stmt_str += "VALUES "
        stmt_str += "(" + ", ".join(self.get_var_vals(vals)) + ")"
        return stmt_str
    
    def delete(self):
        pass

    def get_name(self):
        return self._name

    def get_attributes(self):
        return self._attributes

    def get_var_types(self):
        var_types = []
        for var, type in self._attributes.items():
            var_types.append(var + " " + type)
        return var_types
    
    def get_var_vals(self, vals):
        var_vals = []
        for var, _ in self._attributes.items():
            val = vals[var]
            if (val == None):
                val = "NULL"
            var_vals.append(self.format_string(val))
        return var_vals

    def format_string(self, val):
        if val is not None:
            val = str(val).replace("'", "''")
            val = "'" + val + "'"
        return val

#-----------------------------------------------------------------------

def _test():
    clubs = DataStructure('clubs', {'clubid':'INTEGER', 
    'name':'TEXT', 'description':'TEXT', 'info_shared':'BIT(2)'})
    print(clubs.drop())
    print(clubs.create())
    print(clubs.select())
    print(clubs.update())
    print(clubs.insert({'clubid':1, 
    'name':'Women\'s Club Lacrosse', 'description':'Free for all to join!',
    'info_shared':11}))
    print(clubs.delete())
    print()
    clubmembers = DataStructure('clubmembers', {'clubid':'INTEGER', 
    'netid':'TEXT', 'is_moderator':'BOOL'})
    print(clubmembers.drop())
    print(clubmembers.create())
    print(clubmembers.select())
    print(clubmembers.update())
    #print(clubmembers.insert())
    print(clubmembers.delete())
    print()
    users = DataStructure('users', {'netid':'TEXT', 'is_admin':'BOOL',
    'first_name':'TEXT', 'last_name':'TEXT', 'photo':'TEXT', 
    'phone':'TEXT', 'instagram':'TEXT', 'snapchat':'TEXT'})
    print(users.drop())
    print(users.create())
    print(users.select())
    print(users.update())
    #print(users.insert())
    print(users.delete())
    print()
    creationreqs = DataStructure('creationreqs', {'netid':'TEXT',
    'name':'TEXT', 'description':'TEXT', 'info_shared':'BIT(2)'})
    print(creationreqs.drop())
    print(creationreqs.create())
    print(creationreqs.select())
    print(creationreqs.update())
    #print(creationreqs.insert())
    print(creationreqs.delete())
    print()
    joinreqs = DataStructure('joinreqs', {'clubid':'INTEGER', 
    'netid':'TEXT'})
    print(joinreqs.drop())
    print(joinreqs.create())
    print(joinreqs.select())
    print(joinreqs.update())
    #print(joinreqs.insert())
    print(joinreqs.delete())
    print()

if __name__ == '__main__':
    _test()
