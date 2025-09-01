###############################################################################
#
#     Title : PgCheck.py
#    Author : Zaihua Ji,  zji@ucar.edu
#      Date : 08/26/2020
#             2025-02-10 transferred to package rda_python_dscheck from
#             https://github.com/NCAR/rda-shared-libraries.git
#   Purpose : python library module for for holding some global variables and
#             functions for dscheck utility
#
#    Github : https://github.com/NCAR/rda-python-dscheck.git
#
###############################################################################
#
import os
import re
import time
from rda_python_common import PgLOG
from rda_python_common import PgCMD
from rda_python_common import PgSIG
from rda_python_common import PgUtil
from rda_python_common import PgLock
from rda_python_common import PgFile
from rda_python_common import PgOPT
from rda_python_common import PgDBI

# global variables
LOOP = 0
PLIMITS = {}
DWHOSTS = {}     # hosts are down
RUNPIDS = {}
SHELLS = {}      # shell names used by specialists

#
# define initially the needed option values
#
PgOPT.OPTS = {                         # (!= 0) - setting actions
   'PC' : [0x0004, 'ProcessCheck',    1],
   'AC' : [0x0008, 'AddCheck',        1],
   'GD' : [0x0010, 'GetDaemon',       0],
   'SD' : [0x0020, 'SetDaemon',       1],
   'GC' : [0x0040, 'GetCheck',        0],
   'DL' : [0x0080, 'Delete',          1],
   'UL' : [0x0100, 'UnLockCheck',     1],
   'EC' : [0x0200, 'EmailCheck',      0],
   'IC' : [0x0400, 'InterruptCheck',  1],
   'CH' : [0x1000, 'CheckHost',       0],
   'SO' : [0x1000, 'SetOptions',      1],

   'AW' : [0, 'AnyWhere',      0],
   'BG' : [0, 'BackGround',    0],
   'CP' : [0, 'CheckPending',  0],
   'CS' : [0, 'CheckStatus',   0],
   'FI' : [0, 'ForceInterrrupt', 0],
   'FO' : [0, 'FormatOutput',  0],
   'LO' : [0, 'LogOn',         0],
   'MD' : [0, 'PgDataset',     3],
   'NC' : [0, 'NoCommand',     0],
   'ND' : [0, 'NewDaemon',     0],
   'NT' : [0, 'NoTrim',        0],
   'WR' : [0, 'WithdsRqst',    0],
   'WU' : [0, 'WithdsUpdt',    0],

   'DM' : [1, 'DaemonMode',      1],  # for action PC, start|quit|logon|logoff
   'DV' : [1, 'Divider',         1],  # default to <:>
   'ES' : [1, 'EqualSign',       1],  # default to <=>
   'FN' : [1, 'FieldNames',      0],
   'LH' : [1, 'LocalHost',       0,  ''],
   'MT' : [1, 'MaxrunTime',      0],
   'OF' : [1, 'OutputFile',      0],
   'ON' : [1, 'OrderNames',      0],
   'AO' : [1, 'ActOption',       1],  # default to <!>
   'WI' : [1, 'WaitInterval',    1],

   'AN' : [2, 'ActionName',     0],
   'AV' : [2, 'ArgumentVector', 0],
   'AX' : [2, 'ArgumenteXtra',  0],
   'CC' : [2, 'CarbonCopy',     0],
   'CD' : [2, 'CheckDate',    256],
   'CI' : [2, 'CheckIndex',    16],
   'CM' : [2, 'Command',        1],
   'CT' : [2, 'CheckTime',     32],
   'DB' : [2, 'Debug',          0],
   'DC' : [2, 'DoneCount',     17],
   'DF' : [2, 'DownFlags',      1],
   'DI' : [2, 'DaemonIndex',   16],
   'DS' : [2, 'Dataset',        1],
   'ER' : [2, 'ERrormessage',   0],
   'EV' : [2, 'Environments',   1],
   'FC' : [2, 'FileCount',     17],
   'HN' : [2, 'HostName',       1],
   'IF' : [2, 'InputFile',      0],
   'MC' : [2, 'MaxCount',      17],
   'MH' : [2, 'MatchHost',      1],
   'MO' : [2, 'Modules',        1],
   'PI' : [2, 'ParentIndex',   17],
   'PL' : [2, 'ProcessLimit',  17],
   'PO' : [2, 'Priority',      17],
   'PQ' : [2, 'PBSQueue',       0],
   'QS' : [2, 'QSubOptions',    0],
   'SN' : [2, 'Specialist',     1],
   'ST' : [2, 'Status',         0],
   'SZ' : [2, 'DataSize',      16],
   'TC' : [2, 'TryCount',      17],
   'WD' : [2, 'WorkDir',        0],
}

PgOPT.ALIAS = {
   'AN' : ['Action'],
   'BG' : ['b'],
   'CF' : ['Confirmation', 'ConfirmAction'],
   'CM' : ['CommandName'],
   'DL' : ['RM', 'Remove'],
   'DS' : ['Dsid', 'DatasetID'],
   'DV' : ['Delimiter', 'Separater'],
   'EV' : ['Envs'],
   'GZ' : ['GMT', 'GreenwichZone', 'UTC'],
   'MC' : ['MaximumCount', 'MaxTryCount'],
   'MH' : ['MatchHostname'],
   'NC' : ['NoRemoteCommand'],
   'MO' : ['Mods'],
   'PI' : ['ParentCheckIndex'],
   'QS' : ['PBSOptions'],
   'SO' : ['SetBatchOptions'],
   'SZ' : ['Size', "ProcSize"],
   'UL' : ['UnLock'],
   'WD' : ["WorkDirectory"],
   'WR' : ["WithRequest"],
   'WU' : ["WithUpdate"],
}

PgOPT.TBLHASH['dscheck'] = {
#SHORTNM KEYS(PgOPT.OPTS) DBFIELD
   'C' : ['CI', "cindex",         0],
   'O' : ['CM', "command",        1],
   'V' : ['AV', "argv",           1],
   'T' : ['DS', "dsid",           1],
   'A' : ['AN', "action",         1],
   'U' : ['ST', "status",         1],
   'P' : ['PQ', "pbsqueue",       1],
   'R' : ['PI', "pindex",         0],
   'B' : ['DF', "dflags",         0],
   'F' : ['FC', "fcount",         0],
   'J' : ['DC', "dcount",         0],
   'K' : ['TC', "tcount",         0],
   'L' : ['MC', "mcount",         0],
   'Z' : ['SZ', "size",           0],
   'D' : ['CD', "date",           1],
   'Y' : ['CT', "time",           1],
   'H' : ['HN', "hostname",       1],
   'N' : ['SN', "specialist",     1],
   'W' : ['WD', "workdir",        1],
   'M' : ['MO', "modules",        1],
   'I' : ['EV', "environments",   1],
   'Q' : ['QS', "qoptions",       1],
   'X' : ['AX', "argextra",      -1],
   'E' : ['ER', "errmsg",        -1],
}

PgOPT.TBLHASH['dsdaemon'] = {
#SHORTNM KEYS(PgOPT.OPTS) DBFIELD
   'I' : ['DI', "dindex",         0],
   'C' : ['CM', "command",        1],
   'H' : ['HN', "hostname",       1],
   'M' : ['MH', "matchhost",      1],
   'S' : ['SN', "specialist",     1],
   'P' : ['PL', "proclimit",      0],
   'O' : ['PO', "priority",       0],
}

CHKHOST = {
   'curhost' : PgLOG.get_host(1),
   'chkhost' : None,
   'hostcond' : None,
   'isbatch' : 0
}

PgOPT.PGOPT['dscheck']   = "COVTUPFJDNW"            # default
PgOPT.PGOPT['chkall']    = "COVTAUPRBFJKLZDYHNWMIQXE"   # default to all   
PgOPT.PGOPT['dsdaemon']  = "ICHQSPO"                 # default to all
PgOPT.PGOPT['waitlimit'] = 280      # limit of C and P request checks at a time
PgOPT.PGOPT['totallimit'] = 380     # maximum number of checks can be started on PBS

PBSQUEUES = {'rda' : None, 'htc' : 'casper@casper-pbs'}
PBSTIMES = {'default' : 21600, 'rda' : PgLOG.PGLOG['PBSTIME'], 'htc' : 86400}
#DOPTHOSTS = {'rda-work' : None, 'PBS' : ['!subconv -Q']}
DOPTHOSTS = {'rda-work' : None, 'PBS' : None, 'cron' : None}
DSLMTS = {}
EMLMTS = {}

#
# get the maximum running time for batch processes
#
def max_batch_time(qname):

   if CHKHOST['curhost'] == PgLOG.PGLOG['PBSNAME']:
      if not (qname and qname in PBSTIMES): qname = 'default'
      return PBSTIMES[qname]
   else:
      return 0

