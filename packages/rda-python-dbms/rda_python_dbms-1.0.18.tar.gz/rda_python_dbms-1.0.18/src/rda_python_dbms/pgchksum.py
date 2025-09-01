#!/usr/bin/env python3
#
##################################################################################
#
#     Title: pgchksum
#    Author: Zaihua Ji, zji@ucar.edu
#      Date: 05/24/2021
#             2025-04-09 transferred to package rda_python_dbms from
#             https://github.com/NCAR/rda-utility-programs.git
#   Purpose: re-evaluate checksums, data sizes and timestamps for files archived
#            on glade, object store and Globus Quasar server; and optionally to fix them
#
#    Github: https://github.com/NCAR/rda-python-dbms.git
#
##################################################################################
#
import sys
import re
import time
from rda_python_common import PgLOG
from rda_python_common import PgDBI
from rda_python_common import PgUtil 
from rda_python_common import PgFile
from rda_python_common import PgCMD
from rda_python_common import PgSplit

PGSUM = {
   'd' : [],   # delay mode option, value array
   's' : [],   # specialist login name array for email notice, default to none
   'f' : [],   # file name array, default to none
   'i' : [],   # dataset id array, default for all
   'o' : '',   # r - random, s - sequencial
   'p' : '',   # working path, default to PgLOG.PGLOG['UPDTWKP']/pgchksum
   'c' : 0,    # number of files to re-evauate checksums, default 0 for all
   'k' : 0,    # skip the number of files to re-evauate checksums
   'm' : 0,    # 1 for check/fix files missing checksum only
   'n' : 0,    # 1 for not sending email
   'r' : 0,    # running time in unit of hour
   't' : '',   # file type, W(Web), S(Saved) or Q(Quasar)
   'x' : 0     # 1 for fixing checksum, data size and timestamp
}

PVALS = {
   'STEP' : None,
   'CND' : None,
   'TYPE' : None,
   'OFFSET' : '',
   'emllog' : PgLOG.LOGWRN,
   'emlsum' : PgLOG.LOGWRN,
   'emlerr' : PgLOG.LOGERR,
   'begin' : 0,
   'end' : 0
}

