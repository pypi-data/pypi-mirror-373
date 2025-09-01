#
###############################################################################
#
#     Title : MyDBI.py  -- My DataBase Interface
#    Author : Zaihua Ji,  zji@ucar.edu
#      Date : 03/07/2016
#             2024-04-11 restored the deleted one
#   Purpose : Python library module to handlequery and manipulate MySQL database
#
#    Github : https://github.com/NCAR/rda-python-dbms.git
#
###############################################################################

import os
import re
import time
import mysql.connector as MySQL
from os import path as op
from rda_python_common import PgLOG

mydb = None    # reference to a connected database object
curtran = 0    # 0 - no transaction, > 0 - in transaction, current action count
NMISSES = []   # array of mising userno
LMISSES = []   # array of mising logname
TABLES = {}      # record table field information
SPECIALIST = {}  # hash array refrences to specialist info of dsids
SYSDOWN = {}
MYDBI = {}
ADDTBLS = []
MYSIGNS = ['!', '<', '>', '<>']

MYSTRS = {
   'wfile' : ['wfile']
}

# hard coded socket paths for machine_dbnames
DBSOCKS = {
  'default' : "/data/dssdb/tmp/mysql.sock",
  'obsua'   : "/data/upadb/tmp/mysql.sock",
  'ivaddb'  : "/data/ivaddb/tmp/mysql.sock",
  'ispddb'  : "/data/ispddb/tmp/mysql.sock"
}

# hard coded db ports for machine_dbnames
DBPORTS = {
  'default' : 3306,
  'obsua'   : 3307,
  'upadb'   : 3307,
  'ispddb'  : 3307
}

# home path for check db on alter host
VIEWHOMES = {
  'default' : PgLOG.PGLOG['DSSDBHM']
}

#
#  MySQL specified query timestamp format
#
fmtyr = lambda fn: "year({})".format(fn)
fmtqt = lambda fn: "quarter({})".format(fn)
fmtmn = lambda fn: "month({})".format(fn)
fmtdt = lambda fn: "date({})".format(fn)
fmtym = lambda fn: "date_format({}, '%Y-%m')".format(fn)
fmthr = lambda fn: "hour({})".format(fn)

#
# set environments and defaults
#
def SETMYDBI(name, value):
   MYDBI[name] = PgLOG.get_environment(name, value)

SETMYDBI('CDHOST', 'rda-db.ucar.edu')  # common domain for db host for master server
SETMYDBI('DEFNAME', 'dssdb')
SETMYDBI('DEFHOST', PgLOG.PGLOG['PSQLHOST'])
SETMYDBI("DEFPORT", 0)
SETMYDBI("DEFSOCK", '')
SETMYDBI("DBNAME", MYDBI['DEFNAME'])
SETMYDBI("LNNAME", MYDBI['DBNAME'])
SETMYDBI("PWNAME", MYDBI['LNNAME'])
SETMYDBI("DBHOST", (os.environ['DSSDBHOST'] if os.environ.get('DSSDBHOST') else MYDBI['DEFHOST']))
SETMYDBI("DBPORT", 0)
SETMYDBI("LOGACT", PgLOG.LOGERR)   # default logact
SETMYDBI("DBSOCK", '')
SETMYDBI("DATADIR", PgLOG.PGLOG['DSDHOME'])
SETMYDBI("BCKPATH", PgLOG.PGLOG['DSSDBHM'] + "/backup")
SETMYDBI("SQLPATH", PgLOG.PGLOG['DSSDBHM'] + "/sql")
SETMYDBI("VWNAME", MYDBI['DBNAME'])
SETMYDBI("VWPORT", 0)
SETMYDBI("VWSOCK", '')

MYDBI['DBSHOST'] = PgLOG.get_short_host(MYDBI['DBHOST'])
MYDBI['DEFSHOST'] = PgLOG.get_short_host(MYDBI['DEFHOST'])
MYDBI['VWHOST'] = PgLOG.PGLOG['PVIEWHOST']
MYDBI['VWSHOST'] = PgLOG.get_short_host(MYDBI['VWHOST'])
MYDBI['VWHOME'] =  (VIEWHOMES[PgLOG.PGLOG['HOSTNAME']] if PgLOG.PGLOG['HOSTNAME'] in VIEWHOMES else VIEWHOMES['default'])
MYDBI['VHSET'] = 0
MYDBI['MTRANS'] = 5000  # max number of changes in one transactions
MYDBI['MAXICNT'] = 3000000  # maximum number of records in each table

#
# create a myddl command string and return it
#
def get_myddl_command(tname):

   ms = re.match(r'^(.+)\.(.+)$', tname)
   if ms:
      dbname = ms.group(1)
      tname = ms.group(2)
   else:
      dbname = MYDBI['DBNAME']

   return "myddl {} -aa -h {} -d {} -u {}".format(tname, MYDBI['DBHOST'], dbname, MYDBI['LNNAME'])

#
# set default connection for dssdb MySQL Server
#
def dssdb_dbname():
   default_dbinfo(MYDBI['DEFNAME'], PgLOG.PGLOG['PSQLHOST'])

#
# set default connection for obsua MySQL Server
#
def obsua_dbname():
   default_dbinfo('obsua', "rda-db-rep.ucar.edu", None, None, 3307)

#
# set default connection for ivadb MySQL Server
#
def ivaddb_dbname():
   default_dbinfo('ivaddb', "rda-db-icoads.ucar.edu")

#
# set a default database info with hard coded info
#
def default_dbinfo(dbname = None, dbhost = None, lnname = None, pwname = None, dbport = None, socket = None):

   if not dbname: dbname = MYDBI['DEFNAME']
   if not dbhost: dbhost = MYDBI['DEFHOST']
   if dbport is None: dbport = MYDBI['DEFPORT']
   if socket is None:  socket = MYDBI['DEFSOCK']

   set_dbname(dbname, lnname, pwname, dbhost, dbport, socket)

#
# get the datbase sock file name of a given dbname for local connection
#
def get_dbsock(dbname):
   
   return (DBSOCKS[dbname] if dbname in DBSOCKS else DBSOCKS['default'])

#
# get the datbase port number of a given dbname for remote connection
#
def get_dbport(dbname):

   return (DBPORTS[dbname] if dbname in DBPORTS else DBPORTS['default'])

#
# set connection for viewing database information
#
def view_dbinfo(dbname = None, lnname = None, pwname = None):

   if not dbname: dbname = MYDBI['DEFNAME']

   set_dbname(dbname, lnname, pwname, PgLOG.PGLOG['PVIEWHOST'], MYDBI['VWPORT'])
   if dbname and dbname != MYDBI['VWNAME']: MYDBI['VWNAME'] = dbname

#
# set connection for given dbname
#
def set_dbname(dbname = None, lnname = None, pwname = None, dbhost = None, dbport = None, socket = None):

   changed = 0

   if dbname and dbname != MYDBI['DBNAME']:
      MYDBI['PWNAME'] = MYDBI['LNNAME'] = MYDBI['DBNAME'] = dbname
      changed = 1
   if lnname and lnname != MYDBI['LNNAME']:
      MYDBI['PWNAME'] = MYDBI['LNNAME'] = lnname
      changed = 1
   if pwname and pwname != MYDBI['PWNAME']:
      MYDBI['PWNAME'] = pwname
      changed = 1
   if dbhost and dbhost != MYDBI['DBHOST']:
      MYDBI['DBHOST'] = dbhost
      MYDBI['DBSHOST'] = PgLOG.get_short_host(dbhost)
      changed = 1
   if MYDBI['DBSHOST'] == PgLOG.PGLOG['HOSTNAME']:
      if socket is None: socket = get_dbsock(dbname)
      if socket != MYDBI['DBSOCK']:
         MYDBI['DBSOCK'] = socket
         changed = 1
   else:
      if not dbport: dbport = get_dbport(dbname)
      if dbport != MYDBI['DBPORT']:
         MYDBI['DBPORT'] = dbport
         changed = 1

   if changed and mydb is not None: mydisconnect(1)

#
# start a database transaction and exit if fails
#
def starttran():

   global curtran

   if curtran: endtran()   # try to end previous transaction
   if not (mydb and mydb.is_connected): myconnect(1)
   mydb.start_transaction()
   curtran = 1

#
# end a transaction with changes committed and exit if fails
#
def endtran():

   global curtran
   if curtran and mydb and mydb.is_connected(): mydb.commit()
   curtran = 0

#
# end a transaction without changes committed and exit inside if fails
#
def aborttran():

   global curtran
   if curtran and mydb and mydb.is_connected(): mydb.rollback()
   curtran = 0

