#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: '2021-04-28 17:27:30 trottar'
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#
import math
import numpy as np
# Import pandas package
import pandas as pd

# Read in character sheets and convert to dataframe
char_stat = pd.read_csv('../characters/character_stats.csv', index_col=0)
# Convert dataframe to dictionary
char_stat = char_stat.to_dict()

npc_stat = pd.read_csv('../npcs/npc_stats.csv', index_col=0)
npc_stat = npc_stat.to_dict()

item_table = pd.read_csv('../items/items.csv', index_col=0)
item_table = item_table.to_dict()

def gen_dict_extract(key, var):
    if hasattr(var,'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result
						
def keys_exists(element, *keys):
    '''
    Check if *keys (nested) exists in `element` (dict).
    '''
    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True

# Lists to convert from ability score to modifier
ability_val = np.linspace(1,26,26)
mod_val = [-5,-4,-4,-3,-3,-2,-2,-1,-1,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8]

# Function for initialize checks
def initialize(character, roll, bonus=0):
	character = character.lower()
	if keys_exists(char_stat, "lvl", character):
		try:
			char_stat['init'][character]
		except KeyError:
			return(int(0))
		dex_mod = int(char_stat['init'][character])
		init_check = roll + dex_mod + bonus
		return(int(init_check))
	else:
		try:
			npc_stat['init'][character]
		except KeyError:
			return(int(0))
		dex_mod = int(npc_stat['init'][character])
		init_check = roll + dex_mod + bonus
		return(int(init_check))	

def damage_check(combat_type, damage_type, attacker, a_roll, defender, d_roll, a_bonus=0, d_bonus=0):
	combat_type = combat_type.lower() 
	attacker = attacker.lower()
	defender = defender.lower()
	# Function for combat results
	if keys_exists(char_stat, "lvl", attacker):
		try:
			char_stat[combat_type]
		except KeyError:
			return(combat_type,'is not an attack type')
		try:
			attack_val = a_roll+int(char_stat[combat_type][attacker])+a_bonus
		except KeyError:
			return(attacker,'is not a valid attacker')
	else:
		try:
			npc_stat[combat_type]
		except KeyError:
			return(combat_type,'is not an attack type')
		try:
			attack_val = a_roll+int(npc_stat[combat_type][attacker])+a_bonus
		except KeyError:
			return(attacker,'is not a valid attacker')
	if keys_exists(char_stat, "lvl", defender):
		try:
			defend_val = int(char_stat[damage_type][defender])+d_bonus
		except KeyError:
			return(defender,'is not a valid defender')
	else:
		try:
			defend_val = int(npc_stat[damage_type][defender])+d_bonus
		except KeyError:
			return(defender,'is not a valid defender')
	versus = attacker+' attacks '+defender
	damage = attack_val - defend_val
	if damage > 0 :
		return(f'%s \n ---------------------\n {defender}\'s armor penetrated') % (versus)
	else:
		return(f'%s \n ---------------------\n {defender}\'s armor NOT penetrated') % (versus)
	
def stat_check(character, stat=None):
	character = character.lower()
	if stat != None:
		stat = stat.lower()
	if stat==None:
		generated_items = [i for i in zip(list(char_stat.keys()),gen_dict_extract(character,char_stat))]
		return generated_items
	else:
		return(f'%s has %s %s') % (character,char_stat[stat][character],stat)
	
def item_check(item):
	item = item.lower()
	generated_items = [i for i in zip(list(item_table.keys()),gen_dict_extract(item,item_table))]
	for tup in generated_items[:]:
		if "-" in tup:
			generated_items.remove(tup)
	return generated_items