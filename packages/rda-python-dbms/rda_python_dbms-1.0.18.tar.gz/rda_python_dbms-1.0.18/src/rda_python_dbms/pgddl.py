#!/usr/bin/env python3
#
##################################################################################
#
#     Title : pgddl
#    Author : Zaihua Ji, zji@ucar.edu
#      Date : 11/15/2020
#             2025-04-04 transferred to package rda_python_dbms from
#             https://github.com/NCAR/rda-database.git
#   Purpose : process a ddl (Data Definition Language) file to manipulate data
#             definition of a table defined in tablename.json
#
#    Github : https://github.com/NCAR/rda-python-dbms.git
#
##################################################################################
#
import os
import sys
import re
import pwd
from os import path as op
from rda_python_common import PgDBI
from rda_python_common import PgLOG
from rda_python_common import PgUtil
from . import PgDDLLib

PGACT = {
   'PKY' : ['', 'DEL', 'ADD'],  # DEL - to drop, ADD - to add primary key
   'UNQ' : ['', 'DEL', 'ADD'],  # DEL - to drop, ADD - to add unique constraint
   'CMT' : ['', 'DEL', 'ADD'],  # DEL - to set null, ADD to set comment 
   'DFT' : ['', 'DEL', 'ADD'],  # DEL - to drop, ADD - to set default value
   'JSN' : ['', 'ADD'],         # ADD - to add a new defination json file
   'NNL' : ['', 'DEL', 'ADD'],  # DEL - to drop, ADD - to set not null
   'IDX' : ['', 'DEL', 'ADD', 'CHG'],  # DEL/ADD/CHG - to drop, add and rename index
   'REF' : ['', 'DEL', 'ADD'],  # DEL - to drop, ADD - to add reference
   'TBL' : ['', 'DEL', 'ADD'],  # DEL - drop table, ADD - create table
   'FLD' : ['', 'DEL', 'ADD', 'MOD', 'CHG'],  # ADD/DEL/CHG/MOD - to add, drop, change and modify field
}

ACTIONS = {
   'a' : 'ADD',
   'c' : 'CHG',
   'd' : 'DEL',
   'm' : 'MOD'
}

OPTIONS = {
   'a' : ['TBL', 'IDX', 'REF'],
   'f' : 'FLD',
   'c' : 'CMT',
   'd' : 'DFT',
   'j' : 'JSN',
   'n' : 'NNL',
   'i' : 'IDX',
   'p' : 'PKY',
   'r' : 'REF',
   't' : 'TBL',
   'u' : 'UNQ'
}

VALUES = {
   'TBL' : [],
   'IDX' : [],
   'FLD' : [],
   'DFT' : [],
   'NNL' : [],
   'REF' : [],
   'UNQ' : []
}

DBFLDS = {
   'd' : 'dbname',
   'c' : 'scname',
   'h' : 'dbhost',
   'p' : 'dbport',
   'u' : 'lnname',
   'w' : 'pwname',
}

#
# main function to excecute this script
#
def main():

   option = 't'
   actopt = False
   tablenames = action = None
   dbopt = getall = False
   argv = sys.argv[1:]
   for arg in argv:
      ms = re.match(r'^-([abcdefhlmpstTuwxy])$', arg)
      if ms:
         option = ms.group(1)
         actopt = False
         if option in 'abefm':
            if option == "b":
               PgLOG.PGLOG['BCKGRND'] = 1
            elif option == "a":
               getall= True
            elif option == "e":
               PgDDLLib.PGDDL['override'] = True
            elif option == "f":
               PgDDLLib.PGDDL['usefile'] = True
            elif option == "m":
               PgDDLLib.PGDDL['mysqldb'] = True
            option = None
         continue

      ms = re.match(r'^-(\w)(\w)$', arg)
      if ms:
         action = ms.group(1)
         option = ms.group(2)
         actopt = True
         if option in OPTIONS and action in ACTIONS:
            act = ACTIONS[action]
            if option == 'a' and action != 'a':
               PgLOG.pglog("{}: Invalid Action to {} ALL".format(arg, act), PgLOG.LGEREX)
            opt = OPTIONS['t'] if option == 'a' else OPTIONS[option]
            if act in PGACT[opt][1:]:
               if option == 'a':
                  for opt in OPTIONS['a']:
                     PGACT[opt][0] = act
               else:
                  PGACT[opt][0] = act
               if 'ap'.find(option) > -1: option = 't'
               continue
         PgLOG.pglog(arg + ": Invalid Action", PgLOG.LGEREX)

      if re.match(r'^-.*', arg): PgLOG.pglog(arg + ": Unknown Option", PgLOG.LGEREX)
      if not option: PgLOG.pglog(arg + ": Value passed in without leading Option", PgLOG.LGEREX)

      if actopt:
         VALUES[OPTIONS[option]].append(arg)
      elif option in DBFLDS:
         PgDDLLib.DBINFO[DBFLDS[option]] = arg
         dbopt = True
      elif option == 'T':
         PgDDLLib.PGDDL['TBPATH'] = arg
      elif option == 'l':
         PgDDLLib.PGDDL['username'] = arg
      elif option == 'x':
         PgDDLLib.PGDDL['suffix'].append(arg)
      elif option == 'y':
         PgDDLLib.PGDDL['prefix'].append(arg)
      elif option == 's':
         PgDBI.PGDBI['SCPATH'] = arg
      else:
         VALUES[OPTIONS[option]].append(arg)
   
   if dbopt:
      PgDBI.default_scinfo(PgDDLLib.DBINFO['dbname'], PgDDLLib.DBINFO['scname'], PgDDLLib.DBINFO['dbhost'],
                           PgDDLLib.DBINFO['lnname'], PgDDLLib.DBINFO['pwname'], PgDDLLib.DBINFO['dbport'])   
   if VALUES['TBL']:
      tablenames = VALUES['TBL']
   elif getall:
      tablenames = PgDDLLib.allschematables();         # action on all tables
   if not (tablenames and action): PgLOG.show_usage('pgddl')
   PgLOG.PGLOG['LOGFILE'] = "pgddl.log"
   PgLOG.cmdlog("pgddl {}".format(' '.join(argv)))

   # process all or given tables to add/drop table/pkey/index/reference/field
   act = PGACT['TBL'][0]
   if act: PgDDLLib.process_tables(tablenames, act, 'TBL')
   for opt in PGACT:
      act = PGACT[opt][0]
      if opt == 'TBL' or not act: continue
      names = VALUES[opt] if opt in VALUES and VALUES[opt] else None
      PgDDLLib.process_tables(tablenames, act, opt, names)

   PgLOG.cmdlog()
   PgLOG.pgexit(0)

#
# call main() to start program
#
if __name__ == "__main__": main()
