#!/usr/bin/env python

#-----------------------------------------------------------------------
# db_structure.py
# Author: Drew Curran
#-----------------------------------------------------------------------

class DataStructure:

    def __init__(self, name, index, vals):
        self._name = name
        self._index = index
        self._vals = vals
        self._attributes = {**index, **vals}

    def drop(self):
        return "DROP TABLE IF EXISTS " + self._name

    def create(self):
        stmt_str = "CREATE TABLE " + self._name + " "
        var_types = []
        for var, type in self._attributes.items():
            var_types.append(var + " " + type)
        stmt_str += "(" + ", ".join(var_types) + ")"
        return stmt_str

    def select(self, selection="*"):
        return "SELECT " + selection + " FROM " + self._name
    
    def update(self, index, vals):
        stmt_str = "UPDATE clubs SET "
        for key in self._attributes.keys():
            try:
                val = self.format_string(vals[key])
                stmt_str += key + " = COALESCE(" + val + ", " + key + ") "
            except:
                pass
        stmt_str += "WHERE "
        first = True
        for key in self._attributes.keys():
            try:
                if first:
                    val = self.format_string(index[key])
                    stmt_str += key + " = " + val + " "
                    first = False
                else:
                    val = self.format_string(index[key])
                    stmt_str += "AND " + key + " = " + val + " "
            except:
                pass
            
        return stmt_str

    def insert(self, vals):
        stmt_str = "INSERT INTO " + self._name  + " "
        stmt_str += "(" + ", ".join(self._attributes.keys()) + ") "
        stmt_str += "VALUES "
        var_vals = []
        for key in self._attributes.keys():
            try:
                val = self.format_string(vals[key])
            except:
                pass
            var_vals.append(val)
        stmt_str += "(" + ", ".join(var_vals) + ")"
        return stmt_str
    
    def delete(self):
        pass

    def get_name(self):
        return self._name

    def get_index(self):
        return self._index
    
    def get_vals(self):
        return self._vals

    def get_attributes(self):
        return self._attributes

    def format_string(self, val):
        if val is not None:
            val = str(val).replace("'", "''")
            val = "'" + val + "'"
        else:
            val = "NULL"
        return val

#-----------------------------------------------------------------------

def _test():
    clubs = DataStructure('clubs', {'clubid':'INTEGER'}, 
    {'name':'TEXT', 'description':'TEXT', 'info_shared':'BIT(2)'})
    print(clubs.drop())
    print(clubs.create())
    print(clubs.select())
    print(clubs.update({'name':'Women\'s Club Lacrosse'}, 
    {'clubid':8, 'info_shared':'00'}))
    print(clubs.insert({'clubid':1, 
    'name':'Women\'s Club Lacrosse',
    'description':'Free for all to join!', 'info_shared':'11'}))
    print(clubs.delete())
    print()
    clubmembers = DataStructure('clubmembers', {'clubid':'INTEGER'},
    {'netid':'TEXT', 'is_moderator':'BOOL'})
    print(clubmembers.drop())
    print(clubmembers.create())
    print(clubmembers.select())
    #print(clubmembers.update())
    #print(clubmembers.insert())
    print(clubmembers.delete())
    print()
    users = DataStructure('users', {'netid':'TEXT'},
    {'is_admin':'BOOL', 'first_name':'TEXT', 'last_name':'TEXT', 
    'photo':'TEXT', 'phone':'TEXT', 'instagram':'TEXT', 
    'snapchat':'TEXT'})
    print(users.drop())
    print(users.create())
    print(users.select())
    #print(users.update())
    #print(users.insert())
    print(users.delete())
    print()
    creationreqs = DataStructure('creationreqs', {'netid':'TEXT'},
    {'name':'TEXT', 'description':'TEXT', 'info_shared':'BIT(2)'})
    print(creationreqs.drop())
    print(creationreqs.create())
    print(creationreqs.select())
    #print(creationreqs.update())
    #print(creationreqs.insert())
    print(creationreqs.delete())
    print()
    joinreqs = DataStructure('joinreqs', {'clubid':'INTEGER'}, 
    {'netid':'TEXT'})
    print(joinreqs.drop())
    print(joinreqs.create())
    print(joinreqs.select())
    #print(joinreqs.update())
    #print(joinreqs.insert())
    print(joinreqs.delete())
    print()

if __name__ == '__main__':
    _test()