#
# record error message to dscheck record and clean the lock
#
def record_dscheck_error(errmsg, logact = (MYDBI['LOGACT']|PgLOG.EXITLG)):

   cnd = PgLOG.PGLOG['DSCHECK']['chkcnd']
   if PgLOG.PGLOG['NOQUIT']: PgLOG.PGLOG['NOQUIT'] = 0
   dflags = PgLOG.PGLOG['DSCHECK']['dflags']

   myrec = myget("dscheck", "mcount, tcount, lockhost, pid", cnd, logact)
   if not myrec: return 0
   if not myrec['pid'] and not myrec['lockhost']: return 0
   (chost, cpid) = PgLOG.current_process_info()
   if myrec['pid'] != cpid or myrec['lockhost'] != chost: return 0

   # update dscheck record only if it is still locked by the current process
   record = {}
   record['chktime'] = int(time.time())
   if logact&PgLOG.EXITLG:
      record['status'] = "E"
      record['pid'] = 0   # release lock
   if dflags:
      record['dflags'] = dflags
      record['mcount'] = myrec['mcount'] + 1
   else:
      record['dflags'] = ''

   if errmsg:
      errmsg = PgLOG.break_long_string(errmsg, 512, None, 50, None, 50, 25)
      if myrec['tcount'] > 1: errmsg = "Try {}: {}".format(myrec['tcount'], errmsg)
      record['errmsg'] = errmsg

   return myupdt("dscheck", record, cnd, logact)

#
# local function to log query error
#
def qelog(myerr, sleep, sqlstr, vals, mycnt, logact = 0):

   retry = " Sleep {}(sec) & ".format(sleep) if sleep else " "
   if not logact: logact = MYDBI['LOGACT']

   if sqlstr:
      if sqlstr.find("Retry ") == 0:
         retry += "the {} ".format(PgLOG.int2order(mycnt+1))
      elif sleep:
         retry += "the {} Retry: \n".format(PgLOG.int2order(mycnt+1))
      elif mycnt:
         retry = " Error the {} Retry: \n".format(PgLOG.int2order(mycnt))
      else:
         retry = "\n"
      sqlstr = retry + sqlstr
   else:
      sqlstr = ''

   if vals: sqlstr += " with values: " + str(vals)

   if myerr.errno: sqlstr = "{}{}".format(str(myerr), sqlstr)
   if logact&PgLOG.EXITLG and PgLOG.PGLOG['DSCHECK']: record_dscheck_error(sqlstr, logact)
   PgLOG.pglog(sqlstr, logact)
   if sleep: time.sleep(sleep)

   return PgLOG.FAILURE    # if not exit in PgLOG.pglog()

#
# try to add a new table according the table not exist error
#
def try_add_table(errstr, logact):

   ms = re.match(r"1146.* Table '.+\.(.+)' doesn't exist", errstr)
   if ms:
      tname = ms.group(1)
      add_a_table(tname)

#
# add a new table for given table name
#
def add_a_table(tname, logact):

   if tname not in ADDTBLS:
      PgLOG.pgsystem(get_myddl_command(tname), logact)
      ADDTBLS.append(tname)

#
# local function to log query error
#
def check_dberror(myerr, mycnt, sqlstr, ary, logact = 0):

   ret = PgLOG.FAILURE

   if not logact: logact = MYDBI['LOGACT']
   if mycnt < PgLOG.PGLOG['DBRETRY']:
      if myerr.errno == 1040 or myerr.errno == 2003 or myerr.errno == 2005:
         if MYDBI['DBNAME'] == MYDBI['DEFNAME'] and MYDBI['DBSHOST'] != MYDBI['DEFSHOST']:
            default_dbinfo()
            qelog(myerr, 0, "Retry Connecting to {} on {}".format(MYDBI['DBNAME'], MYDBI['DBHOST']), ary, mycnt, PgLOG.MSGLOG)
         else:
            qelog(myerr, 5+5*mycnt, "Retry Connecting", ary, mycnt, PgLOG.LOGWRN)

         return PgLOG.SUCCESS
      elif myerr.errno == -1 or myerr.errno == 2006 or myerr.errno == 2013:   # lost connection & reconnect server
         qelog(myerr, 0, "Retry Connecting", ary, mycnt, PgLOG.LOGWRN)
         myconnect(1, mycnt + 1)
         return (PgLOG.FAILURE if not mydb else PgLOG.SUCCESS)
      elif myerr.errno == 1205:   #  try to lock again
         qelog(myerr, 10, "Retry Locking", ary, mycnt, PgLOG.LOGWRN)
         return PgLOG.SUCCESS
      elif myerr.errno == 1146 and logact&PgLOG.ADDTBL:   #  try to add table
         qelog(myerr, 0, "Retry after adding a table", ary, mycnt, PgLOG.LOGWRN)
         try_add_table(str(myerr), logact)
         return PgLOG.SUCCESS

   if logact&PgLOG.DOLOCK and myerr.errno == 1205: logact &= ~PgLOG.EXITLG   # no exit for lock error
   return qelog(myerr, 0, sqlstr, ary, mycnt, logact)

#
# return hash reference to mysql batch mode command and output file name
#
def mybatch(sqlfile, foreground = 0):

   if(MYDBI['VWHOST'] and MYDBI['VWHOME'] and
      MYDBI['DBSHOST'] == MYDBI['VWSHOST'] and MYDBI['DBNAME'] == MYDBI['VWNAME']):
      slave = "/{}/{}.slave".format(MYDBI['VWHOME'], MYDBI['VWHOST'])
      if not op.exists(slave):
         set_dbname(None, None, None, MYDBI['DEFHOST'], MYDBI['DEFPORT'])

   if MYDBI['DBSHOST'] == PgLOG.PGLOG['HOSTNAME']:
      if not MYDBI['DBSOCK']: MYDBI['DBSOCK'] = get_dbsock(MYDBI['DBNAME'])
      options = "-h localhost -S " + MYDBI['DBSOCK']
   else:
      if not MYDBI['DBPORT']: MYDBI['DBPORT'] = get_dbport(MYDBI['DBNAME'])
      options = "-h {} -P {}".format(MYDBI['DBHOST'], MYDBI['DBPORT'])

   options += " -u {} -p{} {}".format(MYDBI['LNNAME'], MYDBI['PWNAME'], MYDBI['DBNAME'])

   if sqlfile: return options

   if foreground:
      batch = "mysql -vvv {} < {} |".format(options, sqlfile)
   else:
      batch['out'] = sqlfile
      if re.search(r'\.sql$', batch['out']):
         batch['out'] = re.sub(r'\.sql$', '.out', batch['out'])
      else:
         batch['out'] += ".out"

      batch['cmd'] = "mysql {} < {} > {} 2>&1".format(options, sqlfile , batch['out'])

   return batch

#
# start a connection to dssdb database and return a DBI object; None if error
# force connect if connect > 0
#
def myconnect(reconnect = 0, mycnt = 0):

   global mydb

   if mydb and reconnect:
      if mydb.is_connected(): return mydb    # no need reconnect
      try:
         mydb.reconnect()
         return mydb
      except MySQL.Error as myerr:
         check_dberror(myerr, mycnt+1, '', None, MYDBI['LOGACT'])
         mydisconnect(1)
   elif mydb:
      return mydb
   elif reconnect:
      reconnect = 0   # initial connection

   if(MYDBI['DBSHOST'] != PgLOG.PGLOG['HOSTNAME'] and MYDBI['VWHOST'] and
      MYDBI['VWHOME'] and MYDBI['DBSHOST'] == MYDBI['VWSHOST'] and MYDBI['DBNAME'] == MYDBI['VWNAME']):
      slave = "/{}/{}.slave".format(MYDBI['VWHOME'], MYDBI['VWHOST'])
      if not op.exists(slave): set_dbname(None, None, None, MYDBI['DEFHOST'], MYDBI['DEFPORT'])

   while True:
      config = {'database' : MYDBI['DBNAME'],
                    'user' : MYDBI['LNNAME'],
                'auth_plugin' : 'mysql_native_password',
                'password' : '******'}
      if MYDBI['DBSHOST'] == PgLOG.PGLOG['HOSTNAME']:
         if not MYDBI['DBSOCK']: MYDBI['DBSOCK'] = get_dbsock(MYDBI['DBNAME'])
         config['host'] = 'localhost'
         config['unix_socket'] = MYDBI['DBSOCK']
      else:
         if not MYDBI['DBPORT']: MYDBI['DBPORT'] = get_dbport(MYDBI['DBNAME'])
         config['host'] = MYDBI['DBHOST'] if MYDBI['DBHOST'] else MYDBI['CDHOST']
         if MYDBI['DBPORT']: config['port'] = MYDBI['DBPORT'] 

      sqlstr = "MySQL.connect(**{})".format(config)
      if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, sqlstr)

      config['password'] = MYDBI['PWNAME']
      config['autocommit'] = True
      try:
         PgLOG.PGLOG['MYDBBUF'] = mydb = MySQL.connect(**config)
         if reconnect: PgLOG.pglog("{} Reconnected at {}".format(sqlstr, PgLOG.current_datetime()), PgLOG.MSGLOG|PgLOG.FRCLOG)
         return mydb
      except MySQL.Error as myerr:
         if not check_dberror(myerr, mycnt, sqlstr, None, MYDBI['LOGACT']|PgLOG.EXITLG): return PgLOG.FAILURE 
         mycnt += 1