#
# main function to excecute this script
#
def main():

   pgname = "pgchksum"
   argv = sys.argv[1:]
   option = None
 
   for arg in argv:
      ms = re.match(r'^-(.+)$', arg)
      if ms:
         option = ms.group(1)
         if option == 'b':
            PgLOG.PGLOG['BCKGRND'] = 1   # processing in backgroup mode
            option = None
         elif option in PGSUM:
            if option in ['m', 'n', 'x']:
               PGSUM[option] = 1
               option = None
         else:
            PgLOG.pglog(arg + ": Unknown option", PgLOG.LGEREX)
      elif option:
         if isinstance(PGSUM[option], list):
            if option == 'i': arg = PgUtil.format_dataset_id(arg)
            PGSUM[option].append(arg)
         elif not PGSUM[option]:
            if option == 'o' and arg not in ['s', 'r']:
               PgLOG.pglog("{}: Value must be 'r' or 's' for Option -{}".format(arg, option), PgLOG.LGEREX)
            PGSUM[option] = int(arg) if PGSUM[option] == 0 else arg
            option = None
         else:
            PgLOG.pglog("{}: value specified already for Option -{}".format(arg, option), PgLOG.LGEREX)
      else:
         PgLOG.pglog(arg + ": value passed without leading Option", PgLOG.LGEREX)
   
   if not PGSUM['t']:
      print("Usage: pgchksum -t (W|S|Q) [-b] [-m] [-n] [-x] [-c FileCount] \\")
      print("                [-d [Hostnames] [RerunCount]] [-f FileNames] [-i DatasetIDs] \\")
      print("                [-k SkipCount] [-o r|s] [-s Specialists]")
      print("  -b - background process and no screen output")
      print("  -c - File count to re-evaluate checksum; for all gathered files if not specified")
      print("  -d - delayed mode background/batch processes on RDA machines/DAV SLURM nodes")
      print("  -f - Re-evaluate the specify File names only")
      print("  -i - Dataset IDs the files belong; for all files if not specified")
      print("  -k - skip the given file count to re-evaluate checksum")
      print("  -m - check/fix files missing checksum only, works with a single dsid provided via option -i")
      print("  -n - do not send email notice to anybody")
      print("  -o - order files radomly (r) or sequencially (s) by file ID, default to not ordering")
      print("  -p - working path, default to PgLOG.PGLOG['UPDTWKP']/pgchksum")
      print("  -r - batch running hours, works with -d")
      print("  -s - specialists to receive email notice in addtion to the running specialist")
      print("  -t - mandatory file type: W-Web, S-Saved or Q-Quasar files")
      print("  -x - fix the missing and wrong checksum, data size and tiemstamp")
      PgLOG.pgexit(0)
   elif PGSUM['t'] not in 'QSW':
      PgLOG.pglog(PGSUM['t'] + ": Unknown File Type, must be one of 'QSW'", PgLOG.LGEREX)

    # set different log file
   PgLOG.PGLOG['LOGFILE'] = pgname + '.log'
   PgLOG.set_suid(PgLOG.PGLOG['EUID'])
   PVALS['begin'] = int(time.time())
   pgcmd = "{} {}".format(pgname, PgLOG.argv_to_string(argv, 1))
   PgLOG.cmdlog("{} {}".format(pgcmd, PVALS['begin']))
   if not PGSUM['n']:
      PVALS['emllog'] = PgLOG.LGWNEM
      PVALS['emlsum'] = PgLOG.LOGWRN|PgLOG.EMLSUM
      PVALS['emlerr'] = PgLOG.LOGERR|PgLOG.EMEROL
      PgDBI.PGDBI['LOGACT'] = PVALS['emlerr']
      if PGSUM['s']: PgLOG.add_carbon_copy(PGSUM['s'])

   if not PGSUM['p']: PGSUM['p'] = PgLOG.PGLOG['UPDTWKP']+ "/pgchksum"
   PgFile.change_local_directory(PGSUM['p'], PVALS['emlerr'])
   
   if PGSUM['t'] == 'W':
      cnt = get_checksum_wfilelist() 
   elif PGSUM['t'] == 'S':
      cnt = get_checksum_sfilelist() 
   elif PGSUM['t'] == 'Q':
      cnt = get_checksum_bfilelist() 
   else:
      PgLOG.pglog(PGSUM['t'] + ": Unknown File Type", PgLOG.LGEREX)
   
   if PGSUM['d']:
      if PGSUM['r'] > 0: PgCMD.set_one_boption('qoptions', "-l walltime={}:00:00".format(PGSUM['r']))
      PgCMD.init_dscheck(0, '', pgname, '', 'CS', '', None, PGSUM['d'])
   
   if cnt:
      fcnt = PGSUM['c']
      pgrecs = PGSUM['f']
      if PgLOG.PGLOG['DSCHECK']: PgLOG.set_dscheck_fcount(fcnt, PVALS['emlerr'])
      PVALS['STEP'] = fcnt/100
      if PVALS['STEP'] < 10: PVALS['STEP'] = 10   # minimum incremental step
      if PVALS['STEP'] > 500: PVALS['STEP'] = 500   # maximum incremental step

      msg = 'Check '
      if PGSUM['x']: msg += 'and Fix '
      msg += "checksum/size/timestamp for {} {} files{}".format(fcnt, PVALS['TYPE'], PVALS['OFFSET'])
      PgLOG.pglog(msg, PVALS['emlsum'])
      cnts = {'cnt' : 0, 'pcnt' : 0, 'xcnt' : 0, 'ecnt' : 0, 'mcnt' : 0, 'ncnt' : 0, 'tcnt' : 0, 'scnt' : 0}

      if PGSUM['t'] == 'W':
         evaluate_webfile_checksum(fcnt, pgrecs, cnts)
      elif PGSUM['t'] == 'S':
         evaluate_savedfile_checksum(fcnt, pgrecs, cnts)
      else:
         evaluate_backfile_checksum(fcnt, pgrecs, cnts)
      dump_progress(fcnt, fcnt, cnts, PVALS['emlsum'])

      PVALS['end'] = int(time.time())
      if not PGSUM['n']: send_check_email(pgcmd, cnts['cnt'], fcnt)

   if PgLOG.PGLOG['DSCHECK']:
      if PgLOG.PGLOG['ERRMSG']:
         PgDBI.record_dscheck_error(PgLOG.PGLOG['ERRMSG'])
      else:
         PgCMD.record_dscheck_status("D")

   PgLOG.cmdlog(None, PVALS['end'])
   
   PgLOG.pgexit(0)

