import re

STATUS_OK = ['Satisfiable', 'Unsatisfiable', 'Theorem', 'CounterSatisfiable']
STATUS_OUT = ['ResourceOut', 'GaveUp']
STATUS_ALL = STATUS_OK + STATUS_OUT

PATS = {
   "RUNTIME":                      re.compile(r"^\s*(\d*\.\d*)\s*task-clock:u"),
   "USERTIME":                     re.compile(r"^# User time\s*: (\S*) s"),
   "MILINS":                       re.compile(r"^\s*([0-9,]*)\s*instructions:u"),
   "STATUS":                       re.compile(r"^# SZS status (\S*)"),
   "PROCESSED":                    re.compile(r"^# Processed clauses\s*: (\S*)"),
   "GENERATED":                    re.compile(r"^# Generated clauses\s*: (\S*)"),
   "PROOFLEN":                     re.compile(r"^# Proof object total steps\s*: (\S*)"),
   "PRUNED":                       re.compile(r"^# Removed by relevancy pruning/SinE\s*: (\S*)"),
   "CURR_PROCESSED_CLAUSES":       re.compile(r"^# Current number of processed clauses\s*: (\S*)"),
   "CURR_PROCESSED_POS_OR_UC":     re.compile(r"^#\s*Positive orientable unit clauses\s*: (\S*)"),
   "CURR_PROCESSED_POS_NOT_OR_UC": re.compile(r"^#\s*Positive unorientable unit clauses\s*: (\S*)"),
   "CURR_PROCESSED_NEG_UC":        re.compile(r"^#\s*Negative unit clauses\s*: (\S*)"),
   "CURR_PROCESSED_NON_UC":        re.compile(r"^#\s*Non-unit-clauses\s*: (\S*)"),
   "WATCHLIST_NON_UNIT_CLAUSES":   re.compile(r"^#\s*Inserted watchlist non unit clauses\s*: (\S*)"),
   "WATCHLIST_UNIT_CLAUSES":       re.compile(r"^#\s*Inserted watchlist unit clausess*: (\S*)"),
   "WATCHLIST_CHECKS":             re.compile(r"^#\s*Watchlist checks\s*: (\S*)"),
   "WATCHLIST_CHECKS_Unit":        re.compile(r"^#\s*Watchlist unit clause checks\s*: (\S*)"),
   "PROCESS_CLAUSE_LOOPS":         re.compile(r"^#\s*Given clause loop iterations\s*: (\S*)")
}

def value(strval):
   if strval.isdigit():
      return int(strval)
   if strval.find(".") >= 0:
      try:
         return float(strval)
      except:
         pass
   return strval

def parse(f_out, trains=False, out=None, proof=False):
   result = {}
   result["STATUS"] = "Unknown"
   if trains:
      result["POS"] = []
      result["NEG"] = []
   if proof:
      result["PROOF"] = []
   if f_out is not None:
      out = open(f_out)
   else:
      out = out.strip().split("\n")
            

   inproof = False
   for line in out:
      line = line.rstrip()
      # search for patterns from PATS
      if (len(line) > 2) and ((line[0] == "#" and line[1] == " " )or line[0] == " "):
         for pat in PATS:
            mo = PATS[pat].search(line)
            if mo:
               result[pat] = value(mo.group(1))
      # search for training samples
      if trains and line.startswith("cnf(") and ("$false" not in line):
         if "trainpos" in line:
            result["POS"].append(line)
         elif "trainneg" in line:
            result["NEG"].append(line)
      # search for proof
      if proof:
         if line.startswith("# SZS output start"):
            inproof = True
            continue
         if inproof and line.startswith("# SZS output end"):
            inproof = False
            continue
         if inproof:
            result["PROOF"].append(line)

   if "RUNTIME" in result:
      result["RUNTIME"] /= 1000.0
   elif "USERTIME" in result:
      result["RUNTIME"] = result["USERTIME"]
   if "MILINS" in result:
      result["MILINS"] = int(result["MILINS"].replace(",",""))/(10**6)
   return result

def solved(result, limit=None):
   ok = "STATUS" in result and result["STATUS"] in STATUS_OK
   if limit:
      return ok and result["RUNTIME"] <= limit
   return ok

def error(result):
   return "STATUS" not in result or result["STATUS"] not in STATUS_ALL

