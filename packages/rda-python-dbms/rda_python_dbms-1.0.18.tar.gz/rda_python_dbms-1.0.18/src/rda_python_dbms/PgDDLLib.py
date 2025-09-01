#
###############################################################################
#
#     Title : PgDDLLib.py  -- Data Definition Language of manipulating tables
#    Author : Zaihua Ji,  zji@ucar.edu
#      Date : 09/17/2020
#             2025-04-04 transferred to package rda_python_dbms from
#             https://github.com/NCAR/rda-shared-libraries.git
#   Purpose : python library module to create and process sql codes to add,
#             delete and modify table structures. All subroutines will exit on
#             errors
#
#    Github : https://github.com/NCAR/rda-shared-dbms.git
#
###############################################################################

import os
import re
import json
from os import path as op
from rda_python_common import PgDBI
from rda_python_common import PgLOG
from rda_python_common import PgUtil
from rda_python_common import PgFile

DBINFO = {
   'dbname' : "",
   'scname' : "",
   'lnname' : "",
   'pwname' : "",
   'dbhost' : "",
   'dbport' : 0
}

TABLES = {}
PGDDL = {
   'TBPATH' : PgLOG.join_paths(op.dirname(op.abspath(__file__)), "tables"),
   'suffix' : [],
   'prefix' : [],
   'override' : False,
   'usefile' : False,
   'mysqldb' : False,       # True to get mysql table info
   'username' : PgLOG.PGLOG['CURUID']
}

NEWTABLE = False

# 
# retrieve table data definition in a .tb or .json file
#
def get_table_def(tbfile, tablename, prefix, suffix, ext, scname):

   tbname = tablename
   # add prefix/suffix if not yet
   if prefix:
      if not re.match(r'^{}_'.format(prefix), tbname):
         tbname = prefix + '_' + tbname
      else:
         prefix = None
   if suffix:
      if not re.search(r'_{}$'.format(suffix), tbname):
         tbname += '_' + suffix
      else:
         suffix = None
   if tablename in TABLES:
      table = TABLES[tablename]
      if prefix or suffix: table['name'] = tbname
      return table


   curtag = None   # 'database', 'schema', 'desc' => 'comment', 'column', 'index', 'ref'
   dbname = None

   tf = open(tbfile)
   if ext == 'json':
      table = json.load(tf)
      if 'database' in table and not DBINFO['dbname']: dbname = table['database']
      if 'schema' in table and not (scname or DBINFO['scname']): scname = table['schema']
      validate_unique_keys(table)
   else:
      table = {'name' : tbname, 'column' : []}
      trimopt = 0
      curhead = None
      while True:
         line = tf.readline()
         if not line: break
         line = PgLOG.pgtrim(line, trimopt)
         if not line: continue   # empty or comment only line, skip it
         if trimopt == 0:
            if line[0] == '#':
               ms = re.match(r'^#\s*(\w+):\s+(\S.*)$', line)
               if ms:
                  curhead = ms.group(1).lower()
                  if 'header' not in table: table['header'] = {}
                  table['header'][curhead] = ms.group(2)
               elif curhead:
                  if len(line) == 1:
                     curhead = None
                  else:
                     ms = re.match(r'^#\s*(\S.*)$', line)
                     if ms: table['header'][curhead] += ' ' + ms.group(1)
               continue
            trimopt = 1

         ms = re.match(r'^<(.+)>', line)
         if ms:
            curtag = ms.group(1)   # begin/end tag found
            if curtag[0] == '/': curtag = None
            continue

         if not curtag: continue   # no tag defined, skip line
   
         # process for curtag
         if curtag == 'desc':         # get table comment
            table['comment'] = line
         elif curtag == 'database' or curtag == 'schema':
            table['schema'] = line
            if not (scname or DBINFO['dbname']): scname = table['schema']
         elif curtag == 'field':
            parse_column(table, line)
         elif curtag == 'index':
            parse_index(table, line)
         elif curtag == 'ref':
            parse_reference(table, line)
   tf.close()

   if dbname or scname:
      if not dbname: dbname = DBINFO['dbname']
      if not scname: scname = DBINFO['scname']
      PgDBI.default_scinfo(dbname, scname, DBINFO['dbhost'], DBINFO['lnname'],
                           DBINFO['pwname'], DBINFO['dbport'])

   if prefix or suffix:
      otname = table['name']
      table['name'] = tbname
      if 'index' in table:
         for index in table['index']:
            idxname = index['name']
            if tbname not in idxname and otname in idxname:
               index['name'] = idxname.replace(otname, tbname)
      if 'ref' in table:
         for ref in table['ref']:
            refname = ref['name']
            if tbname not in refname and otname in refname:
               ref['name'] = refname.replace(otname, tbname)
      if 'unique' in table:
         for unique in table['unique']:
            unqname = unique['name']
            if tbname not in unqname and otname in unqname:
               unique['name'] = unqname.replace(otname, tbname)
   table['database'] = PgDBI.PGDBI['DBNAME']
   table['schema'] = PgDBI.PGDBI['SCNAME']

   TABLES[tablename] = table

   return table

#
# retrieve table info db server
#
def get_table_description(tablename, prefix, suffix):

   tbname = tablename
   # remove prefix/suffix if in 
   if prefix and re.match(r'^{}_'.format(prefix), tbname):
      tbname = re.sub(r'^{}_'.format(prefix), '', tbname)
   if suffix and re.search(r'_{}$'.format(suffix), tbname):
      tbname = re.sub(r'_{}$'.format(suffix), '', tbname)

   if PGDDL['mysqldb']:
      return get_mysql_description(tablename, tbname)
   else:
      return get_postgresql_description(tablename, tbname)