#
# send an email for checking result
#
def send_check_email(pgcmd, cnt, fcnt):

   s = 'es' if cnt > 1 else ''
   cstr = 'With {} Mismatch{}'.format(cnt, s)
   subject = "PGCHKSUM for {} {} Files {}".format(PVALS['TYPE'], fcnt, cstr)
   buf = PgLOG.cmd_execute_time(pgcmd, PVALS['end']-PVALS['begin']) + " Finished  on " + PgLOG.PGLOG['HOSTNAME']

   if PVALS['CND']: buf += "\n{} Files: {}".format(PVALS['TYPE'], PVALS['CND'])   
   PgLOG.set_email(buf, PgLOG.EMLTOP)

   if PgLOG.PGLOG['DSCHECK']:
      PgDBI.build_customized_email("dscheck", "einfo", "cindex = {}".format(PgLOG.PGLOG['DSCHECK']['cindex']),
                                   subject, PgLOG.LOGWRN)
   else:
      PgLOG.pglog(subject, PgLOG.LOGWRN|PgLOG.SNDEML)

#
# get the checksum filelist for wfile
#
def get_checksum_wfilelist():

   PVALS['TYPE'] = "Web"
   PVALS['BUCKET'] = 'rda-data'
   flds = "wid, wfile, type, locflag, data_size, checksum, date_modified, time_modified"

   if PGSUM['f']:
      pgrecs = PgDBI.pgmhget('wfile', 'wid, dsid', {'wfile' : PGSUM['f']})
      cnt = len(pgrecs['wid']) if pgrecs else 0
      if cnt > 0:
         PGSUM['f'] = {}
         for i in range(cnt):
            dsid = pgrecs['dsid'][i]
            pgrec = PgSplit.pgget_wfile(dsid, flds, 'wid = {}'.format(pgrecs['wid'][i]))
            pgrec['dsid'] = dsid
            PgUtil.addrecord(PGSUM['f'], pgrec, i)
      return cnt

   fcnt = PGSUM['c']
   PVALS['CND'] = ''
   dscnt = len(PGSUM['i'])
   if dscnt == 1:
      dsid = PGSUM['i'][0]
      if PgLOG.PGLOG['DSCHECK']: PgCMD.set_dscheck_attribute("dsid", dsid, PVALS['emlerr'])
      if PGSUM['m']: PVALS['CND'] += "(checksum IS NULL OR checksum < ' ') "
   elif dscnt > 1:
      PVALS['CND'] = "dsid IN ({}) ".format(','.join(PGSUM['i']))

   if PGSUM['o']: PVALS['CND'] += "ORDER BY {} ".format('wid' if PGSUM['o'] == 's' else "RANDOM()")
   if fcnt: PVALS['CND'] += "LIMIT {} ".format(fcnt)
   if PGSUM['k']:
      PVALS['OFFSET'] = "OFFSET {}".format(PGSUM['k'])
      PVALS['CND'] += PVALS['OFFSET']

   if dscnt == 1:
      wfrecs = PgSplit.pgmget_wfile(dsid, flds, PVALS['CND'])
      cnt = len(wfrecs['wid']) if wfrecs else 0
   else:
      pgrecs = PgDBI.pgmget('wfile', 'wid, dsid', PVALS['CND'])
      cnt = len(pgrecs['wid']) if pgrecs else 0
      wfrecs = {}
      if cnt > 0:
         for i in range(cnt):
            dsid = pgrecs['dsid'][i]
            pgrec = PgSplit.pgget_wfile(dsid, flds, 'wid = {}'.format(pgrecs['wid'][i]))
            pgrec['dsid'] = dsid
            PgUtil.addrecord(wfrecs, pgrec, i)
   if cnt > 0:
      if fcnt == 0 or fcnt > cnt: PGSUM['c'] = cnt
      PGSUM['f'] = wfrecs
   else:
      PgLOG.pglog("No {} file found for {}".format(PVALS['TYPE'], PVALS['CND']), PVALS['emlerr'])

   return cnt

