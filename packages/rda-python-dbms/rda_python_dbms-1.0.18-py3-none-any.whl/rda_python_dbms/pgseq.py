#!/usr/bin/env python3
#
##################################################################################
#
#     Title : pgseq
#    Author : Zaihua Ji, zji@ucar.edu
#      Date : 12/31/2020
#             2025-04-09 transferred to package rda_python_dbms from
#             https://github.com/NCAR/rda-database.git
#   Purpose : check all tables for given schemas to reset the related sequences
#
#    Github : https://github.com/NCAR/rda-python-dbms.git
#
##################################################################################

import sys
import re
from rda_python_common import PgLOG
from rda_python_common import PgDBI
from rda_python_common import PgUtil

SINFO = {
   'ht' : 'rda-pgdb-02.ucar.edu',
   'db' : 'rdadb',
   'pt' : 5432,
   'us' : '',
   'pw' : '',
}

#
# main function to run this program
#
def main():

   option = None
   alltb = 0
   scnames = []
   tbnames = []
   argv = sys.argv[1:]

   for arg in argv:
      if arg == "-b":
         PgLOG.MYLOG['BCKGRND'] = 1
      elif re.match(r'^-([cdhptuw])$', arg):
         option = arg[1]
      elif re.match(r'^-', arg):
         PgLOG.pglog(arg + ": Invalid Option", PgLOG.LGWNEX)
      elif option:
         if option == 'd':
            SINFO['db'] = arg
         elif option == 'h':
            SINFO['ht'] = arg
         elif option == 'p':
            SINFO['pt'] = int(arg)
         elif option == 'w':
            SINFO['pw'] = arg
         elif option == 'u':
            SINFO['us'] = arg
         elif option == 'c':
            scnames.append(arg)
         elif option == 't':
            tbnames.append(arg)
      else:
         PgLOG.pglog(arg + ": Passed in without leading Option", PgLOG.LGWNEX)

   if not scnames:
      print("Usage: pgseq [-h HostName] [-d DatabaseName] -c SchemaNames  \\")
      print("             [-t TableNames] [-u UserName] [-p Password]")
      print("   -h: PostgreSQL Database server hostname, default to " + SINFO['ht'])
      print("   -p: PostgreSQL Database server port number, default to " + str(SINFO['pt']))
      print("   -d: PostgreSQL Database name, default to " + SINFO['db'])
      print("   -c: Reset sequences for the provided Schemas, at least provide one")
      print("   -t: Table names to reset sequences, default to all tables in the schema")
      print("   -u: Provide database login username if other than the schema name")
      print("   -w: database login password")
      sys.exit(0)

   PgLOG.cmdlog("pgseq {}".format(' '.join(argv)))
   for scname in scnames:
      reset_table_sequence(scname, tbnames)
   PgLOG.cmdlog()
   sys.exit(0)

def reset_table_sequence(scname, tbnames):

   us = SINFO['us'] if SINFO['us'] else scname
   pw = SINFO['pw'] if SINFO['pw'] else us
   PgDBI.default_scinfo(SINFO['db'], scname, SINFO['ht'], us, pw, SINFO['pt'])
   scnd = "table_catalog = '{}' AND table_schema = '{}' AND table_type = 'BASE TABLE'".format(SINFO['db'], scname)
   if tbnames:
      cnd = " AND table_name "
      tcnt = len(tbnames)
      if tcnt == 1:
         cnd += "= '{}'".format(tbnames[0])
      else:
         cnd += "IN ('{}'".format(tbnames[0])
         for i in range(1, tcnt):
            cnd += ", '{}'".format(tbnames[i])
         cnd += ')'
   else:
      cnd = ''
   pgrecs = PgDBI.pgmget('information_schema.tables', 'table_name', scnd + cnd)
   tbnames = pgrecs['table_name'] if pgrecs else []
   tcnt = len(tbnames)
   if tcnt == 0:
      PgLOG.pglog("{}.{}: No Table Name found".format(SINFO['db'], scname), PgLOG.LOGWRN)
      return

   scnt = 0
   scnd = "sequence_catalog = '{}' AND sequence_schema = '{}' AND sequence_name LIKE ".format(SINFO['db'], scname)
   qscname = PgDBI.pgname(scname)
   for tbname in tbnames:
      cnd = "'{}_%_seq'".format(tbname)
      pgrecs = PgDBI.pgmget('information_schema.sequences', 'sequence_name', scnd + cnd)
      if not pgrecs: continue
      qscname = PgDBI.pgname(scname)
      qtname = '{}.{}'.format(qscname, PgDBI.pgname(tbname))
      for sname in pgrecs['sequence_name']:
         fname = sname[len(tbname)+1:-4]
         fcnd = "table_name = '{}' AND table_schema = '{}' AND column_name = '{}'".format(tbname, scname, fname)
         if not PgDBI.pgget('information_schema.columns', '', fcnd): continue
         pgrec = PgDBI.pgget(qtname, "MAX({}) mval".format(PgDBI.pgname(fname)))
         mval = pgrec['mval'] if pgrec and pgrec['mval'] else 1
         qsname = '{}.{}'.format(qscname, PgDBI.pgname(sname))
         qstr = "setval('{}', {})".format(qsname, mval)
         pgrec = PgDBI.pgget('', qstr)
         if pgrec:
            PgLOG.pglog("{}.{}: Sequence Value set to {}".format(scname, sname, pgrec['setval']), PgLOG.LOGWRN)
            scnt += 1

   if scnt > 1 and tcnt > 1:
      PgLOG.pglog("{}.{}: {}/{} Sequences/Tables Reset Values".format(SINFO['db'], scname, scnt, tcnt), PgLOG.LOGWRN)

#
# call main() to start program
#
if __name__ == "__main__": main()
