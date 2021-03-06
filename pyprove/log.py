from datetime import datetime
from sys import argv, exc_info
import os
import sys
import atexit
import traceback

REPORTS_DIR = os.getenv("EXPRES_REPORTS", "./00REPORTS")

def terminating(cache):
   msg("Terminating.")
   if "last_traceback" in dir(sys):
      traceback.print_last(file=open(cache[1],"a"))

def trace():
   text(traceback.format_exc())

def mapping(m, info=None):
   if info:
      msg(info)
   size = max([len(str(x)) for x in m])
   pair = "| %%-%ds = %%s" % size
   text("\n".join([pair % (x,m[x]) for x in sorted(m)]))

def start(intro, config=None, script=""):
   msg(intro, script=script, reset=True)
   if config:
      mapping(config)

def msg(msg, cache=[], script="", timestamp=True, reset=False):
   now = datetime.now()
   if not cache:
      script = argv[0] if argv and not script else script
      cache.append(now)
      os.system("mkdir -p %s" % REPORTS_DIR)
      cache.append(("%s/%s__%s.log" % (REPORTS_DIR, script.lstrip("./").replace("/","+"), now.strftime("%y-%m-%d__%H:%M:%S"))).replace(" ","_"))
      atexit.register(terminating, cache)
   elif reset:
      cache[0] = now
   
   msg = ("[%s] %s" % (now-cache[0], msg)) if timestamp else msg
   print(msg)
   if REPORTS_DIR:
      f = open(cache[1],"a")
      f.write(msg+"\n")
      f.flush()
      f.close()

def text(msg0=""):
   msg(msg0, timestamp=False)

def humanbytes(b):
   units = {0 : 'Bytes', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB', 5: 'PB'}
   power = 1024
   n = 0
   while b > power:
      b /= power
      n += 1
   return "%.2f %s" % (b, units[n])

def humanint(n):
   s = str(int(abs(n)))
   r = s[-3:]
   s = s[:-3]
   while s:
      r = s[-3:] + "," + r
      s = s[:-3]
   return r if n >= 0 else "-%s" % r

def humantime(s):
   h = s // 3600
   s -= 3600*h
   m = s // 60
   s -= 60*m
   return "%02d:%02d:%04.1f" % (h,m,s)

exps_2 = {2**n:n for n in range(256)}

def humanexp(n):
   if n in exps_2:
      return "2e%s" % exps_2[n]
   return str(n)