#
# get the checksum filelist for sfile
#
def get_checksum_sfilelist():

   PVALS['TYPE'] = "Saved"
   PVALS['BUCKET'] = 'rda-decsdata'
   flds = "sid, sfile, dsid, type, locflag, data_size, checksum, date_modified, time_modified"

   hcnd = {}
   fcnt = PGSUM['c']

   cnt = len(PGSUM['f'])
   if cnt > 0:
      PGSUM['f'] = PgDBI.pgmhget('sfile', flds, {'sfile' : PGSUM['f']})
      return (len(PGSUM['f']['sid']) if PGSUM['f'] else 0)

   PVALS['CND'] = ''
   cnt = len(PGSUM['i'])
   if cnt == 1:
      dsid = PGSUM['i'][0]
      PVALS['CND'] = "dsid = '{}'".format(dsid)
      if PgLOG.PGLOG['DSCHECK']: PgCMD.set_dscheck_attribute("dsid", dsid, PVALS['emlerr'])
   elif cnt > 1:
      PVALS['CND'] = "dsid IN ({})".format(','.join(PGSUM['i']))

   if PGSUM['m']:
      if PVALS['CND']: PVALS['CND'] += " AND "
      PVALS['CND'] += "(checksum IS NULL OR checksum < ' ')"

   if PGSUM['o']: PVALS['CND'] += " ORDER BY " + ('sid' if PGSUM['o'] == 's' else "RANDOM()")
   if fcnt: PVALS['CND'] += " LIMIT {}".format(fcnt)
   if PGSUM['k']:
      PVALS['OFFSET'] = " OFFSET {}".format(PGSUM['k'])
      PVALS['CND'] += PVALS['OFFSET']

   pgrecs = PgDBI.pgmget('sfile', flds, PVALS['CND'])
   cnt = len(pgrecs['sid']) if pgrecs else 0
   if cnt > 0:
      if fcnt == 0 or fcnt > cnt: PGSUM['c'] = cnt
      PGSUM['f'] = pgrecs
   else:
      PgLOG.pglog("No {} file found for {}".format(PVALS['TYPE'], PVALS['CND']), PVALS['emlerr'])

   return cnt

#
# get the checksum filelist for bfile
#
def get_checksum_bfilelist():

   PVALS['TYPE'] = "Quasar"
   flds = "bid, bfile, dsid, type, data_size, checksum, date_modified, time_modified"

   fcnt = PGSUM['c']
   cnt = len(PGSUM['f'])
   if cnt > 0:
      PGSUM['f'] = PgDBI.pgmhget('bfile', flds, {'bfile' : PGSUM['f']})
      return (len(PGSUM['f']['bid']) if PGSUM['f'] else 0)

   PVALS['CND'] = ''
   cnt = len(PGSUM['i'])
   if cnt == 1:
      dsid = PGSUM['i'][0]
      PVALS['CND'] = "dsid = '{}' AND ".format(dsid)
      if PgLOG.PGLOG['DSCHECK']: PgCMD.set_dscheck_attribute("dsid", dsid, PVALS['emlerr'])
   elif cnt > 1:
      PVALS['CND'] = "dsid IN ({}) AND ".format(','.join(PGSUM['i']))

   if PGSUM['m']:
      PVALS['CND'] += "(checksum IS NULL OR checksum < ' ') AND "

   PVALS['CND'] += "status = 'A'"

   if PGSUM['o']: PVALS['CND'] += " ORDER BY " + ('bid' if PGSUM['o'] == 's' else "RANDOM()")
   if fcnt: PVALS['CND'] += " LIMIT {}".format(fcnt)
   if PGSUM['k']:
      PVALS['OFFSET'] = " OFFSET {}".format(PGSUM['k'])
      PVALS['CND'] += PVALS['OFFSET']

   pgrecs = PgDBI.pgmget('bfile', flds, PVALS['CND'])
   cnt = len(pgrecs['bid']) if pgrecs else 0
   if cnt > 0:
      if fcnt == 0 or fcnt > cnt: PGSUM['c'] = cnt
      PGSUM['f'] = pgrecs
   else:
      PgLOG.pglog("No {} file found for {}".format(PVALS['TYPE'], PVALS['CND']), PVALS['emlerr'])

   return cnt