#
# get mysql table description
#
def get_mysql_description(otname, tbname):

   table = {'database' : PgDBI.PGDBI['DBNAME'], 'schema' : PgDBI.PGDBI['SCNAME'],
            'name' : tbname, 'column' : []}

   cmd = "echo 'show create table `{}`' | mysql -h {} ".format(otname, PgDBI.PGDBI['DBHOST'])
   if PgDBI.PGDBI['DBPORT']: cmd += "-P {} ".format(PgDBI.PGDBI['DBPORT'])
   cmd += "-u {} -p{} {}".format(PgDBI.PGDBI['LNNAME'], PgDBI.PGDBI['PWNAME'], PgDBI.PGDBI['SCNAME'])
   PgLOG.PGLOG['ERR2STD'] = ['Using a password on the command line']
   buf = PgLOG.pgsystem(cmd, PgLOG.LOGWRN, 20)
   PgLOG.PGLOG['ERR2STD'] = []
   lines = re.split(r'\\n\s*', buf)
   if len(lines) < 3:
      PgLOG.pglog("{}: Fail to get create table info".format(otname), PgLOG.LGEREX)
   lines.pop(0)
   line = lines.pop()
   ms = re.search(r" COMMENT='([^']+)'$", line)
   if ms: table['comment'] = ms.group(1).replace('"', '\\"')
   
   for line in lines:
      line = line.replace('`', '')
      if line[-1] == ',': line = line[:-1]
      ms = re.match(r'^PRIMARY KEY \((\w.*\w)\)', line)
      if ms:
         table['pkey'] = ms.group(1)
         continue
      ms = re.match(r'^FOREIGN KEY (\w.*\w)\((\w.*\w)\) REFERENCES (\w.*\w)\((\w.*\w)\)$', line)
      if ms:
         refname = ms.group(1)
         ref = {'name' : refname, 'column' : ms.group(2),
                'rtable' : ms.group(3), 'rcolumn' : ms.group(4)}
         if tbname != otname and otname in refname:
            ref['name'] = refname.replace(otname, tbname)
         elif tbname not in refname:
            ref['name'] = '{}_{}'.format(tbname, refname)
         if 'ref' not in table: table['ref'] = []
         table['ref'].append(ref)
         continue
      ms = re.match(r'^(UNIQUE |)KEY (\w.*\w) \((\w.*)\)', line)
      if ms:
         idxname = ms.group(2)
         index = {'name' : idxname, 'column' : ms.group(3)}
         if ms.group(1): index['unique'] = 'UNIQUE'
         if tbname != otname and otname in idxname:
            index['name'] = idxname.replace(otname, tbname)
         elif tbname not in idxname:
            index['name'] = '{}_{}'.format(tbname, idxname)
         if 'index' not in table: table['index'] = []
         table['index'].append(index)
         continue
      column = {'name' : ''}
      ms = re.match(r"^(.*) COMMENT '([^']+)'$", line)
      if ms:
         column['comment'] = ms.group(2).replace('"', '\\"')
         line = ms.group(1)
      ms = re.match(r"^(\S+)(.*)$", line)
      if ms:
         column['name'] = ms.group(1)
         line = ms.group(2)
      ms = re.match(r"^\s*(\S+)(.*)$", line)
      if ms:
         type = ms.group(1)
         line = ms.group(2)
         unsigned = isint = False
         ms = re.match(r"^\s*unsigned(.*)$", line)
         if ms:
            line = ms.group(1)
            unsigned = True
         ms = re.match(r'^\s*(\w*)int$', type)
         if ms:
            pint = ms.group(1)
            isint = True
            ms = re.match(r"^\s*(\S.*\S) AUTO_INCREMENT$", line)
            if ms:
               line = ms.group(1)
               sint = 'serial'
            else:
               sint = 'int'
            if pint == 'tiny':
               pint = 'small'
            elif pint == 'medium':
               pint = ''
            elif pint == 'small':
               if unsigned: pint = ''
            elif not pint:
               if unsigned: pint = 'big'
            type = pint + sint
         elif re.match(r'^varchar', type):
            ms = re.match(r"^CHARACTER SET latin1 COLLATE latin1_bin (\S.*\S)$", line)
            if ms: line = ms.group(1)
         elif re.match(r'^(medium|long)text', type):
            type = 'text'
         elif re.match(r'^float($|\()', type):
            type = 'double precision'
         column['type'] = type
      ms = re.match(r"^\s*NOT NULL(.*)$", line)
      if ms:
         column['notnull'] = 'NOT NULL'
         line = ms.group(1)
      ms = re.match(r"^\s*DEFAULT ('.*'|\d+|NULL)(.*)$", line)
      if ms:
         column['default'] = PgDBI.check_default_value(ms.group(1), isint)
         line = ms.group(2)
      if line: PgLOG.pglog("{}: Unknown Column {} info".format(line, column['name']), PgLOG.LGEREX)
      table['column'].append(column)

   return table

