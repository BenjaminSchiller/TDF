import sys

# sys.argv.append(10)
# sys.argv.append(500)
# sys.argv.append(10)

if len(sys.argv) == 4:
    m = int(sys.argv[1])
    n = int(sys.argv[2])
    p = int(sys.argv[3])
    print "computing sum of [%s,%s] with bucket size p=%s" % (m,n,p)
else:
    sys.stderr.write("expecting 3 arguments (%s given)\n" % (len(sys.argv)-1))
    sys.stderr.write("    1: m (first number to sum)\n")
    sys.stderr.write("    2: n (last number to sum)\n")
    sys.stderr.write("    3: p (count of numbers to sum)\n")
    sys.exit(1)


def succeeded(manager, data, task):
    res = task.get_last("output").replace("\n", "")
    data["currentList"].append(res)

def failed(manager, data, task):
    print "FAILED: %s" % task
    print " error: %s" % task.getLast("error").replace("\n", "\n           ")

def timed_out(manager, data, task):
    print "TIMED_OUT: %s" % task

def expired(manager, data, task):
    print "EXPIRED: %s" % task

def get_total_element_count(manager):
    states = ["open", "running", "executed", "timed_out", "expired", "succeeded", "failed"]
    count = 0
    for state in states:
        count += manager.get_element_count(state)
    return count

def end_round(manager, data, roundCounter):
    print "ending round %s (%s) (%s tasks left)" % (roundCounter, str(data["currentList"]), get_total_element_count(manager))
    if len(data["currentList"]) > 1:
        create_tasks(manager, data["currentList"])
        data["currentList"] = []
    elif get_total_element_count(manager) == 0:
        print "FINAL RESULT: %s" % data["currentList"][0]
        data["currentList"] = []

def stop_processing(manager, data, roundCounter):
    states = ["open", "running", "executed", "timed_out", "expired", "succeeded", "failed"]
    for state in states:
        if manager.get_element_count(state) != 0:
            return False
    return True


def create_task(manager, shortList):
    print "creating task for numbers: %s" % str(shortList)
    program = "sum"
    source = "rsync:run.sh"
    input = " ".join(shortList)
    manager.openTask("sum", "rsync:run.sh", input, add_random_start_offset=True)

def create_tasks(manager, longList):
    # print "creating tasks for numbers: %s" % str(longList)
    shortList = []
    for i in longList:
        shortList.append(str(i))
        if len(shortList) is p:
            create_task(manager, shortList)
            shortList = []
    if len(shortList) > 0:
        create_task(manager, shortList)

import sys
sys.path.insert(0, '../../src/')
import tdf
with tdf.TdfManager("SumManager", "cfg/manager.cfg") as manager:
    manager.flushall()

    create_tasks(manager, range(m,n+1))

    data = {"currentList" : []}
    manager.run(data=data, succeeded=succeeded, failed=failed, timed_out=timed_out, expired=expired, stop_processing=stop_processing, end_round=end_round)

    res = (n-m+1) * (n+m) / 2
    print "result should be: %s = (%s+%s) / 2 * (%s-%s+1)" % (res,n,m,n,m)
