import sys
sys.path.insert(0, '../../src/')
import tdf
with tdf.TdfManager("ProgramManager", "cfg/manager.cfg") as manager:
    manager.flushall()

    manager.openTask("from-rsync--script", "rsync:local/path/run.sh", "")
    manager.openTask("from-rsync--tar", "rsync:local/path/program.tar", "")
    manager.openTask("from-rsync--tar-gz", "rsync:local/path/program.tar.gz", "")
    manager.openTask("from-rsync--tar-bz", "rsync:local/path/program.tar.bz", "")
    manager.openTask("from-rsync--tar-bz2", "rsync:local/path/program.tar.bz2", "")
    manager.openTask("from-rsync--zip", "rsync:local/path/program.zip", "")


with tdf.TdfServer("Server", "cfg/server.cfg") as server:
    server.run(3)

with tdf.TdfWorker("Worker", "cfg/worker.cfg") as worker:
    worker.run(2)

with tdf.TdfServer("Server", "cfg/server.cfg") as server:
    server.run(3)

with tdf.TdfWorker("Worker", "cfg/worker.cfg") as worker:
    worker.run(10)

with tdf.TdfServer("Server", "cfg/server.cfg") as server:
    server.run(1)