#
# get postgresql table description
#
def get_postgresql_description(otname, tbname):

   table = {'database' : PgDBI.PGDBI['DBNAME'], 'schema' : PgDBI.PGDBI['SCNAME'],
            'name' : tbname, 'column' : []}

   cmd = "psql {} -h {} -U {} -c".format(PgDBI.PGDBI['DBNAME'], PgDBI.PGDBI['DBHOST'], PgDBI.PGDBI['LNNAME'])
   tablename = "{}.{}".format(PgDBI.pgname(PgDBI.PGDBI['SCNAME']), PgDBI.pgname(otname))

   cmt = pg_table_comment(cmd, tablename)
   if cmt: table['comment'] = cmt

   buf = PgLOG.pgsystem("{} '\d+ {}'".format(cmd, tablename), PgLOG.LOGWRN, 21)
   lines = buf.split('\n')
   if len(lines) < 4: PgLOG.pglog("{}: Fail \d+".format(tablename), PgLOG.LGEREX)
   lines = lines[3:]
   getidx = getfky = 0
   getcol = 1
   for line in lines:
      ms = re.match('^\s+(\S.*\S)\s*$', line)
      if ms: line = ms.group(1)
      if getcol:
         cols = re.split(r'\s*\|\s*', line)
         clen = len(cols)
         if clen > 7:
            column = {'name' : cols[0]}
            cmt = cols[7] if clen == 8 else '|'.join(cols[7:])
            if cmt: column['comment'] = cmt
            if cols[3] == 'not null': column['notnull'] = 'NOT NULL'
            dflt = cols[4]
            type = cols[1]
            isint = False
            ms = re.match(r'^character\s*(\w*)\((\d+)\)$', type)
            if ms:
               type = '{}char({})'.format(('var' if ms.group(1) == 'varying' else ''), ms.group(2))
            else:
               ms = re.match(r'^(\w*)int(eger)*$', type)
               if ms:
                  pint = ms.group(1)
                  isint = True
                  if dflt and re.match(r'^nextval\(', dflt):
                     sint = 'serial'
                     dflt = None
                  else:
                     sint = 'int'
                  type = pint + sint
            column['type'] = type
            if dflt is not None: column['default'] = PgDBI.check_default_value(dflt, isint)
            table['column'].append(column)
            continue
      getcol = 0
      
      if getidx:
         ms = re.match(r'^"(\S+)" (PRIMARY KEY|UNIQUE|)(, |)\w.*\w \((\w.*\w)\)$', line)
         if ms:
            idxname = ms.group(1)
            type = ms.group(2)
            column = ms.group(4)
            if type == 'PRIMARY KEY':
               table['pkey'] = column
            else:
               index = {'name' : idxname, 'column' : column}
               if type == 'UNIQUE': index['unique' : 'UNIQUE']
               if tbname != otname and otname in idxname:
                  index['name'] = idxname.replace(otname, tbname)
               elif tbname not in idxname:
                  index['name'] = '{}_{}'.format(tbname, idxname)
               if 'index' not in table: table['index'] = []
               table['index'].append(index)
            continue
         getidx = 0

      if getfky:
         ms = re.match(r'^"(\w.*\w)" FOREIGN KEY \((\w.*\w)\) REFERENCES (\w.*\w)\((\w.*\w)\)', line)
         if ms:
            refname = ms.group(1)
            ref = {'name' : refname, 'column' : ms.group(2),
                   'rtable' : ms.group(3), 'rcolumn' : ms.group(4)}
            if tbname != otname and otname in refname:
               ref['name'] = refname.replace(otname, tbname)
            elif tbname not in refname:
               ref['name'] = '{}_{}'.format(tbname, refname)
            if 'ref' not in table: table['ref'] = []
            table['ref'].append(ref)
            continue
         getfky = 0
         
      if line == 'Indexes:':
         getidx = 1
      elif line == 'Foreign-key constraints:':
         getfky = 1

   return table

#
# get postgresql table description
#
def pg_table_comment(cmd, tablename):

   buf = PgLOG.pgsystem("{} '\dt+ {}'".format(cmd, tablename), PgLOG.LOGWRN, 21)
   lines = buf.split('\n')
   if len(lines) < 4: PgLOG.pglog("{}: Fail \dt+".format(tablename), PgLOG.LGEREX)
   line = lines.pop()
   cols = re.split(r'\s*\|\s*', line)
   clen = len(cols)
   return cols[7] if clen == 8 else ('|'.join(cols[7:]) if clen > 8 else None)

#
# parsing a line to get column info
#
def parse_column(table, line):

   column = {}
   ms = re.search(r'^(\S.*\S)\s+%(.*)$', line)
   if ms:
      column['comment'] = ms.group(2)    # set column comment
      line = ms.group(1)                # remove column comment from line

   # check if string default value exists
   dflt = None
   ms = re.search(r'^(\S.*\S)\s+"(.*)"$', line)
   if ms:
      dflt = "'{}'".format(ms.group(2))        # record string default value
      line = ms.group(1)

   items = re.split(r'\s+', line)
   ilen = len(items)
   if ilen < 2: PgLOG.pglog("{}: {}, insufficient".format(table['name'], line), PgLOG.LGWNEX)
   column['name'] = items[0];                  # set column name
   column['type'] = items[1].lower()     # set column type

   isint = False
   sint = None
   ms = re.match(r'^(\w*)int$', column['type'])
   if ms:
      pint = ms.group(1)
      sint = 'int'
      isint = True

   unsigned = False
   pkey = None
   unique = {}
   if ilen > 2:     # additional options
      if re.search(r'N', items[2], re.I): column['notnull'] = 'NOT NULL'      # column is not NULL
      if re.search(r'S', items[2], re.I): unsigned = True      # column is UNSIGNED
      if re.search(r'A', items[2], re.I):
         if not sint: PgLOG.pglog(line + ": Wrong SERIAL Type", PgLOG.LGWNEX)
         sint = 'serial'
         pkey = column['name']
         column['pkey'] = 'PRIMARY KEY'
      elif re.search(r'P', items[2], re.I):
         pkey = column['name']
         column['pkey'] = 'PRIMARY KEY'
      if re.search(r'U', items[2], re.I):
         unique['name'] = '{}_{}'.format(table['name'], column['name'])
         unique['column'] = column['name']
         column['unique'] = 'UNIQUE'
      if re.search(r'D', items[2], re.I):   # column has default value
         if ilen > 3: dflt = items[3]

   if isint:
      if pint == 'tiny':
         pint = 'small'
      elif pint == 'medium':
         pint = '' 
      elif pint == 'small':
         if unsigned: pint = ''
      elif not pint:
         if unsigned: pint = 'big'
      column['type'] = pint + sint
   elif column['type'] == 'datetime':
      column['type'] = 'timestamp'
   if dflt is not None: column['default'] = PgDBI.check_default_value(dflt, isint)

   if pkey:
      if 'pkey' not in table:
         table['pkey'] = pkey
      elif pkey not in table['pkey']:
         table['pkey'] += ', ' + pkey
   if unique:
      if 'unique' not in table: table['unique'] = []
      table['unique'].append(unique)
   if 'column' not in table: table['column'] = []
   table['column'].append(column)

