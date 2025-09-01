#!/usr/bin/env python3
#
##################################################################################
#
#     Title: dscheck
#    Author: Zaihua Ji, zji@ucar.edu
#      Date: 09/28/2020
#            2025-02-05 transferred to package rda_python_dscheck from
#            https://github.com/NCAR/rda-utility-programs.git
#   Purpose: python utility program to check and start command saved in dscheck
#
#    Github: https://github.com/NCAR/rda-python-dscheck.git
#
##################################################################################
#
import os
import re
import sys
import time
from os import path as op
from rda_python_common import PgLOG
from rda_python_common import PgCMD
from rda_python_common import PgSIG
from rda_python_common import PgLock
from rda_python_common import PgUtil
from rda_python_common import PgFile
from rda_python_common import PgOPT
from rda_python_common import PgDBI
from . import PgCheck

ALLCNT = 0  # global counting variables

#
# main function to run dscheck
#
def main():

   aname = 'dscheck'
   PgLOG.set_help_path(__file__)
   PgOPT.parsing_input(aname)
   PgCheck.check_dscheck_options(PgOPT.PGOPT['CACT'], aname)
   start_action()

   if PgOPT.OPTS[PgOPT.PGOPT['CACT']][2]: PgLOG.cmdlog()  # log end time if not getting action
   
   PgLOG.pgexit(0)

#
# start action of dscheck
#
def start_action():

   global ALLCNT
   if PgOPT.PGOPT['CACT'] == 'AC':
      add_check_info()
   elif PgOPT.PGOPT['CACT'] == 'CH':
      check_host_connection()
   elif PgOPT.PGOPT['CACT'] == 'DL':
      if 'CI' in PgOPT.params:
         ALLCNT = len(PgOPT.params['CI'])
         delete_check_info()
      if 'DI' in PgOPT.params:
         ALLCNT = len(PgOPT.params['DI'])
         delete_daemon_info()
   elif PgOPT.PGOPT['CACT'] == 'EC':
      email_check_info()
   elif PgOPT.PGOPT['CACT'] == 'GC':
      get_check_info()
   elif PgOPT.PGOPT['CACT'] == 'GD':
      get_daemon_info()
   elif PgOPT.PGOPT['CACT'] == "IC":
      ALLCNT = len(PgOPT.params['CI'])
      interrupt_dschecks()
   elif PgOPT.PGOPT['CACT'] == 'PC':
      PgCMD.set_batch_options(PgOPT.params, 2, 1)
      if 'DM' in PgOPT.params:
         ALLCNT = 0
         handle_dschecks()
      else:
         process_dschecks()
   elif PgOPT.PGOPT['CACT'] == 'SD':
      ALLCNT = len(PgOPT.params['DI'])
      set_daemon_info()
   elif PgOPT.PGOPT['CACT'] == 'SO':
      PgCMD.set_batch_options(PgOPT.params, 2, 1)
      process_dscheck_options()
   elif PgOPT.PGOPT['CACT'] == "UL":
      ALLCNT = len(PgOPT.params['CI']) if 'CI' in PgOPT.params else 0
      unlock_checks()

#
# add a check for customized command
#
def add_check_info():

   cmd = PgOPT.params['CM'].pop(0)
   argstr = PgLOG.argv_to_string(PgOPT.params['CM'], 0)
   if 'AV' in PgOPT.params:
      if argstr: argstr += " "
      argstr += PgLOG.argv_to_string(PgOPT.params['AV'], 0)
   dsid = PgOPT.params['DS'][0] if 'DS' in PgOPT.params else None
   action = PgOPT.params['AN'][0] if 'AN' in PgOPT.params else None
   PgCMD.set_batch_options(PgOPT.params, 2, 1)
   specialist = PgOPT.params['SN'][0] if 'SN' in PgOPT.params else PgOPT.params['LN']
   workdir = PgOPT.params['WD'][0] if 'WD' in PgOPT.params else PgLOG.PGLOG['CURDIR']
   PgCheck.add_one_dscheck(0, '', cmd, dsid, action, workdir, specialist,
                           argstr, None, None, PgOPT.PGOPT['extlog'])

