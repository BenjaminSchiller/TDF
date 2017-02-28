import redis
import time
import ConfigParser
import subprocess32 as subprocess
import os

states = ["open", "running", "executed", "timeout", "timed_out", "expired", "succeeded", "failure", "failed", "archived"]

print_prefix = " "*8
log_name_offset = 10
log_datetime_format = "%Y-%m-%d %H:%M:%S"






class PipelineRes:
    """Helper for retrieving the result(s) from a redis pipeline call."""

    def __init__(self):
        self.res = None


class Pipeline:
    """Helper that encapsulates a redis pipeline call."""

    def __init__(self, r, res=PipelineRes()):
        """Initialize a redis pipeline.
        
        args:
            r (redis connection): the connection to create a pipeline from
            res (PipelineRes object): for storing the results of the executed pipeline
        """
        self.p = r.pipeline(transaction=True)
        self.res = res

    def __enter__(self):
        return self.p
    
    def __exit__(self, type, value, traceback):
        self.res.res = self.p.execute()
        return self.res.res




def log(msg, task=None, p=None):
    datetime = time.strftime(log_datetime_format, time.gmtime())
    line = "%s - %s" % (datetime, msg)
    print line
    if not task is None:
        log = line if task.get("log") is "" else "%s\n%s" % (task.get("log"), line)
        task.set("log", log, p)







class Task:
    def __init__( self, values):
        self.values = values

    def __str__(self):
        return "task %s: %s %s" % (self.get("id"), self.get("program"), self.get("input"))

    def key(self, key):
        return "%s:%s" % (self.get("namespace"), key)

    def current_key(self, key):
        return "%s:%s" % (self.get("round"), key)

    def last_key(self, key):
        for i in range(int(self.get("round")), -1, -1):
            key = "%s:%s" % (i, key)
            if key in self.values:
                return key
        return None

    def get(self, key):
        return self.values[key]

    def get_current(self, key):
        return self.get(self.current_key(key))

    def get_last(self, key):
        return self.get(self.last_key(key))

    def set(self, key, value, r=None):
        self.values[key] = value
        if not r is None:
            r.hmset(self.key("task:%s" % self.get("id")), {key: value})

    def set_current(self, key, value, r=None):
        self.set(self.current_key(key), value, r)

    def set_current_timestamp(self, key, r=None):
        self.set(self.current_key(key), time.time(), r)

    def incr(self, key, r=None):
        self.set(key, int(self.get(key)) + 1, r)

    def open(self, r):
        id = r.incr(self.key("task_id"))
        self.set("id", id)
        self.set("state", "open")
        self.set("0:open", time.time())
        with Pipeline(r) as p:
            p.zadd(self.key("open"), self.get("start_after"), id)
            p.hmset(self.key("task:%i" % id), self.values)

    def is_expired(self):
        return (time.time() > float(self.get("end_before")))

    def is_timed_out(self):
        duration = time.time() - float(self.get_current("running"))
        return (duration > float(self.get("timeout")))

    def is_failed(self):
        err = self.get_current("error")
        return not (err is None or err == "")

    def is_failed_too_often(self):
        return (int(self.get("fails")) > int(self.get("max_fails")))

    def is_timed_out_too_often(self):
        return (int(self.get("timeouts")) > int(self.get("max_timeouts")))

    def is_program_available(self):
        return os.path.isdir('./%s/' % self.get("program")) and os.path.isfile('./%s/run.sh' % self.get("program"))

    def fetch_program(self):
        src = self.get("source")
        if not os.path.isdir('./%s/' % self.get("program")):
            os.makedirs('./%s/' % self.get("program"))
        if not (src.endswith(".zip") or src.endswith(".tar") or src.endswith(".tar.gz") or src.endswith(".tar.bz") or src.endswith(".tar.bz2") or src.endswith("/run.sh") or src.endswith(":run.sh")):
            log("invalid type of archive / program: %s" % src, self.task)
            return False
        if src.startswith("http://") or src.startswith("https://"):
            path = src
            archive = src.split("/")[-1]
            log("downloading %s from %s" % (archive, path), self.task)
            if not os.system("wget %s -P ./%s/" % (path, self.get("program"))) == 0:
                return False
            if not archive.endswith("run.sh"):
                return self.unpack(self.get("program"), archive)
            else:
                return True
        elif src.startswith("rsync:"):
            path = src.replace("rsync:","",1)
            archive = path.split("/")[-1]
            log("rsyncing %s from %s" % (archive, path), self)
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
            log("unzipping %s to %s" % (src, dst), self)
            return os.system("unzip %s -d %s" % (src, dst)) == 0
        elif archive.endswith(".tar"):
            log("untaring %s to %s" % (src, dst), self)
            return os.system("tar -xvf %s -C %s" % (src, dst)) == 0
        elif archive.endswith(".tar.gz"):
            log("untaring %s to %s" % (src, dst), self)
            return os.system("tar -zxvf %s -C %s" % (src, dst)) == 0
        elif archive.endswith(".tar.bz"):
            log("untaring %s to %s" % (src, dst), self)
            return os.system("tar -jxvf %s -C %s" % (src, dst)) == 0
        elif archive.endswith(".tar.bz2"):
            log("untaring %s to %s" % (src, dst), self)
            return os.system("tar -jxvf %s -C %s" % (src, dst)) == 0
        else:
            log("invalid archive for unpacking: %s" % src, self)
            return False

    def move(self, dst_state, score, r, properties_to_update={}):
        remove = r.zrem(self.key(self.get("state")), self.get("id"))

        if remove is 1:
            with Pipeline(r) as p:
                # log
                log("moving task %s: %s -> %s" % (self.get("id"), self.get("state"), dst_state), self, p)

                # add to dst state
                p.zadd(self.key(dst_state), score, self.get("id"))

                # change state stored in task
                if not dst_state is "archived":
                    self.set("state", dst_state, p)

                # set timestamp of this transition
                self.set_current_timestamp(dst_state, p)

                # update addition properties of the task
                for key in properties_to_update:
                    self.set(key, properties_to_update[key], p)

            return True
        else:
            log("could not move task task %s: %s -> %s" % (self.get("id"), self.get("state"), dst_state))
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
        log("initializing '%s' for namespace '%s' (config: '%s')" % (self.name, self.namespace, self.cfg_filename,))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def key(self, key):
        return "%s:%s" % (self.namespace, key)

    def worker_id(self, name):
        id = self.r.get(self.key("worker_id:%s" % name))
        if id is None:
            id = self.r.incr(self.key("worker_id"))
            self.r.set(self.key("worker_id:%s" % name), id)
            self.r.sadd(self.key("worker"), name)
        return id

    def workers(self):
        return self.r.smembers(self.key("worker"))

    def get_task(self, task_id):
        return Task(self.r.hgetall(self.key("task:%s" % task_id)))

    def process_tasks(self, state, data, process1, process2=None):
        size = self.get_element_count(state)
        if size > 0:
            log("processing %s %s tasks" % (size, state))
            for id in self.r.zscan(self.key(state))[1]:
                task = self.get_task(id[0])
                process1(self, data, task)
                if not process2 is None:
                    process2(self, data, task)
        return size

    def get_element_count(self, state):
        return self.r.zcard(self.key(state))

 