#
# return a MySQL cursor upon success
#
def mycursor():

   mycur = None

   if not mydb:
      myconnect()   
      if not mydb: return PgLOG.FAILURE

   mycnt = 0
   while True:
      try:
         mycur = mydb.cursor()
      except MySQL.Error as myerr:
         if mycnt == 0 and not mydb.is_connected():
            myconnect(1)
         elif not check_dberror(myerr, mycnt, '', None, MYDBI['LOGACT']|PgLOG.EXITLG):
            return PgLOG.FAILURE 
      else:
         break
      mycnt += 1

   return mycur

#
# disconnect to dssdb database
#
def mydisconnect(stopit = 1):

   global mydb
   if mydb:
      if stopit: mydb.close()
      PgLOG.PGLOG['MYDBBUF'] = mydb = None

#
# decode mysql byte fields for multiple records 
#
def decode_byte_records(flds, myrecs):

   cnt = len(myrecs[flds[0]])
   for fld in flds:
      if fld in myrecs:
         for i in range(cnt):
            val = myrecs[fld][i]
            if hasattr(val, 'decode'): myrecs[fld][i] = val.decode()

#
# decode mysql byte fields for single record
#
def decode_byte_record(flds, myrec):

   for fld in flds:
      if fld in myrec:
         val = myrec[fld]
         if hasattr(val, 'decode'): myrec[fld] = val.decode()

#
# gather table field default information as hash array with field names as keys
# and default values as values
# the whole table information is cached to a hash array with table names as keys
#
def mytable(tablename, logact = MYDBI['LOGACT']):

   if tablename in TABLES: return TABLES[tablename].copy()  # cached already

   intms = r'^(tinyint|smallint|mediumint|bigint|int)$'
   numms = r'^(\d+)$'
   fields = "column_name col, data_type typ, is_nullable nil, column_default def"
   condition = table_condition(tablename)
   mycnt = 0
   while True:
      myrecs = mymget('information_schema.columns', fields, condition, logact)
      cnt = len(myrecs['col']) if myrecs else 0
      if cnt: break
      if mycnt == 0 and logact&PgLOG.ADDTBL:
         add_a_table(tablename, logact)
      else:
         return PgLOG.pglog(tablename + ": Table not exists", logact)
      mycnt += 1

   mytable = {}
   decode_byte_records(['typ', 'def'], myrecs)
   for i in range(cnt):
      name = myrecs['col'][i]
      typ = myrecs['typ'][i]
      dflt = myrecs['def'][i]
      isint = re.match(intms, typ)
      if dflt != None:
         if isint and isinstance(dflt, str) and re.match(numms, dflt):
            dflt = int(dflt)
      elif myrecs['nil'][i] == 'YES':
         dflt = None
      elif isint:
         dflt = 0
      else:
         dflt = ''
      mytable[name] = dflt

   TABLES[tablename] = mytable.copy()
   return mytable

#
# local fucntion: insert prepare for myadd() and mymadd()
#
def prepare_insert(tablename, fields):

   strfld = ""
   strplc = ""
   sep = ''
   for fld in fields:
      strfld += sep + fld
      strplc += sep + "%s"
      sep = ","

   sqlstr = "INSERT INTO {} ({}) VALUES ({})".format(tablename, strfld, strplc)
   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, sqlstr) 

   return sqlstr


#
# local fucntion: prepare default value for single record
#
def prepare_default(tablename, record, logact = 0):

   table = mytable(tablename, logact)

   for fld in record:
      val = record[fld]
      if val is None:
         vlen = 0
      elif isinstance(val, str):
         vlen = len(val)
      else:
         vlen = 1
      if vlen == 0: record[fld] = table[fld]

#
# local fucntion: prepare default value for multiple records
#
def prepare_defaults(tablename, records, logact = 0):

   table = mytable(tablename, logact)

   for fld in records:
      vals = records[fld]
      vcnt = len(vals)
      for i in range(vcnt):
         if vals[i] is None:
            vlen = 0
         elif isinstance(vals[i], str):
            vlen = len(vals[i])
         else:
            vlen = 1
         if vlen == 0: records[fld][i] = table[fld]

#
# insert one record into tablename
# tablename: add record for one table name each call
#    record: hash reference with keys as field names and hash values as field values
# return PgLOG.SUCCESS or PgLOG.FAILURE
#
def myadd(tablename, record, logact = 0):

   global curtran
   if not logact: logact = MYDBI['LOGACT']
   if not record: return PgLOG.pglog("Nothing adds to " + tablename, logact)
   if(logact&PgLOG.DODFLT): prepare_default(tablename, record, logact)

   fields = list(record)
   values = tuple(record.values())

   sqlstr = prepare_insert(tablename, fields)
   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, "Insert to " + tablename + " for " + str(values))

   ret = mycnt = ccnt = 0
   while True:
      mycur = mycursor()
      if not mycur: return PgLOG.FAILURE
      try:
         mycur.execute(sqlstr, values)
         if(logact&PgLOG.AUTOID):
            ret = mycur.lastrowid
         else:
            ret = 1
         mycur.close()
         ccnt = 1
      except MySQL.Error as myerr:
         if not check_dberror(myerr, mycnt, sqlstr, values, logact): return PgLOG.FAILURE
      else:
         break
      mycnt += 1

   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, "myadd: 1 record added to " + tablename + ", return " + str(ret))
   if(logact&PgLOG.ENDLCK):
      endtran()
   elif curtran:
      curtran += ccnt
      if curtran > MYDBI['MTRANS']: starttran()

   return ret

#
# insert multiple records into tablename
# tablename: add records for one table name each call
#   records: dict with field names as keys and  each value is a list of field values
#  return PgLOG.SUCCESS or PgLOG.FAILURE
#
def mymadd(tablename, records, logact = 0):

   global curtran
   if not logact: logact = MYDBI['LOGACT']
   if not records: return PgLOG.pglog("Nothing to insert to table " + tablename, logact)
   if logact&PgLOG.DODFLT: prepare_defaults(tablename, records, logact)

   fields = list(records)
   v = records.values()
   values = tuple(zip(*v))
   cntrow = len(values)
   ids = [] if logact&PgLOG.AUTOID else None

   sqlstr = prepare_insert(tablename, fields)
   if PgLOG.PGLOG['DBGLEVEL']:
      for row in values: PgLOG.mydbg(1000, "Insert: " + str(row))

   count = mycnt = 0
   while True:
      mycur = mycursor()
      if not mycur: return PgLOG.FAILURE
      if ids is None:
         while count < cntrow:
            ncount = count + MYDBI['MTRANS']
            if ncount > cntrow: ncount = cntrow
            try:
               mycur.executemany(sqlstr, values[count:ncount])
               count = ncount
            except MySQL.Error as myerr:
               if not check_dberror(myerr, mycnt, sqlstr, values[count], logact): return PgLOG.FAILURE
               break
      else:
         while count < cntrow:
            record = values[count]
            try:
               mycur.execute(sqlstr, record)
               ids.append(mycur.lastrowid)
               count += 1
            except MySQL.Error as myerr:
               if not check_dberror(myerr, mycnt, sqlstr, record, logact): return PgLOG.FAILURE
               break
      if count >= cntrow: break
      mycnt += 1

   mycur.close()
   if(PgLOG.PGLOG['DBGLEVEL']): PgLOG.mydbg(1000, "mymadd: {} of {} record(s) added to {}".format(count, cntrow, tablename))

   if(logact&PgLOG.ENDLCK):
      endtran()
   elif curtran:
      curtran += count
      if curtran > MYDBI['MTRANS']: starttran()

   return (ids if ids else count)

#
# local function: select prepare for myget() and mymget()
#
def prepare_select(tablenames, fields = None, condition = None, logact = 0):

   sqlstr = ''   
   if tablenames:
      if logact&PgLOG.DOLOCK:
         starttran()
         if condition:
            condition += " FOR UPDATE"
         else:
            condition = "FOR UPDATE"
      if fields:
         sqlstr = "SELECT " + fields
      else:
         sqlstr = "SELECT count(*) cntrec"

      sqlstr += " FROM " + tablenames
      if condition:
         if re.match(r'^\s*(ORDER|GROUP|HAVING|OFFSET|LIMIT)\s', condition, re.I):
            sqlstr += " " + condition      # no where clause, append directly
         else:
            sqlstr += " WHERE " + condition

   elif fields:
      sqlstr = "SELECT " + fields
   elif condition:
      sqlstr = condition

   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, sqlstr)

   return sqlstr