#
# dump the program running progress
#
def dump_progress(ccnt, fcnt, cnts, logact):
   
   cntmsg = str(ccnt)
   chkmsg = "Integrity-Checked"
   ttlmsg = " of {}".format(fcnt) if fcnt > ccnt else ""

   if cnts['pcnt'] > 0:
      cntmsg += "/{}".format(cnts['pcnt'])
      chkmsg += "/Passed-checking"

   if cnts['xcnt'] > 0:
      cntmsg += "/{}".format(cnts['xcnt'])
      chkmsg += "/Fixed"

   if cnts['mcnt'] > 0:
      cntmsg += "/{}".format(cnts['mcnt'])
      chkmsg += "/Checksum-mismatch"

   if cnts['ncnt'] > 0:
      cntmsg += "/{}".format(cnts['ncnt'])
      chkmsg += "/Checksum-miss"

   if cnts['scnt'] > 0:
      cntmsg += "/{}".format(cnts['scnt'])
      chkmsg += "/Size-mismatch"

   if cnts['tcnt'] > 0:
      cntmsg += "/{}".format(cnts['tcnt'])
      chkmsg += "/Timestamp-mismatch"

   if cnts['ecnt'] > 0:
      cntmsg += "/{}".format(cnts['ecnt'])
      chkmsg += "/Nonexist"

   PgLOG.pglog("{}{} {} files{} {}".format(cntmsg, ttlmsg, PVALS['TYPE'], PVALS['OFFSET'], chkmsg), logact)

#
# evaluate checksums for web files
#
def evaluate_webfile_checksum(fcnt, pgrecs, cnts):

   for i in range(fcnt):
      if i and i%PVALS['STEP'] == 0:
         if PgLOG.PGLOG['DSCHECK']: PgCMD.add_dscheck_dcount(PVALS['STEP'], 0, PVALS['emlerr'])
         dump_progress(i, fcnt, cnts, PgLOG.LOGWRN)

      pgrec = PgUtil.onerecord(pgrecs, i)
      locflag = pgrec['locflag']
      if locflag == 'O':
         fname = "{}/{}".format(pgrec['dsid'], pgrec['wfile'])
         evaluate_object_file(fname, pgrec, 'rda-data', cnts)
      else:
         fname = pgrec['wfile']
         if not re.match(r'^/', fname):
            fname = "{}/{}/{}".format(PgLOG.PGLOG['DSDHOME'], pgrec['dsid'], fname)
         evaluate_disk_file(fname, pgrec, cnts)

#
# evaluate checksums for saved files
#
def evaluate_savedfile_checksum(fcnt, pgrecs, cnts):

   for i in range(fcnt):
      if i and i%PVALS['STEP'] == 0:
         if PgLOG.PGLOG['DSCHECK']: PgCMD.add_dscheck_dcount(PVALS['STEP'], 0, PVALS['emlerr'])
         dump_progress(i, fcnt, cnts, PgLOG.LOGWRN)

      pgrec = PgUtil.onerecord(pgrecs, i)
      locflag = pgrec['locflag']
      if locflag == 'O':
         fname = "{}/{}".format(pgrec['dsid'], pgrec['sfile'])
         evaluate_object_file(fname, pgrec, 'rda-decsdata', cnts)
      else:
         fname = pgrec['sfile']
         if not re.match(r'^/', fname):
            fname = "{}/{}/{}/{}".format(PgLOG.PGLOG['DECSHOME'], pgrec['dsid'], pgrec['type'], fname)
         evaluate_disk_file(fname, pgrec, cnts)

#
# evaluate checksums for quasar backup files (check size and timestamp only for now)
#
def evaluate_backfile_checksum(fcnt, pgrecs, cnts):

   for i in range(fcnt):
      if i and i%PVALS['STEP'] == 0:
         if PgLOG.PGLOG['DSCHECK']: PgCMD.add_dscheck_dcount(PVALS['STEP'], 0, PVALS['emlerr'])
         dump_progress(i, fcnt, cnts, PgLOG.LOGWRN)

      pgrec = PgUtil.onerecord(pgrecs, i)
      fname = "/{}/{}".format(pgrec['dsid'], pgrec['bfile'])
      evaluate_quasar_file(fname, pgrec, 'rda-quasar', cnts)