class TdfServer(Tdf):
    def __init__(self, *args, **kwargs):
        super(TdfServer, self).__init__(*args, **kwargs)

    def flushall(self):
        log("FLUSHALL !!!!")
        self.r.flushall()


    def process_open_tasks(self):
        return self.process_tasks("open", {}, self.process_open)

    def process_running_tasks(self):
        return self.process_tasks("running", {}, self.process_running)

    def process_executed_tasks(self):
        return self.process_tasks("executed", {}, self.process_executed)


    def process_open(self, manager, data, task):
        if task.is_expired():
            task.move("expired", time.time(), self.r)

    def process_running(self, manager, data, task):
        if task.is_expired():
            task.move("expired", time.time(), self.r)
        elif task.is_timed_out():
            task.incr("timeouts")
            properties_to_update={"timeouts": task.get("timeouts")}
            if task.is_timed_out_too_often():
                task.move("timeout", time.time(), self.r, properties_to_update)
                task.move("timed_out", time.time(), self.r)
            else:
                task.incr("round")
                properties_to_update["round"] = task.get("round")
                task.move("timeout", time.time(), self.r, properties_to_update)
                task.move("open", time.time(), self.r)

    def process_executed(self, manager, data, task):
        if task.is_expired():
            task.move("expired", time.time(), self.r)
        elif task.is_failed():
            task.incr("fails")
            if task.is_failed_too_often():
                task.move("failure", time.time(), self.r, {"fails": task.get("fails")})
                task.move("failed", time.time(), self.r)
            else:
                task.move("failure", time.time(), self.r, {"fails": task.get("fails")})
                task.incr("round")
                task.move("open", time.time(), self.r, {"round": task.get("round")})
        else:
            task.move("succeeded", time.time(), self.r)

    def run(self, rounds=float("Inf")):
        round_counter = 0
        while round_counter < rounds:
            start = time.time()

            processed_tasks = self.process_open_tasks()
            processed_tasks += self.process_running_tasks()
            processed_tasks += self.process_executed_tasks()
            
            end = time.time()
            duration = end - start
            round_duration = float(self.cfg.get("server", "round_duration"))
            sleep = round_duration - duration
            if sleep > 0:
                time.sleep(sleep)
            log("%s: processed %s tasks" % (round_counter, processed_tasks))
            round_counter += 1