#
# validate primay and unique keys
#
def validate_unique_keys(table):

   for column in table['column']:
      pkey = None
      unique = {}
      if 'pkey' in column:
         pkey = column['name']
         if 'pkey' not in table:
            table['pkey'] = pkey
         elif pkey not in table['pkey']:
            table['pkey'] += ', ' + pkey
      if 'unique' in column:
         unique['name'] = '{}_{}'.format(table['name'], column['name'])
         unique['column'] = column['name']
         if 'unique' not in table:
            table['unique'] = [unique]
         else:
            for unq in table['unique']:
               if unique['name'] == unq['name'] or unique['column'] == unq['column']: continue
               table['unique'].append(unique)

#
# parsing a line to get index info  
#
def parse_index(table, line):

   index = {}

   ms = re.search(r'^(\S+)\s+\((.*)\)\s*(U*)', line, re.I)
   if ms:
      iname = ms.group(1)
      index['column'] = ms.group(2)
      unique = ms.group(3)
   else:
      PgLOG.pglog("{}: {}, insufficient index info".format(table['name'], line), PgLOG.LGWNEX)

   if re.match(r'^\d+$', iname):
      index['name'] = "{}_idx_{}".format(table['name'], iname)     # set index name
   else:
      index['name'] = iname
      
   if unique: index['unique'] = 'UNIQUE'

   if 'index' not in table: table['index'] = []
   table['index'].append(index)

#
# parsing a line to get ref info
#
def parse_reference(table, line):

   ref = {}

   items = re.split(r'\s+', line)
   ilen = len(items)
   if ilen < 3: PgLOG.pglog("{}: {}, insufficient".format(table['name'], line), PgLOG.LGWNEX)

   if re.match(r'^\d+$', items[0]):
      ref['name'] = "{}_ref_{}".format(table['name'], items[0])     # set index nam
   else:
      ref['name'] = items[0]
   ref['column'] = items[1]      # set ref column name
   ref['rtable'] = items[2]      # set refrenced table.column

   if ilen > 3:
      ref['rcolumn'] = items[3]      # set refrenced table.column
      if ilen > 4:
         for i in range(4, ilen):
            ref['rcolumn'] += " " + items[i]

   if 'ref' not in table: table['ref'] = []
   table['ref'].append(ref)

#
# action string to drop a table
#
def drop_table_action(ptname):

   return 'DROP TABLE {};\n'.format(ptname)

#
#  action string to create a new table
#
def create_table_action(table, ptname):
   
   firstline = 1
   sqlstr = 'CREATE TABLE {} ('.format(ptname)
   cmtstr = ''
   # add comments for table and all columns
   if 'comment' in table: cmtstr = 'COMMENT ON TABLE {} IS \'{}\';\n'.format(ptname, table['comment'])

   sep = '\n'
   # add all columns
   for column in table['column']:
      pcname = PgDBI.pgname(column['name'])
      sqlstr += sep + add_one_column_line(pcname, column)
      if 'comment' in column:
         cmtstr += 'COMMENT ON COLUMN {}.{} IS \'{}\';\n'.format(ptname, pcname, column['comment'])
      sep = ',\n'
   if 'pkey' in table:
      sqlstr += ",\nPRIMARY KEY ({})".format(PgDBI.pgname(table['pkey'], ','))
   if 'unique' in table:
      for unique in table['unique']:
         puname = PgDBI.pgname(unique['name'])
         pucol = PgDBI.pgname(unique['column'], ',')
         sqlstr += ",\nCONSTRANT {} UNIQUE ({})".format(puname, pucol)
   sqlstr += "\n);\n"

   return sqlstr + cmtstr

#
# action string to drop primary key
#
def drop_pkey_action(ptname):

   return "ALTER TABLE {} DROP PRIMARY KEY;\n".format(ptname)

#
# action string to add primary key
#   
def add_pkey_action(ptname, pkey):

   return "ALTER TABLE {} ADD PRIMARY KEY ({});\n".format(ptname, PgDBI.pgname(pkey, ','))

#
# action string to drop unique constraint
#
def drop_unique_action(ptname, puname):

   return "ALTER TABLE {} DROP CONSTRAINT {};\n".format(ptname, puname)

#
# action string to add unique constraint
#   
def add_unique_action(ptname, puname, unique):

   pucol = PgDBI.pgname(unique['column'], ',')
   return "ALTER TABLE {} ADD CONSTRAINT {} UNIQUE ({});\n".format(ptname, puname, pucol)

#
# action string to drop an index
#
def drop_index_action(piname):

   return "DROP INDEX {};\n".format(piname)

#
# action string to add indices
#
def add_index_action(ptname, piname, ustr, index):

   picol = PgDBI.pgname(index['column'], ',')
   return "CREATE{} INDEX {} ON {} ({});\n".format(ustr, piname, ptname, picol)

#
# action string to change index name
#
def change_index_action(poname, piname):

   return "ALTER INDEX {} RENAME TO {};\n".format(poname, piname)

