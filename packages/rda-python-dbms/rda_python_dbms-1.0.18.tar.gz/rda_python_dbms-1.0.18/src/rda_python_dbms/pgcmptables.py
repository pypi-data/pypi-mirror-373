#!/usr/bin/env python3
#
##################################################################################
#
#     Title : pgcmptables
#    Author : Zaihua Ji, zji@ucar.edu
#      Date : 07/17/2023
#             2025-04-09 transferred to package rda_python_dbms from
#             https://github.com/NCAR/rda-utility-programs.git
#   Purpose : check and compare table columns, indexes and data of identical tables
#             between two servers
#
#    Github : https://github.com/NCAR/rda-python-dbms.git
#
##################################################################################

import sys
import os
import re
from os import path as op
from time import time as tm
import datetime
from datetime import timedelta as td
from datetime import datetime as dt
from rda_python_common import PgLOG
from rda_python_common import PgDBI
from rda_python_common import PgUtil
from . import MyDBI

PVALS = {
   'db' : None,
   'sc' : None,
   'us' : None,
   'pw' : None,
   'ht' : None,
   'pn' : 0,
   'sk' : None,
   'cd' : None,
   'cs' : None,
   'cu' : None,
   'cp' : None,
   'ch' : None,
   'cn' : 0,
   'ck' : None,
   'if' : None,    # input file holds table list of given schema to compare
   'ct' : 'pg',    # db server type, default to MySQL , optional to PostgreSQL
   'a'  : False,   # True for all tables in schema specified
   'f'  : False,   # True to fix table structure and/or data content
   's'  : False,   # True to display mismatching table structure and/or data content detail
   'tb' : [],
   'at' : False,   # True to add tables missing in target schema
   'ns' : False,   # True to convert Nul to space for text fields
   'co' : 1,       # 1, 2, and/or 4, table columns, indexes and/or data; 8 for replace data
   'lm' : 0,       # compare lm table records at a time, 0 to compare all at once
   'umsg' : None
}

TSCHEMA = CSCHEMA = None

#
# main function to run dsarch
#
def main():

   argv = sys.argv[1:]

   for arg in argv:
      if arg == "-b":
         PgLOG.PGLOG['BCKGRND'] = 1
      elif re.match(r'^-(a|f|s|at|ns)$', arg):
         PVALS[arg[1:]] = True
      elif re.match(r'^-(db|ht|if|pn|pw|sc|tb|us|co|lm|cd|ch|cn|cp|cs|cu|ct)$', arg):
         option = arg[1:]
      elif re.match(r'^-', arg):
         PgLOG.pglog(arg + ": Invalid Option", PgLOG.LGWNEX)
      elif option:
         if option == 'tb':
            PVALS[option].append(arg)
         else:
            PVALS[option] = int(arg) if option == 'co' or option == 'lm' else arg
            option = None
      else:
         PgLOG.pglog(arg + ": Invalid parameter", PgLOG.LGWNEX)
   
   PgLOG.PGLOG['LOGFILE'] = "pgcmptables.log"
   sc = PVALS['sc']
   if sc is None and PVALS['db']: sc = PVALS['db']

   if not (PVALS['ht'] and PVALS['ch'] and sc):
      print("Usage:\npgcmptables [-a] [-b] [-f] [-s] [-tb TABLES] [-co CMPOPTION] [-lm LIMIT] -ht HOSTNAME  \\")
      print("    -ch CMPHOST [-sc SCHEMA] [-db DATABASE] [-us USERNAME] [-pw PASSWORD] [-if INPUTFILE]  \\")
      print("    [-cs CMPSCHEMA] [-ct CMPDBTYPE] [-cd CMPDB] [-cu CMPUSER] [-cp CMPPASSWORD]  \\")
      print("    [-po DBPORTNO] [-cn CMPPORTNO] [-sk SOCKET] [-ck CMPSOCKET]")
      print("  Option  -a - compare all tables in the specified schema")
      print("  Option  -f - force to fix the table structures and/or data contents")
      print("  Option  -s - display the mismatching table structures and/or data content detail")
      print("  Option -if - input file name to hold a table list in database schema")
      print("  Option -at - add tables missing in target database schema")
      print("  Option -ns - replace Nul to space in text fields")
      print("  Option -tb - specify the table names, compare all tables in schema if -a presents")
      print("  Option -co - compare option, valid values are 1,2,(4|8); 1-columns, 2-indexes, and/or (4-data or 8-replace)")
      print("  Option -lm - compare limit of records each time; default to 0 for all records at once")
      print("  Option -ht - host name of database server is running on")
      print("  Option -sc - the schema name, default to database name")
      print("  Option -db - the database name, default to -sc")
      print("  Option -us - specify the user name, default to -sc")
      print("  Option -pw - the password, default to -us")
      print("  Option -pn - the port number to connect to remote database")
      print("  Option -sk - the socket to connect to local database")
      print("  Option -ch - host name of the compared database server")
      print("  Option -cs - the schema name is compared, default to -sc")
      print("  Option -ct - the compared database type, my - MySQL, pg - PostgreSQL, default to pg")
      print("  Option -cd - the compared database name, default to -db")
      print("  Option -cu - the compared user name, default to -us")
      print("  Option -cp - the compared password, default to -cu")
      print("  Option -cn - the port number to connect to remote compared database")
      print("  Option -ck - the socket to connect to local compared database")
      sys.exit(0)

   if not PVALS['a']:
      if PVALS['if']: PVALS['tb'].extend(get_table_list(PVALS['if']))
      if not PVALS['tb']:
         PgLOG.pglog("Option -a must present if No table names specified", PgLOG.LGWNEX)
      else:   # check wildcard table names
         tables = PVALS['tb']
         PVALS['tb'] = []
         for tb in tables:
            if tb.find("%") > -1:
               tbls = pg_wildcard_tables(tb, sc)
               for tbl in tbls:
                  if tbl not in PVALS['tb']: PVALS['tb'].append(tbl)
            elif tb not in PVALS['tb']:
               PVALS['tb'].append(tb)
         if not PVALS['tb']:
            PgLOG.pglog(str(tables) + ": No table name identified for Wildcard provided", PgLOG.LGWNEX)

   # expand the parameters provided
   if PVALS['db'] is None: PVALS['db'] = sc
   if PVALS['us'] is None: PVALS['us'] = sc
   if PVALS['pw'] is None: PVALS['ps'] = PVALS['us']
   if PVALS['cs'] is None: PVALS['cs'] = sc
   if PVALS['cd'] is None: PVALS['cd'] = PVALS['db']
   if PVALS['cu'] is None: PVALS['cu'] = PVALS['us']
   if PVALS['cp'] is None: PVALS['cp'] = PVALS['pw']

   PgLOG.cmdlog("pgcmptables {}".format(' '.join(argv)))
   compare_tables(sc)
   PgLOG.cmdlog()
   sys.exit(0)

#
# get the table list from given input file
#
def get_table_list(ifile):

   tables = []
   with open(ifile) as fd:
      lines = fd.readlines() 
      tables = [line.strip() for line in lines]
   return tables