#
# tablenames: comma deliminated string of one or more tables and more than one table for joining,
#     fields: comma deliminated string of one or more field names,
#  condition: querry conditions for where clause
# return a dict reference with keys as field names upon success 
#
def myget(tablenames, fields, condition = None, logact = 0):

   if not logact: logact = MYDBI['LOGACT']
   if fields and condition and not re.search(r'limit 1$', condition, re.I): condition += " LIMIT 1"
   sqlstr = prepare_select(tablenames, fields, condition, logact)
   ucname = True if logact&PgLOG.UCNAME else False
   mycnt = 0
   while True:
      mycur = mycursor()
      if not mycur: return PgLOG.FAILURE
      try:
         mycur.execute(sqlstr)
         v = mycur.fetchone()
         if v:
            if ucname:
               c = [col.upper() for col in mycur.column_names]
            else:
               c = mycur.column_names
            record = dict(zip(c,v))
            if tablenames in MYSTRS: decode_byte_record(MYSTRS[tablenames], record)
         else:
            record = None
         mycur.close()
      except MySQL.Error as myerr:
         if not check_dberror(myerr, mycnt, sqlstr, None, logact): return PgLOG.FAILURE 
      else:
         break
      mycnt += 1

   if record and tablenames and not fields:
      if PgLOG.PGLOG['DBGLEVEL']:
         PgLOG.mydbg(1000, "myget: {} record(s) found from {}".format(record['cntrec'], tablenames))
      return record['cntrec']
   elif PgLOG.PGLOG['DBGLEVEL']:
      cnt = 1 if record else 0
      PgLOG.mydbg(1000, "myget: {} record retrieved from {}".format(cnt, tablenames))

   return record

#
# tablenames: comma deliminated string of one or more tables and more than one table for joining,
#     fields: comma deliminated string of one or more field names,
#  condition: querry conditions for where clause
# return a two dimension array reference with field names and values upon success 
#
def myaget(tablenames, fields, condition = None, logact = 0):

   if not logact: logact = MYDBI['LOGACT']
   if fields and condition and not re.search(r'limit 1$', condition, re.I): condition += " LIMIT 1"
   sqlstr = prepare_select(tablenames, fields, condition, logact)
   ucname = True if logact&PgLOG.UCNAME else False
   mycnt = 0
   while True:
      mycur = mycursor()
      if not mycur: return PgLOG.FAILURE
      try:
         mycur.execute(sqlstr)
         v = mycur.fetchone()
         if v:
            if ucname:
               c = [col.upper() for col in mycur.column_names]
            else:
               c = mycur.column_names
            record = [c, v]
         else:
            record = None
         mycur.close()
      except MySQL.Error as myerr:
         if not check_dberror(myerr, mycnt, sqlstr, None, logact): return PgLOG.FAILURE 
      else:
         break
      mycnt += 1

   if PgLOG.PGLOG['DBGLEVEL']:
      cnt = 1 if record else 0
      PgLOG.mydbg(1000, "myget: {} record retrieved from {}".format(cnt, tablenames))

   return record

#
# tablenames: comma deliminated string of one or more tables and more than one table for joining,
#     fields: comma deliminated string of one or more field names,
#  condition: querry conditions for where clause
# return a dict reference with keys as field names upon success, values for each field name
#        are in a list. All lists are the same length with missing values set to None
#
def mymget(tablenames, fields, condition, logact = 0):

   if not logact: logact = MYDBI['LOGACT']
   if isinstance(condition, dict): return myhget(tablenames, fields, condition, logact)
   sqlstr = prepare_select(tablenames, fields, condition, logact)
   ucname = True if logact&PgLOG.UCNAME else False
   count = mycnt = 0
   while True:
      mycur = mycursor()
      if not mycur: return PgLOG.FAILURE
      try:
         mycur.execute(sqlstr)
         rows = mycur.fetchall()
         if rows:
            if ucname:
               cols = [col.upper() for col in mycur.column_names]
            else:
               cols = mycur.column_names
            ccnt = len(cols)
            values = list(zip(*rows))
            records = {}
            for i in range(ccnt):
               records[cols[i]] = list(values[i])
            if tablenames in MYSTRS: decode_byte_records(MYSTRS[tablenames], records)

         else:
            records = None
         mycur.close()
      except MySQL.Error as myerr:
         if not check_dberror(myerr, mycnt, sqlstr, None, logact): return PgLOG.FAILURE 
      else:
         break
      mycnt += 1

   if PgLOG.PGLOG['DBGLEVEL']:
      count = len(records[cols[0]]) if records else 0
      PgLOG.mydbg(1000, "mymget: {} record(s) retrieved from {}".format(count, tablenames))

   return records

#
# local function: select prepare for myhget()
#
def prepare_hash_select(tablenames, fields, cndstr, cndflds):

   # build condition string
   for fld in cndflds:
      if cndstr:
         cndstr += " AND {}=%s".format(fld)
      else:
         cndstr = fld + "=%s"

   sqlstr = "SELECT {} FROM {} WHERE {}".format(fields, tablenames, cndstr)
   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, sqlstr) 

   return sqlstr

#
# tablenames: comma deliminated string of one or more tables
#     fields: comma deliminated string of one or more field names,
#     cndstr: string query condition for where clause
#    cnddict: condition values, dict with field names : value lists
# return a dict(field names : value lists) upon success 
#
# retrieve multiple records from tablenames one for each row condition in condition dict
#
def myhget(tablenames, fields, cndstr, cnddict, logact = 0):

   if not logact: logact = MYDBI['LOGACT']
   if not tablenames: return PgLOG.pglog("Miss Table name to query", logact)
   if not fields: return PgLOG.pglog("Nothing to query " + tablenames, logact)
   if not cnddict: return PgLOG.pglog("Miss condition dict values to query " + tablenames, logact)
   ucname = True if logact&PgLOG.UCNAME else False

   cndflds = list(cnddict)
   v = cnddict.values()
   values = tuple(zip(*v))
   cntval = len(values)

   sqlstr = prepare_hash_select(tablenames, fields, cndstr, cndflds)
   if PgLOG.PGLOG['DBGLEVEL']:
      for row in values:
         PgLOG.mydbg(1000, "Query from " + tablenames + " for Condition values: " + str(row))

   count = mycnt = 0
   while True:
      mycur = mycursor()
      if not mycur: return PgLOG.FAILURE
      try:
         mycur.executemany(sqlstr, values)
         rows = mycur.fetchall()
         if rows:
            if ucname:
               cols = [col.upper() for col in mycur.column_names]
            else:
               cols = mycur.column_names
            ccnt = len(cols)
            values = list(zip(*rows))
            records = {}
            for i in range(ccnt):
               records[cols[i]] = list(values[i])
            if tablenames in MYSTRS: decode_byte_record(MYSTRS[tablenames], records)
         else:
            records = None
         mycur.close()
      except MySQL.Error as myerr:
         if not check_dberror(myerr, mycnt, sqlstr, values[0], logact): return PgLOG.FAILURE 
      else:
         break
      mycnt += 1

   if PgLOG.PGLOG['DBGLEVEL']:
      count = len(records[cols[0]]) if records else 0
      PgLOG.mydbg(1000, "myhget: {} record(s) retrieved from {}".format(count, tablenames))

   return records

#
# local fucntion: update prepare for mymupdt
#
def prepare_update(tablename, fields, cndstr, cndflds = None):

   strset = []
   # build set string
   for fld in fields:
      strset.append("{}=%s".format(fld))
   strset = ",".join(strset)

   # build condition string
   if not cndstr:
      cndstr = []
      try:
         for fld in cndflds:
            cndstr.append("{}=%s".format(fld))
         cndstr = " AND ".join(cndstr)
      except NameError as e:
         PgLOG.pglog("[prepare_update] NameError: {}".format(e), PgLOG.LGEREX)

   sqlstr = "UPDATE {} SET {} WHERE {}".format(tablename, strset, cndstr)
   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, sqlstr)

   return sqlstr

#
# update one or multiple rows in tablename
# tablename: update for one table name each call
#    record: dict with field names : values
# condition: update conditions for where clause)
# return number of rows undated upon success
#
def myupdt(tablename, record, condition, logact = 0):

   global curtran
   if not logact: logact = MYDBI['LOGACT']
   if not record: PgLOG.pglog("Nothing updates to " + tablename, logact)
   if not condition or isinstance(condition, int): PgLOG.pglog("Miss condition to update " + tablename, logact)
   if logact&PgLOG.DODFLT: prepare_default(tablename, record, logact)

   fields = list(record)
   values = tuple(record.values())

   sqlstr = prepare_update(tablename, fields, condition)
   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, "Update {} for {}".format(tablename, values))

   ret = mycnt = 0
   while True:
      mycur = mycursor()
      if not mycur: return PgLOG.FAILURE
      try:
         mycur.execute(sqlstr, values)
         ret = mycur.rowcount
         mycur.close()
      except MySQL.Error as myerr:
         if not check_dberror(myerr, mycnt, sqlstr, values, logact): return PgLOG.FAILURE 
      else:
         break
      mycnt += 1

   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, "myupdt: {} record(s) updated to {}".format(ret, tablename))
   if(logact&PgLOG.ENDLCK):
      endtran()
   elif curtran:
      curtran += ret
      if curtran > MYDBI['MTRANS']: starttran()

   return ret