#
# evaluate a disk file
#
def evaluate_disk_file(fname, pgrec, cnts):

   info = PgFile.check_local_file(fname, 33, PVALS['emlerr'])   # 33 = 1+32
   if info:
      evaluate_file_status('DSK', fname, pgrec, info, cnts)
   else:
      PgLOG.pglog("{}: Type {} {} file is missing on Disk".format(fname, pgrec['type'], PVALS['TYPE']), PVALS['emllog'])
      cnts['ecnt'] += 1

#
# evaluate an object file
#
def evaluate_object_file(fname, pgrec, bucket, cnts):

   info = PgFile.check_object_file(fname, bucket, 1, PVALS['emlerr'])
   if info:
      evaluate_file_status('OBS', "{}-{}".format(bucket, fname), pgrec, info, cnts)
   else:
      PgLOG.pglog("{}: Type {} {} file is missing in Object Store".format(fname, pgrec['type'], PVALS['TYPE']), PVALS['emllog'])
      cnts['ecnt'] += 1

#
# evaluate a quasar file
#
def evaluate_quasar_file(fname, pgrec, endpoint, cnts):

   info = PgFile.check_backup_file(fname, endpoint, 65, PVALS['emlerr'])
   if info:
      evaluate_file_status('QSR', "{}-{}".format(endpoint, fname), pgrec, info, cnts)
   else:
      PgLOG.pglog("{}: Type {} {} file is missing on Quasar".format(fname, pgrec['type'], PVALS['TYPE']), PVALS['emllog'])
      cnts['ecnt'] += 1

#
# evaluate a file status
#
def evaluate_file_status(lname, fname, pgrec, info, cnts):

   msg = ''
   checksum = info['checksum'] if 'checksum' in info else ''
   diffsum = diffsize = 0
   if checksum:
      if not pgrec['checksum']:
         msg = "Checksum misses"
         cnts['ncnt'] += 1
         diffsum = 2
      elif checksum != pgrec['checksum']:
         msg = "Checksum mismatch"
         cnts['mcnt'] += 1
         diffsum = 1

   if info['data_size'] != pgrec['data_size']:
      if msg: msg += ", "
      msg += "Size mismatch"
      cnts['scnt'] += 1
      diffsize = 1

   difftime = PgUtil.cmptime(info['date_modified'], info['time_modified'], pgrec['date_modified'], pgrec['time_modified'])
   if difftime < 0 or msg and difftime > 0:
      if msg: msg += ", "
      msg += "Timestamp mismatch"
      cnts['tcnt'] += 1

   if msg:
      cnts['cnt'] += 1
      msg = "{}. {}: {}".format(cnts['cnt'], fname, msg)
      msg += "\n{}:".format(lname)
      msg += "{}/{}/{}/{}".format(checksum, info['data_size'], info['date_modified'], info['time_modified'])
      msg += "\nDBS:"
      msg += "{}/{}/{}/{}".format(pgrec['checksum'], pgrec['data_size'], pgrec['date_modified'], pgrec['time_modified'])
      PgLOG.pglog(msg, PVALS['emllog'])
      if PGSUM['x']:
         record = {}
         if diffsize: record['data_size'] = info['data_size']
         if diffsum: record['checksum'] = checksum
         if difftime < 0 or record and difftime:
            record['date_modified'] = info['date_modified'] 
            record['time_modified'] = info['time_modified']
         if record: cnts['xcnt'] += fix_file_info(PGSUM['t'], record, pgrec)
   else:
      cnts['pcnt'] += 1

#
# fix file info
#
def fix_file_info(type, record, pgrec):

   if type == 'W':
      return PgSplit.pgupdt_wfile(pgrec['dsid'], record, "wid = {}".format(pgrec['wid']))
   elif type == 'S':
      return PgDBI.pgupdt('sfile', record, "sid = {}".format(pgrec['sid']))
   else:
      return PgDBI.pgupdt('bfile', record, "bid = {}".format(pgrec['bid']))

#
# call main() to start program
#
if __name__ == "__main__": main()
