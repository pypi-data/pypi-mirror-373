#!/usr/bin/env python3
#
###############################################################################
#
#     Title : pgbackup
#    Author : Zaihua Ji,  zji@ucar.edu
#      Date : 11/15/2020
#             2025-04-04 transferred to package rda_python_dbms from
#             https://github.com/NCAR/rda-database.git
#   Purpose : python code to backup PostgreSQL databases and/or schemas
#             to specified local directories.
#             (You must set login entries in your ~/.pgpass to skip password)
#
#    Github : https://github.com/NCAR/rda-python-dbms.git
#
###############################################################################
#
import sys
import re
from os import path as op
from rda_python_common import PgLOG
from rda_python_common import PgFile
from rda_python_common import PgDBI

USNAME = 'postgres'

DBHOST = 'rda-pgdb-03.ucar.edu'
#DBBACKS = ['ivaddb', 'ispddb', 'upadb']
DBBACKS = []

SCHOST = 'rda-pgdb-02.ucar.edu'
SCDB = 'rdadb'
SCBACKS = ['dssdb', 'citation', 'images', 'metautil', 'search', 'wagtail2',
           'writable', 'IGrML', 'IObML', 'VFixML', 'VGrML', 'VObML',
           'VSatML', 'WFixML', 'WGrML', 'WObML', 'WSatML', ]

BACKDIR = "/data/pgbackup"

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
   option = None
   override = False
   for arg in argv:
      ms = re.match(r'^-(\w)$', arg)
      if ms:
         option = ms.group(1)
         if option == 'b':
            PgLOG.PGLOG['BCKGRND'] = 1
         elif option == 'o':
            override = True
         else:
            PgLOG.pglog("{}: unknow option".format(arg), PgLOG.LGEREX)
   
   PgLOG.cmdlog("pgbackup {}".format(' '.join(argv)))

   PgFile.change_local_directory(BACKDIR, LOGACT)
   bcnt = 0

   for db in DBBACKS:
      bcnt += pg_database_backup(db, override)
   for sc in SCBACKS:
      bcnt += pg_schema_backup(sc, SCDB, override)

   s = 'ies' if bcnt > 1 else 'y'
   title = "pgbackup: {} Backup director{} dumped".format(bcnt, s)
   tmsg = "{} under {}!".format(title, BACKDIR)
   PgLOG.set_email(tmsg, PgLOG.EMLTOP)
   PgLOG.pglog(title, SNDACT)
   PgLOG.cmdlog()   
   PgLOG.pgexit(0)

#
#  bacup one database
#
def pg_database_backup(db, override):

   backdir = db + "_backup"
   cmd = "pg_dump {} -h {} -U {} -w -Fd -j 8 -f {}/".format(db, DBHOST, USNAME, backdir)
   if op.exists(backdir):
      if override:
         PgLOG.pgsystem("rm -rf " + backdir, LOGACT, 5)
      else:
         PgLOG.pglog(backdir + ": Backup directory exists, add option -o to override", LOGACT)
         return 0
   if not PgLOG.pgsystem(cmd, LOGACT, 257):
      PgLOG.pglog("{}: Error dumping database\n{}".format(db, PgLOG.PGLOG['SYSERR']), ERRACT)

   return 1

#
#  bacup one database schema
#
def pg_schema_backup(sc, db, override):

   backdir = "{}_{}_backup".format(db, sc)
   pgsc = PgDBI.pgname(sc)
   if pgsc != sc: pgsc = "'{}'".format(pgsc)
   cmd = "pg_dump {} -h {} -n {} -U {} -w -Fd -j 8 -f {}/".format(db, SCHOST, pgsc, USNAME, backdir)
   if op.exists(backdir):
      if override:
         PgLOG.pgsystem("rm -rf " + backdir, LOGACT, 5)
      else:
         PgLOG.pglog(backdir + ": Backup directory exists, add option -o to override", LOGACT)
         return 0
   if not PgLOG.pgsystem(cmd, LOGACT, 257):
      PgLOG.pglog("{}.{}: Error dumping schema\n{}".format(db, sc, PgLOG.PGLOG['SYSERR']), ERRACT)
      return 0

   return 1

#
# call main() to start program
#
if __name__ == "__main__": main()
