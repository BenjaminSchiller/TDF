#!/bin/bash

name = "TheManager"
cfg_filename = "cfg/tdf-manager.cfg"

def succeeded(task):
    print "SUCCEEDED: %s" % task
    # print "   output: %s" % task.getLast("output").replace("\n", "\n           ")
def failed(task):
    print "FAILED: %s" % task
    # print " error: %s" % task.getLast("error").replace("\n", "\n           ")
def timedOut(task):
    print "TIMED_OUT: %s" % task
def expired(task):
    print "EXPIRED: %s" % task

import tdf
with tdf.TdfManager(name, cfg_filename) as manager:
    # manager.flushall()

    # cmd = "echo 'good1'; >&2 echo 'bad1'; sleep 0.2; echo 'good2'; >&2 echo 'bad2'; sleep 0.2; echo 'good3'; >&2 echo 'bad3'"
    # for i in range(0,10):
    #     manager.openTask(cmd, "", max_fails=1, max_timeouts=1, timeout=0.1)
    #     manager.openTask(cmd, "", max_fails=1, max_timeouts=1, timeout=1.0)
    #     manager.openTask(cmd, "", max_fails=3, max_timeouts=3, timeout=0.3)
    #     manager.openTask("echo 'great!!!!'", "", max_fails=1, max_timeouts=1, timeout=0.1)


    # manager.printTask(manager.getTask(1), printRounds=True)
    # manager.printTask(manager.getTask(2), printRounds=True)
    # manager.printTask(manager.getTask(3), printRounds=True)
    # manager.printTask(manager.getTask(4), printRounds=True)
    # manager.printTask(manager.getTask(5), printRounds=True)
    # manager.printTask(manager.getTask(6), printRounds=True)

    # manager.run(succeeded=succeeded, failed=failed, timedOut=timedOut, expired=expired)

    manager.printStats()
    manager.printAll()