#
# action string to dsrop a reference
def drop_ref_action(ptname, prname):

   return "ALTER TABLE {} DROP FOREIGN KEY {};\n".format(ptname, prname)

#
# action string to add a reference
#
def add_ref_action(ptname, prname, ref):
   
   # add multiple foreign keys if refname not defined
   prcol = PgDBI.pgname(ref['column'], ',')
   prtbl = PgDBI.pgname(ref['rtable'], '.')
   sqlstr = "ALTER TABLE {} ADD CONSTRAINT {} ".format(ptname, prname)
   sqlstr += "FOREIGN KEY ({}) REFERENCES {}".format(prcol, prtbl)
   if 'rcolumn' in ref:
      prrcol = PgDBI.pgname(ref['rcolumn'], ',.')
      sqlstr += '({})'.format(prrcol)
   sqlstr +=  "ON UPDATE CASCADE ON DELETE RESTRICT;\n"

   return sqlstr

#
#  string of adding a single column line
#
def add_one_column_line(pcname, column):

   line = "{} {}".format(pcname, column['type'])
   
   if 'notnull' in column: line += ' NOT NULL'
   if 'default' in column: line += " DEFAULT " + column['default']

   return line

#
# action string to drop a column
#
def drop_column_action(ptname, pcname):

   return "ALTER TABLE {} DROP COLUMN {};\n".format(ptname, pcname)

#
# action string to add a column
#
def add_column_action(ptname, pcname, column):

   return "ALTER TABLE {} ADD COLUMN {};\n".format(ptname, add_one_column_line(pcname, column))

#
# action string to change column name
#
def change_column_action(ptname, poname, pcname):

   return "ALTER TABLE {} RENAME COLUMN {} TO {};\n".format(ptname, poname, pcname)

#
# action string to modify a column
#
def modify_column_action(ptname, pcname, column, tbname):

   sqlstr = ''
   dft = None
   type = column['type']
   ms = re.match(r'^\s*(\w*)serial$', type)
   if ms:
      pint = ms.group(1)
      if pint:
         type = pint + 'int'
      else:
         type = 'integer'
      sqname = f"{tbname}_{pcname}_seq"
      sqlstr = f"CREATE SEQUENCE {sqname} OWNED BY {ptname}.{pcname};\n"
      dft = f"nextval('{sqname}')"
   elif 'default' in column:
      dft = column['default']
   sqlstr += f"ALTER TABLE {ptname}"
   sqlstr += f"\n  ALTER COLUMN {pcname} TYPE {type}"
   if 'notnull' in column:
      sqlstr += f",\n  ALTER COLUMN {pcname} SET {column['notnull']}"
   if dft: sqlstr += f",\n  ALTER COLUMN {pcname} SET DEFAULT {dft}"
   sqlstr += ";\n"
   if 'comment' in column:
      sqlstr += f"COMMENT ON COLUMN {ptname}.{pcname} IS '{column['comment']}';\n"
 
   return sqlstr

#
# action string to clear column comment
#
def drop_column_comment(ptname, pcname):

   return "COMMENT ON COLUMN {}.{} IS NULL;\n".format(ptname, pcname)

#
# action string to add column comment
#
def add_column_comment(ptname, pcname, comment):

   return "COMMENT ON COLUMN {}.{} IS '{}';\n".format(ptname, pcname, comment)

#
# action string to drop column default
#
def drop_column_default(ptname, pcname):

   return "ALTER TABLE {} ALTER COLUMN {} DROP DEFAULT;\n".format(ptname, pcname)

#
# action string to add column default
#
def add_column_default(ptname, pcname, default):

   return "ALTER TABLE {} ALTER COLUMN {} SET DEFAULT {};\n".format(ptname, pcname, default)

#
# action string to drop column not null
#
def drop_column_notnull(ptname, pcname):

   return "ALTER TABLE {} ALTER COLUMN {} DROP NOT NULL;\n".format(ptname, pcname)

#
# action string to add column not null
#
def add_column_notnull(ptname, pcname):

   return "ALTER TABLE {} ALTER COLUMN {} SET NOT NULL;\n".format(ptname, pcname)

#
# action string to clear table comment
#
def drop_table_comment(ptname):

   return "COMMENT ON TABLE {} IS NULL;\n".format(ptname)

#
# action string to add table comment
#
def add_table_comment(ptname, comment):

   return "COMMENT ON TABLE {} IS '{}';\n".format(ptname, comment)

#
# dump table definition into a json file
#
def dump_table_json(table):

   tbpath = "{}/{}".format(PGDDL['TBPATH'], table['schema'])
   PgFile.make_local_directory(tbpath, PgLOG.LGEREX)
   tbfile = "{}/{}.json".format(tbpath, table['name'])
   if not PGDDL['override'] and op.exists(tbfile):
      PgLOG.pglog("{}: remove existing table file before dump again".format(tbfile), PgLOG.LOGERR)
      return

   if 'header' not in table:
      uname = PGDDL['username'] + '@ucar.edu'
      table['header'] = {'author' : uname, 'date' : PgUtil.curdate(), 'description' : 'Auto-generated'}
   tf = open(tbfile, 'w')

   jtable = ['header', 'database', 'schema', 'name', 'pkey', 'column', 'unique',
             'index', 'ref', 'comment']
   jheader = ['author', 'date', 'description']
   jarray = {'unique' : ['name', 'column'],
             'column' : ['name', 'type', 'pkey', 'unique', 'notnull', 'default', 'comment'],
             'index' : ['name', 'column', 'unique'],
             'ref' : ['name', 'column', 'ref']
            }

   cindents = []
   nindents = []
   indent = '  '
   cindents.append(',\n')
   nindents.append('\n') 
   for l in range(4):
      cindents.append(cindents[l] + indent)
      nindents.append(nindents[l] + indent)

   line = '{'
   indent1 = nindents[1]
   for tfld in jtable:
      if tfld not in table: continue
      if tfld == 'header':
         line += indent1 + '"' + tfld + '": {' + nindents[2]
         line += get_hash_fields(table['header'], jheader, cindents[2]) 
         line += nindents[1] + '}'
      elif tfld in jarray:
         line += indent1 + '"' + tfld + '": ['
         indent2 = nindents[2]
         for fld in table[tfld]:
            val = get_hash_fields(fld, jarray[tfld], cindents[3])
            line += indent2 + '{' + nindents[3] + val + nindents[2] + '}'
            indent2 = cindents[2]
         line += nindents[1] + ']'
      else:
         line += indent1 + '"{}": "{}"'.format(tfld, table[tfld])
      indent1 = cindents[1]
   line += nindents[0] + '}'

   tf.write(line)