#
# compare tables, and do fix according values of option -c & -f
#
def compare_tables(sc):

   global TSCHEMA, CSCHEMA

   TSCHEMA = "Postgres Database.Schema {}.{} on {}".format(PVALS['db'], sc, PVALS['ht'])
   if PVALS['ct'] == 'my':
      CSCHEMA = "MySQL Database {} on {}".format(PVALS['cd'], PVALS['ch'])
   else:
      CSCHEMA = "Postgres Database.Schema {}.{} on {}".format(PVALS['cd'], PVALS['cs'], PVALS['ch'])

   if not PVALS['tb']: compare_schema_tables(sc)

   tbcnt = len(PVALS['tb'])
   if tbcnt > 1:
      bt = tm() 
      PgLOG.pglog("Compare {} Tables between {} and {}".format(tbcnt, TSCHEMA, CSCHEMA), PgLOG.LOGWRN)

   for tb in PVALS['tb']:
      if PVALS['co']&1: compare_table_columns(tb, sc)
      if PVALS['co']&2: compare_table_indexes(tb, sc)
      if PVALS['co']&4:
         compare_table_records(tb, sc, PVALS['lm'])
      elif PVALS['co']&8:
         replace_table_records(tb, sc, PVALS['lm'])
         
   if tbcnt > 1:
      rmsg = PgLOG.seconds_to_string_time(tm() - bt)
      PgLOG.pglog("{} Tables Compared ({}) between {} and {}".format(tbcnt, rmsg, TSCHEMA, CSCHEMA), PgLOG.LOGWRN)

#
# gather table names for a given wildcard name
#
def pg_wildcard_tables(tb, sc):

   ttbl = 'information_schema.tables'
   tfld = 'table_name tnm'
   tcnd = "table_schema = '{}' AND table_name LIKE '{}' AND table_type = 'BASE TABLE'"
   pg_target_scname(sc, PVALS['db'])
   ttables = PgDBI.pgmget(ttbl, tfld, tcnd.format(sc, tb))
   return ttables['tnm'] if ttables else []

#
# Set Target Schema information for Postgres database connection
#
def pg_target_scname(sc, db):

   PgDBI.set_scname(db, sc, PVALS['us'], PVALS['pw'], PVALS['ht'], PVALS['pn'], PVALS['sk'])

#
# Set comparing Schema information for Postgres database connection
#
def pg_compare_scname(sc, db):

   PgDBI.set_scname(db, sc, PVALS['cu'], PVALS['cp'], PVALS['ch'], PVALS['cn'], PVALS['ck'])
   return sc

#
# Set comparing Database information for MySQL database connection
#
def my_compare_dbname(db):

   MyDBI.set_dbname(db, PVALS['cu'], PVALS['cp'], PVALS['ch'], PVALS['cn'], PVALS['ck'])
   return db

#
# replace records for a given table
#
def replace_table_records(tb, sc, lmt):

   PgLOG.pglog("{}: Replace Table Data Contents in {} from {}".format(tb, TSCHEMA, CSCHEMA), PgLOG.LOGWRN)

   if PVALS['ct'] == 'my':
      cd = my_compare_dbname(PVALS['cd'])
      (ckey, cfld) = my_table_ukey(tb, cd)
      cidxs = my_table_indexes(tb, cd)
   else:
      cs = pg_compare_scname(PVALS['cs'], PVALS['cd'])
      (ckey, cfld) = pg_table_ukey(tb, cs)
      cidxs = pg_table_indexes(tb, cs)

   pg_target_scname(sc, PVALS['db'])
   dcnt = pg_clean_records(tb, sc)
   if dcnt < 0: return
   # remove indexes for speeding up inserts
   tidxs = pg_table_indexes(tb, sc)
   if tidxs: pg_delete_indexes(tb, sc, tidxs, False)

   ttcnt = tccnt = rcnt = coff = 0
   crecs = []
   while coff > -1:
      rcnt += 1
      bt = tm()
      if PVALS['ct'] == 'my':
         cd = my_compare_dbname(PVALS['cd'])
         crecs = my_table_records(tb, cd, ckey, lmt, coff, False)
      else:
         cs = pg_compare_scname(PVALS['cs'], PVALS['cd'])
         crecs = pg_table_records(tb, cs, ckey, lmt, coff, False)
      ccnt = len(crecs)
      tccnt += ccnt
      tstr = " ({} total)".format(tccnt) if tccnt > ccnt else ''
      rmsg = PgLOG.seconds_to_string_time(tm() - bt)
      PgLOG.pglog("{}: Got {} Records{} ({}) in {}".format(tb, ccnt, tstr, rmsg, CSCHEMA), PgLOG.LOGWRN)
      coff = -1 if (lmt == 0 or ccnt < lmt) else (coff + lmt)
      if ccnt == 0: continue

      pg_target_scname(sc, PVALS['db'])
      tcnt = pg_add_records(tb, sc, crecs, False)
      ttcnt += tcnt

   # add indexes
   if cidxs: pg_add_indexes(tb, sc, cidxs, False)

   if rcnt > 1:
      PgLOG.pglog("{}: Total {} Records Got in {}".format(tb, tccnt, CSCHEMA), PgLOG.LOGWRN)
      PgLOG.pglog("{}: Total {} Records Added in {}".format(tb, ttcnt, TSCHEMA), PgLOG.LOGWRN)

#
# Clean the Postgres target table by deleting all the records
#
def pg_clean_records(tb, sc):

   msg = "{}: Clean all table records in {}".format(tb, TSCHEMA)
   PgLOG.pglog(msg, PgLOG.LOGWRN)
   if not PVALS['f']:
      msg = "{}: Add Option -f to clean the table Records in {}".format(tb, TSCHEMA)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      return -1

   bt = tm()
   tbl = '{}.{}'.format(PgDBI.pgname(sc), PgDBI.pgname(tb))
   PgDBI.pgexec("TRUNCATE TABLE " + tbl, PgLOG.LGEREX)
   rmsg = PgLOG.seconds_to_string_time(tm() - bt)
   PgLOG.pglog("{}: Cleaned Table ({}) from {}".format(tb, rmsg, TSCHEMA), PgLOG.LOGWRN)

   return 0