#
# update multiple records in tablename
# tablename: update for one table name each call
#   records: update values, dict with field names : value lists
#   cnddict: condition values, dict with field names : value lists
# return number of records updated upon success
#
def mymupdt(tablename, records, condhash, logact = 0):

   global curtran
   if not logact: logact = MYDBI['LOGACT']
   if not records: PgLOG.pglog("Nothing updates to " + tablename, logact)
   if not condhash or isinstance(condhash, int): PgLOG.pglog("Miss condition to update to " + tablename, logact)
   if logact&PgLOG.DODFLT: prepare_defaults(tablename, records, logact)

   fields = list(records)
   fldvals = tuple(records.values())
   cntrow = len(fldvals[0])
   cndflds = list(condhash)
   cndvals = tuple(condhash.values())
   count = len(cndvals[0])
   if count != cntrow: return PgLOG.pglog("Field/Condition value counts Miss match {}/{} to update {}".format(cntrow, count, tablename), logact)
   v = fldvals + cndvals
   values = tuple(zip(*v))

   sqlstr = prepare_update(tablename, fields, None, condhash)
   if PgLOG.PGLOG['DBGLEVEL']:
      for row in values: PgLOG.mydbg(1000, "Update {} for {}".format(tablename, row))

   count = mycnt = 0
   while True:
      mycur = mycursor()
      if not mycur: return PgLOG.FAILURE
      while count < cntrow:
         ncount = count + MYDBI['MTRANS']
         if ncount > cntrow: ncount = cntrow
         try:
            mycur.executemany(sqlstr, values[count:ncount])
            count = ncount
         except MySQL.Error as myerr:
            if not check_dberror(myerr, mycnt, sqlstr, values[0], logact): return PgLOG.FAILURE
            break
      if count >= cntrow: break
      mycnt += 1

   mycur.close()

   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, "mymupdt: {}/{} record(s) updated to {}".format(count, cntrow, tablename))
   if(logact&PgLOG.ENDLCK):
      endtran()
   elif curtran:
      curtran += count
      if curtran > MYDBI['MTRANS']: starttran()
   
   return count

#
# delete one or mutiple records in tablename according condition
# tablename: delete for one table name each call
# condition: delete conditions for where clause
# return number of records deleted upon success
#
def mydel(tablename, condition, logact = 0):

   global curtran
   if not logact: logact = MYDBI['LOGACT']
   if not condition: PgLOG.pglog("Miss condition to delete from " + tablename, logact)

   sqlstr = "DELETE FROM {} WHERE {}".format(tablename, condition)
   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(100, sqlstr)

   ret = mycnt = 0
   while True:
      mycur = mycursor()
      if not mycur: return PgLOG.FAILURE
      try:
         mycur.execute(sqlstr)
         ret = mycur.rowcount
         mycur.close()
      except MySQL.Error as myerr:
         if not check_dberror(myerr, mycnt, sqlstr, None, logact): return PgLOG.FAILURE 
      else:
         break
      mycnt += 1

   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, "mydel: {} record(s) deleted from {}".format(ret, tablename))
   if logact&PgLOG.ENDLCK:
      endtran()
   elif curtran:
      curtran += ret
      if curtran > MYDBI['MTRANS']: starttran()

   return ret

#
# sqlstr: a complete sql string
# return number of record affected upon success
#
def myexec(sqlstr, logact = 0):

   global curtran
   if not logact: logact = MYDBI['LOGACT']
   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(100, sqlstr)

   ret = mycnt = 0
   while True:
      mycur = mycursor()
      if not mycur: return PgLOG.FAILURE
      try:
         mycur.execute(sqlstr)
         ret = mycur.rowcount
         mycur.close()
      except MySQL.Error as myerr:
         if not check_dberror(myerr, mycnt, sqlstr, None, logact): return PgLOG.FAILURE 
      else:
         break
      mycnt += 1

   if PgLOG.PGLOG['DBGLEVEL']: PgLOG.mydbg(1000, "myexec: {} record(s) affected for {}".format(ret, sqlstr))
   if logact&PgLOG.ENDLCK:
      endtran()
   elif curtran:
      curtran += ret
      if curtran > MYDBI['MTRANS']: starttran()

   return ret

#
# tablename: one table name to a temporary table
# fromtable: table name data gathing from
#    fields: table name data gathing from
# condition: querry conditions for where clause
# return number of records created upon success
#
def mytemp(tablename, fromtable, fields, condition = None, logact = 0):

   sqlstr = "CREATE TEMPORARY TABLE {} SELECT {} FROM {}".format(tablename, fields, fromtable)
   if condition: sqlstr += " WHERE " + condition

   return myexec(sqlstr, logact)

#
# get condition for given table name for accessing information_schema
#
def table_condition(tablename):

   ms = re.match(r'(.+)\.(.+)', tablename)
   if ms:
      dbname = ms.group(1)
      tbname = ms.group(2)
   else:
      dbname = MYDBI['DBNAME']
      tbname = tablename

   return "TABLE_NAME = '{}' AND TABLE_SCHEMA = '{}'".format(tbname, dbname)

#
# check if a given table name exists or not
# tablename: one table name to check
#
def mycheck(tablename, logact = 0):

   condition = table_condition(tablename)

   ret = myget('information_schema.tables', None, condition, logact)
   return (PgLOG.SUCCESS if ret else PgLOG.FAILURE)

#
# group of functions to check parent records and add an empty one if missed 
# return user.uid upon success, 0 otherwise
#
def check_user_uid(userno, date = None):

   if not userno: return 0
   if type(userno) is str: userno = int(userno)
      
   if date is None:
      datecond = "until_date IS NULL"
      date = 'today'
   else:
      datecond = "(start_date IS NULL OR start_date <= '{}') AND (until_date IS NULL OR until_date >= '{}')".format(date, date)

   myrec = myget("user", "uid", "userno = {} AND {}".format(userno, datecond), MYDBI['LOGACT'])
   if myrec: return myrec['uid']

   if userno not in NMISSES:
      PgLOG.pglog("{}: Scientist ID NOT on file for {}".format(userno, date), PgLOG.LGWNEM)
      NMISSES.append(userno)

   # check again if a user is on file with different date range
   myrec = myget("user", "uid", "userno = {}".format(userno), MYDBI['LOGACT'])
   if myrec: return myrec['uid']

   myrec = ucar_user_info(userno)
   if not myrec: myrec = {'userno' : userno, 'stat_flag' : 'M'}
   uid = myadd("user", myrec, (MYDBI['LOGACT']|PgLOG.EXITLG|PgLOG.AUTOID))
   if uid: PgLOG.pglog("{}: Scientist ID Added as user.uid = {}".format(userno, uid), PgLOG.LGWNEM)

   return uid

# return user.uid upon success, 0 otherwise
def get_user_uid(logname, date = None):
   
   if not logname: return 0
   if not date:
      date = 'today'
      datecond = "until_date IS NULL"
   else:
      datecond = "(start_date IS NULL OR start_date <= '{}') AND (until_date IS NULL OR until_date >= '{}')".format(date, date)

   myrec = myget("user", "uid", "logname = '{}' AND {}".format(logname, datecond), MYDBI['LOGACT'])
   if myrec: return myrec['uid']
   
   if logname not in LMISSES:
      PgLOG.pglog("{}: UCAR Login Name NOT on file for {}".format(logname, date), PgLOG.LGWNEM)
      LMISSES.append(logname)

   # check again if a user is on file with different date range
   myrec = myget("user", "uid", "logname = '{}'".format(logname), MYDBI['LOGACT'])
   if myrec: return myrec['uid']

   myrec = ucar_user_info(0, logname)
   if not myrec: myrec = {'logname' : logname, 'stat_flag' : 'M'}
   uid = myadd("user", myrec, (MYDBI['LOGACT']|PgLOG.EXITLG|PgLOG.AUTOID))
   if uid: PgLOG.pglog("{}: UCAR Login Name Added as user.uid = {}".format(logname, uid), PgLOG.LGWNEM)

   return uid