#   json.dump(table, tf, indent=2)
   tf.close()
   PgLOG.pglog("{}: table definition dumped".format(tbfile), PgLOG.LOGWRN)

def get_hash_fields(fld, jtmp, cindent):

   indent = ''
   line = ''
   for tmp in jtmp:
      if tmp not in fld: continue
      val = fld[tmp]
      if tmp == 'default' and val == 'NULL': continue 
      line += indent + r'"{}": "{}"'.format(tmp, val)
      indent = cindent
   for tmp in fld:
      if tmp in jtmp: continue
      val = fld[tmp]
      if tmp == 'default' and val == 'NULL': continue 
      line += indent + r'"{}": "{}"'.format(tmp, val)
      indent = cindent
   return line      

#
# Function: process_tables(tablenames: reference to array of table names)
#
# add or drop indices and/or references for all tables, not all actions
# can happen at the same time. Actions on tables, actions on references and
# actions on primary keys & indices must be done separately.
#
def process_tables(tablenames, act, opt, names = None):

   global NEWTABLE

   if not tablenames: return   # nothing to process

   tblcnt = len(tablenames)   
   if PGDDL['suffix']:
      suffix = get_table_suffix(tblcnt)
   else:
      suffix = None
   if PGDDL['prefix']:
      prefix = get_table_prefix(tblcnt)
   else:
      prefix = None

   for i in range(tblcnt):
      tablename = tablenames[i]
      ext = 'tb' if opt == 'JSN' else 'json'
      pre = prefix[i] if prefix else None
      suf = suffix[i] if suffix else None
      ms = re.match(r'^(.*)\.(tb|json)$', tablename)
      if ms:
         tablename = ms.group(1)
         ext = ms.group(2)
      scname = None
      ms = re.match(r'^(.+)\.(.+)$', tablename)
      if ms:
         scname = ms.group(1)
         tablename = ms.group(2)
      table = None
      if tablename in TABLES:
         table = TABLES[tablename]
      else:
         tbpath = PGDDL['TBPATH']
         if ext == 'json': tbpath += '/' + PgDBI.PGDBI['SCNAME']
         tbfile = "{}.{}".format(tablename, ext)
         getdef = False
         if op.exists(tbfile):
            getdef = True
         else:
            tbfile = "{}/{}".format(tbpath, tbfile)
            if op.exists(tbfile): getdef = True
         if getdef:
            table = get_table_def(tbfile, tablename, pre, suf, ext, scname)
            if table and (pre or suf):
               PgLOG.pglog("{}: Use table info in {}".format(table['name'], tbfile), PgLOG.LOGWRN)
         elif opt == 'JSN' and not PGDDL['usefile']:
            table = get_table_description(tablename, pre, suf)
            if table:
               PgLOG.pglog("{}: Use table info in {}.{}".format(table['name'], table['schema'], tablename), PgLOG.LOGWRN)
            else:
               PgLOG.pglog("{}: Cannot get table info in {}.{}".format(table['name'], table['schema'], tablename), PgLOG.LOGERR)
               continue
         elif not (pre or suf):
            table = get_root_table_def(tablename, tbpath, scname, ext)
         if not table:
            tbfile = "{}.{}".format(tablename, ext)
            PgLOG.pglog("{}: Cannot find table info file for Schema {}".format(tbfile, scname), PgLOG.LOGERR)
            continue

      sqlstr = None
      tbname = '{}.{}'.format(PgDBI.PGDBI['SCNAME'], table['name'])
      ptname = PgDBI.pgname(tbname, '.')
      if opt == 'TBL':
         if act == 'ADD':    # add table
            if PgDBI.pgcheck(ptname, PgLOG.LGEREX):
               PgLOG.pglog(tbname + ": Cannot ADD, table exists already", PgLOG.LOGERR)
               continue
            sqlstr = create_table_action(table, ptname)
            NEWTABLE = True
         elif act == 'DEL':    # drop table
            sqlstr = drop_table_action(ptname)
         PgDBI.pgexec(sqlstr, PgLOG.LGEREX)
         PgLOG.pglog("{}: {} table".format(tbname, act), PgLOG.LOGWRN)
      elif opt == 'CMT':
         if not names and 'comment' in table:
            sqlstr = add_table_comment(ptname, table['comment'])
            PgDBI.pgexec(sqlstr, PgLOG.LGEREX)
            PgLOG.pglog("{}: {} {}".format(tbname, act, opt), PgLOG.LOGWRN)
         for column in table['column']:
            colname = column['name']
            pcname = PgDBI.pgname(colname)
            if names and colname not in names: continue
            if act == 'ADD':    # add column comment
               if 'comment' not in column:
                  if names: PgLOG.pglog("{}: No {} {} to {}".format(tbname, opt, act, colname), PgLOG.LOGWRN)
                  continue
               sqlstr = add_column_comment(ptname, pcname, column['comment'])
            elif act == 'DEL':  # clear column comment
               sqlstr = drop_column_comment(ptname, pcname)
            PgDBI.pgexec(sqlstr, PgLOG.LGEREX)
            PgLOG.pglog("{}: {} {} to {}".format(tbname, act, opt, colname), PgLOG.LOGWRN)
      elif opt == 'DFT':
         for column in table['column']:
            colname = column['name']
            pcname = PgDBI.pgname(colname)
            if names and colname not in names: continue
            if column['type'].find('serial') > -1:
               if names: PgLOG.pglog("{}: Cannt {} {} for SERIAL column {}".format(tbname, opt, act, colname), PgLOG.LOGWRN)
               continue
            if act == 'ADD':    # add column default
               if 'default' not in column:
                  if names: PgLOG.pglog("{}: No {} {} for {}".format(tbname, opt, act, colname), PgLOG.LOGWRN)
                  continue
               sqlstr = add_column_default(ptname, pcname, column['default'])
            elif act == 'DEL':  # clear column comment
               sqlstr = drop_column_default(ptname, pcname)
            PgDBI.pgexec(sqlstr, PgLOG.LGEREX)
            PgLOG.pglog("{}: {} {} to {}".format(tbname, act, opt, colname), PgLOG.LOGWRN)
      elif opt == 'NNL':
         for column in table['column']:
            colname = column['name']
            pcname = PgDBI.pgname(colname)
            if names and colname not in names: continue
            if act == 'ADD':    # add column notnull
               if 'notnull' not in column:
                  if names: PgLOG.pglog("{}: No {} {} to {}".format(tbname, opt, act, colname), PgLOG.LOGWRN)
                  continue
               sqlstr = add_column_notnull(ptname, pcname)
            elif act == 'DEL':  # clear column notnull
               sqlstr = drop_column_notnull(ptname, pcname)
            PgDBI.pgexec(sqlstr, PgLOG.LGEREX)
            PgLOG.pglog("{}: {} {} to {}".format(tbname, act, opt, colname), PgLOG.LOGWRN)
      elif opt == 'REF':
         if 'ref' not in table:
            if not NEWTABLE: PgLOG.pglog(tbname + ": No reference defined", PgLOG.LOGWRN)
            continue
         for ref in table['ref']:
            refname = ref['name']
            prname = PgDBI.pgname(refname)
            if names and refname not in names: continue
            if act == 'ADD': # add reference
               sqlstr = add_ref_action(ptname, prname, ref)
            elif act == 'DEL': # drop reference
               sqlstr = drop_ref_action(ptname, prname)
            PgDBI.pgexec(sqlstr, PgLOG.LGEREX)
            PgLOG.pglog("{}: {} {} {} to {}({})".format(tbname, act, opt, refname, ref['rtable'], ref['rcolumn']), PgLOG.LOGWRN)
      elif opt == 'PKY':
         if 'pkey' not in table:
            PgLOG.pglog(tbname + ": No primary key defined", PgLOG.LGEREX)
         if act == 'ADD':     # add primary key
            sqlstr = add_pkey_action(ptname, table['pkey'])
         elif act == 'DEL':   # drop primary key
            sqlstr = drop_pkey_action(ptname)
         PgDBI.pgexec(sqlstr, PgLOG.LGEREX)
         PgLOG.pglog("{}: {} {} {}".format(tbname, act, opt, table['pkey']), PgLOG.LOGWRN)
      elif opt == 'UNQ':
         if 'unique' not in table:
            PgLOG.pglog(tbname + ": No unique constraint defined", PgLOG.LGEREX)
         for unique in table['unique']:
            unqname = unique['name']
            puname = PgDBI.pgname(unqname)
            if names and unqname not in names: continue
            if act == 'ADD':     # add index
               sqlstr = add_unique_action(ptname, unique)
            elif act == 'DEL':   # drop index
               sqlstr = drop_unique_action(ptname, puname)
            PgDBI.pgexec(sqlstr, PgLOG.LGEREX)
            PgLOG.pglog("{}: {} {} {} ({})".format(tbname, act, opt, unqname, unique['column']), PgLOG.LOGWRN)
      elif opt == 'IDX':
         if 'index' not in table:
            if not NEWTABLE: PgLOG.pglog(tbname + ": No index defined", PgLOG.LGEREX)
            continue
         if act == 'CHG':
            poname = PgDBI.pgname(names.pop(0))
            if len(names) != 1:
               PgLOG.pglog("{}: need old & new index names to {}".format(tbname, act), PgLOG.LOGWRN)
         ncnt = len(names) if names else 0
         for i in range(ncnt):
            if re.match(r'^\d+$', names[i]): names[i] = "{}_idx_{}".format(ptname, names[i])
         for index in table['index']:
            idxname = index['name']
            piname = PgDBI.pgname(idxname)
            ustr = ' UNIQUE' if 'unique' in index else ''
            if ncnt > 0 and idxname not in names: continue
            if act == 'ADD':      # add index
               sqlstr = add_index_action(ptname, piname, ustr, index)
            elif act == 'DEL':    # drop index
               sqlstr = drop_index_action(piname)
            elif act == 'CHG':    # change index name
               sqlstr = change_index_action(poname, piname)
            PgDBI.pgexec(sqlstr, PgLOG.LGEREX)
            PgLOG.pglog("{}: {}{} {} {} ({})".format(tbname, act, ustr, opt, idxname, index['column']), PgLOG.LOGWRN)
      elif opt == 'FLD':
         if not names:
            PgLOG.pglog("{}: Miss column name to {}".format(tbname, act), PgLOG.LGEREX)
         if not ('column' in table and table['column']):
            PgLOG.pglog(tbname + ": No column defined", PgLOG.LGEREX)
         if act == 'CHG':
            poname = PgDBI.pgname(names.pop(0))
            if len(names) != 1:
               PgLOG.pglog("{}: need old & new columnnames to {}".format(tbname, act), PgLOG.LOGWRN)
         for column in table['column']:
            colname = column['name']
            pcname = PgDBI.pgname(colname)
            if colname not in names: continue
            if act == 'DEL':
               sqlstr = drop_column_action(ptname, pcname)
            elif act == 'ADD':
               sqlstr = add_column_action(ptname, pcname, column)
            elif act == 'CHG':
               sqlstr = change_column_action(ptname, poname, pcname)
            elif act == 'MOD':
               sqlstr = modify_column_action(ptname, pcname, column, table['name'])
            PgDBI.pgexec(sqlstr, PgLOG.LGEREX)
            PgLOG.pglog("{}: {} {} {}".format(tbname, act, opt, colname), PgLOG.LOGWRN)
      elif opt == 'JSN':      # dump table to json
         dump_table_json(table)