#
# compare records for a given table
#
def compare_table_records(tb, sc, lmt):

   PgLOG.pglog("{}: Compare Table Data Contents between {} and {}".format(tb, TSCHEMA, CSCHEMA), PgLOG.LOGWRN)

   tbt = tm()
   if PVALS['ct'] == 'my':
      cd = my_compare_dbname(PVALS['cd'])
      (ckey, cfld) = my_table_ukey(tb, cd)
   else:
      cs = pg_compare_scname(PVALS['cs'], PVALS['cd'])
      (ckey, cfld) = pg_table_ukey(tb, PVALS['cs'])

   msg = ''
   pg_target_scname(sc, PVALS['db'])
   (tkey, tfld) = pg_table_ukey(tb, sc)
   if ckey != tkey:
      msg = "Mismatch Unique Key {}/{}".format(tkey, ckey)
   elif cfld != tfld:
      msg = "Mismatch Column Name {}/{}".format(tfld, cfld)
   if msg:
      PgLOG.pglog("{}: {} in {} to compare data contents".format(tb, msg, TSCHEMA), PgLOG.LOGWRN)
      return

   ttcnt = tccnt = coff = toff = 0
   rcnt = tmcnt = mccnt = mtcnt = 0
   dcnt = acnt = ucnt = 0
   matched = True
   PVALS['umsg'] = ''
   crecs = []
   trecs = []
   drecs = []
   arecs = []
   urecs = []
   while coff > -1 or toff > -1:
      clmt = tlmt = lmt
      rcnt += 1         
      if coff < 0:
         crecords = []
         ccnt = 0
      else:
         if mccnt: clmt -= mccnt
         bt = tm()
         if PVALS['ct'] == 'my':
            cd = my_compare_dbname(PVALS['cd'])
            crecords = my_table_records(tb, cd, ckey, clmt, coff)
         else:
            cs = pg_compare_scname(PVALS['cs'], PVALS['cd'])
            crecords = pg_table_records(tb, PVALS['cs'], ckey, clmt, coff)
         ccnt = len(crecords)
         tccnt += ccnt
         tstr = " ({} total)".format(tccnt) if tccnt > ccnt else ''
         rmsg = PgLOG.seconds_to_string_time(tm() - bt)
         PgLOG.pglog("{}: Got {} Records{} ({}) in {}".format(tb, ccnt, tstr, rmsg, CSCHEMA), PgLOG.LOGWRN)
         coff = -1 if (lmt == 0 or ccnt < clmt) else (coff + clmt)

      if toff < 0:
         trecords = []
         tcnt = 0
      else:
         bt = tm()
         if mtcnt: tlmt -= mtcnt
         pg_target_scname(sc, PVALS['db'])
         trecords = pg_table_records(tb, sc, tkey, tlmt, toff)
         tcnt = len(trecords)
         ttcnt += tcnt
         tstr = " ({} total)".format(ttcnt) if ttcnt > tcnt else ''
         rmsg = PgLOG.seconds_to_string_time(tm() - bt)
         PgLOG.pglog("{}: Got {} Records{} ({}) in {}".format(tb, tcnt, tstr, rmsg, TSCHEMA), PgLOG.LOGWRN)
         toff = -1 if (lmt == 0 or tcnt < tlmt) else (toff + tlmt)

      if mccnt:
         ccnt += mccnt
         crecords = crecs + crecords
         mccnt = 0
      elif mtcnt:
         tcnt += mtcnt
         trecords = trecs + trecords
         mtcnt = 0

      mcnt = i = j = 0

      while j < tcnt:
         trec = trecords[j]
         while i < ccnt:
            crec = crecords[i]
            ret = compare_unique_keys(tkey, trec, crec)
            if ret == 0:
               urec = compare_one_record(tkey, tfld, trec, crec)
               if urec:
                  urecs.append(urec)
               else:
                  mcnt += 1
               i += 1
               j += 1
               break
            elif ret < 0:
               drecs.append(trec)
               j += 1
               break
            elif ret > 0:
               arecs.append(crec)
               i += 1
         if i >= ccnt: break

      if i < ccnt:
         if toff < 0:
            arecs += crecords[i:ccnt]
            if not drecs:
               acnt += pg_add_records(tb, sc, arecs)
               arecs = []
               matched = False
         else:
            crecs = crecords[i:ccnt]
            mccnt = len(crecs)
            s = 's' if mccnt > 1 else ''
            PgLOG.pglog("{}: recompare {} record{} in {}".format(tb, mccnt, s, CSCHEMA), PgLOG.LOGWRN)
      elif j < tcnt:
         if coff < 0:
            drecs += trecords[j:tcnt]
         else:
            trecs = trecords[j:tcnt]
            mtcnt = len(trecs)
            s = 's' if mtcnt > 1 else ''
            PgLOG.pglog("{}: recompare {} record{} in {}".format(tb, mtcnt, s, TSCHEMA), PgLOG.LOGWRN)

      nd = len(drecs)
      na = len(arecs)
      nu = len(urecs)
      if (mcnt+na+nd+nu) > 0:
         PgLOG.pglog("{}: {}/{}/{}/{} Records Matched/To Delete/To Add/To Update".format(tb, mcnt, nd, na, nu), PgLOG.LOGWRN)
      tmcnt += mcnt

   mc = 0
   if drecs and arecs:
      (mc, drecs, arecs) = pg_rematch_records(drecs, arecs, urecs, tkey, tfld)
      tmcnt += mc

   nd = len(drecs)
   na = len(arecs)
   nu = len(urecs)
   if (mc > 0 or rcnt > 1) and (nd+na+nu) > 0:
      PgLOG.pglog("{}: Total {}/{}/{}/{} Records Matched/To Delete/To Add/To Update".format(tb, tmcnt, nd, na, nu), PgLOG.LOGWRN)

   pg_target_scname(sc, PVALS['db'])
      
   if drecs:
      dcnt += pg_delete_records(tb, sc, tkey, drecs)
      matched = False
   if arecs:
      acnt += pg_add_records(tb, sc, arecs)
      matched = False
   if urecs:
      ucnt += pg_update_records(tb, sc, tkey, urecs)
      matched = False

   if rcnt > 1:
      rmsg = PgLOG.seconds_to_string_time(tm() - tbt)
      if matched:
         PgLOG.pglog("{}: All {} records matched ({})".format(tb, ttcnt, rmsg), PgLOG.LOGWRN)
      else:
         PgLOG.pglog("{}: Got Total {} Records in {}".format(tb, tccnt, CSCHEMA), PgLOG.LOGWRN)
         PgLOG.pglog("{}: Got Total {} Records in {}".format(tb, ttcnt, TSCHEMA), PgLOG.LOGWRN)
         PgLOG.pglog("{}: Total {}/{}/{}/{} Records Matched/Deleted/Added/Updated ({})".format(tb, tmcnt, dcnt, acnt, ucnt, rmsg), PgLOG.LOGWRN)

#
# rematch between delete/add records
#
def pg_rematch_records(drecs, arecs, urecs, tkey, tfld):

   drecs = ukeysort(drecs, tkey)
   arecs = ukeysort(arecs, tkey)
   dcnt = len(drecs)
   acnt = len(arecs)
   mcnt = i = j = 0
   rdrecs = []
   rarecs = []
   while j < dcnt:
      drec = drecs[j]
      while i < acnt:
         arec = arecs[i]
         ret = compare_unique_keys(tkey, drec, arec)
         if ret == 0:
            urec = compare_one_record(tkey, tfld, drec, arec)
            if urec:
               urecs.append(urec)
            else:
               mcnt += 1
            i += 1
            j += 1
            break
         elif ret < 0:
            rdrecs.append(drec)
            j += 1
            break
         elif ret > 0:
            rarecs.append(arec)
            i += 1
      if i >= acnt: break

   if i < acnt:
      rarecs += arecs[i:acnt]
   elif j < dcnt:
      rdrecs += drecs[j:dcnt]

   return (mcnt, rdrecs, rarecs)

#
# delete from Postgres target table for records not in the comparing database server
#
def pg_delete_records(tb, sc, ukey, mrecs, domsg = True):

   mcnt = len(mrecs)
   s = 's' if mcnt > 1 else ''
   if domsg:
      msg = "{}: {} Record{} found in {}, but not in {}".format(tb, mcnt, s, TSCHEMA, CSCHEMA)
      if PVALS['s']: msg += "\n" + "\n".join(map(str, mrecs))
      PgLOG.pglog(msg, PgLOG.LOGWRN)
   if not PVALS['f']:
      msg = "{}: Add Option -f to delete the {} Record{} from {}".format(tb, mcnt, s, TSCHEMA)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      return 0

   bt = tm()
   tbl = '{}.{}'.format(PgDBI.pgname(sc), PgDBI.pgname(tb))
   urecs = PgUtil.array2hash(mrecs, ukey)
   dcnt = PgDBI.pgmdel(tbl, urecs)
   rmsg = PgLOG.seconds_to_string_time(tm() - bt)
   PgLOG.pglog("{}: Deleted {} Record{} ({}) from {}".format(tb, dcnt, s, rmsg, TSCHEMA), PgLOG.LOGWRN)

   return dcnt

