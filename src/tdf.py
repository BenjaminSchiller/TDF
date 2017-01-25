import redis, time
from time import gmtime, strftime
import ConfigParser
import subprocess32 as subprocess
import os

states = ["open", "running", "executed", "timeout", "timed_out", "expired", "succeeded", "failure", "failed", "archived"]

logPrefix = " "*0
printPrefix = " "*8
logNameOffset = 10
logDatetimeFormat = "%Y-%m-%d %H:%M:%S"






class PipelineResult:
    def __init__(self):
        pass
    def setResult(self, res):
        self.res = res
    def getResult(self):
        return self.res

class Pipeline:
    def __init__(self, r, res=PipelineResult()):
        self.p = r.pipeline(transaction=True)
        self.res = res
    def __enter__(self):
        return self.p
    def __exit__(self, type, value, traceback):
        self.res.setResult(self.p.execute())
        return self.res.getResult()





def getCurrentTimestamp():
        return time.time()

def taskToStr(task, verbose=False):
    if verbose:
        return "task:%s: %s %s @%s (%s)" % (task.get("id"), task.get("program"), task.get("input"), task.get("state"), task.getCurrentValue("worker"))
    else:
        return "task:%s" % task.get("id")

def log(tdf, msg, task=None, p=None):
    prefix = tdf.name + " "*(logNameOffset-len(tdf.name))
    datetime = strftime(logDatetimeFormat, gmtime())
    line = "%s - %s %s" % (datetime, prefix, msg)
    print logPrefix + line
    if not task is None:
        log = line if task.get("log") is "" else "%s\n%s" % (task.get("log"), line)
        task.set("log", log, p)







class Task:
    def __init__( self, values):
        self.values = values

    def __str__(self):
        return "task %s: %s %s" % (self.get("id"), self.get("program"), self.get("input"))

    def getKey(self, key):
        return "%s:%s" % (self.get("namespace"), key)

    def currentKey(self, key):
        return "%s:%s" % (self.get("round"), key)

    def lastKey(self, key):
        for i in range(int(self.get("round")), -1, -1):
            key = "%s:%s" % (i, key)
            if key in self.values:
                return key
        return None

    def get(self, key):
        return self.values[key]

    def getCurrent(self, key):
        return self.get(self.currentKey(key))

    def getLast(self, key):
        return self.get(self.lastKey(key))

    def set(self, key, value, r=None):
        self.values[key] = value
        if not r is None:
            r.hmset(self.getKey("task:%s" % self.get("id")), {key: value})

    def setCurrent(self, key, value, r=None):
        self.set(self.currentKey(key), value, r)

    def setCurrentTimestamp(self, key, r=None):
        self.set(self.currentKey(key), getCurrentTimestamp(), r)

    def incr(self, key, r=None):
        self.set(key, int(self.get(key)) + 1, r)

    def open(self, r):
        id = r.incr(self.getKey("task_id"))
        self.set("id", id)
        self.set("state", "open")
        self.set("0:open", getCurrentTimestamp())
        with Pipeline(r) as p:
            p.zadd(self.getKey("open"), self.get("start_after"), id)
            p.hmset(self.getKey("task:%i" % id), self.values)

    def isExpired(self):
        return (getCurrentTimestamp() > float(self.get("end_before")))

    def isTimedOut(self):
        duration = getCurrentTimestamp() - float(self.getCurrent("running"))
        return (duration > float(self.get("timeout")))

    def isFailed(self):
        err = self.getCurrent("error")
        return not (err is None or err == "")

    def isFailedTooOften(self):
        return (int(self.get("fails")) > int(self.get("max_fails")))

    def isTimedOutTooOften(self):
        return (int(self.get("timeouts")) > int(self.get("max_timeouts")))

    def isProgramAvailable(self):
        return os.path.isdir('./%s/' % self.get("program")) and os.path.isfile('./%s/run.sh' % self.get("program"))

    def fetchProgram(self):
        src = self.get("source")
        if not os.path.isdir('./%s/' % self.get("program")):
            os.makedirs('./%s/' % self.get("program"))
        if not (src.endswith(".zip") or src.endswith(".tar") or src.endswith(".tar.gz") or src.endswith(".tar.bz") or src.endswith(".tar.bz2") or src.endswith("/run.sh") or src.endswith(":run.sh")):
            print "invalid type of archive / program: %s" % src
            return False
        if src.startswith("http://") or src.startswith("https://"):
            path = src
            archive = src.split("/")[-1]
            print "downloading %s from %s" % (archive, path)
            if not os.system("wget %s -P ./%s/" % (path, self.get("program"))) == 0:
                return False
            if not archive.endswith("run.sh"):
                return self.unpack(self.get("program"), archive)
            else:
                return True
        elif src.startswith("rsync:"):
            path = src.replace("rsync:","",1)
            archive = path.split("/")[-1]
            print "rsyncing %s from %s" % (archive, path)
            if not os.system("rsync -auvzl %s ./%s/" % (path, self.get("program"))) == 0:
                return False
            if not archive.endswith("run.sh"):
                return self.unpack(self.get("program"), archive)
            else:
                return True

    def unpack(self, programName, archive):
        src = "./%s/%s" % (programName, archive)
        dst = "./%s/" % (programName,)
        if archive.endswith(".zip"):
            print "unzipping %s to %s" % (src, dst)
            return os.system("unzip %s -d %s" % (src, dst)) == 0
        elif archive.endswith(".tar"):
            print "untaring %s to %s" % (src, dst)
            return os.system("tar -xvf %s -C %s" % (src, dst)) == 0
        elif archive.endswith(".tar.gz"):
            print "untaring %s to %s" % (src, dst)
            return os.system("tar -zxvf %s -C %s" % (src, dst)) == 0
        elif archive.endswith(".tar.bz"):
            print "untaring %s to %s" % (src, dst)
            return os.system("tar -jxvf %s -C %s" % (src, dst)) == 0
        elif archive.endswith(".tar.bz2"):
            print "untaring %s to %s" % (src, dst)
            return os.system("tar -jxvf %s -C %s" % (src, dst)) == 0
        else:
            print "invalid archive for unpacking: %s" % src
            return False

    def move(self, tdf, dst_state, score, r, propertiesToUpdate={}):
        remove = r.zrem(self.getKey(self.get("state")), self.get("id"))

        if remove is 1:
            with Pipeline(r) as p:
                # log
                log(tdf, "moving task %s: %s -> %s" % (self.get("id"), self.get("state"), dst_state), self, p)

                # add to dst state
                p.zadd(self.getKey(dst_state), score, self.get("id"))

                # change state stored in task
                if not dst_state is "archived":
                    self.set("state", dst_state, p)

                # set timestamp of this transition
                self.setCurrentTimestamp(dst_state, p)

                # update addition properties of the task
                for key in propertiesToUpdate:
                    self.set(key, propertiesToUpdate[key], p)

            return True
        else:
            log(tdf, "could not move task task %s: %s -> %s" % (self.get("id"), self.get("state"), dst_state))
            return False