#
# get table definition information from a root table name
#
def get_root_table_def(tbname, tbpath, scname, ext):

   ms = re.match(r'^(.+)_([^_]+)$', tbname)
   if not ms: return None
   tname = ms.group(1)
   suf = ms.group(2) if ext == 'json' else None
   tbfile = "{}.{}".format(tname, ext)
   getdef = False
   if op.exists(tbfile):
      getdef = True
   else:
      tbfile = "{}/{}".format(tbpath, tbfile)
      if op.exists(tbfile): getdef = True
   if getdef:
      table = get_table_def(tbfile, tname, None, suf, ext, scname)
      if table:
         PgLOG.pglog("{}: Use table info in {}".format(table['name'], tbfile), PgLOG.LOGWRN)
         return table

   ms = re.match(r'^([^_]+)_(.+)$', tbname)
   if not ms: return None
   tname = ms.group(2)
   pre = ms.group(1) if ext == 'json' else None
   tbfile = "{}.{}".format(tname, ext)
   if op.exists(tbfile):
      getdef = True
   else:
      tbfile = "{}/{}".format(tbpath, tbfile)
      if op.exists(tbfile): getdef = True
   if getdef:
      table = get_table_def(tbfile, tname, pre, None, ext, scname)
      if table:
         PgLOG.pglog("{}: Use table info in {}".format(table['name'], tbfile), PgLOG.LOGWRN)
         return table

   return None