#
# Add to the Postgres target table for records in the comparing database server
#
def pg_add_records(tb, sc, mrecs, domsg = True):

   mcnt = len(mrecs)
   s = 's' if mcnt > 1 else ''
   if domsg:
      msg = "{}: {} Record{} missed in {}, but in {}".format(tb, mcnt, s, TSCHEMA, CSCHEMA)
      if PVALS['s']: msg += "\n" + "\n".join(map(str, mrecs))
      PgLOG.pglog(msg, PgLOG.LOGWRN)
   if not PVALS['f']:
      msg = "{}: Add Option -f to add the {} Record{} into {}".format(tb, mcnt, s, TSCHEMA)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      return 0

   bt = tm()
   tbl = '{}.{}'.format(PgDBI.pgname(sc), PgDBI.pgname(tb))
   arecs = PgUtil.array2hash(mrecs)
   acnt = PgDBI.pgmadd(tbl, arecs)
   rmsg = PgLOG.seconds_to_string_time(tm() - bt)
   PgLOG.pglog("{}: Added {} Record{} ({}) in {}".format(tb, acnt, s, rmsg, TSCHEMA), PgLOG.LOGWRN)

   return acnt

#
# Update the Postgres target table for records different than in the comparing database server
#
def pg_update_records(tb, sc, ukey, mrecs, domsg = True):

   mcnt = len(mrecs)
   s = 's' if mcnt > 1 else ''
   if domsg:
      msg = "{}: {} Record{} mismatched between {} and {}".format(tb, mcnt, s, TSCHEMA, CSCHEMA)
      if PVALS['s']: msg += PVALS['umsg']
      PgLOG.pglog(msg, PgLOG.LOGWRN)
   if not PVALS['f']:
      msg = "{}: Add Option -f to update the {} Record{} in {}".format(tb, mcnt, s, TSCHEMA)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      return 0

   bt = tm()
   tbl = '{}.{}'.format(PgDBI.pgname(sc), PgDBI.pgname(tb))
   ucnt = 0
   urec = {}
   for mrec in mrecs:   
      prec = {}
      for fld in mrec:
         if fld in ukey:
            urec[fld] = mrec[fld]
         else:
            prec[fld] = mrec[fld]
      ucnt += PgDBI.pghupdt(tbl, prec, urec)
   rmsg = PgLOG.seconds_to_string_time(tm() - bt)
   PgLOG.pglog("{}: Updated {} Record{} ({}) in {}".format(tb, ucnt, s, msg, TSCHEMA), PgLOG.LOGWRN)

   return ucnt

#
# Compare primary/unique key values bewteen databases
#
def compare_unique_keys(ukey, trec, crec):

   for fld in ukey:
      if trec[fld] > crec[fld]:
         return 1
      elif trec[fld] < crec[fld]:
         return -1
   return 0

#
# Compare column values, other than the priamry/unique keys, bewteen databases
#
def compare_one_record(ukey, flds, trec, crec):

   mfld = []
   mrec = {}
   for fld in flds:
      if trec[fld] != crec[fld]: mfld.append(fld)
   if mfld:
      srec = []
      for fld in ukey:
         mrec[fld] = trec[fld]
         srec.append("{}:{}".format(fld, trec[fld]))
      if PVALS['s']: PVALS['umsg'] += "\n{}=> ".format(','.join(srec))
      srec = []
      for fld in mfld:
         mrec[fld] = crec[fld]
         srec.append("{}:{}/{}".format(fld, trec[fld], crec[fld]))
      if PVALS['s']: PVALS['umsg'] += ','.join(srec)
            
   return mrec

#
#  check and get Postgres table unique key field names 
#
def pg_table_ukey(tb, sc):
   
   tbl = 'pg_indexes'
   fld = "indexname idx, indexdef def"
   cnd = "schemaname = '{}' AND tablename = '{}' AND indexdef LIKE 'CREATE UNIQUE INDEX%'".format(sc, tb)
   pstr = " AND indexname LIKE '%_pkey'"
   ukey = []
   flds = []
   pgrec = PgDBI.pgget(tbl, fld, cnd + pstr)
   if not pgrec: pgrec = PgDBI.pgget(tbl, fld, cnd)
   if pgrec:
      ustr = re.search(r'\((.+)\)$', pgrec['def']).group(1)
      if ustr.find('"') > -1: ustr = ustr.replace('"', '')
      ukey = ustr.split(', ')

   tbl = 'information_schema.columns'
   fld = "column_name col"
   cnd = "table_schema = '{}' AND table_name = '{}'".format(sc, tb)
   pgrecs = PgDBI.pgmget(tbl, fld, cnd)
   if pgrecs:
      for col in pgrecs['col']:
         if col in ukey: continue
         flds.append(col)

   sflds = sorted(flds)
   if ukey:
      return (ukey, sflds)
   else:
      return (sflds, [])

#
#  check and get MySQL table unique key field names 
#
def my_table_ukey(tb, db):
   
   ukey = []
   flds = []

   tbl = 'information_schema.statistics'
   fld = "index_name idx, column_name col, non_unique unq, seq_in_index seq"
   cnd = "table_schema = '{}' AND table_name = '{}' AND non_unique = 0".format(db, tb)
   pstr = " AND index_name = 'PRIMARY' ORDER BY seq"
   myrecs = MyDBI.mymget(tbl, fld, cnd + pstr)
   if not myrecs:
      ostr = " ORDER BY idx, seq"
      myrecs = MyDBI.mymget(tbl, fld, cnd + ostr)
   
   if myrecs:
      cnt = len(myrecs['idx'])
      idx = None
      for i in range(cnt):
         rec = PgUtil.onerecord(myrecs, i)
         if not ukey or rec['idx'] == idx:
            ukey.append(rec['col'])
            idx = rec['idx']
         else:
            break

   tbl = 'information_schema.columns'
   fld = "column_name col"
   cnd = "table_schema = '{}' AND table_name = '{}'".format(db, tb)
   myrecs = MyDBI.mymget(tbl, fld, cnd)
   if myrecs:
      for col in myrecs['col']:
         if col in ukey: continue
         flds.append(col)

   sflds = sorted(flds)
   if ukey:
      return (ukey, sflds)
   else:
      return (sflds, [])

#
# sort array records by unique key
#
def ukeysort(recs, ukey):
   
   kcnt = len(ukey)    # count of keys to be sorted on
   desc = [1]*kcnt
   count = len(recs)    # row count of recs
   if count < 2: return recs       # no need of sording

   # prepare the dict list for sortting
   srecs = [None]*count
   for i in range(count):
      rec = []
      for key in ukey:
         rec.append(recs[i][key])
      rec.append(i)
      srecs[i] = rec

   srecs = PgUtil.quicksort(srecs, 0, count-1, desc, kcnt)

   rets = [None]*count
   for i in range(count):
      rets[i] = recs[srecs[i][kcnt]]

   return rets

