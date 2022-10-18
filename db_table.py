#!/usr/bin/env python

#-----------------------------------------------------------------------
# db_structure.py
# Author: Drew Curran
#-----------------------------------------------------------------------

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

#-----------------------------------------------------------------------

def _test():
    clubs = Table('clubs', {'clubid':'INTEGER'}, 
    {'name':'TEXT', 'description':'TEXT', 'info_shared':'BIT(2)'})
    # print(clubs.drop())
    # print(clubs.create())
    # print(clubs.select())
    # print(clubs.update({'name':'Women\'s Club Lacrosse'}, 
    # {'clubid':8, 'info_shared':'00'}))
    # print(clubs.insert({'clubid':1, 
    # 'name':'Women\'s Club Lacrosse',
    # 'description':'Free for all to join!', 'info_shared':'11'}))
    # print(clubs.delete({'clubid':1, 
    # 'name':'Women\'s Club Lacrosse'}))
    print()
    clubmembers = Table('clubmembers', {'clubid':'INTEGER'},
    {'netid':'TEXT', 'is_moderator':'BOOL'})
    print()
    users = Table('users', {'netid':'TEXT'},
    {'is_admin':'BOOL', 'first_name':'TEXT', 'last_name':'TEXT', 
    'photo':'TEXT', 'phone':'TEXT', 'instagram':'TEXT', 
    'snapchat':'TEXT'})
    print()
    creationreqs = Table('creationreqs', {'netid':'TEXT'},
    {'name':'TEXT', 'description':'TEXT', 'info_shared':'BIT(2)'})
    print()
    joinreqs = Table('joinreqs', {'clubid':'INTEGER'}, 
    {'netid':'TEXT'})
    print()

if __name__ == '__main__':
    _test()