#
# get table name suffixes
#
def get_table_suffix(tcnt):
   
   scnt = len(PGDDL['suffix']) if PGDDL['suffix'] else 0
   if scnt >= tcnt:
      suffix = PGDDL['suffix']
   elif scnt == 1:
      suffix = [PGDDL['suffix'][0]]*tcnt
   else:
      PgLOG.pglog("{}/{}: miss match suffix to table counts".format(scnt, tcnt), PgLOG.LGEREX)

   return suffix

#
# get table name prefixes
#
def get_table_prefix(tcnt):
   
   pcnt = len(PGDDL['prefix']) if PGDDL['prefix'] else 0
   if pcnt >= tcnt:
      prefix = PGDDL['prefix']
   elif pcnt == 1:
      prefix = [PGDDL['prefix'][0]]*tcnt
   else:
      PgLOG.pglog("{}/{}: miss match prefix to table counts".format(pcnt, tcnt), PgLOG.LGEREX)

   return prefix

#
# Function: alltablenames() return reference to array of table names
#
def alltablenames():

   return PgFile.local_glob(PGDDL['TBPATH'] + "/*.tb")

#
# Function: allschematables() return reference to array of all table names under
# schema/dbname
#
def allschematables():


   if PGDDL['mysqldb']:
      return get_mysql_tablenames()
   else:
      return get_postgresql_tablenames()

#
# get mysql tablenames
#
def get_mysql_tablenames():

   tables = []
   cmd = "echo 'show tables' | mysql -h {} ".format(PgDBI.PGDBI['DBHOST'])
   if PgDBI.PGDBI['DBPORT']: cmd += "-P {} ".format(PgDBI.PGDBI['DBPORT'])
   cmd += " -u {} -p{} {}".format(PgDBI.PGDBI['LNNAME'], PgDBI.PGDBI['PWNAME'], PgDBI.PGDBI['SCNAME'])
   buf = PgLOG.pgsystem(cmd, PgLOG.LOGWRN, 16)
   lines = buf.split('\n')
   if len(lines) < 2:
      PgLOG.pglog(PgDBI.PGDBI['SCNAME'] + ": Fail to get table info", PgLOG.LGEREX)
   lines.pop(0)
   lines.pop()
   for line in lines:
      tables.append(line)

   return tables

#
# get postgresql table names
#
def get_postgresql_tablenames():

   tables = []
   cmd = "psql {} -h {} -U {} -c".format(PgDBI.PGDBI['DBNAME'], PgDBI.PGDBI['DBHOST'], PgDBI.PGDBI['LNNAME'])
   cmd += " \"\dt '{}.*'\"".format(PgDBI.PGDBI['SCNAME'])
   buf = PgLOG.pgsystem(cmd, PgLOG.LOGWRN, 17)
   lines = buf.split('\n')
   if len(lines) < 4: PgLOG.pglog("{}: Fail \dt".format(PgDBI.PGDBI['SCNAME']), PgLOG.LGEREX)
   lines = lines[3:-1]
   for line in lines:
      items = re.split('[\s|]+', line)
      if not (len(items) == 4 and items[2] == 'table'): continue
      tables.append(items[1])

   return tables