#
# gather all or a limited number of a Postgres table records and sorted by a unique key
#
def pg_table_records(tb, sc, ukey, lmt, off, dosort = True):

   tbl = '{}.{}'.format(PgDBI.pgname(sc), PgDBI.pgname(tb))
   cnd = ''
   if lmt:
      if dosort:
         cnd = "ORDER BY {} ".format(','.join(ukey))
         dosort = False
      cnd += "LIMIT {}".format(lmt)
      if off: cnd += " OFFSET {}".format(off)
   pgrecs = PgDBI.pgmget(tbl, '*', cnd)
   cnt = len(pgrecs[ukey[0]]) if pgrecs else 0
   recs = []
   if cnt > 0:
      recs = PgUtil.hash2array(pgrecs)
      if dosort: recs = ukeysort(recs, ukey)

   return recs

#
# get all field names of a MySQL table for given type
#
def my_table_types(tb, db, ftype, stype = 'data'):

   tbl = 'information_schema.columns'
   fld = "column_name col"
   cnd = "table_schema = '{}' AND table_name = '{}' and {}_type = '{}'"
   myrecs = MyDBI.mymget(tbl, fld, cnd.format(db, tb, stype, ftype))
   return myrecs['col'] if myrecs else []

#
# gather all or a limited number of a MySQL table records and sorted by a unique key
#
def my_table_records(tb, db, ukey, lmt, off, dosort = True):

   tbl = '{}.{}'.format(db, tb)
   cnd = ''
   if lmt:
      if dosort:
         cnd = "ORDER BY {} ".format(','.join(ukey))
         dosort = False
      cnd += "LIMIT {}".format(lmt)
      if off: cnd += " OFFSET {}".format(off)
   myrecs = MyDBI.mymget(tbl, '*', cnd)
   cnt = len(myrecs[ukey[0]]) if myrecs else 0
   recs = []
   if cnt > 0:
      tflds = my_table_types(tb, db, 'time')
      if tflds:
         for tfld in tflds:
            for i in range(cnt):
               tval = myrecs[tfld][i]
               if isinstance(tval, td):
                  myrecs[tfld][i] = (dt.min + tval).time()
      if PVALS['ns']:
         tflds = my_table_types(tb, db, 'text')
         if tflds:
            for tfld in tflds:
               for i in range(cnt):
                  tval = myrecs[tfld][i]
                  if isinstance(tval, str):
                     myrecs[tfld][i] = tval.replace("\0", "")
      tflds = my_table_types(tb, db, 'tinyint(1)', 'column')
      if tflds:
         for tfld in tflds:
            for i in range(cnt):
               tval = myrecs[tfld][i]
               if isinstance(tval, int):
                  myrecs[tfld][i] = True if tval else False
      recs = PgUtil.hash2array(myrecs)
      if dosort: recs = ukeysort(recs, ukey)

   return recs

#
# compare indexes for a given table between database servers
#
def compare_table_indexes(tb, sc):

   PgLOG.pglog("{}: Compare Table Indexes between {} and {}".format(tb, TSCHEMA, CSCHEMA), PgLOG.LOGWRN)

   if PVALS['ct'] == 'my':
      cd = my_compare_dbname(PVALS['cd'])
      cindexes = my_table_indexes(tb, cd)
   else:
      cs = pg_compare_scname(PVALS['cs'], PVALS['cd'])
      cindexes = pg_table_indexes(tb, cs)
   ccnt = len(cindexes)
   s = 'es' if ccnt > 1 else ''
   PgLOG.pglog("{}: {} Index{} Found in {}".format(tb, ccnt, s, CSCHEMA), PgLOG.LOGWRN)

   pg_target_scname(sc, PVALS['db'])
   tindexes = pg_table_indexes(tb, sc)
   tcnt = len(tindexes)
   s = 'es' if tcnt > 1 else ''
   PgLOG.pglog("{}: {} Index{} Found in {}".format(tb, tcnt, s, TSCHEMA), PgLOG.LOGWRN)

   didxs = []
   aidxs = []
   uidxs = []
   PVALS['umsg'] = ''
   matched = True
   i = j = 0
   while j < tcnt:
      tidx = tindexes[j]
      while i < ccnt:
         cidx = cindexes[i]
         if tidx['idx'] == cidx['idx'] or re.match(cidx['idx'], tidx['idx']):
            act = compare_one_index(tidx, cidx)
            if act == 1:
               uidxs.append({'idx' : cidx['idx'], 'tidx' : tidx['idx']})
               if PVALS['s']: PVALS['umsg'] += "\n{}/{}".format(tidx['idx'], cidx['idx'])
            elif act == 2:
               didxs.append(tidx)
               aidxs.append(cidx)
            i += 1
            j += 1
            break
         elif tidx['idx'] < cidx['idx']:
            didxs.append(tidx)
            j += 1
            break
         else:
            aidxs.append(cidx)
            i += 1
      if i >= ccnt: break
   if i < ccnt:
      aidxs.extend(cindexes[i:ccnt])
   elif j < tcnt:
      didxs.extend(tindexes[j:tcnt])

   pg_target_scname(sc, PVALS['db'])
   if didxs: 
      pg_delete_indexes(tb, sc, didxs)
      matched = False
   if aidxs:
      pg_add_indexes(tb, sc, aidxs)
      matched = False
   if uidxs:
      pg_update_indexes(tb, sc, uidxs)
      matched = False

   if matched: PgLOG.pglog(tb + ": All Table Indexes matched", PgLOG.LOGWRN)


#
# compare one index of a given table name, for index name, column names included,
# and index uniqueness, between database servers
#
def compare_one_index(tidx, cidx):

   if tidx['col'] != cidx['col'] or tidx['unq'] != cidx['unq']: return 2
   if tidx['idx'] != cidx['idx']: return 1
   return 0

#
# delete from Postgres target table for indexes not in the comparing database server
#
def pg_delete_indexes(tb, sc, midxs, domsg = True):

   mcnt = len(midxs)
   s = 'es' if mcnt > 1 else ''
   if domsg:
      msg = "{}: {} Index{} found in {}, but not in {}".format(tb, mcnt, s, TSCHEMA, CSCHEMA)
      if PVALS['s']: msg += "\n" + "\n".join(map(str, midxs))
      PgLOG.pglog(msg, PgLOG.LOGWRN)
   if not PVALS['f']:
      msg = "{}: Add Option -f to drop the {} Index{} from {}".format(tb, mcnt, s, TSCHEMA)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      return

   bt = tm()
   dcnt = 0
   for midx in midxs:
      idx = midx['idx']
      pidx = PgDBI.pgname(idx)
      if re.search(r'_pkey$', idx):
         tbl = '{}.{}'.format(PgDBI.pgname(sc), PgDBI.pgname(tb))
         sqlstr = "ALTER TABLE {} DROP CONSTRAINT {}".format(tbl, pidx)
      else:
         sqlstr = "DROP INDEX {}".format(pidx)
      if PgDBI.pgexec(sqlstr): dcnt += 1
   rmsg = PgLOG.seconds_to_string_time(tm() - bt)
   PgLOG.pglog("{}: Dropped {} of the {} Index{} ({}) from {}".format(tb, dcnt, mcnt, s, rmsg, TSCHEMA), PgLOG.LOGWRN)

