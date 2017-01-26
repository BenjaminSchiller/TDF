# sources - example for the use of TDF

A worker can obtain a program from different sources (currently using rsync or wget).
Such a program must always contain a `run.sh` script (must be executable) and may contains any number of other files and directories.

In case a program does not consist of only a `run.sh`script, it must be provided as an archive.
In this example, we show the different archives that are supported by the worker.

Commonly, server and worker(s) run in an infinite loop in separate processes.
To show the actual workflow of TDF and its components, we launch server, worker, and master sequentially in a single program.


## The dummy program (`run.sh`)

The dummy program ([`run.sh`](local/path/run.sh)) outputs the current date, sleeps for 2 seconds, and output the date again.

	#!/bin/bash
	
	date
	sleep 2
	date

It should not fail :-D

To show the capabilities of the worker to obtain a program from various archives, we provide the [`run.sh`](local/path/run.sh) script as well as the following archives in [`local/path/`](local/path/):

	local/
		path/
			program.tar			program.tar.bz			program.tar.bz2			program.tar.gz			program.zip			run.sh

In this example, the programs are obtained using rsync.
Note that the use of wget (via http or https) works analogously.


## Configuration files

All configuration files used by the example program are located in [cfg/](cfg/).


## Description

The complete example is provided in the [`sources.py`](sources.py) script.

First, a manager is initialized to empty the current database (only for this example!).

Then, the manager creates six tasks with different program names, each of which points to a different source.
Afterwards, server and worker are initialized to process the open tasks.
Before executing a task, the worker first fetches the program from the corresponding source.
After moving a task to the state executed, the server processes them and moves them to the state succeeded.
After worker and server processed all six tasks, the manager creates two tasks with invalid or non-existing sources.
Their execution fails and the server moves them to the state failed afterwards.

Finally, this workflow is repeated.
While the results and the overall workflow is the same, the worker does not fetch the corresponding program as they are already available from the first execution.


## Log output