#
# check if enough information entered on command line and/or input file
# for given action(s)
#
def check_dscheck_options(cact, aname):

   errmsg = [
      "Option -DM(-DaemonMode) works with Action -PC(-ProcessCheck) only",
      "Do not specify Check Index for Daemon Mode",
      "Miss check index per Info option -CI(-CheckIndex)",
      "Need Machine Hostname per -HN for new daemon control",
      "Need Application command name per -CM for new daemon control",
      "Must be {} to process Checks in daemon mode".format(PgLOG.PGLOG['RDAUSER']),
      "Miss Command information per Info option -CM(-Command)",
   ]
   erridx = -1
   PgOPT.set_uid(aname)

   if 'CI' in PgOPT.params: validate_checks()
   if 'DS' in PgOPT.params: validate_datasets()

   if 'DM' in PgOPT.params:
      if cact != "PC":
         erridx = 0
      elif PgLOG.PGLOG['CURUID'] != PgLOG.PGLOG['RDAUSER']:
         erridx = 5
      elif 'CI' in PgOPT.params:
         erridx = 1
   elif cact == "DL":
      if not ('CI' in PgOPT.params or 'DI' in PgOPT.params): erridx = 2
   elif cact == 'SD':
      validate_daemons()
      if 'SD' in PgOPT.params:
         if 'HN' not in PgOPT.params:
            erridx = 3
         elif 'CM' not in PgOPT.params:
            erridx = 4
   elif cact == "AC":
      if 'CM' not in PgOPT.params:
         erridx = 6
   elif 'CI' not in PgOPT.params and (cact == "IC" or cact == "UL" and 'LL' not in PgOPT.params):
      erridx = 2

   if erridx >= 0: PgOPT.action_error(errmsg[erridx], cact)

   if cact == "PC" or cact == 'UL':
      if PgLOG.PGLOG['CURUID'] != PgOPT.params['LN']:
         PgOPT.action_error("{}: cannot process Checks as {}".format(PgLOG.PGLOG['CURUID'], PgOPT.params['LN']), cact)
      if 'LH' in PgOPT.params:
         chkhost = PgLOG.get_short_host(PgOPT.params['LH'])
         if not chkhost: chkhost = PgLOG.get_host(1)
         CHKHOST['chkhost'] = CHKHOST['curhost'] = chkhost
         if PgLOG.valid_batch_host(chkhost):
            PgLOG.reset_batch_host(chkhost)
            CHKHOST['isbatch'] = 1
            CHKHOST['hostcond'] = "IN ('{}', '{}')".format(chkhost, PgLOG.PGLOG['HOSTNAME'])
         else:
            if PgUtil.pgcmp(chkhost, PgLOG.PGLOG['HOSTNAME'], 1):
               PgOPT.action_error("{}: Cannot handle checks on {}".format(PgLOG.PGLOG['HOSTNAME'], chkhost), cact)
            CHKHOST['hostcond'] = "= '{}'".format(chkhost)

   if 'DM' in PgOPT.params:
      if PgLOG.PGLOG['CHKHOSTS'] and PgLOG.PGLOG['CHKHOSTS'].find(PgLOG.PGLOG['HOSTNAME']) < 0:
         PgOPT.action_error("Daemon mode can only be started on '{}'".format(PgLOG.PGLOG['CHKHOSTS']), cact)
      if re.match(r'^(start|begin)$', PgOPT.params['DM'], re.I):
         if not ('NC' in PgOPT.params or 'LH' in PgOPT.params): PgOPT.params['NC'] = 1 
         wtime = PgOPT.params['WI'] if 'WI' in PgOPT.params else 0
         mtime = PgOPT.params['MT'] if 'MT' in PgOPT.params else 0
         logon = PgOPT.params['LO'] if 'LO' in PgOPT.params else 0
         PgSIG.start_daemon(aname, PgLOG.PGLOG['CURUID'], 1, wtime, logon, 0, mtime)
      else:
         PgSIG.signal_daemon(PgOPT.params['DM'], aname, PgOPT.params['LN'])
   else:
      if cact == "PC":
         PgSIG.validate_single_process(aname, PgOPT.params['LN'], PgLOG.argv_to_string())
      elif cact == "SO":
         plimit = PgOPT.params['PL'][0] if 'PL' in PgOPT.params and PgOPT.params['PL'][0] > 0 else 1
         PgSIG.validate_multiple_process(aname, plimit, PgOPT.params['LN'], PgLOG.argv_to_string())
      wtime = PgOPT.params['WI'] if 'WI' in PgOPT.params else 30
      logon = PgOPT.params['LO'] if 'LO' in PgOPT.params else 1
      PgSIG.start_none_daemon(aname, cact, PgOPT.params['LN'], 1, wtime, logon)
      if not ('CI' in PgOPT.params or 'DS' in PgOPT.params or PgOPT.params['LN'] == PgLOG.PGLOG['RDAUSER']):
         PgOPT.set_default_value("SN", PgOPT.params['LN'])

   # minimal wait interval in seconds for next check
   PgOPT.PGOPT['minlimit'] = PgOPT.params['WI'] = PgSIG.PGSIG['WTIME']

#
# process counts of hosts in dsdaemon control records for given command and specialist
#
def get_process_limits(cmd, specialist, logact = 0):

   ckey = "{}-{}".format(cmd, specialist)
   if ckey in PLIMITS: return PLIMITS[ckey]

   cnd = "command = '{}' AND specialist = '{}'".format(cmd, specialist)
   if CHKHOST['chkhost']:
      ecnd = " AND hostname = '{}'".format(CHKHOST['chkhost'])
      hstr = " for " + CHKHOST['chkhost']
   else:
      ecnd = " ORDER by priority, hostname"
      hstr = ""

   pgrecs = PgDBI.pgmget("dsdaemon", "hostname, bqueues, matchhost, proclimit, priority", cnd + ecnd, logact)
   if not pgrecs and PgDBI.pgget("dsdaemon", "", cnd, logact) == 0:
      pgrecs = PgDBI.pgmget("dsdaemon", "hostname, matchhost, proclimit, priority",
                            "command = 'ALL' AND specialist = '{}'{}".format(specialist, ecnd), logact)

   cnt = (len(pgrecs['hostname']) if pgrecs else 0)
   if cnt == 0:
      PLIMITS[ckey] = 0
      return 0

   j = 0
   PLIMITS[ckey] = {'host' : [], 'priority' : [], 'acnt' : [], 'match' : [], 'pcnd' : []}
   for i in range(cnt):
      if pgrecs['proclimit'][i] <= 0: continue
      host = pgrecs['hostname'][i]
      PLIMITS[ckey]['host'].append(host)
      PLIMITS[ckey]['priority'].append(pgrecs['priority'][i])
      PLIMITS[ckey]['acnt'].append(pgrecs['proclimit'][i])
      PLIMITS[ckey]['match'].append(pgrecs['matchhost'][i])
      PLIMITS[ckey]['pcnd'].append("{} AND pid > 0 AND lockhost = '{}'".format(cnd, host))

   if not PLIMITS[ckey]['host']: PLIMITS[ckey] = 0
   return PLIMITS[ckey]

#
# find a available host name to process a dscheck record
# 
def get_process_host(limits, hosts, cmd, act, logact = 0):

   cnt = len(limits['host'])
   for i in range(cnt):
      host = limits['host'][i]
      if host in DWHOSTS: continue     # the host is down
      if limits['acnt'][i] > PgDBI.pgget("dscheck", "", limits['pcnd'][i], logact):
         if cmd == 'dsrqst' and act == 'PR':
            mflag = 'G'
         else:
            mflag = limits['match'][i]
         if PgLOG.check_process_host(hosts, host, mflag): return i

   return -1

#
# reset the cached process limits
#
def reset_process_limits():

   global LOOP, DWHOSTS, PLIMITS

   if LOOP%3 == 0:
      PLIMITS = {}   # clean the cache for available processes on hosts

   if LOOP%10 == 0:
      DWHOSTS = {}
      PgLOG.set_pbs_host(None, 1)

   LOOP += 1

#
# start dschecks
#
def start_dschecks(cnd, logact = 0):

   rcnt = 0
   check_dscheck_locks(cnd, logact)
   if not CHKHOST['chkhost']: email_dschecks(cnd, logact)
   purge_dschecks(cnd, logact)

#   if 'NC' in PgOPT.params or not CHKHOST['chkhost']: return 0 
   if 'NC' in PgOPT.params: return 0 
   if CHKHOST['isbatch'] and 'CP' in PgOPT.params: check_dscheck_pends(cnd, logact)
