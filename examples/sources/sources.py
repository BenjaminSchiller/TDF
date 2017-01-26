import sys
sys.path.insert(0, '../../src/')
import tdf

def log(msg, lines=5):
    print "%s- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -" % ("\n"*lines)
    print "- - - %s" % msg
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"

log("first, we empty the redis database (only for the example!)", lines=0)
with tdf.TdfManager("SourcesManager", "cfg/manager.cfg") as manager: manager.flushall()

for i in range(0,2):
    if i == 0:
        log("creating tasks with different names and sources (no input required)")
    else:
        log("re-creating all tasks (this time, the worker dows not need to fetch the respective program)")
    with tdf.TdfManager("SourcesManager", "cfg/manager.cfg") as manager:
        manager.openTask("source-rsync--script", "rsync:local/path/run.sh", "")
        manager.openTask("source-rsync--tar", "rsync:local/path/program.tar", "")
        manager.openTask("source-rsync--tar-gz", "rsync:local/path/program.tar.gz", "")
        manager.openTask("source-rsync--tar-bz", "rsync:local/path/program.tar.bz", "")
        manager.openTask("source-rsync--tar-bz2", "rsync:local/path/program.tar.bz2", "")
        manager.openTask("source-rsync--zip", "rsync:local/path/program.zip", "")

    log("the server has nothing to do yet (only checks if open tasks are expired")
    with tdf.TdfServer("Server", "cfg/server.cfg") as server: server.run(5)

    for j in range(0,2):
        log("the worker executes three tasks")
        with tdf.TdfWorker("Worker", "cfg/worker.cfg") as worker: worker.run(3)
        log("the server processes the three tasks that the worker executed")
        with tdf.TdfServer("Server", "cfg/server.cfg") as server: server.run(1)

    log("creating tasks with invalid / non-existing sources")
    with tdf.TdfManager("SourcesManager", "cfg/manager.cfg") as manager:
        manager.openTask("source-rsync--invald", "rsync:this/path/is/invalid/program.wrongExtension", "")
        manager.openTask("source-rsync--non-existing", "rsync:this/path/does/not/exist/blafasel.zip", "")

    log("the worker executes the two new tasks, both should fail (idles for two rounds)")
    with tdf.TdfWorker("Worker", "cfg/worker.cfg") as worker: worker.run(4)
    log("the server processes the two failed tasks that the worker executed (and idles for 4 rounds)")
    with tdf.TdfServer("Server", "cfg/server.cfg") as server: server.run(5)