class Tdf(object):
    def __init__(self, name, cfg_filename):
        self.cfg_filename = cfg_filename
        self.cfg = ConfigParser.RawConfigParser()
        self.cfg.read(cfg_filename)
        host = self.cfg.get("redis", "host")
        port = self.cfg.get("redis", "port")
        db = self.cfg.get("redis", "db")
        password = self.cfg.get("redis", "password")
        if password == "None":
            password = None
        self.namespace = self.cfg.get("tdf", "namespace")
        self.name = name
        self.r = redis.StrictRedis(host=host, port=port, db=db, password=password)
        log(self, "initializing '%s' for namespace '%s' (config: '%s')" % (self.name, self.namespace, self.cfg_filename,))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def getKey(self, key):
        return "%s:%s" % (self.namespace, key)

    def getWorkerId(self, name):
        id = self.r.get(self.getKey("worker_id:%s" % name))
        if id is None:
            id = self.r.incr(self.getKey("worker_id"))
            self.r.set(self.getKey("worker_id:%s" % name), id)
            self.r.sadd(self.getKey("worker"), name)
        return id

    def getWorkers(self):
        return self.r.smembers(self.getKey("worker"))

    def getTask(self, task_id):
        return Task(self.r.hgetall(self.getKey("task:%s" % task_id)))

    def processTasks(self, state, data, process1, process2=None):
        size = self.getElementCount(state)
        if size > 0:
            log(self, "processing %s %s tasks" % (size, state))
            for id in self.r.zscan(self.getKey(state))[1]:
                task = self.getTask(id[0])
                process1(self, data, task)
                if not process2 is None:
                    process2(self, data, task)
        return size

    def getElementCount(self, state):
        return self.r.zcard(self.getKey(state))

 