#
# Add to the Postgres target table for indexes in the comparing database server
#
def pg_add_indexes(tb, sc, midxs, domsg = True):

   mcnt = len(midxs)
   s = 'es' if mcnt > 1 else ''
   if domsg:
      msg = "{}: {} Index{} missed in {}, but in {}".format(tb, mcnt, s, TSCHEMA, CSCHEMA)
      if PVALS['s']: msg += "\n" + "\n".join(map(str, midxs))
      PgLOG.pglog(msg, PgLOG.LOGWRN)
   if not PVALS['f']:
      msg = "{}: Add Option -f to create the {} Index{} into {}".format(tb, mcnt, s, TSCHEMA)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      return

   bt = tm()
   acnt = 0
   tbl = '{}.{}'.format(PgDBI.pgname(sc), PgDBI.pgname(tb))
   for midx in midxs:
      idx = midx['idx']
      pidx = PgDBI.pgname(idx)
      if re.search(r'_pkey$', idx):
         sqlstr = "ALTER TABLE {} ADD PRIMARY KEY ({})".format(tbl, midx['col'])
      else:
         ustr = 'UNIQUE ' if midx['unq'] else ''
         sqlstr = "CREATE {}INDEX {} ON {} ({})".format(ustr, pidx, tbl, midx['col'])
      if PgDBI.pgexec(sqlstr): acnt += 1
   rmsg = PgLOG.seconds_to_string_time(tm() - bt)
   PgLOG.pglog("{}: Created {} of {} Index{} ({}) in {}".format(tb, acnt, mcnt, s, rmsg, TSCHEMA), PgLOG.LOGWRN)

#
# Update the Postgres target table for index names different than in the comparing database server
#
def pg_update_indexes(tb, sc, midxs, domsg = True):

   mcnt = len(midxs)
   s = 'es' if mcnt > 1 else ''
   if domsg:
      msg = "{}: {} Index{} mismatched between {} and {}".format(tb, mcnt, s, TSCHEMA, CSCHEMA)
      if PVALS['s']: msg += PVALS['umsg']
      PgLOG.pglog(msg, PgLOG.LOGWRN)
   if not PVALS['f']:
      msg = "{}: Add Option -f to rename the {} Index{} in {}".format(tb, mcnt, s, TSCHEMA)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      return

   ucnt = 0
   for midx in midxs:
      tbl = pg_table_index(midx['idx'], sc)
      if tbl:
         msg = "{}: Cannot rename Index {} to {} of Table {} in {}".format(tb, midx['tidx'], midx['idx'], tbl, TSCHEMA)
         PgLOG.pglog(msg, PgLOG.LOGWRN)
         continue
      sqlstr = 'ALTER INDEX {} RENAME TO {}'.format(PgDBI.pgname(midx['tidx']), PgDBI.pgname(midx['idx']))
      if PgDBI.pgexec(sqlstr): ucnt += 1
   PgLOG.pglog("{}: {} of the {} Index{} Renamed in {}".format(tb, ucnt, mcnt, s, TSCHEMA), PgLOG.LOGWRN)

#
# gather all indexes of a Postgres table
#
def pg_table_indexes(tb, sc):
   
   tbl = 'pg_indexes'
   fld = "indexname idx, indexdef def"
   cnd = "schemaname = '{}' AND tablename = '{}' ORDER BY idx".format(sc, tb)
   pgrecs = PgDBI.pgmget(tbl, fld, cnd.format(sc, tb))
   cnt = len(pgrecs['idx']) if pgrecs else 0

   recs = []
   if cnt == 0: return recs

   for i in range(cnt):
      rec = PgUtil.onerecord(pgrecs, i)
      idef = rec['def']
      rec['unq'] = 1 if re.match(r'^CREATE UNIQUE INDEX', idef) else 0
      col = re.search(r'\((.+)\)$', idef).group(1)
      rec['col'] = col.replace('"', '') if col.find('"') > -1 else col
      recs.append(rec)

   return sorted(recs, key = lambda cmp: cmp['idx'])

#
# gather all indexes of a Postgres table
#
def pg_table_index(idx, sc):
   
   tbl = 'pg_indexes'
   fld = "tablename tbl"
   cnd = "indexname = '{}' AND schemaname = '{}'".format(idx, sc)
   pgrec = PgDBI.pgget(tbl, fld, cnd)

   if pgrec:
      return pgrec['tbl']
   else:
      return None

#
# gather all indexes of a MySQL table
#
def my_table_indexes(tb, db):
   
   tbl = 'information_schema.statistics'
   fld = "index_name idx, column_name col, non_unique unq, seq_in_index seq"
   cnd = "table_schema = '{}' AND table_name = '{}' ORDER BY idx, seq"
   myrecs = MyDBI.mymget(tbl, fld, cnd.format(db, tb))
   cnt = len(myrecs['idx']) if myrecs else 0

   recs = []
   pi = -1
   for i in range(cnt):
      rec = PgUtil.onerecord(myrecs, i)
      if rec['idx'] == 'PRIMARY': rec['idx'] = tb + '_pkey'
      rec['unq'] = 0 if rec['unq'] == 1 else 1
      if rec['seq'] > 1: 
         recs[pi]['col'] += ', ' + rec['col']
      else:
         recs.append(rec)
         pi += 1

   return sorted(recs, key = lambda cmp: cmp['idx'])

#
# compare columns for given table
#
def compare_table_columns(tb, sc):

   PgLOG.pglog("{}: Compare Table Columns between {} and {}".format(tb, TSCHEMA, CSCHEMA), PgLOG.LOGWRN)

   if PVALS['ct'] == 'my':
      cd = my_compare_dbname(PVALS['cd'])
      ccolumns = my_table_columns(tb, cd)
   else:
      cs = pg_compare_scname(PVALS['cs'], PVALS['cd'])
      ccolumns = pg_table_columns(tb, cs)
   ccnt = len(ccolumns)
   if ccnt == 0:
      PgLOG.pglog("{}: Table Not Exists in {} to compare columns".format(tb, CSCHEMA), PgLOG.LOGWRN)
      return
   s = 's' if ccnt > 1 else ''
   PgLOG.pglog("{}: {} Column{} Found in {}".format(tb, ccnt, s, CSCHEMA), PgLOG.LOGWRN)

   pg_target_scname(sc, PVALS['db'])
   tcolumns = pg_table_columns(tb, sc)
   tcnt = len(tcolumns)
   if tcnt == 0:
      PgLOG.pglog("{}: Table Not Exists in {} to compare columns".format(tb, TSCHEMA), PgLOG.LOGWRN)
      return
   s = 's' if tcnt > 1 else ''
   PgLOG.pglog("{}: {} Column{} Found in {}".format(tb, tcnt, s, TSCHEMA), PgLOG.LOGWRN)

   dcols = []
   acols = []
   ucols = []
   PVALS['umsg'] = ''
   matched = True
   i = j = 0
   while j < tcnt:
      tcol = tcolumns[j]
      while i < ccnt:
         ccol = ccolumns[i]
         if tcol['col'] == ccol['col']:
            ucol = compare_one_column(tcol, ccol)
            if ucol: ucols.append(ucol)
            i += 1
            j += 1
            break
         elif tcol['col'] < ccol['col']:
            dcols.append(tcol)
            j += 1
            break
         else:
            acols.append(ccol)
            i += 1
      if i >= ccnt: break
   if i < ccnt:
      acols.extend(ccolumns[i:ccnt])
   elif j < tcnt:
      dcols.extend(tcolumns[j:tcnt])

   pg_target_scname(sc, PVALS['db'])
   if dcols:
      pg_delete_columns(tb, sc, dcols)
      matched = False
   if acols:
      pg_add_columns(tb, sc, acols)
      matched = False
   if ucols:
      pg_update_columns(tb, sc, ucols)
      matched = False

   if matched: PgLOG.pglog(tb + ": All Table Columns matched", PgLOG.LOGWRN)