#
# get ucar user info for given userno (scientist number) or logname (Ucar login)
#
def ucar_user_info(userno, logname = None):

   MATCH = {
      'upid' : "upid",
      'uid'  : "userno",
      'username' : "logname",
      'lastName' : "lstname",
      'firstName' : "fstname",
      'active' : "stat_flag",
      'internalOrg' : "division",
      'externalOrg' : "org_name",
      'country' : "country",
      'forwardEmail' : "email",
      'email' : "ucaremail",
      'phone' : "phoneno"
   }

   buf = PgLOG.pgsystem("pgperson " + ("-uid {}".format(userno) if userno else "-username {}".format(logname)), PgLOG.LOGWRN, 20)
   if not buf: return None

   myrec = {}
   for line in buf.split('\n'):
      ms = re.match(r'^(.+)<=>(.*)$', line)
      if ms:
         (key, val) = ms.groups()
         if key in MATCH: 
            if key == 'upid' and myrec: break  # get one record only
         myrec[MATCH[key]] = val

   if not myrec: return None

   if userno:
      myrec['userno'] = userno
   elif myrec['userno']:
      myrec['userno'] = userno = int(myrec['userno'])
   if myrec['upid']: myrec['upid'] = int(myrec['upid'])          
   if myrec['stat_flag']: myrec['stat_flag'] = 'A' if myrec['stat_flag'] == '1' else 'C'
   if myrec['email'] and re.search(r'\.ucar\.edu$', myrec['email']. re.I):
      myrec['email'] = myrec['ucaremail']
   myrec['country'] = set_country_code(myrec['email'], myrec['country'])
   if myrec['division']:
      val = "NCAR"
   else:
      val = None
   myrec['org_type'] = get_org_type(val, myrec['email'])

   buf = PgLOG.pgsystem("pgusername {}".format(myrec[logname]), PgLOG.LOGWRN, 20)
   if not buf: return myrec

   for line in buf.split('\n'):
      ms = re.match(r'^(.+)<=>(.*)$', line)
      if ms:
         (key, val) = ms.groups()
         if key == 'startDate':
            m = re.match(r'^(\d+-\d+-\d+)\s', val)
            if m:
               myrec['start_date'] = m.group(1)
            else:
               myrec['start_date'] = val

         if key == 'endDate':
            m = re.match(r'^(\d+-\d+-\d+)\s', val)
            if m:
               myrec['until_date'] = m.group(1)
            else:
               myrec['until_date'] = val

   return myrec

#
#  set country code for given coutry name or email address
#
def set_country_code(email, country = None):

   codes = {
      'CHINA'   : "P.R.CHINA",
      'ENGLAND' : "UNITED.KINGDOM",
      'FR'      : "FRANCE",
      'KOREA'   : "SOUTH.KOREA",
      'USSR'    : "RUSSIA",
      'US'      : "UNITED.STATES",
      'U.S.A.'  : "UNITED.STATES"
   }

   if country:
      country = country.upper()
      ms = re.match(r'^(\w+)\s(\w+)$', country)
      if ms:
         country = ms.group(1) + '.' + ms.group(2)
      elif country in codes:
         country = codes[country]
   else:
      country = email_to_country(email)

   return country

# return wuser.wuid upon success, 0 otherwise
def check_wuser_wuid(email, date = None):

   if not email: return 0
   emcond = "email = '{}'".format(email)
   if not date:
      date = 'today'
      datecond = "until_date IS NULL"
   else:
      datecond = "(start_date IS NULL OR start_date <= '{}') AND (until_date IS NULL OR until_date >= '{}')".format(date, date)

   myrec = myget("wuser", "wuid", "{} AND {}".format(emcond, datecond), MYDBI['LOGACT'])
   if myrec: return myrec['wuid']

   # check again if a user is on file with different date range
   myrec = myget("wuser", "wuid", emcond, PgLOG.LOGERR)
   if myrec: return myrec['wuid']

   # now add one in
   record = {'email' : email} 
   # check again if a ruser is on file
   myrec = myget("ruser", "*", emcond + " AND end_date IS NULL", MYDBI['LOGACT'])
   if not myrec: myrec = myget("ruser", "*", emcond, MYDBI['LOGACT'])

   if myrec:
      record['ruid'] = myrec['id']
      record['fstname'] = myrec['fname']
      record['lstname'] = myrec['lname']
      record['country'] = myrec['country']
      record['org_type'] = get_org_type(myrec['org_type'], myrec['email'])
      record['start_date'] = str(myrec['rdate'])
      if myrec['end_date']:
         record['until_date'] = str(myrec['end_date'])
         record['stat_flag'] = 'C'
      else:
         record['stat_flag'] = 'A'

      if myrec['title']: record['utitle'] = myrec['title']
      if myrec['mname']: record['midinit'] = myrec['mname'][0]
      if myrec['org']: record['org_name'] = myrec['org']
   else:
      record['stat_flag'] = 'M'
      record['org_type'] = get_org_type('', email)
      record['country'] = email_to_country(email)

   wuid = myadd("wuser", record, PgLOG.LOGERR|PgLOG.AUTOID)
   if wuid:
      if myrec:
         PgLOG.pglog("{}({}, {}) Added as wuid({})".format(email, myrec['lname'], myrec['fname'], wuid), PgLOG.LGWNEM)
      else:
         PgLOG.pglog("{} Added as wuid({})".format(email, wuid), PgLOG.LGWNEM)
      return wuid

   return 0

#
# for given email to get long country name
#
def email_to_country(email):
   
   ms = re.search(r'\.(\w\w)$', email)
   if ms:
      myrec = myget("countries", "token", "domain_id = '{}'".format(ms.group(1)), MYDBI['LOGACT']|PgLOG.EXITLG)
      if myrec: return myrec['token']
   elif re.search(r'\.(gov|edu|mil|org|com|net)$', email):
      return "UNITED.STATES"
   else:
      return "UNKNOWN"

#
# check wfile recursively to find the matching record
#
def check_wfile_recursive(wfile, dscond):

   myrec = myget("wfile", "*", "{} = '{}'".format(dscond, wfile), MYDBI['LOGACT'])
   if not myrec:
      if wfile.find('/') > -1:
         myrec = check_wfile_recursive(op.basename(wfile), dscond)
      else:
         myrec = myget("wfile", "*", "{} LIKE '%{}'".format(dscond, wfile), MYDBI['LOGATC'])

   return myrec

#
# if filelists is published for given dataset, reset it to 'P'
#
def reset_rdadb_version(dsid):

   myexec("UPDATE dataset SET version = version + 1 WHERE dsid = '{}'".format(dsid), MYDBI['LOGACT'])

#
# check the use rdadb flag in table dataset for a given dataset and given values
#
def use_rdadb(dsid, logact = 0, vals = None):

   ret = ''   # default to empty in case dataset not in RDADB
   if dsid:
      myrec = myget("dataset", "use_rdadb", "dsid = '{}'".format(dsid), MYDBI['LOGACT']|PgLOG.EXITLG)
      if myrec:
         ret = 'N'   # default to 'N' if dataset record in RDADB already
         if myrec['use_rdadb']:
            if not vals: vals = "IPYMW"  # default to Internal; Publishable; Yes RDADB
            if vals.find(myrec['use_rdadb']) > -1:
               ret = myrec['use_rdadb']
      elif logact:
         PgLOG.pglog("Dataset '{}' is not in RDADB!".format(dsid), logact)

   return ret

#
#   fld: field name for querry condition
#  vals: reference to aaray of values
# isstr: 1 for string values requires quotes and support wildcard
# noand: 1 for skiping the leading ' AND ' for condition
# return a condition string for a given field
#
def get_field_condition(fld, vals, isstr = 0, noand = 0):
   
   cnd = wcnd = negative = ''
   sign = "="
   logic = " OR "
   count =  len(vals) if vals else 0
   if count == 0: return ''
   ncnt = scnt = wcnt = cnt = 0
   for i in range(count):
      val = vals[i]
      if val is None or (i > 0 and val == vals[i-1]): continue      
      if i == 0 and val == MYSIGNS[0]:
         negative = "NOT "
         logic = " AND "
         continue
      if scnt == 0 and isinstance(val, str):
         ms = re.match(r'^({})$'.format('|'.join(MYSIGNS[1:])), val)
         if ms:
            osign = sign = ms.group(1)
            scnt += 1
            if sign == "<>":
               scnt += 1
               sign = negative + "BETWEEN"
            elif negative:
               sign = "<=" if (sign == ">") else ">="
            continue
      if isstr:
         if not isinstance(val, str): val = str(val)
         if sign == "=":
            if not val:
               ncnt += 1   # found null string
            elif val.find('%') > -1:
               sign = negative + "LIKE"
            elif re.search(r'[\[\(\?\.]', val):
               sign = negative + "REGEXP"
         if val.find("'") != 0:
            val = "'{}'".format(val)
      elif isinstance(val, str):
         if val.find('.') > -1:
            val = float(val)
         else:
            val = int(val)
      if sign == "=":
         if cnt > 0: cnd += ", "
         cnd += str(val)
         cnt += 1
      else:
         if sign == "AND":
            wcnd += " {} {}".format(sign, val)
         else:
            if wcnt > 0: wcnd += logic
            wcnd += "{} {} {}".format(fld, sign, val)
            wcnt += 1
         if re.search(r'BETWEEN$', sign):
            sign = "AND"
         else:
            sign = "="
            scnt = 0

   if scnt > 0:
      s = 's' if scnt > 1 else ''
      PgLOG.pglog("Need {} value{} after sign '{}'".format(scnt, s, osign), PgLOG.LGEREX)
   if wcnt > 1: wcnd = "({})".format(wcnd)
   if cnt > 0:
      if cnt > 1:
         cnd = "{} {}IN ({})".format(fld, negative, cnd)
      else:   
         cnd = "{} {} {}".format(fld, ("<>" if negative else "="), cnd)
      if ncnt > 0:
         ncnd = "{} IS {}NULL".format(fld, negative)
         cnd = "({}{}{})".format(cnd, logic, ncnd)
      if wcnt > 0: cnd = "({}{}{})".format(cnd, logic, wcnd)
   elif wcnt > 0:
      cnd = wcnd
   if cnd and not noand: cnd = " AND " + cnd

   return cnd