class TdfWorker(Tdf):
    def __init__(self, *args, **kwargs):
        super(TdfWorker, self).__init__(*args, **kwargs)
        self.worker_id = self.worker_id(self.name)
        self.task = None

    def claim_open_task(self):
        openTasks = self.r.zrange(self.key("open"), 0, 0)
        if openTasks is None or len(openTasks) is 0:
            log("no open task to claim")
            return False
        else:
            self.task = self.get_task(openTasks[0])
            claim = self.task.move("running", time.time(), self.r, {self.task.current_key("worker"): self.name})
            if claim:
                log("claimed task %s" % self.task.get("id"))
                return True
            else:
                log("could not claim task %s" % self.task.get("id"))
                self.task = None
                return False

    def execute_task(self):
        if self.task is None:
            log("cannot execute, no task claimed")
            return False
        else:
            log("executing task %s: %s %s" % (self.task.get("id"), self.task.get("program"), self.task.get("input")), self.task)

            if not self.task.is_program_available():
                log("attempting to fetch program '%s' from '%s'" % (self.task.get("program"), self.task.get("source")))
                if self.task.fetch_program():
                    log("fetched program '%s'" % self.task.get("program"))
                else:
                    log("could not fetch program '%s'" % self.task.get("program"))
                    out = ""
                    err = "could not fetch program '%s' at worker '%s'" % (self.task.get("program"), self.name)
                    timed_out = False

            if self.task.is_program_available():
                cmd = "cd ./%s/; ./run.sh %s" % (self.task.get("program"), self.task.get("input"))
                out, err, timed_out = self.execute(cmd, self.task.get("timeout"))
            else:
                out = ""
                err = "program './%s/run.sh' does not exist!" % self.task.get("program")
                timed_out = False

            properties_to_update = {self.task.current_key("output"): out, self.task.current_key("error"): err}

            if timed_out:
                err += "\nTERMINATED - execution timed out..."
                log("task %s was terminated (timeout)" % self.task.get("id"))

                self.task.incr("timeouts")
                properties_to_update["timeouts"] = self.task.get("timeouts")
                if self.task.is_timed_out_too_often():
                    moved = self.task.move("timeout", time.time(), self.r, properties_to_update)
                    if not moved:
                        log("could not mark task %i as timed out (already timed out by server?)" % self.task.get("id"))
                    else:
                        moved = self.task.move("timed_out", time.time(), self.r)
                else:
                    moved = self.task.move("timeout", time.time(), self.r, properties_to_update)
                    if not moved:
                        log("could not re-open task %i as timed out (already re-opened by server?)" % self.task.get("id"))
                    else:
                        self.task.incr("round")
                        moved = self.task.move("open", time.time(), self.r, {"round": self.task.get("round")})

                self.task = None
                return False
            else:
                moved = self.task.move("executed", time.time(), self.r, properties_to_update)
                if not moved:
                    log("could not mark task %s as executed (timed out by server?)" % self.task.get("id"))
                    self.task = None
                    return False
                else:
                    self.task = None
                    return True

    def read_log(self, filename):
        with open(filename, "r") as f:
            return f.read()

    def make_dirs(self, filename):
        dirs = os.path.dirname(filename)
        if not dirs is "":
            if not os.path.exists(dirs):
                os.makedirs(dirs)

    def execute(self, cmd, timeout):
        output_filename = self.cfg.get("worker", "task_output_filename").replace("$worker", self.name).replace("$taskId", self.task.get("id")).replace("$round", self.task.get("round")).replace("$program", self.task.get("program"))
        error_filename = self.cfg.get("worker", "task_error_filename").replace("$worker", self.name).replace("$taskId", self.task.get("id")).replace("$round", self.task.get("round")).replace("$program", self.task.get("program"))
        self.make_dirs(output_filename)
        self.make_dirs(error_filename)
        with open(output_filename, "w") as out:
            with open(error_filename, "w") as err:
                timed_out = False
                try:
                    code = subprocess.call(cmd, shell=True, timeout=float(timeout), stdout=out, stderr=err)
                except subprocess.TimeoutExpired:
                    timed_out = True
        output = self.read_log(output_filename)
        error = self.read_log(error_filename)
        return output, error, timed_out

    def run(self, rounds=float("Inf")):
        round_counter = 0
        while round_counter < rounds:
            if self.claim_open_task():
                if self.execute_task():
                    time.sleep(float(self.cfg.get("worker", "sleep_after_success")))
                else:
                    time.sleep(float(self.cfg.get("worker", "sleep_after_failure")))
            else:
                time.sleep(float(self.cfg.get("worker", "sleep_after_no_process_claimed")))
            round_counter += 1