#
# delete from Postgres target table for columns not in the comparing database server
#
def pg_delete_columns(tb, sc, mcols, domsg = True):

   mcnt = len(mcols)
   s = 's' if mcnt > 1 else ''
   if domsg:
      msg = "{}: {} Column{} found in {}, but not in {}".format(tb, mcnt, s, TSCHEMA, CSCHEMA)
      if PVALS['s']: msg += "\n" + "\n".join(map(str, mcols))
      PgLOG.pglog(msg, PgLOG.LOGWRN)
   if not PVALS['f']:
      msg = "{}: Add Option -f to drop the {} Column{} from {}".format(tb, mcnt, s, TSCHEMA)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      return

   bt = tm()
   dcnt = 0
   tbl = '{}.{}'.format(PgDBI.pgname(sc), PgDBI.pgname(tb))
   for mcol in mcols:
      col = PgDBI.pgname(mcol['col'])
      sqlstr = 'ALTER TABLE {} DROP COLUMN {}'.format(tbl, col)
      if PgDBI.pgexec(sqlstr): dcnt += 1
   rmsg = PgLOG.seconds_to_string_time(tm() - bt)
   PgLOG.pglog("{}: Dropped {} of the {} Column{} ({}) from {}".format(tb, dcnt, mcnt, s, rmsg, TSCHEMA), PgLOG.LOGWRN)

#
# Add to the Postgres target table for columns in the comparing database server
#
def pg_add_columns(tb, sc, mcols, domsg = True):

   mcnt = len(mcols)
   s = 's' if mcnt > 1 else ''
   if domsg:
      msg = "{}: {} Column{} missed in {}, but in {}".format(tb, mcnt, s, TSCHEMA, CSCHEMA)
      if PVALS['s']: msg += "\n" + "\n".join(map(str, mcols))
      PgLOG.pglog(msg, PgLOG.LOGWRN)
   if not PVALS['f']:
      msg = "{}: Add Option -f to add the {} Column{} into {}".format(tb, mcnt, s, TSCHEMA)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      return

   bt = tm()
   acnt = dcnt = 0
   tbl = '{}.{}'.format(PgDBI.pgname(sc), PgDBI.pgname(tb))
   for mcol in mcols:
      col = PgDBI.pgname(mcol['col'])
      sqlstr = 'ALTER TABLE {} ADD COLUMN {} {}'.format(tbl, col, mcol['typ'])
      if PgDBI.pgexec(sqlstr): acnt += 1
      if 'def' in mcol:
         mdef = 'NULL' if mcol['def'] == None else "'{}'".format(mcol['def'])
         sqlstr = "ALTER TABLE {} ALTER COLUMN {} SET DEFAULT {}".format(tbl, col, mdef)
         if PgDBI.pgexec(sqlstr): dcnt += 1
   if acnt:
      rmsg = PgLOG.seconds_to_string_time(tm() - bt)
      PgLOG.pglog("{}: Added {} of the {} column{} ({}) in {}".format(tb, acnt, mcnt, s, rmsg, TSCHEMA), PgLOG.LOGWRN)
   if dcnt: PgLOG.pglog("{}: {} of the {} column{} Set Default in {}".format(tb, dcnt, mcnt, s, TSCHEMA), PgLOG.LOGWRN)

#
# Update the Postgres target table for column types and default values different
# than in the comparing database server
#
def pg_update_columns(tb, sc, mcols, domsg = True):

   mcnt = len(mcols)
   s = 's' if mcnt > 1 else ''
   if domsg:
      msg = "{}: {} Column{} mismatched between {} and {}".format(tb, mcnt, s, TSCHEMA, CSCHEMA)
      if PVALS['s']: msg += PVALS['umsg']
      PgLOG.pglog(msg, PgLOG.LOGWRN)
   if not PVALS['f']:
      msg = "{}: Add Option -f to modify the {} Column{} in {}".format(tb, mcnt, s, TSCHEMA)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      return

   tbl = '{}.{}'.format(PgDBI.pgname(sc), PgDBI.pgname(tb))
   dcnt = tcnt = 0
   for mcol in mcols:
      col = PgDBI.pgname(mcol['col'])
      if 'typ' in mcol:
         sqlstr = "ALTER TABLE {} ALTER COLUMN {} TYPE {}".format(tbl, col, mcol['typ'])
         if PgDBI.pgexec(sqlstr): tcnt += 1
      if 'def' in mcol:
         mdef = 'NULL' if mcol['def'] == None else "'{}'".format(mcol['def'])
         sqlstr = "ALTER TABLE {} ALTER COLUMN {} SET DEFAULT {}".format(tbl, col, mdef)
         if PgDBI.pgexec(sqlstr): dcnt += 1

   if tcnt: PgLOG.pglog("{}: {} of {} Column{} Changed Type in {}".format(tb, tcnt, mcnt, s, TSCHEMA), PgLOG.LOGWRN)
   if dcnt: PgLOG.pglog("{}: {} of {} Column{} Set Default in {}".format(tb, dcnt, mcnt, s, TSCHEMA), PgLOG.LOGWRN)

#
# compare one column for given table
#
def compare_one_column(tcol, ccol):

   mfld = []
   mcol = {}
   if tcol['def'] != ccol['def']: mfld.append('def')
   if tcol['typ'] != ccol['typ']: mfld.append('typ')
   if mfld:
      srec = []
      for fld in mfld:
         mcol[fld] = ccol[fld]
         srec.append("{} {}/{}".format(fld, tcol[fld], ccol[fld]))
      mcol['col'] = tcol['col']
      if PVALS['s']: PVALS['umsg'] += "\n{}:{}".format(tcol['col'], ','.join(srec))

   return mcol

#
# gather all columns of a MySQL table
#
def pg_table_columns(tb, sc):
   
   recs = []
   tbl = 'information_schema.columns'
   intms = r'^(smallint||bigint|integer)$'
   fld = "column_name col, data_type typ, character_maximum_length siz, is_nullable nil, column_default def, udt_name udt"
   cnd = "table_schema = '{}' AND table_name = '{}'"
   pgrecs = PgDBI.pgmget(tbl, fld, cnd.format(sc, tb))
   if not pgrecs: return recs

   cnt = len(pgrecs['col'])
   for i in range(cnt):
      rec = PgUtil.onerecord(pgrecs, i)
      typ = rec['typ']
      siz = rec['siz']
      if typ == 'character':
         rec['typ'] = 'char({})'.format(siz)
      elif typ == 'character varying':
         rec['typ'] = 'varchar({})'.format(siz)
      elif typ == 'time without time zone':
         rec['typ'] = 'time'
      elif typ == 'timestamp without time zone':
         rec['typ'] = 'timestamp'
      elif typ == 'USER-DEFINED':
         typ = rec['udt']
         offset = typ.find('_')
         rec['typ'] = typ[0:offset] if offset > 0 else typ
      elif typ == 'double precision':
         rec['typ'] = 'double'
      isint = re.match(intms, typ)
      dflt = rec['def']
      if dflt == None:
         if rec['nil'] == 'NO':
            rec['def'] = 0 if isint else ''
      elif isint and re.match(r'^nextval\(', dflt):
         rec['def'] = 0
      else:
         ms = re.match(r"^'(.*)'", dflt)
         if ms: dflt = ms.group(1)
         rec['def'] = int(dflt) if isint else dflt
            
      recs.append(rec)

   return sorted(recs, key = lambda cmp: cmp['col'])