class TdfServer(Tdf):
    def __init__(self, *args, **kwargs):
        super(TdfServer, self).__init__(*args, **kwargs)

    def flushall(self):
        log(self, "FLUSHALL !!!!")
        self.r.flushall()


    def processOpenTasks(self):
        return self.processTasks("open", {}, self.processOpen)

    def processRunningTasks(self):
        return self.processTasks("running", {}, self.processRunning)

    def processExecutedTasks(self):
        return self.processTasks("executed", {}, self.processExecuted)


    def processOpen(self, manager, data, task):
        if task.isExpired():
            task.move(self, "expired", getCurrentTimestamp(), self.r)

    def processRunning(self, manager, data, task):
        if task.isExpired():
            task.move(self, "expired", getCurrentTimestamp(), self.r)
        elif task.isTimedOut():
            task.incr("timeouts")
            propertiesToUpdate={"timeouts": task.get("timeouts")}
            if task.isTimedOutTooOften():
                task.move(self, "timeout", getCurrentTimestamp(), self.r, propertiesToUpdate)
                task.move(self, "timed_out", getCurrentTimestamp(), self.r)
            else:
                task.incr("round")
                propertiesToUpdate["round"] = task.get("round")
                task.move(self, "timeout", getCurrentTimestamp(), self.r, propertiesToUpdate)
                task.move(self, "open", getCurrentTimestamp(), self.r)

    def processExecuted(self, manager, data, task):
        if task.isExpired():
            task.move(self, "expired", getCurrentTimestamp(), self.r)
        elif task.isFailed():
            task.incr("fails")
            if task.isFailedTooOften():
                task.move(self, "failure", getCurrentTimestamp(), self.r, {"fails": task.get("fails")})
                task.move(self, "failed", getCurrentTimestamp(), self.r)
            else:
                task.move(self, "failure", getCurrentTimestamp(), self.r, {"fails": task.get("fails")})
                task.incr("round")
                task.move(self, "open", getCurrentTimestamp(), self.r, {"round": task.get("round")})
        else:
            task.move(self, "succeeded", getCurrentTimestamp(), self.r)

    def run(self, rounds=float("Inf")):
        roundCounter = 0
        while roundCounter < rounds:
            start = time.time()

            processedTasks = self.processOpenTasks()
            processedTasks += self.processRunningTasks()
            processedTasks += self.processExecutedTasks()
            
            end = time.time()
            duration = end - start
            roundDuration = float(self.cfg.get("server", "round_duration"))
            sleep = roundDuration - duration
            if sleep > 0:
                time.sleep(sleep)
            log(self, "%s: processed %s tasks" % (roundCounter, processedTasks))
            roundCounter += 1