import random


def do_nothing(task):
    pass

def stop_processing(manager, data, round_counter):
    return False

def end_round(manager, data, round_counter):
    return False

class TdfManager(Tdf):
    def __init__(self, *args, **kwargs):
        super(TdfManager, self).__init__(*args, **kwargs)

    def flushall(self):
        log("FLUSHALL !!!!")
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
        log("opened task %s: %s %s" % (task.get("id"), task.get("program"), task.get("input")))
        return task

    def process_succeeded_tasks(self, data, success):
        return self.process_tasks("succeeded", data, success, self.process_succeeded)

    def process_failed_tasks(self, data, failure):
        return self.process_tasks("failed", data, failure, self.process_failed)

    def process_timed_out_tasks(self, data, timed_out):
        return self.process_tasks("timed_out", data, timed_out, self.process_timed_out)

    def process_expired_tasks(self, data, expired):
        return self.process_tasks("expired", data, expired, self.process_expired)


    def process_succeeded(self, manager, data, task):
        task.move("archived", time.time(), self.r)

    def process_failed(self, manager, data, task):
        task.move("archived", time.time(), self.r)

    def process_timed_out(self, manager, data, task):
        task.move("archived", time.time(), self.r)

    def process_expired(self, manager, data, task):
        task.move("archived", time.time(), self.r)


    def run(self, data={}, succeeded=do_nothing, failed=do_nothing, timed_out=do_nothing, expired=do_nothing, stop_processing=stop_processing, end_round=end_round):
        round_counter = 0
        while True:
            start = time.time()

            self.process_succeeded_tasks(data, succeeded)
            self.process_failed_tasks(data, failed)
            self.process_timed_out_tasks(data, timed_out)
            self.process_expired_tasks(data, expired)
            
            end = time.time()
            duration = end - start
            round_duration = float(self.cfg.get("manager", "round_duration"))
            sleep = round_duration - duration
            end_round(self, data, round_counter)
            round_counter += 1
            if stop_processing(self, data, round_counter):
                break
            if sleep > 0:
                time.sleep(sleep)


    def print_stats(self, skip_empty=True):
        print print_prefix + "~ ~ ~ ~ ~ ~ ~ ~ ~ ~"
        for state in states:
            size = self.get_element_count(state)
            if not skip_empty or size > 0:
                print print_prefix + "~ %s:%s%s" % (state, " "*(log_name_offset-len(state)), size)
        print print_prefix + "~ ~ ~ ~ ~ ~ ~ ~ ~ ~"

    def print_all(self, verbose=False):
        print print_prefix + "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~"
        for state in states:
            if verbose:
                print print_prefix + "~ %s:%s%s" % (state, " "*(10-len(state)), self.get_element_count(state))
                for t in self.r.zscan(self.key(state))[1]:
                    if verbose:
                        t = "task:%s: %s %s @%s (%s)" % (task.get("id"), 
                            task.get("program"), task.get("input"), 
                            task.get("state"), task.getCurrentValue("worker"))
                        print print_prefix + "             %s" % t
            else:
                print print_prefix + "~ %s:%s%s" % (state, " "*(10-len(state)), self.r.zscan(self.key(state))[1])
        print print_prefix + "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~"

    def print_task(self, task, print_values=False, print_rounds=False, print_out=False, print_err=False, print_all=False):
        print "task:%s" % task.get("id")
        if print_all:
            print_values = True
            print_rounds = True
            print_out = True
            print_err = True
        if print_values:
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
            if print_rounds:
                order = []
                for state in states:
                    key = "%s:%s" % (r, state)
                    if key in task.values:
                        order.append(state)
                if len(order) > 0:
                    print "    round %s: %s" % (r, " -> ".join(order))
            if print_out:
                if "%s:output" % r in task.values:
                    print "    %s:out = %s" % (r, task.get("%s:output" % r).replace("\n", "\n" + " "*12))
            if print_err:
                if "%s:error" % r in task.values:
                    print "    %s:err = %s" % (r, task.get("%s:error" % r).replace("\n", "\n" + " "*12))