#
# gather all columns of a MySQL table
#
def my_table_columns(tb, db):
   
   recs = []
   tbl = 'information_schema.columns'
   intms = r'^(tinyint|mediumint|smallint||bigint|int|integer)( |$)'
   fld = "column_name col, column_type typ, character_maximum_length siz, is_nullable nil, column_default def, extra ext"
   cnd = "table_schema = '{}' AND table_name = '{}'"
   myrecs = MyDBI.mymget(tbl, fld, cnd.format(db, tb))
   if not myrecs: return recs
   MyDBI.decode_byte_records(['typ', 'def'], myrecs)

   cnt = len(myrecs['col'])
   for i in range(cnt):
      rec = PgUtil.onerecord(myrecs, i)
      typ = rec['typ']
      siz = rec['siz']
      if typ == 'datetime':
         rec['typ'] = 'timestamp'
      elif re.match(r'^(medium|long)text', typ):
         rec['typ'] = 'text'
      elif re.match(r'^float($|\()', typ):
         rec['typ'] = 'double'
      elif re.match(r'^enum\(', typ):
         rec['typ'] = 'enum'

      isint = re.match(intms, typ)
      if isint:
         ms = re.match(r'^(\w+) unsigned', typ)
         if ms:
            typ = ms.group(1)
            uns = True
         else:
            uns = False
         if typ == 'int' or type == 'integer':
            rec['typ'] = 'bigint' if (uns or rec['ext'] == 'auto_increment') else 'integer'
         elif typ == 'mediumint':
            rec['typ'] = 'integer'
         elif typ == 'tinyint':
            rec['typ'] = 'smallint'
         elif typ == 'smallint':
            rec['typ'] = 'integer' if uns else 'smallint'
         elif uns:
            rec['typ'] = typ

      dflt = rec['def']
      if dflt == None:
         if rec['nil'] == 'NO':
            rec['def'] = 0 if isint else ''
      elif isint and rec['ext'] == 'auto_increment':
         rec['def'] = 0
      elif isinstance(dflt, str):
         ms = re.match(r"^'(.*)'", dflt)
         if ms: dflt = ms.group(1)
         rec['def'] = int(dflt) if isint else dflt
      elif not isint and isinstance(dflt, int):
         rec['def'] = str(dflt)

      recs.append(rec)

   return sorted(recs, key = lambda cmp: cmp['col'])

#
# compare table list for all tables in a given schema between database servers
#
def compare_schema_tables(sc):

   PgLOG.pglog("Compare Schema Tables between {} and {}".format(TSCHEMA, CSCHEMA), PgLOG.LOGWRN)
   ttbl = 'information_schema.tables'
   tfld = 'table_name tnm'
   tcnd = "table_schema = '{}' and table_type = 'BASE TABLE' ORDER BY table_name"

   if PVALS['ct'] == 'my':
      cd = my_compare_dbname(PVALS['cd'])
      ctables = MyDBI.mymget(ttbl, tfld, tcnd.format(cd))
      if ctables: MyDBI.decode_byte_records(['tnm'], ctables)
   else:
      cs = pg_compare_scname(PVALS['cs'], PVALS['cd'])
      ctables = PgDBI.pgmget(ttbl, tfld, tcnd.format(cs))
   ccnt = len(ctables['tnm']) if ctables else 0
   s = 's' if ccnt > 1 else ''
   PgLOG.pglog("{} Table{} Found in {}".format(ccnt, s, CSCHEMA), PgLOG.LOGWRN)

   pg_target_scname(sc, PVALS['db'])
   ttables = PgDBI.pgmget(ttbl, tfld, tcnd.format(sc))
   tcnt = len(ttables['tnm']) if ttables else 0
   s = 's' if tcnt > 1 else ''
   PgLOG.pglog("{} Table{} Found in {}".format(tcnt, s, TSCHEMA), PgLOG.LOGWRN)

   dtbls = []
   atbls = []
   matched = True
   i = j = 0
   while j < tcnt:
      ttbl = ttables['tnm'][j]
      while i < ccnt:
         ctbl = ctables['tnm'][i]
         if ttbl == ctbl:
            PVALS['tb'].append(ttbl)
            i += 1
            j += 1
            break
         elif ttbl < ctbl:
            dtbls.append(ttbl)
            j += 1
            break
         else:
            atbls.append(ctbl)
            i += 1
      if i >= ccnt: break
   if i < ccnt:
      atbls.extend(ctables['tnm'][i:ccnt])
   elif j < tcnt:
      dtbls.extend(ttables['tnm'][j:tcnt])

   if dtbls:
      mcnt = len(dtbls)
      matched = False
      s = 's' if mcnt > 1 else ''
      msg = "{} table{} Found Only in {}\n".format(mcnt, s, TSCHEMA)
      msg += "\n".join(dtbls)
      PgLOG.pglog(msg, PgLOG.LOGWRN)

   if atbls:
      mcnt = len(atbls)
      matched = False
      s = 's' if mcnt > 1 else ''
      tstr = "Add " if PVALS['at'] else ""
      msg = "{}{} table{} Missed in {}\n".format(tstr, mcnt, s, TSCHEMA)
      msg += "\n".join(atbls)
      PgLOG.pglog(msg, PgLOG.LOGWRN)
      if PVALS['at']: pg_add_tables(sc, atbls)

   if matched: PgLOG.pglog(sc + ": All Schema Table Names matched", PgLOG.LOGWRN)

#
# add missing tables into target database server
#
def pg_add_tables(sc, tables):
   
   myopt = " -m" if PVALS['ct'] == 'my' else ""
   db = PVALS['db']
   us = PVALS['us']
   pw = PVALS['pw']
   ht = PVALS['ht']
   pn = PVALS['pn']
   cd = PVALS['cd']
   cs = PVALS['cs']
   cu = PVALS['cu']
   cp = PVALS['cp']
   ch = PVALS['ch']
   cn = PVALS['cn']
   tport = " -p {}".format(pn) if pn else ""
   cport = " -p {}".format(cn) if cn else ""

   for tb in tables:
      # dump json file in case not exists
      cmd = "pgddl {} -aj -h {} -d {} -c {} -u {} -w {}{}{}".format(tb, ch, cd, cs, cu, cp, cport, myopt)
      PgLOG.pgsystem(cmd, PgLOG.LOGWRN, 7)
      # create table from json file
      cmd = "pgddl {} -aa -h {} -d {} -c {} -u {} -w {}{}".format(tb, ht, db, sc, us, pw, tport)
      PgLOG.pgsystem(cmd, PgLOG.LGWNEX, 7)
      PVALS['tb'].append(tb)

#
# call main() to start program
#
if __name__ == "__main__": main()