class TdfWorker(Tdf):
    def __init__(self, *args, **kwargs):
        super(TdfWorker, self).__init__(*args, **kwargs)
        self.worker_id = self.getWorkerId(self.name)
        self.task = None

    def claimOpenTask(self):
        openTasks = self.r.zrange(self.getKey("open"), 0, 0)
        if openTasks is None or len(openTasks) is 0:
            log(self, "no open task to claim")
            return False
        else:
            self.task = self.getTask(openTasks[0])
            claim = self.task.move(self, "running", getCurrentTimestamp(), self.r, {self.task.currentKey("worker"): self.name})
            if claim:
                log(self, "claimed task %s" % self.task.get("id"))
                return True
            else:
                log(self, "could not claim task %s" % self.task.get("id"))
                self.task = None
                return False

    def executeTask(self):
        if self.task is None:
            log(self, "cannot execute, no task claimed")
            return False
        else:
            log(self, "executing task %s: %s %s" % (self.task.get("id"), self.task.get("program"), self.task.get("input")), self.task)

            if not self.task.isProgramAvailable():
                log(self, "attempting to fetch program '%s' from '%s'" % (self.task.get("program"), self.task.get("source")))
                if self.task.fetchProgram():
                    log(self, "fetched program '%s'" % self.task.get("program"))
                else:
                    log(self, "could not fetch program '%s'" % self.task.get("program"))
                    out = ""
                    err = "could not fetch program '%s' at worker '%s'" % (self.task.get("program"), self.name)
                    timedOut = False

            if self.task.isProgramAvailable():
                cmd = "cd ./%s/; ./run.sh %s" % (self.task.get("program"), self.task.get("input"))
                out, err, timedOut = self.execute(cmd, self.task.get("timeout"))
            else:
                out = ""
                err = "program './%s/run.sh' does not exist!" % self.task.get("program")
                timedOut = False

            propertiesToUpdate = {self.task.currentKey("output"): out, self.task.currentKey("error"): err}

            if timedOut:
                err += "\nTERMINATED - execution timed out..."
                log(self, "task %s was terminated (timeout)" % self.task.get("id"))

                self.task.incr("timeouts")
                propertiesToUpdate["timeouts"] = self.task.get("timeouts")
                if self.task.isTimedOutTooOften():
                    moved = self.task.move(self, "timeout", getCurrentTimestamp(), self.r, propertiesToUpdate)
                    if not moved:
                        log(self, "could not mark task %i as timed out (already timed out by server?)" % self.task.get("id"))
                    else:
                        moved = self.task.move(self, "timed_out", getCurrentTimestamp(), self.r)
                else:
                    moved = self.task.move(self, "timeout", getCurrentTimestamp(), self.r, propertiesToUpdate)
                    if not moved:
                        log(self, "could not re-open task %i as timed out (already re-opened by server?)" % self.task.get("id"))
                    else:
                        self.task.incr("round")
                        moved = self.task.move(self, "open", getCurrentTimestamp(), self.r, {"round": self.task.get("round")})

                self.task = None
                return False
            else:
                moved = self.task.move(self, "executed", getCurrentTimestamp(), self.r, propertiesToUpdate)
                if not moved:
                    log(self, "could not mark task %s as executed (timed out by server?)" % self.task.get("id"))
                    self.task = None
                    return False
                else:
                    self.task = None
                    return True

    def readLog(self, filename):
        with open(filename, "r") as f:
            return f.read()

    def makeDirs(self, filename):
        dirs = os.path.dirname(filename)
        if not dirs is "":
            if not os.path.exists(dirs):
                os.makedirs(dirs)

    def execute(self, cmd, timeout):
        output_filename = self.cfg.get("worker", "task_output_filename").replace("$worker", self.name).replace("$taskId", self.task.get("id")).replace("$round", self.task.get("round")).replace("$program", self.task.get("program"))
        error_filename = self.cfg.get("worker", "task_error_filename").replace("$worker", self.name).replace("$taskId", self.task.get("id")).replace("$round", self.task.get("round")).replace("$program", self.task.get("program"))
        self.makeDirs(output_filename)
        self.makeDirs(error_filename)
        with open(output_filename, "w") as out:
            with open(error_filename, "w") as err:
                timedOut = False
                try:
                    code = subprocess.call(cmd, shell=True, timeout=float(timeout), stdout=out, stderr=err)
                except subprocess.TimeoutExpired:
                    timedOut = True
        output = self.readLog(output_filename)
        error = self.readLog(error_filename)
        return output, error, timedOut

    def run(self, rounds=float("Inf")):
        roundCounter = 0
        while roundCounter < rounds:
            if self.claimOpenTask():
                if self.executeTask():
                    time.sleep(float(self.cfg.get("worker", "sleep_after_success")))
                else:
                    time.sleep(float(self.cfg.get("worker", "sleep_after_failure")))
            else:
                time.sleep(float(self.cfg.get("worker", "sleep_after_no_process_claimed")))
            roundCounter += 1






import random


def doNothing(task):
    pass

def stopProcessing(manager, data, roundCounter):
    return False

def endRound(manager, data, roundCounter):
    return False