#
# delete dscheck daemon controls for given daemon control indices
#
def delete_daemon_info():

   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Delete {} dscheck daemon control{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   delcnt = 0
   for i in range(ALLCNT):
      delcnt += PgDBI.pgdel("dsdaemon", "dindex = {}".format(PgOPT.params['DI'][i]), PgOPT.PGOPT['extlog'])
   PgLOG.pglog("{} of {} dscheck daemon control{} deleted".format(delcnt, ALLCNT, s), PgOPT.PGOPT['wrnlog'])

#
# delete checks for given check indices
#
def delete_check_info():

   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Delete {} dscheck record{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   delcnt = 0
   for i in range(ALLCNT):
      cidx = PgLock.lock_dscheck(PgOPT.params['CI'][i], 2, PgOPT.PGOPT['extlog'])
      if cidx <= 0: continue
      delcnt += PgCMD.delete_dscheck(None, "cindex = {}".format(cidx), PgOPT.PGOPT['extlog'])
   PgLOG.pglog("{} of {} check record{} deleted".format(delcnt, ALLCNT, s), PgOPT.PGOPT['wrnlog'])

#
# email notice of check status for specialist
#
def email_check_info():

   cnd = PgOPT.get_hash_condition("dscheck", None, None, 1)
   pgrecs = PgDBI.pgmget("dscheck", "*", cnd + " ORDER BY cindex", PgOPT.PGOPT['extlog'])

   allcnt = (len(pgrecs['cindex']) if pgrecs else 0)
   if not allcnt: return PgLOG.pglog("{}: No Check Information Found to send email for {}".format(PgLOG.PGLOG['CURUID'], cnd), PgLOG.LOGWRN)
   if allcnt > 1:
      s = 's'
      ss = "are"
   else:
      s = ''
      ss = "is"
   subject = "{} active Check Record{}".format(allcnt, s)
   mbuf = "{} {} listed:\n".format(subject, ss)
   pgrecs = {'status' : get_check_status(pgrecs, allcnt)}

   for i in range(allcnt):
      if i > 0: mbuf += PgLOG.PGLOG['SEPLINE']
      mbuf += build_check_message(PgUtil.onerecord(pgrecs, i))

   if 'CC' in PgOPT.params: PgLOG.add_carbon_copy(PgOPT.params['CC'])
   subject += " found"
   PgLOG.send_email(subject, PgOPT.params['LN'], mbuf)
   PgLOG.pglog("Email sent to {} With Subject '{}'".format(PgOPT.params['LN'], subject), PgLOG.LOGWRN)

#
# build email message for a given check record
#
def build_check_message(pgrec):

   msg = "Check Index: {}\nCommand: {} {}".format(pgrec['cindex'], pgrec['command'], pgrec['argv'])
   if pgrec['argextra']: msg += PgLOG.break_long_string(pgrec['argextra'], 100, "...", 1)
   msg += ("\nWork Directory: {}\n".format(pgrec['workdir']) +
           "Initial Execution: {} {} byb {}\n".format(pgrec['date'], pgrec['time'], pgrec['specialist']) +
           "Current Status: {}\n".format(pgrec['status']))
   if pgrec['errmsg']:
     msg += "Error Message: {}\n".format(pgrec['errmsg'])
   elif not pgrec['pid']:
     msg += "Error Message: Aborted abnormally\n";     

   return msg

#
# get dscheck daemon control information
#
def get_daemon_info():

   tname = "dsdaemon"
   hash = PgOPT.TBLHASH[tname]   
   PgLOG.pglog("Get dscheck daemon control information from RDADB ...", PgLOG.WARNLG)

   oflds = lens = fnames = None
   if 'FN' in PgOPT.params: fnames = PgOPT.params['FN']
   fnames = PgDBI.fieldname_string(fnames, PgOPT.PGOPT[tname], PgOPT.PGOPT[tname])
   onames = PgOPT.params['ON'] if 'ON' in PgOPT.params else "I"
   qnames = fnames + PgOPT.append_order_fields(onames, fnames, tname)
   condition = PgOPT.get_hash_condition(tname, None, None, 1); 
   if 'ON' in PgOPT.params and 'OB' in PgOPT.params:
      oflds = PgOPT.append_order_fields(onames, None, tname)
   else:
      condition += PgOPT.get_order_string(onames, tname)

   pgrecs = PgDBI.pgmget(tname, PgOPT.get_string_fields(qnames, tname), condition, PgOPT.PGOPT['extlog'])
   if pgrecs:
      if 'OF' in PgOPT.params: lens = PgUtil.all_column_widths(pgrecs, fnames, hash)
      if oflds: pgrecs = PgUtil.sorthash(pgrecs, fnames, hash, PgOPT.params['OB'])

   PgOPT.OUTPUT.write(PgOPT.get_string_titles(fnames, hash, lens) + "\n")
   if pgrecs:
      cnt = PgOPT.print_column_format(pgrecs, fnames, hash, lens)
      s = 's' if cnt > 1 else ''
      PgLOG.pglog("{} daemon control{} retrieved".format(cnt, s), PgOPT.PGOPT['wrnlog'])
   else:
      PgLOG.pglog("No daemon control information retrieved", PgOPT.PGOPT['wrnlog'])

#
# get check information
#
def get_check_info():

   tname = 'dscheck'
   hash = PgOPT.TBLHASH[tname]     
   PgLOG.pglog("Get check information from RDADB ...", PgLOG.WARNLG)

   lens = oflds = fnames = None
   if 'FN' in PgOPT.params: fnames = PgOPT.params['FN'] 
   fnames = PgDBI.fieldname_string(fnames, PgOPT.PGOPT[tname], PgOPT.PGOPT['chkall'])
   onames = PgOPT.params['ON'] if 'ON' in PgOPT.params else "I"
   condition = PgOPT.get_hash_condition(tname, None, None, 1); 
   if 'ON' in PgOPT.params and 'OB' in PgOPT.params:
      oflds = PgOPT.append_order_fields(onames, None, tname)
   else:
      condition += PgOPT.get_order_string(onames, tname)

   pgrecs = PgDBI.pgmget(tname, "*", condition, PgOPT.PGOPT['extlog'])
   if pgrecs:
      if 'CS' in PgOPT.params:
         pgrecs['status'] = get_check_status(pgrecs)
         if fnames.find('U') < 0: fnames == 'U'
      if 'FO' in PgOPT.params: lens = PgUtil.all_column_widths(pgrecs, fnames, hash)
      if oflds: pgrecs = PgUtil.sorthash(pgrecs, oflds, hash, PgOPT.params['OB'])

   PgOPT.OUTPUT.write(PgOPT.get_string_titles(fnames, hash, lens) + "\n")
   if pgrecs:
      cnt = PgOPT.print_column_format(pgrecs, fnames, hash, lens)
      s = 's' if cnt > 1 else ''
      PgLOG.pglog("{} check record{} retrieved".format(cnt, s), PgOPT.PGOPT['wrnlog'])
   else:
      PgLOG.pglog("No check information retrieved", PgOPT.PGOPT['wrnlog'])

#
# add or modify dscheck daemon control information
#
def set_daemon_info():

   tname = "dsdaemon"
   hash = PgOPT.TBLHASH[tname]
   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Set information of {} dscheck daemon control{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   addcnt = modcnt = 0
   flds = PgOPT.get_field_keys(tname, None, 'I')
   PgOPT.validate_multiple_values(tname, ALLCNT, flds)

   for i in range(ALLCNT):  
      didx = PgOPT.params['DI'][i] if 'DI' in PgOPT.params else 0
      if didx > 0:
         cnd = "dindex = {}".format(didx)
         pgrec = PgDBI.pgget(tname, "*", cnd, PgOPT.PGOPT['extlog'])
         if not pgrec: PgOPT.action_error("Miss daemon record for " + cnd, 'SD')
      else:
         pgrec  = None

      record = PgOPT.build_record(flds, pgrec, tname, i)
      if record:
         if 'priority' in record and (record['priority'] < 0 or record['priority'] > 10):
            PgOPT.action_error("{}: Priority value must in range 0(highest) - 10(lowest)".format(record['priority']), 'SD')

         if pgrec:
            modcnt += PgDBI.pgupdt(tname, record, cnd, PgOPT.PGOPT['extlog'])
         else:
            if 'specialist' not in record and PgOPT.params['LN'] != PgLOG.PGLOG['RDAUSER']: record['specialist'] = PgOPT.params['LN']
            didx = PgDBI.pgadd(tname, record, PgOPT.PGOPT['extlog']|PgLOG.AUTOID)
            if didx:
               PgLOG.pglog("Daemon Control Index {} added".format(didx), PgOPT.PGOPT['wrnlog'])
               addcnt += 1

   PgLOG.pglog("{}/{} of {} daemon control{} added/modified in RDADB!".format(addcnt, modcnt, ALLCNT, s), PgOPT.PGOPT['wrnlog'])

#
# expand check status info
#
def get_check_status(pgrecs, cnt = 0):

   if not cnt: cnt = (len(pgrecs['cindex']) if pgrecs else 0)
   stats = [None]*cnt
   for i in range(cnt):
      pgrec = PgUtil.onerecord(pgrecs, i)
      if pgrec['pid']:
         percent = complete_percentage(pgrec)
         runhost = ""
         if percent < 0:
            stats[i] = "Pending"
         else:
            stats[i] = get_execution_string(pgrec['status'], pgrec['tcount'])
            rtime = PgCheck.dscheck_runtime(pgrec['stttime'])
            if rtime: stats[i] += " {}".format(rtime)
            if percent > 0: stats[i] += ", {}% done".format(percent)
            if pgrec['runhost']: runhost = pgrec['runhost']
         stats[i] += PgLock.lock_process_info(pgrec['pid'], pgrec['lockhost'], runhost)
      else:
         stats[i] = PgCheck.dscheck_status(pgrec['status'])
         if pgrec['status'] == 'D' or pgrec['status'] == 'P':
            runhost = (pgrec['runhost'] if pgrec['runhost'] else pgrec['lockhost'])
            if runhost: stats[i] += " on " + runhost
         elif pgrec['status'] == 'C' and pgrec['pindex']:
            stats[i] = "Wait on CHK {}".format(pgrec['pindex'])

   return stats

#
# get the percentage of the check job done 
#
def complete_percentage(check):

   percent = 0

   if check['bid'] and not check['stttime']:
      percent = -1
   elif check['fcount'] > 0 and check['dcount']:
      percent = int(100*check['dcount']/check['fcount'])
   elif check['command'] == "dsrqst" and check['oindex']:
      if check['otype'] == 'P':
         percent = get_partition_percentage(check['oindex'])
      else:
         percent = get_dsrqst_percentage(check['oindex'])

   return (percent if percent < 100 else 99)

#
# get a request percentage finished
#
def get_dsrqst_percentage(ridx):

   rcnd = "rindex = {}".format(ridx)
   pgrqst = PgDBI.pgget("dsrqst", "fcount, pcount", rcnd)
   if pgrqst:
      fcnt = pgrqst['fcount'] if pgrqst['fcount'] else 0
      if fcnt < 1: fcnt = PgDBI.pgget("wfrqst", "", rcnd)
      if fcnt > 0:
         dcnt = pgrqst['pcount'] if pgrqst['pcount'] else 0
         if dcnt < 1: dcnt = PgDBI.pgget("wfrqst", "", rcnd + " AND status = 'O'")
         if dcnt > 0:
            percent = int(100*dcnt/fcnt)
            if percent > 99: percent = 99
            return percent
   return 0

#
# get a partition percentage finished
#
def get_partition_percentage(pidx, cidx = 0):

   pcnd = "pindex = {}".format(pidx)
   pgrec = PgDBI.pgget('ptrqst', "fcount", pcnd)
   if pgrec:
      fcnt = pgrec['fcount'] if pgrec['fcount'] else 0
      if fcnt < 1: fcnt = PgDBI.pgget("wfrqst", "", pcnd)
      if fcnt > 0:
         dcnt = PgDBI.pgget("wfrqst", "", pcnd + " AND status = 'O'")
         if dcnt > 0:
            percent = int(100*dcnt/fcnt)
            if percent > 99: percent = 99
            return percent
   return 0

#
#  get excecution string for give try count
#
def get_execution_string(stat, trycnt = 0):

   str = PgCheck.dscheck_status(stat)
   if trycnt > 1: str += "({})".format(PgLOG.int2order(trycnt))

   return str

#
# interrupt checks for given dscheck indices
#
def interrupt_dschecks():

   s = 's' if ALLCNT > 1 else ''
   delcnt = 0
   for i in range(ALLCNT):
      cidx = PgOPT.params['CI'][i]
      cnd = "cindex = {}".format(cidx)
      cstr = "Check Index {}".format(cidx)
      pgrec = PgDBI.pgget("dscheck", "*", cnd, PgOPT.PGOPT['extlog'])
      if not pgrec: PgLOG.pglog(cstr +": NOT in RDADB", PgOPT.PGOPT['extlog'])
      pid = pgrec['pid']
      if pid == 0:
         PgLOG.pglog(cstr + ": Check is not under process; no interruption", PgOPT.PGOPT['wrnlog'])
         continue

      host = pgrec['lockhost']
      if not PgFile.local_host_action(host, "interrupt check", cstr, PgOPT.PGOPT['errlog']): continue

      opts = "-h {} -p {}".format(host, pid)
      buf = PgLOG.pgsystem("rdaps " + opts, PgLOG.LOGWRN, 20)  # 21 = 4 + 16
      if buf:
         ms = re.match(r'^\s*(\w+)\s+', buf)
         if ms:
            uid = ms.group(1)
            if uid != PgOPT.params['LN']:
               PgLOG.pglog("{}: login name '{}'; must be '{}' to interrupt".format(cstr, PgOPT.params['LN'], uid), PgOPT.PGOPT['wrnlog'])
               continue
            if 'FI' not in PgOPT.params:
               PgLOG.pglog("{}: locked by {}/{}; must add Mode option -FI (-ForceInterrupt) to interrupt".format(cstr, pid, host), PgOPT.PGOPT['wrnlog'])
               continue
            if not PgLOG.pgsystem("rdakill " + opts, PgLOG.LOGWRN, 7):
               PgLOG.pglog("{}: Failed to interrupt Check locked by {}/{}".format(cstr, pid, host), PgOPT.PGOPT['errlog'])
               continue
         else:
            PgLOG.pglog("{}: check process stopped for {}/{}".format(cstr, pid, host), PgOPT.PGOPT['wrnlog'])

      pgrec = PgDBI.pgget("dscheck", "*", cnd, PgOPT.PGOPT['extlog'])
      if not pgrec['pid']:
         if PgLock.lock_dscheck(cidx, 1, PgOPT.PGOPT['extlog']) <= 0: continue
      elif pid != pgrec['pid'] or host != pgrec['lockhost']:
         PgLOG.pglog("{}: Check is relocked by {}/{}".format(cstr, pgrec['pid'], pgrec['lockhost']), PgOPT.PGOPT['errlog'])
         continue

      pgrec['status'] = 'I'
      PgCMD.delete_dscheck(pgrec, None, PgOPT.PGOPT['extlog'])
      if pgrec['command'] == 'dsupdt':
         if pgrec['oindex']:
            cnd = "cindex = {} AND pid = {} AND ".format(pgrec['oindex'], pid)
            if PgDBI.pgexec("UPDATE dcupdt set pid = 0 WHERE {}lockhost = '{}'".format(cnd, host), PgOPT.PGOPT['extlog']):
               PgLOG.pglog("Update Control Index {} unlocked".format(pgrec['oindex']), PgLOG.LOGWRN)
         else:
            cnd = "dsid = '{}' AND pid = {} AND ".format(pgrec['dsid'], pid)

         dlupdt = PgDBI.pgget("dlupdt", "lindex", "{}hostname = '{}'".format(cnd , host))
         if dlupdt and PgDBI.pgexec("UPDATE dlupdt set pid = 0 WHERE lindex = {}".format(dlupdt['lindex']), PgOPT.PGOPT['extlog']):
            PgLOG.pglog("Update Local File Index {} unlocked".format(dlupdt['lindex']), PgLOG.LOGWRN)

      elif pgrec['command'] == 'dsrqst':
         record = {'status' : 'I', 'pid' : 0}
         if pgrec['otype'] == 'P':
            table = "ptrqst"
            field = "pindex"
            msg = "Request Partition Index"
         else:
            table = "dsrqst"
            field = "rindex"
            msg = "Request Index"

         if pgrec['oindex']:
            cnd = "{} = {} AND pid = {} AND lockhost = '{}'".format(field, pgrec['oindex'], pid, host)
         else:
            cnd = "dsid = '{}' AND pid = {} AND lockhost = '{}'".format(pgrec['dsid'], pid, host)

         if PgDBI.pgupdt(table, record, cnd, PgOPT.PGOPT['extlog']):
            PgLOG.pglog("{} {} unlocked".format(msg, pgrec['oindex']), PgLOG.LOGWRN)
      delcnt += 1

   if ALLCNT > 1: PgLOG.pglog("{} of {} check{} interrupted".format(delcnt, ALLCNT, s), PgLOG.LOGWRN)


#
# unlock checks for given check indices
#
def unlock_checks():

   if ALLCNT > 0:
      s = 's' if ALLCNT > 1 else ''   
      PgLOG.pglog("Unlock {} check{} ...".format(ALLCNT, s), PgLOG.WARNLG)
      modcnt = 0
      for cidx in PgOPT.params['CI']:
         pgrec = PgDBI.pgget("dscheck", "pid, lockhost", "cindex = {}".format(cidx), PgOPT.PGOPT['extlog'])
         if not pgrec:
            PgLOG.pglog("Check {}: Not exists".format(cidx), PgOPT.PGOPT['errlog'])
         elif not pgrec['pid']:
            PgLOG.pglog("Check {}: Not locked".format(cidx), PgOPT.PGOPT['wrnlog'])
         elif PgLock.lock_dscheck(cidx, -1, PgOPT.PGOPT['extlog']) > 0:
            modcnt += 1
            PgLOG.pglog("Check {}: Unlocked {}/{}".format(cidx, pgrec['pid'], pgrec['lockhost']), PgOPT.PGOPT['wrnlog'])
         elif(PgFile.check_host_down(None, pgrec['lockhost']) and
              PgLock.lock_dscheck(cidx, -2, PgOPT.PGOPT['extlog']) > 0):
            modcnt += 1
            PgLOG.pglog("Check {}: Force unlocked {}/{}".format(cidx, pgrec['pid'], pgrec['lockhost']), PgOPT.PGOPT['wrnlog'])
         else:
            PgLOG.pglog("Check {}: Unable to unlock {}/{}".format(cidx, pgrec['pid'], pgrec['lockhost']), PgOPT.PGOPT['wrnlog'])

      if ALLCNT > 1: PgLOG.pglog("{} of {} check{} unlocked from RDADB".format(modcnt, ALLCNT, s), PgLOG.LOGWRN)
   else:
      cnd = "lockhost = '{}' AND ".format(PgLOG.get_host(1))
      PgCheck.check_dsrqst_locks(cnd, PgOPT.PGOPT['extlog'])
      PgCheck.check_dsupdt_locks(cnd, PgOPT.PGOPT['extlog'])
      PgCheck.check_dscheck_locks(cnd, PgOPT.PGOPT['extlog'])

#
# process the checks
#
def process_dschecks():

   logact = PgLOG.LOGERR

   if PgLOG.PGLOG['CURUID'] == PgLOG.PGLOG['RDAUSER'] and (time.time()%(3*PgSIG.PGSIG['CTIME'])) < 60:
      logact |= PgLOG.EMEROL

   cnd = PgOPT.get_hash_condition("dscheck", "ST", None, 1)
   if cnd: cnd += " AND "
   if 'SN' not in PgOPT.params and PgOPT.params['LN'] != PgLOG.PGLOG['RDAUSER']:
       cnd += "specialist = '{}' AND ".format(PgOPT.params['LN'])

   if 'WR' in PgOPT.params: PgCheck.start_dsrqsts(cnd, logact)
   if 'WU' in PgOPT.params: PgCheck.start_dsupdts(cnd, logact)

   acnd = PgOPT.get_hash_condition("dscheck", None, "ST", 1)
   if acnd: acnd += " AND "
   PgCheck.start_dschecks(cnd + acnd, logact)

   if PgLOG.PGLOG['ERRCNT']: send_error_email()

#
# process the checks
#
def process_dscheck_options():

   logact = PgLOG.LOGERR

   if PgLOG.PGLOG['CURUID'] == PgLOG.PGLOG['RDAUSER'] and (time.time()%(3*PgSIG.PGSIG['CTIME'])) < 60:
      logact |= PgLOG.EMEROL

   cnd = PgOPT.get_hash_condition("dscheck", "ST", None, 1)
   if cnd: cnd += " AND "
   if 'SN' not in PgOPT.params and PgOPT.params['LN'] != PgLOG.PGLOG['RDAUSER']:
       cnd += "specialist = '{}' AND ".format(PgOPT.params['LN'])

   acnd = PgOPT.get_hash_condition("dscheck", None, "ST", 1)
   if acnd: acnd += " AND "
   PgCheck.set_dscheck_options(PgLOG.get_host(1), cnd + acnd, logact)

   if PgLOG.PGLOG['ERRCNT']: send_error_email()

#
# send an email notice to the running specialist
#
def send_email_notice(cmd, pgrec):

   s = 's' if pgrec['tcount'] > 1 else ''
   msg = ("Check Index {} for command:\n  {}\n".format(pgrec['cindex'], cmd) +
          "under '{}' has be executed {} time{}.\n".format(pgrec['workdir'], pgrec['tcount'], s))
   if pgrec['errmsg']:
      msg += "Error message from previous execution:\n  {}\n".format(pgrec['errmsg'])

   msg += ("If there is any problem, please fix it, delete the dscheck record via " +
           "'dscheck dl -ci '\nand restart the command.\n".format(pgrec['cindex']))

   PgLOG.send_email("Check Index {} reprocessed {} time{}".format(pgrec['cindex'], pgrec['tcount'], s), None, msg) 

#
# rdadata daemon handles the daemon controls
#
def handle_dschecks():

   logact = ccnt = rcnt = ucnt = 0
   PgLOG.PGLOG['NOQUIT'] = 1
   ctime = 4*PgSIG.PGSIG['CTIME']
   etime = ctime

   while not PgSIG.PGSIG['QUIT']:
      if etime >= ctime:
         logact = PgLOG.LGEREX|PgLOG.EMEROL
         etime = 0
      else:
         logact = PgLOG.LGEREX

      ncnt = 0
      cnt = PgCheck.start_dsrqsts("", logact)
      ncnt += cnt
      rcnt += cnt
      cnt = PgCheck.start_dsupdts("", logact)
      ncnt += cnt
      ucnt += cnt
      cnt = PgCheck.start_dschecks("", logact)
      ncnt += cnt
      ccnt += cnt

      if PgLOG.PGLOG['ERRCNT']: send_error_email()
      if not ncnt: PgDBI.pgdisconnect(1)

      etime += PgSIG.sleep_daemon()

   PgLOG.PGLOG['NOQUIT'] = 0
   PgSIG.stop_daemon(prepare_quit(ccnt, rcnt, ucnt))

#
# send an error email to the specialist
#
def send_error_email():
   
   msg = "Error message for DSCHECK on " + PgLOG.PGLOG['HOSTNAME']

   PgLOG.set_email(msg, PgLOG.EMLTOP)
   msg = PgLOG.send_email(msg)
   PgLOG.pglog(msg, PgLOG.MSGLOG|PgLOG.FRCLOG)

#
# prepare a summary string for quit
#
def prepare_quit(ccnt, rcnt, ucnt):

   msg = ""
   if rcnt > 0:
      s = 's' if rcnt > 1 else ''
      msg = "{} dsrqst{}".format(rcnt, s)
   if ccnt > 0:
      if msg: msg += ", "
      s = 's' if ccnt > 1 else ''
      msg += "{} dscheck{}".format(ccnt, s)
   if ucnt > 0:
      if msg: msg += ", "
      s = 's' if ucnt > 1 else ''
      msg += "{} dsupdt{}".format(ucnt, s)

   return msg

#
# check a daemon host if connectable
#
def check_host_connection():
   
   tname = "dsdaemon"
   hash = PgOPT.TBLHASH[tname]
   condition = PgOPT.get_hash_condition(tname, None, "H", 1)
   if 'HN' in PgOPT.params:
      pgrecs = {'specialist' : [], 'hostname' : []}
      spclsts = PgDBI.pgmget(tname, "DISTINCT specialist", condition, PgOPT.PGOPT['extlog'])
      if spclsts:
         for specialist in spclsts['specialist']:
            for hostname in PgOPT.params['HN']:
               pgrecs['specialist'].append(specialist)
               pgrecs['hostname'].append(hostname)
   else:
      pgrecs = PgDBI.pgmget(tname, "DISTINCT specialist, hostname", condition, PgOPT.PGOPT['extlog'])

   cnt = len(pgrecs['specialist']) if pgrecs else 0
   if not cnt:
      PgLOG.pglog("No daemon host found to check connectivity", PgLOG.LOGWRN)
      return
   if cnt > 1: PgLOG.pglog("Check {} daemon hosts for connectivity ...".format(cnt), PgLOG.WARNLG)

   for i in range(cnt):
      specialist = pgrecs['specialist'][i]
      hostname = pgrecs['hostname'][i]
      cmd = "ssh {} ps".format(hostname)
      if specialist != PgLOG.PGLOG['CURUID']:
         if PgLOG.PGLOG['CURUID'] != PgLOG.PGLOG['RDAUSER']:
            PgLOG.pglog("{}: Cannot check connection to '{}' for {}".format(PgLOG.PGLOG['CURUID'], hostname, specialist), PgLOG.LOGERR)
            continue
         else:
            cmd = "pgstart_{} {}".format(specialist, cmd)

      PgLOG.pglog("Check conection to '{}' for {} ...".format(hostname, specialist), PgLOG.WARNLG)
      PgLOG.pgsystem(cmd, PgLOG.LOGERR, 4, None, 15)

#
# call main() to start program
#
if __name__ == "__main__": main()