#   set_dscheck_options(CHKHOST['chkhost'], cnd, logact)
   reset_process_limits()
   if CHKHOST['isbatch']: rcnt = PgDBI.pgget("dscheck", "", "lockhost = '{}' AND pid > 0".format(PgLOG.PGLOG['PBSNAME']), logact)

   cnd += "pid = 0 AND status <> 'D' AND einfo IS NULL AND (qoptions IS NULL OR LEFT(qoptions, 1) != '!') ORDER by hostname DESC, cindex"
   pgrecs = PgDBI.pgmget("dscheck", "*", cnd, logact)
   cnt = (len(pgrecs['cindex']) if pgrecs else 0)
   pcnt = 0
   for i in range(cnt):
      if (pcnt + rcnt) > PgOPT.PGOPT['totallimit']: break
      pgrec = PgUtil.onerecord(pgrecs, i)
      if(pgrec['fcount'] and pgrec['dcount'] >= pgrec['fcount'] or
         pgrec['tcount'] and pgrec['tcount'] >= pgrec['mcount'] or
         pgrec['pindex'] and PgDBI.pgget("dscheck", "", "cindex = {} AND status <> 'D'".format(pgrec['pindex']), logact)):
         continue
      if pgrec['dflags'] and PgFile.check_storage_dflags(pgrec['dflags'], pgrec, logact): continue
      ret = start_one_dscheck(pgrec, logact)
      if ret > 0: pcnt += ret

   if cnt > 1: PgLOG.pglog("{} of {} DSCHECK records started on {}".format(pcnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)
   return pcnt

#
#  check long locked dschecks and unlock them if the processes are dead
#
def check_dscheck_locks(cnd, logact = 0):

   global RUNPIDS
   ltime = int(time.time())
   lochost = PgLOG.PGLOG['HOSTNAME']
   cnd += "pid > 0 AND "
   dtime = ltime - PgSIG.PGSIG['DTIME']
   ctime = ltime - PgSIG.PGSIG['CTIME']
   rtime = ltime - PgSIG.PGSIG['RTIME']
   cnd += "chktime > 0 AND (chktime < {} OR chktime < {} AND lockhost = '{}' OR chktime < {} AND lockhost = 'rda_config')".format(ctime, dtime, lochost, rtime)

   pgrecs = PgDBI.pgmget("dscheck", "*", cnd, logact)
   cnt = (len(pgrecs['cindex']) if pgrecs else 0)
   lcnt = 0
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      lmsg = "{}({}) at {} on {}".format(pgrec['lockhost'], pgrec['pid'], PgLOG.current_datetime(), PgLOG.PGLOG['HOSTNAME'])
      cidx = pgrec['cindex']
      if CHKHOST['chkhost'] or pgrec['lockhost'] == lochost:
         spid = "{}{}".format(pgrec['lockhost'], pgrec['pid'])
         if spid not in RUNPIDS and PgLock.lock_dscheck(cidx, 0) > 0:
            PgLOG.pglog("CHK{}: unlocked {}".format(cidx, lmsg), PgLOG.LOGWRN)
            lcnt += 1
         else:
            update_dscheck_time(pgrec, ltime, logact)
      elif not pgrec['lockhost'] or pgrec['lockhost'] == 'rda_config':
         record = {'pid' : 0, 'lockhost' : ''}
         if PgDBI.pgupdt("dscheck", record, "cindex = {} AND pid = {}".format(cidx, pgrec['pid']), logact):
            PgLOG.pglog("CHK{}: unlocked {}".format(cidx, lmsg), PgLOG.LOGWRN)
            lcnt += 1
      elif (logact&PgLOG.EMEROL) == PgLOG.EMEROL:
         PgLOG.pglog("Chk{}: time NOT updated for {} of {}".format(cidx, dscheck_runtime(pgrec['chktime'], ltime), lmsg), logact)

   if cnt > 0: 
      s = 's' if cnt > 1 else ''
      PgLOG.pglog("{} of {} DSCHECK record{} unlocked on {}".format(lcnt, cnt, s, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)
   RUNPIDS = {}

#
#  check long pending dschecks and kill them
#
def check_dscheck_pends(cnd, logact = 0):

   ltime = int(time.time()) - PgSIG.PGSIG['RTIME']
   cnd += "pid > 0 AND "
   cnd += "lockhost {} AND status = 'P' AND subtime > 0 AND subtime < {}".format(CHKHOST['hostcond'], ltime)
   pgrecs = PgDBI.pgmget("dscheck", "pid", cnd, logact)
   cnt = (len(pgrecs['pid']) if pgrecs else 0)

   pcnt = 0
   for i in range(cnt):
      pid = pgrecs['pid'][i]
      info = PgSIG.get_pbs_info(pid, 0, logact)
      if info and info['State'] == 'Q':
         PgLOG.pgsystem("rdakill -h {} -p {}".format(PgLOG.PGLOG['PBSNAME'], pid), PgLOG.LOGWRN, 5)
         pcnt += 1

   if cnt > 0:
      s = 's' if cnt > 1 else ''
      PgLOG.pglog("{} of {} Pending DSCHECK record{} stopped on {}".format(pcnt, cnt, s, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

#
# update dscheck time in case in pending status or
# the command does not updateupdates not on time by itself
#
def update_dscheck_time(pgrec, ltime, logact = 0):

   record = {'chktime' : ltime}
   if(CHKHOST['chkhost'] and CHKHOST['chkhost'] == PgLOG.PGLOG['PBSNAME']
      and pgrec['lockhost'] == PgLOG.PGLOG['PBSNAME']):
      info = PgSIG.get_pbs_info(pgrec['pid'], 0, logact)
      if info:
         stat = info['State']
         if stat != pgrec['status']: record['status'] = stat
   else:
      if pgrec['lockhost'] != PgLOG.PGLOG['HOSTNAME']: return    # connot update dscheck time
      if PgSIG.check_host_pid(pgrec['lockhost'], pgrec['pid']):
         if pgrec['status'] != "R": record['status'] = "R"
      else:
         if pgrec['status'] == "R": record['status'] = "F"

   if pgrec['stttime']:
      if pgrec['command'] == "dsrqst" and pgrec['oindex']:
         (record['fcount'], record['dcount'], record['size']) = PgCMD.get_dsrqst_counts(pgrec, logact)

   elif 'status' in record and record['status'] == 'R':
      record['stttime'] = ltime

   cnd = "cindex = {} AND pid = {}".format(pgrec['cindex'], pgrec['pid'])
   if PgDBI.pgget("dscheck", "", "{} AND chktime = {}".format(cnd, pgrec['chktime']), logact):
      # update only the chktime is not changed yet
      PgDBI.pgupdt("dscheck", record, cnd, logact)

#
# return a running time string for given start and end times of the process
#
def dscheck_runtime(start, end = None):

   stime = ''
   
   if start:
      if not end: end = int(time.time())
      rtime = (end - start)
      if rtime >= 60:
         stime = PgLOG.seconds_to_string_time(rtime)

   return stime

#
#  check dschecks and purge them if done already
#
def purge_dschecks(cnd, logact = 0):

   cnd += "pid = 0 AND einfo IS NULL AND bid "
   cnd += ('> 0' if CHKHOST['curhost'] == PgLOG.PGLOG['PGBATCH'] else '= 0')
   pgrecs = PgDBI.pgmget("dscheck", "*", cnd, logact)
   cnt = (len(pgrecs['cindex']) if pgrecs else 0)
   ctime = int(time.time()) - PgSIG.PGSIG['CTIME']
   dcnt = 0
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      if(pgrec['status'] == "D" or
         pgrec['status'] == "R" and pgrec['chktime'] < ctime or
         pgrec['fcount'] and pgrec['dcount'] >= pgrec['fcount'] or
         pgrec['tcount'] and pgrec['tcount'] >= pgrec['mcount']):
         if PgLock.lock_dscheck(pgrec['cindex'], 1) <= 0: continue
         dcnt += PgCMD.delete_dscheck(pgrec, None, logact)

   if dcnt and cnt > 1: PgLOG.pglog("{} of {} DSCHECK records purged on {}".format(dcnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

#
#  check dschecks and send saved email
#
def email_dschecks(cnd, logact = 0):

   emlact = PgLOG.LOGWRN|PgLOG.FRCLOG
   if logact and (logact&PgLOG.EMEROL) == PgLOG.EMEROL: emlact |= PgLOG.EMEROL
   cnd += "pid = 0 AND einfo IS NOT NULL"
   pgrecs = PgDBI.pgmget("dscheck", "cindex", cnd, logact)
   cnt = (len(pgrecs['cindex']) if pgrecs else 0)
   ecnt = 0
   for i in range(cnt):
      cidx = pgrecs['cindex'][i]
      if PgLock.lock_dscheck(cidx, 1) <= 0: continue
      pgrec = PgDBI.pgget("dscheck", "*", "cindex = {}".format(cidx), logact)
      einfo = pgrec['einfo'] if pgrec else None
      if einfo:
         if pgrec['dflags'] and pgrec['tcount'] and pgrec['tcount'] < pgrec['mcount']:
            msgary = PgFile.check_storage_dflags(pgrec['dflags'], pgrec, logact)
            if msgary:
               einfo = "The Check will be resubmitted after the down storage Up again:\n{}\n{}".format("\n".join(msgary), einfo)

         sent = 1 if(PgLOG.send_customized_email("Chk{}".format(cidx), einfo, emlact) and
                 PgDBI.pgexec("UPDATE dscheck set einfo = NULL WHERE cindex = {}".format(cidx), logact)) else -1
      else:
         sent = 0

      PgLock.lock_dscheck(cidx, 0)
      if sent == -1: break
      ecnt += sent

   if ecnt and cnt > 1: PgLOG.pglog("{} of {} DSCHECK emails sent on {}".format(ecnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

#
# start a dscheck job for given dscheck record
#
def start_one_dscheck(pgrec, logact = 0):

   cidx = pgrec['cindex']
   specialist = pgrec['specialist']
   host = CHKHOST['chkhost']
   dlimit = get_system_down_limit(host, logact)
   if dlimit < 0:
      PgLock.lock_dscheck(cidx, 0)
      return 0

   limits = get_process_limits(pgrec['command'], specialist, logact)
   if not limits:
      if pgrec['hostname'] and (logact&PgLOG.EMEROL) == PgLOG.EMEROL:
         host = PgLOG.get_host(1)
         if PgLOG.check_process_host(pgrec['hostname'], host, 'I'):
            PgLOG.pglog("Chk{}: {} is not configured properly to run on {} for {}".format(cidx, pgrec['command'], host, specialist), logact)
      return 0

   lidx = get_process_host(limits, pgrec['hostname'], pgrec['command'], pgrec['action'], logact)
   if lidx < 0 or skip_dscheck_record(pgrec, host, logact): return 0
   cmd = "pgstart_{} ".format(specialist) if PgLOG.PGLOG['CURUID'] == PgLOG.PGLOG['RDAUSER'] else ""
   if not PgUtil.pgcmp(host, PgLOG.PGLOG['PBSNAME'], 1):
      if reach_dataset_limit(pgrec): return 0
      cmd += get_specialist_shell(specialist) + 'qsub '
      options = get_pbs_options(pgrec, dlimit, logact)
      if options:
         cmd += options
      elif pgrec['status'] == 'E':
         return 0
      bstr = " in {} Queue {} ".format(PgLOG.PGLOG['PBSNAME'], pgrec['pbsqueue'])
   else:
      bstr = ""
      cmd += "rdasub -bg "

   if pgrec['workdir']:
      if pgrec['workdir'].find('$') > -1:
         cmd += "-cwd '{}' ".format(pgrec['workdir'])
      else:
         cmd += "-cwd {} ".format(pgrec['workdir'])
   else:
      cmd += "-cwd '$HOME' "

   chkcmd = pgrec['command']
   cmd += "-cmd " + chkcmd
   if pgrec['argv']:
      argv = pgrec['argv']
      if pgrec['argextra']: argv += pgrec['argextra']
      cmd += ' ' + argv + PgCMD.append_delayed_mode(chkcmd, argv)
      chkcmd += ' ' + argv

   PgLOG.pglog("Chk{}: issues '{}' onto {} for {}".format(cidx, chkcmd, host, pgrec['specialist']), PgLOG.LOGWRN)
   PgLOG.PGLOG['ERR2STD'] = ['chmod: changing']
   cstr = PgLOG.pgsystem(cmd, logact&(~PgLOG.EXITLG), 278)  # 2+4+16+256
   PgLOG.PGLOG['ERR2STD'] = []
   pid = 0
   if cstr:
      lines = cstr.split('\n')
      for line in lines:
         if not line: continue
         ms = re.match(r'^Job <(\d+)> is submitted', line)
         if ms:
            pid = int(ms.group(1))
            break
         ms = re.match(r'^(\d+)\.casper-pbs', line)
         if ms:
            pid = int(ms.group(1))
            break
         ms = re.match(r'^Submitted batch job (\d+)', line)
         if ms:
            pid = int(ms.group(1))
            break
   if not pid:
      if PgLOG.PGLOG['SYSERR']:
         if PgLOG.PGLOG['SYSERR'].find('Job not submitted') > -1:
            cstr = "submit job"
         elif PgLOG.PGLOG['SYSERR'].find('working directory') > -1:
            cstr = "change working directory"
         else:
            cstr = "execute"
         PgLock.lock_dscheck(cidx, 0)
         return PgLOG.pglog("Chk{}: {} Failed {} on {}{}{}\n{}".format(cidx, PgCMD.get_command_info(pgrec),
                            cstr, PgLOG.PGLOG['HOSTNAME'], bstr, PgUtil.curtime(1), PgLOG.PGLOG['SYSERR']),
                            PgLOG.LOGWRN|PgLOG.FRCLOG)

   PgLOG.pglog("Chk{}: {} started on {}{}{}".format(cidx, PgCMD.get_command_info(pgrec), 
               PgLOG.PGLOG['HOSTNAME'], bstr, PgUtil.curtime(1)), PgLOG.LOGWRN|PgLOG.FRCLOG)
   return fill_dscheck_info(pgrec, pid, host, logact)

#
# get qsub shell command
#
def get_specialist_shell(specialist):

   if specialist not in SHELLS:
      pgrec = PgDBI.pgget("dssgrp", "shell_flag", "logname = '{}'".format(specialist))
      if pgrec and pgrec['shell_flag'] == 'B':
         SHELLS[specialist] = 'bash'
      else:
         SHELLS[specialist] = 'tcsh'

   return SHELLS[specialist]

#
# get and cache process limit for a given dsid
#
def get_dataset_limit(dsid):

   if dsid in DSLMTS: return DSLMTS[dsid]

   pgrec = PgDBI.pgget('dslimit', 'processlimit', "dsid = '{}'".format(dsid))
   dslmt = 45
   if pgrec:
      dslmt = pgrec['processlimit']
   elif 'default' in DSLMTS:
      dslmt = DSLMTS['default']
   else:
      pgrec = PgDBI.pgget('dslimit', 'processlimit', "dsid = 'all'")
      if pgrec: DSLMTS['default'] = dslmt = pgrec['processlimit']
   DSLMTS[dsid] = dslmt

   return DSLMTS[dsid]
   
#
# check if reaching running limit for a specified dataset
#
def reach_dataset_limit(pgrec):

   if pgrec['command'] != 'dsrqst': return 0
   dsid = pgrec['dsid']
   if dsid and pgrec['action'] in ['BR', 'SP', 'PP']:
      dslmt = get_dataset_limit(dsid)
      lmt = PgDBI.pgget('dscheck', '', "dsid = '{}' AND status <> 'C' AND action IN ('BR', 'SP', 'PP')".format(dsid))
      if lmt > dslmt:
         PgLock.lock_dscheck(pgrec['cindex'], 0)
         return 1
   return 0

#
# get and cache request limit for a given given email
#
def get_user_limit(email):

   if email in EMLMTS: return EMLMTS[email]

   emlmts = [20, 10, 36]
   flds = 'maxrqstcheck, maxpartcheck'
   pgrec = PgDBI.pgget('userlimit', flds, "email = '{}'".format(email))
   if pgrec:
      emlmts = [pgrec['maxrqstcheck'], pgrec['maxpartcheck']] 
   elif 'default' in EMLMTS:
      emlmts = EMLMTS['default']
   else:
      pgrec = PgDBI.pgget('userlimit', flds, "email = 'all'".format(email))
      if pgrec:
         EMLMTS['default'] = emlmts = [pgrec['maxrqstcheck'], pgrec['maxpartcheck']] 
   EMLMTS[email] = emlmts.copy()

   return EMLMTS[email]
   
#
# check if reaching running limit for a specified dataset
#
def reach_dataset_limit(pgrec):

   if pgrec['command'] != 'dsrqst': return 0
   dsid = pgrec['dsid']
   if dsid and pgrec['action'] in ['BR', 'SP', 'PP']:
      dslmt = get_dataset_limit(dsid)
      lmt = PgDBI.pgget('dscheck', '', "dsid = '{}' AND status <> 'C' AND action IN ('BR', 'SP', 'PP')".format(dsid))
      if lmt > dslmt:
         PgLock.lock_dscheck(pgrec['cindex'], 0)
         return 1
   return 0

#
# check and return the time limit in seconds before a planned system down for given hostname
#
def get_system_down_limit(hostname, logact = 0):

   dlimit = 0
   down = PgDBI.get_system_downs(hostname, logact)
   if down['start']:
      dlimit = down['start'] - down['curtime'] - 2*PgSIG.PGSIG['CTIME']
      if dlimit < PgOPT.PGOPT['minlimit']: dlimit = -1

   return dlimit

#
# check and get the option string for submit a PBS job
#
def get_pbs_options(pgrec, limit = 0, logact = 0):

   opttime = 0
   qoptions = build_dscheck_options(pgrec, 'qoptions', 'PBS')
   qname = get_pbsqueue_option(pgrec)
   maxtime = max_batch_time(qname)
   runtime = PBSTIMES['default']

   if qoptions:
      ms = re.match(r'^(-.+)/(-.+)$', qoptions)
      if ms: qoptions = ms.group(2 if pgrec['otype'] == 'P' else 1)

      ms = re.search(r'-l\s+\S*walltime=([\d:-]+)', qoptions)
      if ms:
         optval = ms.group(1)
         vcs = optval.split(':')
         vcl = len(vcs)
         vds = vcs[0].split('-')
         opttime = 3600*int(vds[0])
         if len(vds) > 1:
            opttime *= 24
            opttime += 3600*int(vds[1])
         if vcl > 1:
            opttime += 60*int(vcs[1])
            if vcl > 2: opttime += int(vcs[2])
      runtime = opttime
      qoptions += ' '

   if limit > 0 and runtime > limit: runtime = limit
   if runtime > maxtime: runtime = maxtime
   if runtime != opttime and runtime != PBSTIMES['default']:
      optval = "walltime={}:{:02}:{:02}".format(int(runtime/3600), int(runtime/60)%60, runtime%60)
      if opttime:
         if runtime < opttime: qoptions = re.sub(r'walltime=[\d:-]+', optval, qoptions)
      elif qoptions.find('-l ') > -1:
         qoptions = re.sub(r'-l\s+', "-l {},".format(optval), qoptions)
      else:
         qoptions += "-l " + optval

   if pgrec['modules']:
      options = build_dscheck_options(pgrec, 'modules', 'PBS')
      if options: qoptions += "-mod {} ".format(options)
   if pgrec['environments']:
      options = build_dscheck_options(pgrec, 'environments', 'PBS')
      if options: qoptions += "-env {} ".format(options)

   if qname: qoptions += "-q {} ".format(qname)

   return qoptions

#
# check rda queue for pending jobs to switch PBS queue if needed
#
def get_pbsqueue_option(pgrec):

   qname = pgrec['pbsqueue']
   if qname in PBSQUEUES: return PBSQUEUES[qname]

   return None

#
#  build individual option string for given option name 
#
def build_dscheck_options(pgcheck, optname, optstr = None):

   options = pgcheck[optname]
   if not options or options == 'default': return ''
   if not re.match(r'^!', options): return options
   cidx = pgcheck['cindex']
   # reget the option field to see if it is processed
   pgrec = PgDBI.pgget('dscheck', optname, 'cindex = {}'.format(cidx))
   if not pgrec or options != pgrec[optname]: return options

   record = {}
   errmsg = ''
   record[optname] = options = PgCMD.get_dynamic_options(options[1:], pgcheck['oindex'], pgcheck['otype'])
   if not options and PgLOG.PGLOG['SYSERR']:
      record['status'] = pgcheck['status'] = 'E'
      record['pid'] = 0
      record['tcount'] = pgcheck['tcount'] + 1
      if not optstr: optstr = optname.capitalize()
      errmsg = "Chk{}: Fail to build {} Options, {}".format(cidx, optstr, PgLOG.PGLOG['SYSERR'])
   PgDBI.pgupdt("dscheck", record, "cindex = {}".format(cidx))
   if errmsg:
      pgrqst = None
      if pgcheck['otype'] == 'R':
         ridx = pgcheck['oindex']
         pgrqst = PgDBI.pgget('dsrqst', '*', 'rindex = {}'.format(ridx))
         if pgrqst:
            record = {}
            record['status'] = PgOPT.send_request_email_notice(pgrqst, errmsg, 0, 'E')
            record['ecount'] = pgrqst['ecount'] + 1
            PgDBI.pgupdt("dsrqst", record, "rindex = {}".format(ridx), PgOPT.PGOPT['errlog'])
            errmsg = ''
      elif pgcheck['otype'] == 'P':
         pidx = pgcheck['oindex']
         pgpart = PgDBI.pgget('ptrqst', 'rindex', 'pindex = {}'.format(pidx))
         if pgpart:
            PgDBI.pgexec("UPDATE ptrqst SET status = 'E' WHERE pindex = {}".format(pidx))
            ridx = pgpart['rindex']
            pgrqst = PgDBI.pgget('dsrqst', '*', 'rindex = {}'.format(ridx))
            if pgrqst and pgrqst['status'] != 'E':
               record = {}
               record['status'] = PgOPT.send_request_email_notice(pgrqst, errmsg, 0, 'E')
               record['ecount'] = pgrqst['ecount'] + 1
               PgDBI.pgupdt("dsrqst", record, "rindex = {}".format(ridx), PgOPT.PGOPT['errlog'])
               errmsg = ''
      if errmsg: PgLOG.pglog(errmsg, PgOPT.PGOPT['errlog'])
   return options

#
# fill up dscheck record in case the command does not do it itself
#
def fill_dscheck_info(ckrec, pid, host, logact = 0):

   chkcnd = "cindex = {}".format(ckrec['cindex'])
   PgDBI.pgexec("UPDATE dscheck SET tcount = tcount+1 WHERE " + chkcnd, logact)
   if pid and PgLock.lock_host_dscheck(ckrec['cindex'], pid, host, logact) <= 0: return 1 # under processing

   record = {}
   stat = 'R'
   if pid:
      record['pid'] = pid
      if host == PgLOG.PGLOG['PBSNAME']:
         info = PgSIG.get_pbs_info(pid, 0, logact, 2)
         if info: stat = info['State']
      else:
         record['runhost'] = PgLOG.PGLOG['HOSTNAME']
         record['bid'] = 0
   else:
      stat = 'F'
   record['status'] = stat            

   record['stttime'] = record['subtime'] = record['chktime'] = int(time.time())
   pgrec = PgDBI.pgget("dscheck", "status, stttime", chkcnd, logact)
   if not pgrec: return 0
   if pgrec['status'] != ckrec['status'] or pgrec['stttime'] > ckrec['stttime']: return 1
   if not pid and PgLock.lock_dscheck(ckrec['cindex'], 0) <= 0: return 1

   return PgDBI.pgupdt("dscheck", record, chkcnd, logact)

#
# return 1 to skip running if the dscheck record is not ready; 0 otherwise
#
def skip_dscheck_record(pgrec, host, logact = 0):
 
   workdir = pgrec['workdir']
   if workdir and workdir.find('$') > -1: workdir = '' 

   if PgFile.check_host_down(workdir, host, logact): return 1
   if pgrec['command'] == "dsrqst":
      if PgFile.check_host_down(PgLOG.PGLOG['RQSTHOME'], host, logact): return 1
   elif pgrec['command'] == "dsupdt" or pgrec['command'] == "dsarch":
      if PgFile.check_host_down(PgLOG.PGLOG['DSDHOME'], host, logact): return 1

   newrec = PgDBI.pgget("dscheck", "pid, status, stttime, tcount", "cindex = {}".format(pgrec['cindex']), logact)
   if(not newrec or newrec['pid'] > 0 or newrec['status'] != pgrec['status'] or
      newrec['stttime'] > pgrec['stttime'] or newrec['tcount'] > pgrec['tcount']): return 1
   if PgLock.lock_dscheck(pgrec['cindex'], 1) <= 0: return 1

   if pgrec['subtime'] or pgrec['stttime']:
      newrec = {'stttime' : 0, 'subtime' : 0, 'runhost' : '', 'bid' : 0}
      (newrec['ttltime'], newrec['quetime']) = PgCMD.get_dscheck_runtime(pgrec)
      if not PgDBI.pgupdt("dscheck", newrec, "cindex = {}".format(pgrec['cindex']), logact): return 1
   
   return 0

#
# start recording Queued reuqests to checks
#
def start_dsrqsts(cnd, logact = 0):

   check_dsrqst_locks(cnd, logact)
#   if CHKHOST['chkhost']: return 1
   if not CHKHOST['chkhost']: email_dsrqsts(cnd, logact)
   purge_dsrqsts(cnd, logact)
   rcnd = cnd
   rcnd += ("status = 'Q' AND rqsttype <> 'C' AND (pid = 0 OR pid < ptcount) AND " +
            "einfo IS NULL ORDER BY priority, rindex")
   pgrecs = PgDBI.pgmget("dsrqst", "*",  rcnd, logact)
   cnt = (len(pgrecs['rindex']) if pgrecs else 0)
   ccnt = PgDBI.pgget("dscheck", '', "status = 'C'", logact)
   pcnt = PgDBI.pgget("dscheck", '', "status = 'P'", logact)
   if (ccnt+pcnt) > PgOPT.PGOPT['waitlimit']:
      if cnt: PgLOG.pglog("{}/{} Checks are Waiting/Pending; Add new dscheck records {} later".format(ccnt, pcnt, PgLOG.PGLOG['HOSTNAME']),
                          PgLOG.LOGWRN|PgLOG.FRCLOG)
   rcnt = PgOPT.PGOPT['waitlimit']-ccnt-pcnt
   if cnt == 0:
      acnt = 0
      cnts = start_dsrqst_partitions(None, rcnt, logact)
      rcnt = cnts[0]
      pcnt = cnts[1]
   else:
      tcnt = cnt
      if cnt > rcnt: cnt = rcnt
      if cnt > 1: PgLOG.pglog("Try to add dschecks for {} DSRQST records on {}".format(cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)
   
      i = acnt = ccnt = pcnt = rcnt = 0
      while i < tcnt and ccnt < cnt:
         pgrec = PgUtil.onerecord(pgrecs, i)
         i += 1
         if pgrec['ptcount'] == 0 and validate_dsrqst_partitions(pgrec, logact):
            acnt += add_dsrqst_partitions(pgrec, logact)
         elif pgrec['ptcount'] < 2:
            rcnt += start_one_dsrqst(pgrec, logact)
         else:
            cnts = start_dsrqst_partitions(pgrec, (cnt-ccnt), logact)
            rcnt += cnts[0]
            pcnt += cnts[1]
         ccnt += (acnt+pcnt+rcnt)

   if rcnt > 1: PgLOG.pglog("build {} requests on {}".format(rcnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)
   if pcnt > 1: PgLOG.pglog("build {} request partitions on {}".format(pcnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)
   if acnt > 1: PgLOG.pglog("Add partitions to {} requests on {}".format(acnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

   return rcnt

#
# validate a given request if ok to do partitions
#
def validate_dsrqst_partitions(pgrec, logact = 0):

   pgctl = PgCMD.get_dsrqst_control(pgrec, logact)
   if pgctl and (pgctl['ptlimit'] or pgctl['ptsize']): return True

   record = {'ptcount' : 1}
   pgrec['ptcount'] = 1
   if pgrec['ptlimit']: pgrec['ptlimit'] = record['ptlimit'] = 0
   if pgrec['ptsize']: pgrec['ptsize'] = record['ptsize'] = 0

   PgDBI.pgupdt('dsrqst', record, "rindex = {}".format(pgrec['rindex']), logact)
   return False

#
# call given command to evaluate dynamically the dscheck.qoptions
#
def set_dscheck_options(chost, cnd, logact):

   if chost not in DOPTHOSTS: return
   qcnt = 0
   skipcmds = DOPTHOSTS[chost]
   pgrecs = PgDBI.pgmget("dscheck", "*", cnd + "pid = 0 AND status = 'C' AND LEFT(qoptions, 1) = '!'", logact)
   cnt = len(pgrecs['cindex']) if pgrecs else 0
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      if skipcmds and pgrec['qoptions'] in skipcmds: continue   # skip
      if PgLock.lock_dscheck(pgrec['cindex'], 1) <= 0: continue
      qoptions = build_dscheck_options(pgrec, 'qoptions', 'PBS')
      if not qoptions and pgrec['status'] == 'E': continue  # failed evaluating qoptions
      record = {'pid' : 0, 'qoptions': qoptions}
      qcnt += PgDBI.pgupdt('dscheck', record, "cindex = {}".format(pgrec['cindex']), PgOPT.PGOPT['errlog'])

   if qcnt and cnt > 1: PgLOG.pglog("{} of {} DSCHECK PBS options Dynamically set on {}".format(qcnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

#
# add a new dscheck record if a given request record is due
#
def start_one_dsrqst(pgrec, logact = 0):

   if PgDBI.pgget("dscheck", "", "oindex = {} AND command = 'dsrqst' AND action = 'BR'".format(pgrec['rindex']), logact): return 0

   pgctl = PgCMD.get_dsrqst_control(pgrec, logact)
   if pgctl:
      if 'qoptions' in pgctl and pgctl['qoptions']:
         ms = re.match(r'^(-.+)/(-.+)$', pgctl['qoptions'])
         if ms: pgctl['qoptions'] = ms.group(1)
   argv = "{} BR -RI {} -b -d".format(pgrec['dsid'], pgrec['rindex'])
   return add_one_dscheck(pgrec['rindex'], 'R', "dsrqst", pgrec['dsid'], "BR",
                          '', pgrec['specialist'], argv, pgrec['email'], pgctl, logact)

#
# add a dscheck record for a given request to setup partitions
#
def add_dsrqst_partitions(pgrec, logact = 0):

   if PgDBI.pgget("dscheck", "", "oindex = {} AND command = 'dsrqst'".format(pgrec['rindex']), logact): return 0

   pgctl = PgCMD.get_dsrqst_control(pgrec, logact)
   if pgctl:
      if 'qoptions' in pgctl and pgctl['qoptions']:
         ms =re.match(r'^(-.+)/(-.+)$', pgctl['qoptions'])
         if ms: pgctl['qoptions'] = ms.group(1)
   argv = "{} SP -RI {} -NP -b -d".format(pgrec['dsid'], pgrec['rindex'])
   return add_one_dscheck(pgrec['rindex'], 'R', "dsrqst", pgrec['dsid'], 'SP',
                          '', pgrec['specialist'], argv, pgrec['email'], pgctl, logact)

#
# add multiple dscheck records of partitions for a given request
#
def start_dsrqst_partitions(pgrqst, ccnt, logact = 0):

   cnts = [0, 0]
   if pgrqst:
      rindex = pgrqst['rindex']
      cnd = "rindex = {} AND status = ".format(rindex)
      if pgrqst['pid'] == 0:
         cnt = PgDBI.pgget("ptrqst", "", cnd + "'E'", logact)
         if cnt > 0 and (pgrqst['ecount'] + cnt) <= PgOPT.PGOPT['PEMAX']:
            # set Error partions back to Q
            PgDBI.pgexec("UPDATE ptrqst SET status = 'Q' WHERE {}'E'".format(cnd), PgOPT.PGOPT['extlog'])
   else:
      rindex = 0
      cnd = "status = "
   pgrecs = PgDBI.pgmget("ptrqst", "*", cnd + "'Q' AND pid = 0 ORDER by pindex", logact)
   cnt = len(pgrecs['pindex']) if pgrecs else 0
   if cnt > 0:
      if cnt > ccnt: cnt = ccnt
      pgctl = PgCMD.get_dsrqst_control(pgrqst, logact) if pgrqst else None
      for i in range(cnt):
         pgrec = PgUtil.onerecord(pgrecs, i)
         if pgrec['rindex'] != rindex:
            rindex = pgrec['rindex']
            pgrqst = PgDBI.pgget("dsrqst", "*", "rindex = {}".format(rindex), logact)
            if pgrqst: pgctl = PgCMD.get_dsrqst_control(pgrqst, logact)
         if not pgrqst:  # request missing
              PgDBI.pgdel('ptrqst', "rindex = {}".format(rindex))
              continue
         if pgrec['ptcmp'] == 'Y':
            pgptctl = None
         else:
            pgptctl = PgCMD.get_partition_control(pgrec, pgrqst, pgctl, logact)
            if pgptctl:
               if 'qoptions' in pgptctl and pgptctl['qoptions']:
                  ms = re.match(r'^(-.+)/(-.+)$', pgptctl['qoptions'])
                  if ms: pgptctl['qoptions'] = ms.group(2)
         if PgDBI.pgget("dscheck", "", "oindex = {} AND command = 'dsrqst' AND action = 'PP'".format(pgrec['pindex']), logact): continue
         argv = "{} PP -PI {} -RI {} -b -d".format(pgrqst['dsid'], pgrec['pindex'], pgrqst['rindex'])
         cnts[1] += add_one_dscheck(pgrec['pindex'], 'P', "dsrqst", pgrqst['dsid'], "PP",
                                    '', pgrqst['specialist'], argv, pgrqst['email'], pgptctl, logact)

   elif pgrqst and pgrqst['pid'] == 0 and pgrqst['ptcount'] == PgDBI.pgget("ptrqst", "", cnd + " 'O'", logact):
      cnts[0] = start_one_dsrqst(pgrqst, logact)

   return cnts

#
#  check long procssing reuqests and unlock the processes that are aborted
#
def check_dsrqst_locks(cnd, logact = 0):

   ltime = int(time.time())
   lochost = PgLOG.PGLOG['HOSTNAME']
   cnd += "pid > 0 AND "
   dtime = ltime - PgSIG.PGSIG['DTIME']
   ctime = ltime - PgSIG.PGSIG['CTIME']
   rtime = ltime - PgSIG.PGSIG['RTIME']
   cnd += "locktime > 0 AND (locktime < {} OR locktime < {} AND lockhost = '{}' OR locktime < {} AND lockhost = 'rda_config')".format(ctime, dtime, lochost, rtime)
   check_partition_locks(cnd, ltime, logact)   # check partitions first

   pgrecs = PgDBI.pgmget("dsrqst", "rindex, lockhost, pid, locktime", cnd, logact)
   cnt = (len(pgrecs['rindex']) if pgrecs else 0)
   lcnt = 0
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      lmsg = "{}({}) at {} on {}".format(pgrec['lockhost'], pgrec['pid'], PgLOG.current_datetime(), PgLOG.PGLOG['HOSTNAME'])
      ridx = pgrec['rindex']
      if CHKHOST['chkhost'] or pgrec['lockhost'] == lochost:
         if PgLock.lock_request(ridx, 0) > 0:
            PgLOG.pglog("Rqst{}: unlocked {}".format(ridx, lmsg), PgLOG.LOGWRN)
            lcnt += 1
            continue
         if(PgDBI.pgexec("UPDATE dsrqst set locktime = {} WHERE rindex = {} AND pid = {}".format(ltime, ridx, pgrec['pid']), logact) and
            not PgDBI.pgget("dscheck", "", "oindex = {} AND command = 'dsrqst'".format(ridx))):
            PgLOG.pglog("Rqst{}: time updated for {}".format(ridx, lmsg), PgLOG.LOGWRN|PgLOG.FRCLOG)
      elif(not pgrec['lockhost'] or pgrec['lockhost'] == 'rda_config' or pgrec['lockhost'] == 'partition' and
           not PgDBI.pgget('ptrqst', '', "rindex = {} AND pid > 0".format(ridx), logact)):
         record = {'pid' : 0, 'lockhost' : ''}
         if PgDBI.pgupdt("dsrqst", record, "rindex = {} AND pid = {}".format(ridx, pgrec['pid']), logact):
            PgLOG.pglog("Rqst{}: unlocked {}".format(ridx, pgrec['lockhost'], pgrec['pid'], PgLOG.current_datetime(ltime)), PgLOG.LOGWRN)
            lcnt += 1
            continue
      elif (logact&PgLOG.EMEROL) == PgLOG.EMEROL:
         PgLOG.pglog("Rqst{}: time NOT updated for {} of {}".format(ridx, pgrec['lockhost'], pgrec['pid'], dscheck_runtime(pgrec['locktime'], ltime)), logact)

      RUNPIDS["{}{}".format(pgrec['lockhost'], pgrec['pid'])] = 1

   if cnt > 1: PgLOG.pglog("{} of {} DSRQST records unlocked on {}".format(lcnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

#
#  check long procssing reuqest partitions and unlock the processes that are aborted
#
def check_partition_locks(cnd, ltime, logact = 0):

   pgrecs = PgDBI.pgmget("ptrqst", "pindex, rindex, lockhost, pid, locktime", cnd, (logact&~PgLOG.LGEREX))
   cnt = (len(pgrecs['pindex']) if pgrecs else 0)
   lcnt = 0
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      lmsg = "{}({}) at {} on {}".format(pgrec['lockhost'], pgrec['pid'], PgLOG.current_datetime(), PgLOG.PGLOG['HOSTNAME'])
      pidx = pgrec['pindex']
      if CHKHOST['chkhost'] or pgrec['lockhost'] == PgLOG.PGLOG['HOSTNAME']:
         if PgLock.lock_partition(pidx, 0) > 0:
            PgLOG.pglog("RPT{}: unlocked {}".format(pidx, lmsg), PgLOG.LOGWRN)
            lcnt += 1
            continue
         if(PgDBI.pgexec("UPDATE ptrqst set locktime = {} WHERE pindex = {} AND pid = {}".format(ltime, pidx, pgrec['pid']), logact) and
            PgDBI.pgexec("UPDATE dsrqst set locktime = {} WHERE rindex = {}".format(ltime, pgrec['rindex']), logact) and
            not PgDBI.pgget("dscheck", "", "oindex = {} AND command = 'dsrqst' AND otype = 'P'".format(pidx))):
            PgLOG.pglog("RPT{}: time updated for {}".format(pidx, lmsg), PgLOG.LOGWRN)
      elif not pgrec['lockhost'] or pgrec['lockhost'] == 'rda_config':
         record = {'pid' : 0, 'lockhost' : ''}
         if PgDBI.pgupdt("ptrqst", record, "pindex = {} AND pid = {}".format(pidx, pgrec['pid']), logact):
            PgLOG.pglog("RPT{}: unlocked {}".format(pidx, lmsg), PgLOG.LOGWRN)
            lcnt += 1
            continue
      elif (logact&PgLOG.EMEROL) == PgLOG.EMEROL:
         PgLOG.pglog("RPT{}: time NOT updated for {} of {}".format(pidx, dscheck_runtime(pgrec['locktime'], ltime), lmsg), logact)

      RUNPIDS["{}{}".format(pgrec['lockhost'], pgrec['pid'])] = 1

   if cnt > 1: PgLOG.pglog("{} of {} DSRQST partitions unlocked on {}".format(lcnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

#
#  check dsrqsts and purge them if done already
#
def purge_dsrqsts(cnd, logact = 0):

   (sdate, stime) = PgUtil.get_date_time()
   cnd += "(status = 'P' AND (date_purge IS NULL OR date_purge < '{}' OR date_purge = '{}' AND time_purge < '{}')".format(sdate, sdate, stime)
   cnd += " OR status = 'O' AND (date_purge < '{}' OR date_purge = '{}' AND time_purge < '{}')) ORDER BY rindex".format(sdate, sdate, stime)                   
   pgrecs = PgDBI.pgmget("dsrqst", "rindex, dsid, email, specialist", cnd, logact)
   cnt = (len(pgrecs['rindex']) if pgrecs else 0)
   pgctl = {'qoptions' : "-l walltime=1:00:00"}
   pcnt = 0
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      ridx = pgrec['rindex']
      if PgDBI.pgget("dscheck", "", "oindex = {} AND command = 'dsrqst'".format(ridx), logact): continue
      argv = "{} PR -RI {} -b -d".format(pgrec['dsid'], ridx)
      add_one_dscheck(ridx, 'R', 'dsrqst', pgrec['dsid'], 'PR', '',
                      pgrec['specialist'], argv, pgrec['email'], pgctl, logact)

#
#  check dsrqsts and send saved email
#
def email_dsrqsts(cnd, logact = 0):

   emlact = PgLOG.LOGWRN|PgLOG.FRCLOG
   if logact and (logact&PgLOG.EMEROL) == PgLOG.EMEROL: emlact |= PgLOG.EMEROL
   cnd += "pid = 0 AND einfo IS NOT NULL"
   pgrecs = PgDBI.pgmget("dsrqst", "rindex, ptcount, einfo", cnd, logact)
   cnt = (len(pgrecs['rindex']) if pgrecs else 0)
   ecnt = 0
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      ridx = pgrec['rindex']
      if PgLock.lock_request(ridx, 1) <= 0: continue
      einfo = verify_request_einfo(ridx, pgrec['ptcount'], pgrec['einfo'], logact)
      if einfo:
         sent = 1 if (PgLOG.send_customized_email("Rqst{}".format(ridx), einfo, emlact) and
                      PgDBI.pgexec("UPDATE dsrqst set einfo = NULL WHERE rindex = {}".format(ridx), logact)) else -1
      else:
         sent = 0

      PgLock.lock_request(ridx, 0)
      if sent == -1: break
      ecnt += sent

   if cnt > 1: PgLOG.pglog("{} of {} DSRQST emails sent on {}".format(ecnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

#
# veriy email info for partition errors
# retrun None if not all partitions finished
#
def verify_request_einfo(ridx, ptcnt, einfo, logact = 0): 

   # no further checking if no partitionseinfo is empty   
   if ptcnt < 2 or not einfo: return einfo   
   # partition processes are not all done yet
   if PgDBI.pgget("ptrqst", "", "rindex = {} AND (pid > 0 OR status = 'R')".format(ridx), logact): return None

   pkey = ["<PARTERR>", "<PARTCNT>"]
   # einfo does not contain partition error key
   if einfo.find(pkey[0]) < 0: return einfo
   einfo = re.sub(pkey[0], '', einfo)
   ecnt = PgDBI.pgget("ptrqst", "", "rindex = {} AND status = 'E'".format(ridx), logact)   
   cbuf = "{} of {}".format(ecnt, ptcnt)   
   einfo = re.sub(pkey[1], cbuf, einfo)

   return einfo   

#
# start recording due updates to checks
#
def start_dsupdts(cnd, logact = 0):

   ctime = PgUtil.curtime(1)
   check_dsupdt_locks(cnd, logact)
   if not CHKHOST['chkhost']:
      email_dsupdt_controls(cnd, logact)
      email_dsupdts(cnd, logact)

   cnd += "pid = 0 and cntltime <= '{}' and action > '' AND einfo IS NULL ORDER by cntltime".format(ctime)
   pgrecs = PgDBI.pgmget("dcupdt", "*", cnd, logact)
   cnt = (len(pgrecs['cindex']) if pgrecs else 0)
   ucnt = 0
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      if PgDBI.pgget("dscheck", "pid, lockhost", "oindex = {} AND command = 'dsupdt'".format(pgrec['cindex']), logact): continue
      if pgrec['pindex'] and not PgOPT.valid_data_time(pgrec): continue
      argv = "{} {} -CI {} -b -d".format(pgrec['dsid'], pgrec['action'], pgrec['cindex'])
      if not add_one_dscheck(pgrec['cindex'], 'C', "dsupdt", pgrec['dsid'], pgrec['action'],
                             '', pgrec['specialist'], argv, None, pgrec, logact): break
      ucnt += 1

   if cnt > 1: PgLOG.pglog("update {} of {} DSUPDT controls on {}".format(ucnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)
   return ucnt

#
# check if the parent update control is finished
#
def parent_not_finished(pgrec):

   freq = [0, 0, 0]
   ms = re.match(r'^(\d+)([YMWDH])$', pgrec['frequency'], re.I)
   if ms:
      val = int(ms.group(1))
      unit = ms.group(2).upper()
      if not val: return 0
      if unit == 'Y':
         freq[0] = val
      elif unit == 'M':
         freq[1] = val
      elif unit == 'W':
         freq[2] = 7 * val
      elif unit == 'D':
         freq[2] = val
      elif unit == 'H':    # update frequency is hourly controlled
         freq.append(val)
   else:
      ms = re.match(r'^(\d+)M/(\d+)', pgrec['frequency'], re.I)
      if ms:
         val = int(ms.group(1))
         nf = int(ms.group(2))
         if nf < 2 or nf > 10 or (30%nf): return 0
         freq = [0, val, 0, 0, 0, 0, nf]    # number of fractions in a month

   dtime = PgUtil.adddatetime(pgrec['datatime'], freq[0], freq[1], freq[2], freq[3], freq[4], freq[5], freq[6])
   if PgDBI.pgget("dcupdt", "", "cindex = {} AND datatime < '{}'".format(pgrec['pindex'], dtime), PgOPT.PGOPT['extlog']):
      return 1
   else:
      return 0

#
#  check long procssing updates and unlock the processes that are aborted
#
def check_dsupdt_locks(ocnd, logact = 0):

   ltime = int(time.time())
   lochost = PgLOG.PGLOG['HOSTNAME']
   dtime = ltime - PgSIG.PGSIG['DTIME']
   cnd = ocnd + "pid > 0 AND "
   ctime = ltime - 4*PgSIG.PGSIG['CTIME']
   rtime = ltime - PgSIG.PGSIG['RTIME']
   cnd += "chktime > 0 AND (chktime < {} OR chktime < {} AND lockhost = '{}' OR chktime < {} AND lockhost = 'rda_config')".format(ctime, dtime, lochost, rtime)

   pgrecs = PgDBI.pgmget("dcupdt", "cindex, lockhost, pid, chktime", cnd, logact)
   cnt = (len(pgrecs['cindex']) if pgrecs else 0)
   lcnt = 0
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      lmsg = "{}({}) at {} on {}".format(pgrec['lockhost'], pgrec['pid'], PgLOG.current_datetime(), PgLOG.PGLOG['HOSTNAME'])
      idx = pgrec['cindex']
      if CHKHOST['chkhost'] or pgrec['lockhost'] == lochost:
         if PgLock.lock_update_control(idx, 0) > 0:
            PgLOG.pglog("UC{}: unlocked {}".format(idx, lmsg), PgLOG.LOGWRN)
            lcnt += 1
            continue
         if(PgDBI.pgexec("UPDATE dcupdt SET chktime = {} WHERE cindex = {} AND pid = {}".format(ltime, idx, pgrec['pid']), logact) and
            not PgDBI.pgget("dscheck", "", "oindex = {} AND command = 'dsupdt'".format(idx))):
            PgLOG.pglog("UC{}: time updated for {}".format(idx, lmsg), PgLOG.LOGWRN)
      elif not pgrec['lockhost'] or pgrec['lockhost'] == 'rda_config':
         record = {'pid' : 0, 'lockhost' : ''}
         if PgDBI.pgupdt("dcupdt", record, "cindex = {} AND pid = {}".format(idx, pgrec['pid']), logact):
            PgLOG.pglog("UC{}: unlocked {}".format(idx, lmsg), PgLOG.LOGWRN)
            lcnt += 1
            continue
      elif (logact&PgLOG.EMEROL) == PgLOG.EMEROL:
         PgLOG.pglog("UC{}: time NOT updated for {} of {}".format(idx, dscheck_runtime(pgrec['chktime'], ltime), lmsg), logact)

      RUNPIDS["{}{}".format(pgrec['lockhost'], pgrec['pid'])] = 1

   if cnt > 1: PgLOG.pglog("{} of {} DSUPDT Controls unlocked on {}".format(lcnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

   cnd = ocnd + "pid > 0 AND locktime > 0 AND "
   cnd += "(locktime < {} OR locktime < {} AND hostname = '{}' OR locktime < {} AND hostname = 'rda_config')".format(ctime, dtime, lochost, rtime)

   pgrecs = PgDBI.pgmget("dlupdt", "lindex, hostname, pid, locktime", cnd, logact)
   cnt = (len(pgrecs['lindex']) if pgrecs else 0)
   lcnt = 0
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      lmsg = "{}({}) at {} on {}".format(pgrec['hostname'], pgrec['pid'], PgLOG.current_datetime(), PgLOG.PGLOG['HOSTNAME'])
      idx = pgrec['lindex']
      if CHKHOST['chkhost'] or pgrec['hostname'] == lochost:
         if PgLock.lock_update(idx, None, 0) > 0:
            PgLOG.pglog("Updt{}: unlocked {}".format(idx, lmsg), PgLOG.LOGWRN)
            lcnt += 1
            continue
         PgDBI.pgexec("UPDATE dlupdt SET locktime = {} WHERE lindex = {} AND pid = {}".format(ltime, idx, pgrec['pid']), logact)
      elif not pgrec['hostname'] or pgrec['hostname'] == 'rda_config':
         record = {'pid' : 0, 'hostname' : ''}
         if PgDBI.pgupdt("dlupdt", record, "lindex = {} AND pid = {}".format(idx, pgrec['pid']), logact):
            PgLOG.pglog("Updt{}: unlocked {}".format(idx, lmsg), PgLOG.LOGWRN)
            lcnt += 1
            continue
      elif (logact&PgLOG.EMEROL) == PgLOG.EMEROL:
         PgLOG.pglog("Updt{}: time NOT updated for {} of {}".format(idx, dscheck_runtime(pgrec['locktime'], ltime), lmsg), logact)

      RUNPIDS["{}{}".format(pgrec['hostname'], pgrec['pid'])] = 1

   if cnt > 1: PgLOG.pglog("{} of {} DSUPDT Local Files unlocked on {}".format(lcnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

#
#  check dsupdts and send saved email
#
def email_dsupdt_controls(cnd, logact = 0):

   emlact = PgLOG.LOGWRN|PgLOG.FRCLOG
   if logact and (logact&PgLOG.EMEROL) == PgLOG.EMEROL: emlact |= PgLOG.EMEROL
   cnd += "pid = 0 AND einfo IS NOT NULL"
   pgrecs = PgDBI.pgmget("dcupdt", "cindex", cnd, logact)
   cnt = (len(pgrecs['cindex']) if pgrecs else 0)
   ecnt = 0
   for i in range(cnt):
      cidx = pgrecs['cindex'][i]
      if PgLock.lock_update_control(cidx, 1) <= 0: continue
      pgrec = PgDBI.pgget("dcupdt", "einfo", "cindex = {}".format(cidx), logact)
      if pgrec['einfo']:
         sent = 1 if (PgLOG.send_customized_email("UC{}".format(cidx), pgrec['einfo'], emlact) and
                      PgDBI.pgexec("UPDATE dcupdt set einfo = NULL WHERE cindex = {}".format(cidx), logact)) else -1
      else:
         sent = 0

      PgLock.lock_update_control(cidx, 0)
      if sent == -1: break
      ecnt += sent

   if cnt > 1: PgLOG.pglog("{} of {} DSUPDT Control emails sent on {}".format(ecnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

#
#  check dsupdts and send saved email
#
def email_dsupdts(cnd, logact = 0):

   emlact = PgLOG.LOGWRN|PgLOG.FRCLOG
   if logact and (logact&PgLOG.EMEROL) == PgLOG.EMEROL: emlact |= PgLOG.EMEROL
   cnd += "pid = 0 AND emnote IS NOT NULL"
   pgrecs = PgDBI.pgmget("dlupdt", "lindex, cindex", cnd, logact)
   cnt = (len(pgrecs['lindex']) if pgrecs else 0)
   ecnt = 0
   for i in range(cnt):
      idx = pgrecs['cindex'][i]
      if idx > 0 and PgDBI.pgget("dcupdt", "", "cindex = {} AND pid > 0".format(idx), logact): continue
      idx = pgrecs['lindex'][i]
      if PgLock.lock_update(idx, None, 1) <= 0: continue
      pgrec = PgDBI.pgget("dlupdt", "emnote", "lindex = {}".format(idx), logact)
      if pgrec['emnote']:
         sent = 1 if(PgLOG.send_customized_email("Updtidx", pgrec['emnote'], emlact) and
                     PgDBI.pgexec("UPDATE dlupdt set emnote = NULL WHERE lindex = {}".format(idx), logact)) else -1
      else:
         sent = 0

      PgLock.lock_update(idx, None, 0)
      if sent == -1: break
      ecnt += sent

   if cnt > 0: PgLOG.pglog("{} of {} DSUPDT emails sent on {}".format(ecnt, cnt, PgLOG.PGLOG['HOSTNAME']), PgLOG.WARNLG)

#
# create an dscheck record for a given command
#
def add_one_dscheck(oindex, otype, cmd, dsid, action, workdir, specialist, argv, remail, btctl, logact = 0):

   cidx = 0

   if len(argv) > 100:
      argextra = argv[100:]
      argv = argv[0:100]
   else:
      argextra = None

   record = {'command' : cmd, 'argv' : argv, 'specialist' : specialist, 'workdir' : workdir,
             'dsid' : dsid, 'action' : action, 'oindex' : oindex, 'otype' : otype}
   (record['date'], record['time']) = PgUtil.get_date_time()
   if argextra: record['argextra'] = argextra
   if 'PI' in PgOPT.params: record['pindex'] = PgOPT.params['PI'][0]
   if 'MC' in PgOPT.params and PgOPT.params['MC'][0] > 0: record['mcount'] = PgOPT.params['MC'][0]
   record.update(PgCMD.get_batch_options(btctl))

   if cmd == 'dsrqst' and remail:
      record['remail'] = remail
      if otype == 'P':
         pgcnt = PgDBI.pgget("dscheck", "", "remail = '{}' AND otype = 'P'" .format(remail), logact)
         if pgcnt >= get_user_limit(remail)[1]: return PgLOG.FAILURE
      elif action != 'PR':
         pgcnt = PgDBI.pgget("dscheck", "", "remail = '{}' AND otype = 'R'".format(remail), logact)
         if pgcnt >= get_user_limit(remail)[0]: return PgLOG.FAILURE

   if oindex and otype:
      pgrec = PgDBI.pgget('dscheck', '*', "oindex = {} AND otype = '{}'".format(oindex, otype), logact)
   else:
      pgrec = PgCMD.get_dscheck(cmd, argv, workdir, specialist, argextra, logact)

   if pgrec:
      return PgLOG.pglog("Chk{}: {} added already {} {}".format(pgrec['cindex'], PgCMD.get_command_info(pgrec), pgrec['date'], pgrec['time']), PgLOG.LOGWRN|PgLOG.FRCLOG)

   cidx = PgDBI.pgadd("dscheck", record, logact|PgLOG.AUTOID)
   if cidx:
      PgLOG.pglog("Chk{}: {} added {} {}".format(cidx, PgCMD.get_command_info(record), record['date'], record['time']), PgLOG.LOGWRN|PgLOG.FRCLOG)
   else:
      if oindex and otype:
         PgLOG.pglog("{}-{}-{}: Fail add check for {}".format(cmd, otype, oindex, specialist), PgLOG.LOGWRN|PgLOG.FRCLOG)
      else:
         PgLOG.pglog("{}: Fail add check for {}".format(cmd, specialist), PgLOG.LOGWRN|PgLOG.FRCLOG)

      time.sleep(PgSIG.PGSIG['ETIME'])
      return PgLOG.FAILURE

   return PgLOG.SUCCESS

#
# get dscheck status
#
def dscheck_status(stat):

   STATUS = {
      'C' : "Created",
      'D' : "Done",
      'E' : "Exit",
      'F' : "Finished",
      'H' : "Held",
      'I' : "Interrupted",
      'P' : "Pending",
      'Q' : "Queueing",
      'R' : "Run",
      'S' : "Suspended",
   }
   return (STATUS[stat] if stat in STATUS else "Unknown")

#
# validate given daemon control indices
#
def validate_daemons():

   if PgOPT.OPTS['DI'][2]&8: return     # already validated

   dcnt = len(PgOPT.params['DI']) if 'DI' in PgOPT.params else 0
   if not dcnt:
      if PgOPT.PGOPT['CACT'] == 'SD':
         if 'ND' not in PgOPT.params:
            PgOPT.action_error("Mode option -ND must be present to add new Daemon Control record")
         dcnt = PgOPT.get_max_count("HN", "CM")
         if dcnt > 0:
            PgOPT.params['DI'] = [0]*dcnt
      return
   i = 0
   while i < dcnt:
      val = PgOPT.params['DI'][i]
      if val:
         if not isinstance(val, int):
            if re.match(r'^(!|<|>|<>)$', val):
               if PgOPT.OPTS[PgOPT.PGOPT['CACT']][2] > 0:
                  PgOPT.action_error("Invalid condition '{}' of Daemon Control index".format(val))
               break
            PgOPT.params['DI'][i] = int(val)
      else:
         PgOPT.params['DI'][i] = 0
      i += 1
   if i >= dcnt: # normal daemon control index given
      for i in range(dcnt):
         val = PgOPT.params['DI'][i]
         if not val:
            if PgOPT.PGOPT['CACT'] != 'SD':
               PgOPT.action_error("Daemon Control Index 0 is not allowed\nUse Action SD with Mode option -ND to add new record")
            elif not PgOPT.params['ND']:
               PgOPT.action_error("Mode option -ND must be present to add new Daemon Control record")
            continue
         if i > 0 and val == PgOPT.params['DI'][i-1]: continue
         pgrec = PgDBI.pgget("dsdaemon", "specialist", "dindex = {}".format(val), PgOPT.PGOPT['extlog'])
         if not pgrec:
            PgOPT.action_error("Daemon Control Index '{}' is not in RDADB".format(val))
         elif(PgOPT.OPTS[PgOPT.PGOPT['CACT']][2] > 0 and PgOPT.params['LN'] != pgrec['specialist'] and
              PgLOG.PGLOG['CURUID'] != PgLOG.PGLOG['RDAUSER']):
            PgOPT.action_error("{}: must be {}, owner of Daemon Control Index {}".format(PgOPT.params['LN'], pgrec['specialist'], val))
   else: # found none-equal condition sign
      pgrec = PgDBI.pgmget("dsdaemon", "DISTINCT dindex",
                           PgDBI.get_field_condition("dindex", PgOPT.params['DI'], 0, 1), PgOPT.PGOPT['extlog'])
      if not pgrec: PgOPT.action_error("No Daemon Control matches given Index condition")
      PgOPT.params['DI'] = pgrec['dindex']

   PgOPT.OPTS['DI'][2] |= 8  # set validated flag

#
# validate given check indices
#
def validate_checks():

   if (PgOPT.OPTS['CI'][2]&8) == 8: return # already validated

   if 'CI' in PgOPT.params:
      cnt = len(PgOPT.params['CI'])
      i = 0
      while i < cnt:
         val = PgOPT.params['CI'][i]
         if val:
            if not isinstance(val, int):
               if re.match(r'^(!|<|>|<>)$', val):
                  if PgOPT.OPTS[PgOPT.PGOPT['CACT']][2] > 0:
                     PgOPT.action_error("Invalid condition '{}' of Check index".format(val))
                  break
               PgOPT.params['CI'][i] = int(val)
         else:
            PgOPT.params['CI'][i] = 0
         i += 1
      if i >= cnt: # normal check index given
         for i in range(cnt):
            val = PgOPT.params['CI'][i]
            if not val: PgOPT.action_error("Check Index 0 is not allowed")
            if i > 0 and val == PgOPT.params['CI'][i-1]: continue
            pgrec = PgDBI.pgget("dscheck", "specialist", "cindex = {}".format(val), PgOPT.PGOPT['extlog'])
            if not pgrec:
               PgOPT.action_error("Check Index '{}' is not in RDADB".format(val))
            elif(PgOPT.OPTS[PgOPT.PGOPT['CACT']][2] > 0 and PgOPT.params['LN'] != pgrec['specialist'] and
                 PgLOG.PGLOG['CURUID'] != PgLOG.PGLOG['RDAUSER']):
               PgOPT.action_error("{}: must be {}, owner of Check Index {}".format(PgOPT.params['LN'], pgrec['specialist'], val))
      else: # found none-equal condition sign
         pgrec = PgDBI.pgmget("dscheck", "cindex", PgDBI.get_field_condition("cindex", PgOPT.params['CI'], 0, 1), PgOPT.PGOPT['extlog'])
         if not pgrec: PgOPT.action_error("No Check matches given Index condition")
         PgOPT.params['CI'] = pgrec['cindex']

   PgOPT.OPTS['CI'][2] |= 8  # set validated flag

#
# validate given dataset IDs
#
def validate_datasets():

   if PgOPT.OPTS['DS'][2]&8: return    # already validated
   
   dcnt = len(PgOPT.params['DS'])
   for i in range(dcnt):
      dsid = PgOPT.params['DS'][i]
      if not dsid: PgOPT.action_error("Empty Dataset ID is not allowed")
      if i and dsid == PgOPT.params['DS'][i-1]: continue
      if not PgDBI.pgget("dataset", "", "dsid = '{}'".format(dsid), PgOPT.PGOPT['extlog']):
         PgOPT.action_error("Dataset '{}' is not in RDADB".format(dsid))

   PgOPT.OPTS['DS'][2] |= 8    # set validated flag