#
# build up fieldname string for given or default condition
#
def fieldname_string(fnames, dnames = None, anames = None, wflds = None):

   if not fnames:
      fnames = dnames   # include default fields names
   elif re.match(r'^all$', fnames, re.I):
      fnames = anames   # include all field names

   if not wflds: return fnames
   
   for wfld in wflds:
      if not wfld or fnames.find(wfld) > -1: continue  # empty field, or included already
      if wfld == "Q":
         pos = fnames.find("R")   # request name
      elif wfld == "Y":
         pos = fnames.find("X")   # parent group name
      elif wfld == "G":
         pos = fnames.find("I")   # group name
      else:
         pos = -1   # prepend other with-field names

      if pos == -1:
         fnames = wfld + fnames   # prepend with-field
      else:
         fnames = fnames[0:pos] + wfld + fnames[pos:]   # insert with-field

   return fnames

#
# Function get_group_field_path(gindex: group index
#                                 dsid: dataset id
#                                field: path field name: webpath or savedpath)
# go through group tree upward to find a none-empty path, return it or null
# 
def get_group_field_path(gindex, dsid, field):

   if gindex:
      myrec = myget("dsgroup", "pindex, {}".format(field),
                     "dsid = '{}' AND gindex = {}".format(dsid, gindex), MYDBI['LOGACT']|PgLOG.EXITLG)
   else:
      myrec = myget("dataset", field,
                     "dsid = '{}'".format(dsid), MYDBI['LOGACT']|PgLOG.EXITLG)
   if myrec:
      if myrec[field]:
         return myrec[field]
      elif gindex:
         return get_group_field_path(myrec['pindex'], dsid, field)
   else:
      return None

#
# get the specialist info for a given dataset
#
def get_specialist(dsid, logact = 0):

   if not logact: logact = MYDBI['LOGACT']
   if dsid in SPECIALIST: return SPECIALIST['dsid']

   myrec = myget("dsowner, dssgrp", "specialist, lstname, fstname",
                 "specialist = logname AND dsid = '{}' AND priority = 1".format(dsid), logact)
   if myrec:
      if myrec['specialist'] == "datahelp" or myrec['specialist'] == "dss":
         myrec['lstname'] = "Help"
         myrec['fstname'] = "Data"
   else:
      myrec['specialist'] = "datahelp"
      myrec['lstname'] = "Help"
      myrec['fstname'] = "Data"

   SPECIALIST['dsid'] = myrec  # cache specialist info for dsowner of dsid
   return myrec

#
#  build customized email from get_email()
#
def build_customized_email(table, field, condition, subject, logact = 0):

   msg = PgLOG.get_email()
   
   if not msg: return PgLOG.FAILURE
   
   sender = PgLOG.PGLOG['CURUID'] + "@ucar.edu"
   receiver = PgLOG.PGLOG['EMLADDR'] if PgLOG.PGLOG['EMLADDR'] else (PgLOG.PGLOG['CURUID'] + "@ucar.edu")
   if receiver.find(sender) < 0: PgLOG.add_carbon_copy(sender, 1)
   ebuf = "From: {}\nTo: {}\n".format(sender, receiver)
   if PgLOG.PGLOG['CCDADDR']: ebuf += "Cc: {}\n".format(PgLOG.PGLOG['CCDADDR']) 
   if not subject: subject = "Message from {}-{}".format(PgLOG.PGLOG['HOSTNAME'], PgLOG.get_command())
   ebuf += "Subject: {}!\n\n{}\n".format(subject, msg)

   estat = cache_customized_email(table, field, condition, ebuf, logact)
   if estat and logact:
      PgLOG.pglog("Email {} cached to '{}.{}' for {}, Subject: {}".format(receiver, table, field, condition, subject), logact)

   return estat

#
# email: full user email address
#
# get user real name from table ruser for a given email address
# opts == 1 : include email
# opts == 2 : include org_type
# opts == 4 : include country
# opts == 8 : include valid_email
# opts == 16 : include org
#
def get_ruser_names(email, opts = 0, date = None):

   fields = "lname lstname, fname fstname"

   if opts is None: opts = 0   
   if opts&1: fields += ", email"
   if opts&2: fields += ", org_type"
   if opts&4: fields += ", country"
   if opts&8: fields += ", valid_email"
   if opts&16: fields += ", org"

   if date:
      datecond = "rdate <= '{}' AND (end_date IS NULL OR end_date >= '{}')".format(date, date)
   else:
      datecond = "end_date IS NULL"
      date = time.strftime("%Y-%m-%d", (time.gmtime() if PgLOG.PGLOG['GMTZ'] else time.localtime()))
   emcnd = "email = '{}'".format(email)
   myrec = myget("ruser", fields, "{} AND {}".format(emcnd, datecond), PgLOG.LGEREX)
   if not myrec:   # missing user record add one in
      PgLOG.pglog("{}: email not in ruser for {}".format(email, date), PgLOG.LOGWRN)
      # check again if a user is on file with different date range
      myrec = myget("ruser", fields, emcnd, PgLOG.LGEREX)
      if not myrec and myget("user", '', emcnd):
         fields = "lstname, fstname"
         if opts&1: fields += ", email"
         if opts&2: fields += ", org_type"
         if opts&4: fields += ", country"
         if opts&8: fields += ", email valid_email"
         if opts&16: fields += ", org_name org"
         myrec = myget("user", fields, emcnd, PgLOG.LGEREX)

   if myrec and myrec['lstname']:
      myrec['name'] = (myrec['fstname'].capitalize() + ' ') if myrec['fstname'] else ''
      myrec['name'] += myrec['lstname'].capitalize()
   else:
      if not myrec: myrec = {}
      myrec['name'] = email.split('@')[0]
      if opts&1: myrec['email'] = email

   return myrec

#
# cache a customized email for sending it later
#
def cache_customized_email(table, field, condition, emlmsg, logact = 0):

   myrec = {field : emlmsg}
   if myupdt(table, myrec, condition, logact|PgLOG.ERRLOG):
      if logact: PgLOG.pglog("Email cached to '{}.{}' for {}".format(table, field, condition), logact&(~PgLOG.EXITLG))
      return PgLOG.SUCCESS
   else:
      msg = "cache email to '{}.{}' for {}".format(table, field, condition)
      PgLOG.pglog("Error {}, try to send directly now".format(msg), logact|PgLOG.ERRLOG)
      return PgLOG.send_customized_email(msg, emlmsg, logact)

#
# otype: user organization type
# email: user email address)
#
# return: orgonizaion type like DSS, NCAR, UNIV...
#
def get_org_type(otype, email):

   if not otype: otype = "OTHER"
   if email:
      ms = re.search(r'(@|\.)ucar\.edu$', email)
      if ms:
         mc = ms.group(1)
         if otype == 'UCAR' or otype == 'OTHER': otype = 'NCAR'
         if otype == 'NCAR' and mc == '@':
            ms = re.match(r'^(.+)@', email)
            if ms and myget("dssgrp", "", "logname = '{}'".format(ms.group(1))): otype = 'DECS'
      else:
         ms = re.search(r'\.(mil|org|gov|edu|com|net)(\.\w\w|$)', email)
         if ms:
            otype = ms.group(1).upper()
            if otype == 'EDU': otype = "UNIV"

   return otype

#
# join values and handle the null values
#
def join_values(vstr, vals):

   if vstr:
      vstr += "\n"
   elif vstr is None:
      vstr = ''

   return "{}Value{}({})".format(vstr, ('s' if len(vals) > 1 else ''), ', '.join(map(str, vals)))