The following is a complete dump of the log output of the execution of [`sources.py`](sources.py).

	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - first, we empty the redis database (only for the example!)
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:17:25 - SourcesManager initializing 'SourcesManager' for namespace 'sources' (config: 'cfg/manager.cfg')
	2017-01-26 10:17:25 - SourcesManager FLUSHALL !!!!
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - creating tasks with different names and sources (no input required)
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:17:25 - SourcesManager initializing 'SourcesManager' for namespace 'sources' (config: 'cfg/manager.cfg')
	2017-01-26 10:17:25 - SourcesManager opened task 1: source-rsync--script 
	2017-01-26 10:17:25 - SourcesManager opened task 2: source-rsync--tar 
	2017-01-26 10:17:25 - SourcesManager opened task 3: source-rsync--tar-gz 
	2017-01-26 10:17:25 - SourcesManager opened task 4: source-rsync--tar-bz 
	2017-01-26 10:17:25 - SourcesManager opened task 5: source-rsync--tar-bz2 
	2017-01-26 10:17:25 - SourcesManager opened task 6: source-rsync--zip 
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the server has nothing to do yet (only checks if open tasks are expired
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:17:25 - Server     initializing 'Server' for namespace 'sources' (config: 'cfg/server.cfg')
	2017-01-26 10:17:25 - Server     processing 6 open tasks
	2017-01-26 10:17:25 - Server     0: processed 6 tasks
	2017-01-26 10:17:25 - Server     processing 6 open tasks
	2017-01-26 10:17:26 - Server     1: processed 6 tasks
	2017-01-26 10:17:26 - Server     processing 6 open tasks
	2017-01-26 10:17:26 - Server     2: processed 6 tasks
	2017-01-26 10:17:26 - Server     processing 6 open tasks
	2017-01-26 10:17:27 - Server     3: processed 6 tasks
	2017-01-26 10:17:27 - Server     processing 6 open tasks
	2017-01-26 10:17:27 - Server     4: processed 6 tasks
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the worker executes three tasks
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:17:27 - Worker     initializing 'Worker' for namespace 'sources' (config: 'cfg/worker.cfg')
	2017-01-26 10:17:27 - Worker     moving task 1: open -> running
	2017-01-26 10:17:27 - Worker     claimed task 1
	2017-01-26 10:17:27 - Worker     executing task 1: source-rsync--script 
	2017-01-26 10:17:27 - Worker     attempting to fetch program 'source-rsync--script' from 'rsync:local/path/run.sh'
	rsyncing run.sh from local/path/run.sh
	sending incremental file list
	run.sh
	
	sent 124 bytes  received 35 bytes  318.00 bytes/sec
	total size is 30  speedup is 0.19
	2017-01-26 10:17:27 - Worker     fetched program 'source-rsync--script'
	2017-01-26 10:17:29 - Worker     moving task 1: running -> executed
	2017-01-26 10:17:31 - Worker     moving task 2: open -> running
	2017-01-26 10:17:31 - Worker     claimed task 2
	2017-01-26 10:17:31 - Worker     executing task 2: source-rsync--tar 
	2017-01-26 10:17:31 - Worker     attempting to fetch program 'source-rsync--tar' from 'rsync:local/path/program.tar'
	rsyncing program.tar from local/path/program.tar
	sending incremental file list
	program.tar
	
	sent 219 bytes  received 35 bytes  508.00 bytes/sec
	total size is 2,048  speedup is 8.06
	untaring ./source-rsync--tar/program.tar to ./source-rsync--tar/
	x run.sh
	2017-01-26 10:17:31 - Worker     fetched program 'source-rsync--tar'
	2017-01-26 10:17:33 - Worker     moving task 2: running -> executed
	2017-01-26 10:17:35 - Worker     moving task 3: open -> running
	2017-01-26 10:17:35 - Worker     claimed task 3
	2017-01-26 10:17:35 - Worker     executing task 3: source-rsync--tar-gz 
	2017-01-26 10:17:35 - Worker     attempting to fetch program 'source-rsync--tar-gz' from 'rsync:local/path/program.tar.gz'
	rsyncing program.tar.gz from local/path/program.tar.gz
	sending incremental file list
	program.tar.gz
	
	sent 255 bytes  received 35 bytes  580.00 bytes/sec
	total size is 153  speedup is 0.53
	untaring ./source-rsync--tar-gz/program.tar.gz to ./source-rsync--tar-gz/
	x run.sh
	2017-01-26 10:17:35 - Worker     fetched program 'source-rsync--tar-gz'
	2017-01-26 10:17:37 - Worker     moving task 3: running -> executed
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the server processes the three tasks that the worker executed
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:17:39 - Server     initializing 'Server' for namespace 'sources' (config: 'cfg/server.cfg')
	2017-01-26 10:17:39 - Server     processing 3 open tasks
	2017-01-26 10:17:39 - Server     processing 3 executed tasks
	2017-01-26 10:17:39 - Server     moving task 1: executed -> succeeded
	2017-01-26 10:17:39 - Server     moving task 2: executed -> succeeded
	2017-01-26 10:17:39 - Server     moving task 3: executed -> succeeded
	2017-01-26 10:17:40 - Server     0: processed 6 tasks
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the worker executes three tasks
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:17:40 - Worker     initializing 'Worker' for namespace 'sources' (config: 'cfg/worker.cfg')
	2017-01-26 10:17:40 - Worker     moving task 4: open -> running
	2017-01-26 10:17:40 - Worker     claimed task 4
	2017-01-26 10:17:40 - Worker     executing task 4: source-rsync--tar-bz 
	2017-01-26 10:17:40 - Worker     attempting to fetch program 'source-rsync--tar-bz' from 'rsync:local/path/program.tar.bz'
	rsyncing program.tar.bz from local/path/program.tar.bz
	sending incremental file list
	program.tar.bz
	
	sent 266 bytes  received 35 bytes  602.00 bytes/sec
	total size is 157  speedup is 0.52
	untaring ./source-rsync--tar-bz/program.tar.bz to ./source-rsync--tar-bz/
	x run.sh
	2017-01-26 10:17:40 - Worker     fetched program 'source-rsync--tar-bz'
	2017-01-26 10:17:42 - Worker     moving task 4: running -> executed
	2017-01-26 10:17:44 - Worker     moving task 5: open -> running
	2017-01-26 10:17:44 - Worker     claimed task 5
	2017-01-26 10:17:44 - Worker     executing task 5: source-rsync--tar-bz2 
	2017-01-26 10:17:44 - Worker     attempting to fetch program 'source-rsync--tar-bz2' from 'rsync:local/path/program.tar.bz2'
	rsyncing program.tar.bz2 from local/path/program.tar.bz2
	sending incremental file list
	program.tar.bz2
	
	sent 267 bytes  received 35 bytes  604.00 bytes/sec
	total size is 157  speedup is 0.52
	untaring ./source-rsync--tar-bz2/program.tar.bz2 to ./source-rsync--tar-bz2/
	x run.sh
	2017-01-26 10:17:44 - Worker     fetched program 'source-rsync--tar-bz2'
	2017-01-26 10:17:46 - Worker     moving task 5: running -> executed
	2017-01-26 10:17:48 - Worker     moving task 6: open -> running
	2017-01-26 10:17:48 - Worker     claimed task 6
	2017-01-26 10:17:48 - Worker     executing task 6: source-rsync--zip 
	2017-01-26 10:17:48 - Worker     attempting to fetch program 'source-rsync--zip' from 'rsync:local/path/program.zip'
	rsyncing program.zip from local/path/program.zip
	sending incremental file list
	program.zip
	
	sent 226 bytes  received 35 bytes  522.00 bytes/sec
	total size is 182  speedup is 0.70
	unzipping ./source-rsync--zip/program.zip to ./source-rsync--zip/
	Archive:  ./source-rsync--zip/program.zip
	  inflating: ./source-rsync--zip/run.sh  
	2017-01-26 10:17:48 - Worker     fetched program 'source-rsync--zip'
	2017-01-26 10:17:50 - Worker     moving task 6: running -> executed
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the server processes the three tasks that the worker executed
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:17:52 - Server     initializing 'Server' for namespace 'sources' (config: 'cfg/server.cfg')
	2017-01-26 10:17:52 - Server     processing 3 executed tasks
	2017-01-26 10:17:52 - Server     moving task 4: executed -> succeeded
	2017-01-26 10:17:52 - Server     moving task 5: executed -> succeeded
	2017-01-26 10:17:52 - Server     moving task 6: executed -> succeeded
	2017-01-26 10:17:53 - Server     0: processed 3 tasks
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - creating tasks with invalid / non-existing sources
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:17:53 - SourcesManager initializing 'SourcesManager' for namespace 'sources' (config: 'cfg/manager.cfg')
	2017-01-26 10:17:53 - SourcesManager opened task 7: source-rsync--invald 
	2017-01-26 10:17:53 - SourcesManager opened task 8: source-rsync--non-existing 
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the worker executes the two new tasks, both should fail (idles for two rounds)
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:17:53 - Worker     initializing 'Worker' for namespace 'sources' (config: 'cfg/worker.cfg')
	2017-01-26 10:17:53 - Worker     moving task 7: open -> running
	2017-01-26 10:17:53 - Worker     claimed task 7
	2017-01-26 10:17:53 - Worker     executing task 7: source-rsync--invald 
	2017-01-26 10:17:53 - Worker     attempting to fetch program 'source-rsync--invald' from 'rsync:this/path/is/invalid/program.wrongExtension'
	invalid type of archive / program: rsync:this/path/is/invalid/program.wrongExtension
	2017-01-26 10:17:53 - Worker     could not fetch program 'source-rsync--invald'
	2017-01-26 10:17:53 - Worker     moving task 7: running -> executed
	2017-01-26 10:17:55 - Worker     moving task 8: open -> running
	2017-01-26 10:17:55 - Worker     claimed task 8
	2017-01-26 10:17:55 - Worker     executing task 8: source-rsync--non-existing 
	2017-01-26 10:17:55 - Worker     attempting to fetch program 'source-rsync--non-existing' from 'rsync:this/path/does/not/exist/blafasel.zip'
	rsyncing blafasel.zip from this/path/does/not/exist/blafasel.zip
	sending incremental file list
	rsync: change_dir "/Users/benni/TUD/Projects/TDF/examples/sources//this/path/does/not/exist" failed: No such file or directory (2)
	
	rsync error: some files/attrs were not transferred (see previous errors) (code 23) at main.c(1249) [sender=3.1.2]
	sent 20 bytes  received 12 bytes  64.00 bytes/sec
	total size is 0  speedup is 0.00
	2017-01-26 10:17:55 - Worker     could not fetch program 'source-rsync--non-existing'
	2017-01-26 10:17:55 - Worker     moving task 8: running -> executed
	2017-01-26 10:17:57 - Worker     no open task to claim
	2017-01-26 10:17:59 - Worker     no open task to claim
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the server processes the two failed tasks that the worker executed (and idles for 4 rounds)
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:18:01 - Server     initializing 'Server' for namespace 'sources' (config: 'cfg/server.cfg')
	2017-01-26 10:18:01 - Server     processing 2 executed tasks
	2017-01-26 10:18:01 - Server     moving task 7: executed -> failure
	2017-01-26 10:18:01 - Server     moving task 7: failure -> failed
	2017-01-26 10:18:01 - Server     moving task 8: executed -> failure
	2017-01-26 10:18:01 - Server     moving task 8: failure -> failed
	2017-01-26 10:18:01 - Server     0: processed 2 tasks
	2017-01-26 10:18:02 - Server     1: processed 0 tasks
	2017-01-26 10:18:02 - Server     2: processed 0 tasks
	2017-01-26 10:18:03 - Server     3: processed 0 tasks
	2017-01-26 10:18:03 - Server     4: processed 0 tasks
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - re-creating all tasks (this time, the worker dows not need to fetch the respective program)
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:18:03 - SourcesManager initializing 'SourcesManager' for namespace 'sources' (config: 'cfg/manager.cfg')
	2017-01-26 10:18:03 - SourcesManager opened task 9: source-rsync--script 
	2017-01-26 10:18:03 - SourcesManager opened task 10: source-rsync--tar 
	2017-01-26 10:18:03 - SourcesManager opened task 11: source-rsync--tar-gz 
	2017-01-26 10:18:03 - SourcesManager opened task 12: source-rsync--tar-bz 
	2017-01-26 10:18:03 - SourcesManager opened task 13: source-rsync--tar-bz2 
	2017-01-26 10:18:03 - SourcesManager opened task 14: source-rsync--zip 
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the server has nothing to do yet (only checks if open tasks are expired
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:18:03 - Server     initializing 'Server' for namespace 'sources' (config: 'cfg/server.cfg')
	2017-01-26 10:18:03 - Server     processing 6 open tasks
	2017-01-26 10:18:04 - Server     0: processed 6 tasks
	2017-01-26 10:18:04 - Server     processing 6 open tasks
	2017-01-26 10:18:04 - Server     1: processed 6 tasks
	2017-01-26 10:18:04 - Server     processing 6 open tasks
	2017-01-26 10:18:05 - Server     2: processed 6 tasks
	2017-01-26 10:18:05 - Server     processing 6 open tasks
	2017-01-26 10:18:05 - Server     3: processed 6 tasks
	2017-01-26 10:18:05 - Server     processing 6 open tasks
	2017-01-26 10:18:06 - Server     4: processed 6 tasks
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the worker executes three tasks
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:18:06 - Worker     initializing 'Worker' for namespace 'sources' (config: 'cfg/worker.cfg')
	2017-01-26 10:18:06 - Worker     moving task 10: open -> running
	2017-01-26 10:18:06 - Worker     claimed task 10
	2017-01-26 10:18:06 - Worker     executing task 10: source-rsync--tar 
	2017-01-26 10:18:08 - Worker     moving task 10: running -> executed
	2017-01-26 10:18:10 - Worker     moving task 11: open -> running
	2017-01-26 10:18:10 - Worker     claimed task 11
	2017-01-26 10:18:10 - Worker     executing task 11: source-rsync--tar-gz 
	2017-01-26 10:18:12 - Worker     moving task 11: running -> executed
	2017-01-26 10:18:14 - Worker     moving task 12: open -> running
	2017-01-26 10:18:14 - Worker     claimed task 12
	2017-01-26 10:18:14 - Worker     executing task 12: source-rsync--tar-bz 
	2017-01-26 10:18:16 - Worker     moving task 12: running -> executed
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the server processes the three tasks that the worker executed
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:18:18 - Server     initializing 'Server' for namespace 'sources' (config: 'cfg/server.cfg')
	2017-01-26 10:18:18 - Server     processing 3 open tasks
	2017-01-26 10:18:18 - Server     processing 3 executed tasks
	2017-01-26 10:18:18 - Server     moving task 10: executed -> succeeded
	2017-01-26 10:18:18 - Server     moving task 11: executed -> succeeded
	2017-01-26 10:18:18 - Server     moving task 12: executed -> succeeded
	2017-01-26 10:18:18 - Server     0: processed 6 tasks
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the worker executes three tasks
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:18:18 - Worker     initializing 'Worker' for namespace 'sources' (config: 'cfg/worker.cfg')
	2017-01-26 10:18:18 - Worker     moving task 13: open -> running
	2017-01-26 10:18:18 - Worker     claimed task 13
	2017-01-26 10:18:18 - Worker     executing task 13: source-rsync--tar-bz2 
	2017-01-26 10:18:20 - Worker     moving task 13: running -> executed
	2017-01-26 10:18:22 - Worker     moving task 14: open -> running
	2017-01-26 10:18:22 - Worker     claimed task 14
	2017-01-26 10:18:22 - Worker     executing task 14: source-rsync--zip 
	2017-01-26 10:18:25 - Worker     moving task 14: running -> executed
	2017-01-26 10:18:27 - Worker     moving task 9: open -> running
	2017-01-26 10:18:27 - Worker     claimed task 9
	2017-01-26 10:18:27 - Worker     executing task 9: source-rsync--script 
	2017-01-26 10:18:29 - Worker     moving task 9: running -> executed
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the server processes the three tasks that the worker executed
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:18:31 - Server     initializing 'Server' for namespace 'sources' (config: 'cfg/server.cfg')
	2017-01-26 10:18:31 - Server     processing 3 executed tasks
	2017-01-26 10:18:31 - Server     moving task 13: executed -> succeeded
	2017-01-26 10:18:31 - Server     moving task 14: executed -> succeeded
	2017-01-26 10:18:31 - Server     moving task 9: executed -> succeeded
	2017-01-26 10:18:31 - Server     0: processed 3 tasks
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - creating tasks with invalid / non-existing sources
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:18:31 - SourcesManager initializing 'SourcesManager' for namespace 'sources' (config: 'cfg/manager.cfg')
	2017-01-26 10:18:31 - SourcesManager opened task 15: source-rsync--invald 
	2017-01-26 10:18:31 - SourcesManager opened task 16: source-rsync--non-existing 
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the worker executes the two new tasks, both should fail (idles for two rounds)
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:18:31 - Worker     initializing 'Worker' for namespace 'sources' (config: 'cfg/worker.cfg')
	2017-01-26 10:18:31 - Worker     moving task 15: open -> running
	2017-01-26 10:18:31 - Worker     claimed task 15
	2017-01-26 10:18:31 - Worker     executing task 15: source-rsync--invald 
	2017-01-26 10:18:31 - Worker     attempting to fetch program 'source-rsync--invald' from 'rsync:this/path/is/invalid/program.wrongExtension'
	invalid type of archive / program: rsync:this/path/is/invalid/program.wrongExtension
	2017-01-26 10:18:31 - Worker     could not fetch program 'source-rsync--invald'
	2017-01-26 10:18:31 - Worker     moving task 15: running -> executed
	2017-01-26 10:18:33 - Worker     moving task 16: open -> running
	2017-01-26 10:18:33 - Worker     claimed task 16
	2017-01-26 10:18:33 - Worker     executing task 16: source-rsync--non-existing 
	2017-01-26 10:18:33 - Worker     attempting to fetch program 'source-rsync--non-existing' from 'rsync:this/path/does/not/exist/blafasel.zip'
	rsyncing blafasel.zip from this/path/does/not/exist/blafasel.zip
	sending incremental file list
	rsync: change_dir "/Users/benni/TUD/Projects/TDF/examples/sources//this/path/does/not/exist" failed: No such file or directory (2)
	
	sent 20 bytes  received 12 bytes  64.00 bytes/sec
	total size is 0  speedup is 0.00
	rsync error: some files/attrs were not transferred (see previous errors) (code 23) at main.c(1249) [sender=3.1.2]
	2017-01-26 10:18:33 - Worker     could not fetch program 'source-rsync--non-existing'
	2017-01-26 10:18:33 - Worker     moving task 16: running -> executed
	2017-01-26 10:18:35 - Worker     no open task to claim
	2017-01-26 10:18:37 - Worker     no open task to claim
	
	
	
	
	
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	- - - the server processes the two failed tasks that the worker executed (and idles for 4 rounds)
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	2017-01-26 10:18:39 - Server     initializing 'Server' for namespace 'sources' (config: 'cfg/server.cfg')
	2017-01-26 10:18:39 - Server     processing 2 executed tasks
	2017-01-26 10:18:39 - Server     moving task 15: executed -> failure
	2017-01-26 10:18:39 - Server     moving task 15: failure -> failed
	2017-01-26 10:18:39 - Server     moving task 16: executed -> failure
	2017-01-26 10:18:39 - Server     moving task 16: failure -> failed
	2017-01-26 10:18:40 - Server     0: processed 2 tasks
	2017-01-26 10:18:40 - Server     1: processed 0 tasks
	2017-01-26 10:18:41 - Server     2: processed 0 tasks
	2017-01-26 10:18:41 - Server     3: processed 0 tasks
	2017-01-26 10:18:42 - Server     4: processed 0 tasks
	[Finished in 77.3s]