#!/usr/bin/env python3
#
###############################################################################
#
#     Title : pgdbrestore
#    Author : Zaihua Ji,  zji@ucar.edu
#      Date : 08/14/2025
#   Purpose : python code to restore PostgreSQL databases from specified
#             local directories.
#
#    Github : https://github.com/NCAR/rda-python-dbms.git
#
###############################################################################
#
import sys
import re
import os
from os import path as op
from rda_python_common import PgLOG
from rda_python_common import PgFile
from rda_python_common import PgDBI

USNAME = 'postgres'
LOGACT = PgLOG.LGWNEM
ERRACT = PgLOG.LGEREM
SNDACT = PgLOG.LOGWRN|PgLOG.SNDEML

#
# main function to excecute this script
#
def main():

   # check command line for options
   PgLOG.PGLOG['LOGFILE'] = "pgbackup.log"   # set log file
   argv = sys.argv[1:]
   pname = hname = dname = option = None
   override = False
   options = ['b', 'd', 'h', 'p']
   for arg in argv:
      ms = re.match(r'^-(\w)$', arg)
      if ms:
         option = ms.group(1)
         if option not in options: PgLOG.pglog("{}: unknow option".format(arg), PgLOG.LGEREX)
         if option == 'b': PgLOG.PGLOG['BCKGRND'] = 1
      elif option == 'd':
         dname = arg
      elif option  == 'h':
         hname = arg
      elif option  == 'p':
         pname = arg

   if not (dname and hname and pname):
      print("Usage: pgdbrestore [-b] -d DBNAME -h HostName -p LocalPath")
      print("  -b - background process and no screen output")
      print("  -d - PostgreSQL database name to restore from the local path")
      print("  -h - Hostname the PostgreSQL server is running on")
      print("  -p - Local relative path the dumped database stored")
      sys.exit(0)
  
   PgLOG.cmdlog("pgdbrestore {}".format(' '.join(argv)))
   pg_database_dbrestore(dname, hname, pname)

   title = "pgdbrestore: {}:{}".format(hname, dname)
   tmsg = "{} from {} under {}!".format(title, pname, os.getcwd())
   PgLOG.set_email(tmsg, PgLOG.EMLTOP)
   PgLOG.pglog(title, SNDACT)
   PgLOG.cmdlog()   
   PgLOG.pgexit(0)

#
#  bacup one database
#
def pg_database_dbrestore(dname, hname, pname):

   cmd = "pg_restore -d {} -h {} -U {} -w -j 16 -Fd {}".format(dname, hname, USNAME, pname)
   if not op.exists(pname):
      PgLOG.pglog(pname + ": Restoring local path not exists", ERRACT)
   elif not PgLOG.pgsystem(cmd, LOGACT, 257):
      PgLOG.pglog("{}: Error restoring database\n{}".format(dname, PgLOG.PGLOG['SYSERR']), ERRACT)

#
# call main() to start program
#
if __name__ == "__main__": main()