#
#  check table hostname to find the system down times. Cache the result for 10 minutes
#
def get_system_downs(hostname, logact = 0):

   curtime = int(time.time())
   newhost = 0

   if hostname not in SYSDOWN:
      SYSDOWN[hostname] = {}
      newhost = 1
   if newhost or (curtime - SYSDOWN[hostname]['chktime']) > 600:
      SYSDOWN[hostname]['chktime'] = curtime
      SYSDOWN[hostname]['start'] = 0
      SYSDOWN[hostname]['end'] = 0
      SYSDOWN[hostname]['active'] = 1
      SYSDOWN[hostname]['path'] = None

      myrec = myget('hostname', 'service, domain, UNIX_TIMESTAMP(downstart) start, UNIX_TIMESTAMP(downend) end',
                    "hostname = '{}'".format(hostname), logact)
      if myrec:
         if myrec['service'] == 'N':
            SYSDOWN[hostname]['start'] = curtime
            SYSDOWN[hostname]['active'] = 0
         else:
            start = myrec['start']
            end = myrec['end']
            if start and (not end or end > curtime):
               SYSDOWN[hostname]['start'] = start
               SYSDOWN[hostname]['end'] = end if end else None
            if myrec['service'] == 'S' and myrec['domain'] and re.match(r'^/', myrec['domain']):
               SYSDOWN[hostname]['path'] = myrec['domain']

   SYSDOWN[hostname]['curtime'] = curtime

   return SYSDOWN[hostname]

#
# return seconds for how long the system will continue to be down
#
def system_down_time(hostname, offset, logact = 0):

   down = get_system_downs(hostname, logact)
   if down['start'] and down['curtime'] >= (down['start'] - offset):
      if not down['end']:
         if PgLOG.PGLOG['MYBATCH'] == PgLOG.PGLOG['PBSNAME']:
            return PgLOG.PGLOG['PBSTIME']
         elif PgLOG.PGLOG['MYBATCH'] == PgLOG.PGLOG['SLMNAME']:
            return PgLOG.PGLOG['SLMTIME']
      elif down['curtime'] <= down['end']:
         return (down['end'] - down['curtime'])

   return 0  # the system is not down

#
# return string message if the system is down
#
def system_down_message(hostname, path, offset, logact = 0):

   down = get_system_downs(hostname, logact)
   msg = None
   if down['start'] and down['curtime'] >= (down['start'] - offset):
      match = match_down_path(path, down['path'])
      if match:
         msg = "{}{}:".format(hostname, ('-' + path) if match > 0 else '')
         if not down['active']:
            msg += " Not in Service"
         else:
            msg += " Planned down, started at " + PgLOG.current_datetime(down['start'])
            if not down['end']:
               msg += " And no end time specified"
            elif down['curtime'] <= down['end']:
               msg = " And will end by " + PgLOG.current_datetime(down['end'])

   return msg

#
# return 1 if given path match daemon paths, 0 if not; -1 if cannot compare
#
def match_down_path(path, dpaths):

   if not (path and dpaths): return -1

   paths = re.split(':', dpaths)

   for p in paths:
      if re.match(r'^{}'.format(p), path): return 1

   return 0

# validate is login user is in DECS group
# check all node if skpdsg is false, otherwise check non-DSG nodes
def validate_decs_group(cmdname, logname, skpdsg):
   
   if skpdsg and PgLOG.PGLOG['DSGHOSTS'] and re.search(r'(^|:){}'.format(PgLOG.PGLOG['HOSTNAME']), PgLOG.PGLOG['DSGHOSTS']): return
   if not logname: lgname = PgLOG.PGLOG['CURUID']

   if not myget("dssgrp", '', "logname = '{}'".format(logname), PgLOG.LGEREX):
      PgLOG.pglog("{}: Must be in DECS Group to run '{}' on {}".format(logname, cmdname, PgLOG.PGLOG['HOSTNAME']), PgLOG.LGEREX)

#
# add an allusage record into yearly table; create a new yearly table if it does not exist
# year    -- year to identify the yearly table, evaluated if missing 
# records -- hash to hold one or multiple records.
# Dict keys: email -- user email address,
#         org_type -- organization type
#          country -- country code
#             dsid -- dataset ID 
#             date -- date data accessed
#             time -- time data accessed
#          quarter -- quarter of the year data accessed
#             size -- bytes of data accessed
#           method -- delivery methods: MSS,Web,Ftp,Tape,Cd,Disk,Paper,cArt,Micro
#           source -- usage source flag: W - wusage, O - ordusage
#             midx -- refer to mbr2loc.midx if not 0
#               ip -- user IP address
#           region -- user region name; for example, Colorado
#
# isarray -- if true, mutiple records provided via arrays for each hash key 
# docheck -- if 1, check and add only if record is not on file
# docheck -- if 2, check and add if record is not on file, and update if exists
# docheck -- if 4, check and add if record is not on file, and update if exists,
#            and also checking NULL email value too 
#
def add_yearly_allusage(year, records, isarray = 0, docheck = 0):

   acnt = 0
   if not year:
      ms = re.match(r'^(\d\d\d\d)', str(records['date'][0] if isarray else records['date']))
      if ms: year = ms.group(1)
   tname = "allusage_{}".format(year)
   if isarray:
      cnt = len(records['email'])
      if 'quarter' not in records: records['quarter'] = [0]*cnt
      for i in range(cnt):
         if not records['quarter'][i]:
            ms = re.search(r'-(\d+)-', str(records['date'][i]))
            if ms: records['quarter'][i] = int((int(ms.group(1))-1)/3)+1
      if docheck:
         for i in range(cnt):
            record = {}
            for key in records:
               record[key] = records[key][i]
            cnd = "email = '{}' AND dsid = '{}' AND method = '{}' AND date = '{}' AND time = '{}'".format(
                   record['email'], record['dsid'], record['method'], record['date'], record['time'])
            myrec = myget(tname, 'aidx', cnd, PgLOG.LOGERR|PgLOG.ADDTBL)
            if docheck == 4 and not myrec:
               cnd = "email IS NULL AND dsid = '{}' AND method = '{}' AND date = '{}' AND time = '{}'".format(
                      record['dsid'], record['method'], record['date'], record['time'])
               myrec = myget(tname, 'aidx', cnd, PgLOG.LOGERR|PgLOG.ADDTBL)
            if myrec:
               if docheck > 1: acnt += myupdt(tname, record, "aidx = {}".format(myrec['aidx']), PgLOG.LGEREX)
            else:
               acnt += myadd(tname, record, PgLOG.LGEREX|PgLOG.ADDTBL)
      else:
         acnt = mymadd(tname, records, PgLOG.LGEREX|PgLOG.ADDTBL)
   else:
      record = records
      if not ('quarter' in record and record['quarter']):
         ms = re.search(r'-(\d+)-', str(record['date']))
         if ms: record['quarter'] = int((int(ms.group(1))-1)/3)+1
      if docheck:
         cnd = "email = '{}' AND dsid = '{}' AND method = '{}' AND date = '{}' AND time = '{}'".format(
                record['email'], record['dsid'], record['method'], record['date'], record['time'])
         myrec = myget(tname, 'aidx', cnd, PgLOG.LOGERR|PgLOG.ADDTBL)
         if docheck == 4 and not myrec:
            cnd = "email IS NULL AND dsid = '{}' AND method = '{}' AND date = '{}' AND time = '{}'".format(
                   record['dsid'], record['method'], record['date'], record['time'])
            myrec = myget(tname, 'aidx', cnd, PgLOG.LOGERR|PgLOG.ADDTBL)
         if myrec:
            if docheck > 1: acnt = myupdt(tname, record, "aidx = {}".format(myrec['aidx']), PgLOG.LGEREX)
            return acnt
      acnt = myadd(tname, record, PgLOG.LGEREX|PgLOG.ADDTBL)

   return acnt

#
# add a wusage record into yearly table; create a new yearly table if it does not exist
# year    -- year to identify the yearly table, evaluated if missing 
# records -- hash to hold one or multiple records.
# Dict keys: wid - reference to wfile.wid
#      wuid_read - reference to wuser.wuid, 0 if missing email
#           dsid - reference to dataset.dsid at the time of read
#      date_read - date file read
#      time_read - time file read
#        quarter - quarter of the year data accessed
#      size_read - bytes of data read
#         method - download methods: WEB, CURL, MGET, FTP and MGET
#        locflag - location flag: Glade or Object
#             ip - IP address
#
# isarray -- if true, mutiple records provided via arrays for each hash key 
#
def add_yearly_wusage(year, records, isarray = 0):

   acnt = 0
   if not year:
      ms = re.match(r'^(\d\d\d\d)', str(records['date_read'][0] if isarray else records['date_read']))
      if ms: year = ms.group(1)
   tname = "wusage_{}".format(year)
   if isarray:
      if 'quarter' not in records:
         cnt = len(records['wid'])
         records['quarter'] = [0]*cnt
         for i in range(cnt):
            ms = re.search(r'-(\d+)-', str(records['date_read'][i]))
            if ms: records['quarter'][i] = (int((int(ms.group(1))-1)/3)+1)
      acnt = mymadd(tname, records, PgLOG.LGEREX|PgLOG.ADDTBL)
   else:
      record = records
      if 'quarter' not in record:
         ms = re.search(r'-(\d+)-', str(record['date_read']))
         if ms: record['quarter'] = (int((int(ms.group(1))-1)/3)+1)
      acnt = myadd(tname, record, PgLOG.LGEREX|PgLOG.ADDTBL)

   return acnt
