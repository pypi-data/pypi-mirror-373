#!/usr/bin/env python3
#
###############################################################################
#
#     Title : pgdbdump
#    Author : Zaihua Ji,  zji@ucar.edu
#      Date : 08/14/2025
#   Purpose : python code to dump PostgreSQL databases to specified
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
from rda_python_common import PgUtil

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

   if not (dname and hname):
      print("Usage: pgdbdump [-b] -d DBNAME -h HostName [-p LocalPath]")
      print("  -b - background process and no screen output")
      print("  -d - PostgreSQL database name to dump at the current directory")
      print("  -h - Hostname the PostgreSQL server is running on")
      print("  -p - Local relative path to dump the database, defaults to <DBNAME>_backup_<TODAY>")
      sys.exit(0)
   
   PgLOG.cmdlog("pgdbdump {}".format(' '.join(argv)))
   if not pname: pname = "{}_backup_{}".format(dname, PgUtil.curdate())
   pg_database_dbdump(dname, hname, pname)

   title = "pgdbdump: {}:{}".format(hname, dname, pname)
   tmsg = "{} to {} under {}!".format(title, pname, os.getcwd())
   PgLOG.set_email(tmsg, PgLOG.EMLTOP)
   PgLOG.pglog(title, SNDACT)
   PgLOG.cmdlog()   
   PgLOG.pgexit(0)

#
#  bacup one database
#
def pg_database_dbdump(dname, hname, pname):
   
   cmd = "pg_dump {} -h {} -U {} -w -Fd -j 16 -f {}/".format(dname, hname, USNAME, pname)
   if op.exists(pname):
      PgLOG.pglog(pname + ": Dumping directory exists, remove it", ERRACT)
   elif not PgLOG.pgsystem(cmd, LOGACT, 257):
      PgLOG.pglog("{}: Error dumping database\n{}".format(dname, PgLOG.PGLOG['SYSERR']), ERRACT)

#
# call main() to start program
#
if __name__ == "__main__": main()