class TdfManager(Tdf):
    def __init__(self, *args, **kwargs):
        super(TdfManager, self).__init__(*args, **kwargs)

    def flushall(self):
        log(self, "FLUSHALL !!!!")
        self.r.flushall()

    def openTask( self,
                  program,
                  source,
                  input,
                  start_after=None, 
                  end_before=None, 
                  timeout=None, 
                  max_fails=None,
                  max_timeouts=None,
                  add_random_start_offset=None ):

        if start_after is None:
            start_after = self.cfg.get("task_defaults", "start_after")
        if end_before is None:
            end_before = self.cfg.get("task_defaults", "end_before")
        if timeout is None:
            timeout = self.cfg.get("task_defaults", "timeout")
        if max_fails is None:
            max_fails = self.cfg.get("task_defaults", "max_fails")
        if max_timeouts is None:
            max_timeouts = self.cfg.get("task_defaults", "max_timeouts")
        if add_random_start_offset is None:
            add_random_start_offset = self.cfg.get("task_defaults", "add_random_start_offset") == "True"

        if add_random_start_offset:
            start_after = float(start_after) + random.random()

        task = Task({ "program": program,
                      "source": source,
                      "input": input,
                      "id": -1,
                      "start_after": start_after,
                      "end_before": end_before,
                      "timeout": timeout,
                      "max_fails": max_fails,
                      "max_timeouts": max_timeouts,
                      "state": None,
                      "round": 0,
                      "fails": 0,
                      "timeouts": 0,
                      "log": "", 
                      "namespace": self.namespace} )
        task.open(self.r)
        log(self, "opened task %s: %s %s" % (task.get("id"), task.get("program"), task.get("input")))
        return task

    def processSucceededTasks(self, data, success):
        return self.processTasks("succeeded", data, success, self.processSucceeded)

    def processFailedTasks(self, data, failure):
        return self.processTasks("failed", data, failure, self.processFailed)

    def processTimedOutTasks(self, data, timedOut):
        return self.processTasks("timed_out", data, timedOut, self.processTimedOut)

    def processExpiredTasks(self, data, expired):
        return self.processTasks("expired", data, expired, self.processExpired)


    def processSucceeded(self, manager, data, task):
        task.move(self, "archived", getCurrentTimestamp(), self.r)

    def processFailed(self, manager, data, task):
        task.move(self, "archived", getCurrentTimestamp(), self.r)

    def processTimedOut(self, manager, data, task):
        task.move(self, "archived", getCurrentTimestamp(), self.r)

    def processExpired(self, manager, data, task):
        task.move(self, "archived", getCurrentTimestamp(), self.r)


    def run(self, data={}, succeeded=doNothing, failed=doNothing, timedOut=doNothing, expired=doNothing, stopProcessing=stopProcessing, endRound=endRound):
        roundCounter = 0
        while True:
            start = time.time()

            self.processSucceededTasks(data, succeeded)
            self.processFailedTasks(data, failed)
            self.processTimedOutTasks(data, timedOut)
            self.processExpiredTasks(data, expired)
            
            end = time.time()
            duration = end - start
            roundDuration = float(self.cfg.get("manager", "round_duration"))
            sleep = roundDuration - duration
            endRound(self, data, roundCounter)
            roundCounter += 1
            if stopProcessing(self, data, roundCounter):
                break
            if sleep > 0:
                time.sleep(sleep)


    def printStats(self, skipEmpty=True):
        print printPrefix + "~ ~ ~ ~ ~ ~ ~ ~ ~ ~"
        for state in states:
            size = self.getElementCount(state)
            if not skipEmpty or size > 0:
                print printPrefix + "~ %s:%s%s" % (state, " "*(logNameOffset-len(state)), size)
        print printPrefix + "~ ~ ~ ~ ~ ~ ~ ~ ~ ~"

    def printAll(self, verbose=False):
        print printPrefix + "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~"
        for state in states:
            if verbose:
                print printPrefix + "~ %s:%s%s" % (state, " "*(10-len(state)), self.getElementCount(state))
                for t in self.r.zscan(self.getKey(state))[1]:
                    print printPrefix + "             %s" % taskToStr(self.getTask(t[0]), True)
            else:
                print printPrefix + "~ %s:%s%s" % (state, " "*(10-len(state)), self.r.zscan(self.getKey(state))[1])
        print printPrefix + "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~"

    def printTask(self, task, printValues=False, printRounds=False, printOut=False, printErr=False, printAll=False):
        print "task:%s" % task.get("id")
        if printAll:
            printValues = True
            printRounds = True
            printOut = True
            printErr = True
        if printValues:
            defaults = { "start_after": self.cfg.get("manager", "start_after_default"),
                         "end_before": self.cfg.get("manager", "end_before_default"),
                         "timeout": self.cfg.get("manager", "timeout_default"),
                         "max_fails": self.cfg.get("manager", "max_fails_default") }
            keys = [ "program", "input", 
                     "start_after", "end_before", "timeout", "max_fails",
                     "state", "round", "fails", "timeouts",
                     "log" ]
            for key in keys:
                if key in defaults.keys() and str(task.get(key)) == str(defaults[key]):
                    print "    %s%s %s (default)" % (key, " "*(len("start_after")-len(key)), task.get(key))
                # else:
                print "    %s%s %s" % (key, " "*(len("start_after")-len(key)), task.get(key).replace("\n", "\n" + " "*(len("start_after")+5)))
        for r in range(0,int(task.get("round"))+1):
            if printRounds:
                order = []
                for state in states:
                    key = "%s:%s" % (r, state)
                    if key in task.values:
                        order.append(state)
                if len(order) > 0:
                    print "    round %s: %s" % (r, " -> ".join(order))
            if printOut:
                if "%s:output" % r in task.values:
                    print "    %s:out = %s" % (r, task.get("%s:output" % r).replace("\n", "\n" + " "*12))
            if printErr:
                if "%s:error" % r in task.values:
                    print "    %s:err = %s" % (r, task.get("%s:error" % r).replace("\n", "\n" + " "*12))



