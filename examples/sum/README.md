# sum - example for the use of TDF

In this example, we perform a "distributed" computation of the sum of all numbers in an interval `[m,n]`, e.g., `[10,100]`.


## The program (`run.sh`)

The program ([`run.sh`](run.sh)), executed by a worker, outputs the sum of all numbers passed as arguments to the script.

	#!/bin/bash
	
	sum=0
	for i in $@; do
		sum=$(($sum+$i))
	done
	echo $sum


## Configuration files

All configuration files are located in [cfg/](cfg/).


## Starting server and worker

To start server and worker instances, execute the following commands from the example's main directory:

	# starting the server
	python ../../src/server.py Server cfg/server.cfg
	# starting a worker
	python ../../src/worker.py Worker1 cfg/worker.cfg


## Starting the manager

To start the manager, execute the following command from the example's main directory:

	# starting the manager
	python sum.py $m $n $p

The pgroam takes 3 argument: `m`, `n`, and `p`.
The first two (`m` and `n`) define the interval of numbers to sum up.
The third argument denotes the bucket size of numbers that are grouped together for summing them up in each task.

An example call is:

	python sum.py 10 100 3


## The manager

Initially, the manager splits the interval `[m,n]` into sets of (maximum) size `p`.
For each set, it creates a task to sum them up using the program [`run.sh`](run.sh), which is obtained via the source `rsync:run.sh`.

These tasks, as well as the ones created later by the manager, are processed by worker and server.

The manager processes all timed_out, expired, succeeded, and failed tasks.
It reads the results of all succeeded tasks and creates new tasks to sum up up to `p` of these intermediate results.
The manager stops this process or creating new tasks from the intermediate results as soon as there is only a single succeeded task left and no task reside in open, running, executed, timed_out, expired, and failed.
The output this last succeeded task is the final sum.
The manager outputs this sum and terminates its execution.


## Log output (worker)

	2017-01-26 11:47:28 - Worker1    initializing 'Worker1' for namespace 'sum' (config: 'cfg/worker.cfg')
	2017-01-26 11:47:28 - Worker1    no open task to claim
	2017-01-26 11:47:30 - Worker1    no open task to claim
	2017-01-26 11:47:32 - Worker1    no open task to claim
	2017-01-26 11:47:34 - Worker1    moving task 2: open -> running
	2017-01-26 11:47:34 - Worker1    claimed task 2
	2017-01-26 11:47:34 - Worker1    executing task 2: sum 13 14 15
	2017-01-26 11:47:34 - Worker1    moving task 2: running -> executed
	2017-01-26 11:47:34 - Worker1    moving task 8: open -> running
	2017-01-26 11:47:34 - Worker1    claimed task 8
	2017-01-26 11:47:34 - Worker1    executing task 8: sum 31 32 33
	2017-01-26 11:47:34 - Worker1    moving task 8: running -> executed
	2017-01-26 11:47:34 - Worker1    moving task 9: open -> running
	2017-01-26 11:47:34 - Worker1    claimed task 9
	2017-01-26 11:47:34 - Worker1    executing task 9: sum 34 35 36
	2017-01-26 11:47:34 - Worker1    moving task 9: running -> executed
	2017-01-26 11:47:34 - Worker1    moving task 25: open -> running
	2017-01-26 11:47:34 - Worker1    claimed task 25
	2017-01-26 11:47:34 - Worker1    executing task 25: sum 82 83 84
	2017-01-26 11:47:34 - Worker1    moving task 25: running -> executed
	2017-01-26 11:47:34 - Worker1    moving task 11: open -> running
	2017-01-26 11:47:34 - Worker1    claimed task 11
	2017-01-26 11:47:34 - Worker1    executing task 11: sum 40 41 42
	2017-01-26 11:47:34 - Worker1    moving task 11: running -> executed
	2017-01-26 11:47:34 - Worker1    moving task 30: open -> running
	2017-01-26 11:47:34 - Worker1    claimed task 30
	2017-01-26 11:47:34 - Worker1    executing task 30: sum 97 98 99
	2017-01-26 11:47:34 - Worker1    moving task 30: running -> executed
	2017-01-26 11:47:34 - Worker1    moving task 31: open -> running
	2017-01-26 11:47:34 - Worker1    claimed task 31
	2017-01-26 11:47:34 - Worker1    executing task 31: sum 100
	2017-01-26 11:47:34 - Worker1    moving task 31: running -> executed
	2017-01-26 11:47:34 - Worker1    moving task 18: open -> running
	2017-01-26 11:47:34 - Worker1    claimed task 18
	2017-01-26 11:47:34 - Worker1    executing task 18: sum 61 62 63
	2017-01-26 11:47:34 - Worker1    moving task 18: running -> executed
	2017-01-26 11:47:34 - Worker1    moving task 5: open -> running
	2017-01-26 11:47:34 - Worker1    claimed task 5
	2017-01-26 11:47:34 - Worker1    executing task 5: sum 22 23 24
	2017-01-26 11:47:35 - Worker1    moving task 5: running -> executed
	2017-01-26 11:47:35 - Worker1    moving task 16: open -> running
	2017-01-26 11:47:35 - Worker1    claimed task 16
	2017-01-26 11:47:35 - Worker1    executing task 16: sum 55 56 57
	2017-01-26 11:47:35 - Worker1    moving task 16: running -> executed
	2017-01-26 11:47:35 - Worker1    moving task 1: open -> running
	2017-01-26 11:47:35 - Worker1    claimed task 1
	2017-01-26 11:47:35 - Worker1    executing task 1: sum 10 11 12
	2017-01-26 11:47:35 - Worker1    moving task 1: running -> executed
	2017-01-26 11:47:35 - Worker1    moving task 22: open -> running
	2017-01-26 11:47:35 - Worker1    claimed task 22
	2017-01-26 11:47:35 - Worker1    executing task 22: sum 73 74 75
	2017-01-26 11:47:35 - Worker1    moving task 22: running -> executed
	2017-01-26 11:47:35 - Worker1    moving task 3: open -> running
	2017-01-26 11:47:35 - Worker1    claimed task 3
	2017-01-26 11:47:35 - Worker1    executing task 3: sum 16 17 18
	2017-01-26 11:47:35 - Worker1    moving task 3: running -> executed
	2017-01-26 11:47:35 - Worker1    moving task 19: open -> running
	2017-01-26 11:47:35 - Worker1    claimed task 19
	2017-01-26 11:47:35 - Worker1    executing task 19: sum 64 65 66
	2017-01-26 11:47:35 - Worker1    moving task 19: running -> executed
	2017-01-26 11:47:35 - Worker1    moving task 14: open -> running
	2017-01-26 11:47:35 - Worker1    claimed task 14
	2017-01-26 11:47:35 - Worker1    executing task 14: sum 49 50 51
	2017-01-26 11:47:35 - Worker1    moving task 14: running -> executed
	2017-01-26 11:47:35 - Worker1    moving task 21: open -> running
	2017-01-26 11:47:35 - Worker1    claimed task 21
	2017-01-26 11:47:35 - Worker1    executing task 21: sum 70 71 72
	2017-01-26 11:47:35 - Worker1    moving task 21: running -> executed
	2017-01-26 11:47:35 - Worker1    moving task 26: open -> running
	2017-01-26 11:47:35 - Worker1    claimed task 26
	2017-01-26 11:47:35 - Worker1    executing task 26: sum 85 86 87
	2017-01-26 11:47:35 - Worker1    moving task 26: running -> executed
	2017-01-26 11:47:36 - Worker1    moving task 24: open -> running
	2017-01-26 11:47:36 - Worker1    claimed task 24
	2017-01-26 11:47:36 - Worker1    executing task 24: sum 79 80 81
	2017-01-26 11:47:36 - Worker1    moving task 24: running -> executed
	2017-01-26 11:47:36 - Worker1    moving task 34: open -> running
	2017-01-26 11:47:36 - Worker1    claimed task 34
	2017-01-26 11:47:36 - Worker1    executing task 34: sum 100 186 69
	2017-01-26 11:47:36 - Worker1    moving task 34: running -> executed
	2017-01-26 11:47:36 - Worker1    moving task 6: open -> running
	2017-01-26 11:47:36 - Worker1    claimed task 6
	2017-01-26 11:47:36 - Worker1    executing task 6: sum 25 26 27
	2017-01-26 11:47:36 - Worker1    moving task 6: running -> executed
	2017-01-26 11:47:36 - Worker1    moving task 33: open -> running
	2017-01-26 11:47:36 - Worker1    claimed task 33
	2017-01-26 11:47:36 - Worker1    executing task 33: sum 249 123 294
	2017-01-26 11:47:36 - Worker1    moving task 33: running -> executed
	2017-01-26 11:47:36 - Worker1    moving task 32: open -> running
	2017-01-26 11:47:36 - Worker1    claimed task 32
	2017-01-26 11:47:36 - Worker1    executing task 32: sum 42 96 105
	2017-01-26 11:47:36 - Worker1    moving task 32: running -> executed
	2017-01-26 11:47:36 - Worker1    moving task 17: open -> running
	2017-01-26 11:47:36 - Worker1    claimed task 17
	2017-01-26 11:47:36 - Worker1    executing task 17: sum 58 59 60
	2017-01-26 11:47:36 - Worker1    moving task 17: running -> executed
	2017-01-26 11:47:36 - Worker1    moving task 12: open -> running
	2017-01-26 11:47:36 - Worker1    claimed task 12
	2017-01-26 11:47:36 - Worker1    executing task 12: sum 43 44 45
	2017-01-26 11:47:36 - Worker1    moving task 12: running -> executed
	2017-01-26 11:47:36 - Worker1    moving task 20: open -> running
	2017-01-26 11:47:36 - Worker1    claimed task 20
	2017-01-26 11:47:36 - Worker1    executing task 20: sum 67 68 69
	2017-01-26 11:47:36 - Worker1    moving task 20: running -> executed
	2017-01-26 11:47:37 - Worker1    moving task 13: open -> running
	2017-01-26 11:47:37 - Worker1    claimed task 13
	2017-01-26 11:47:37 - Worker1    executing task 13: sum 46 47 48
	2017-01-26 11:47:37 - Worker1    moving task 13: running -> executed
	2017-01-26 11:47:37 - Worker1    moving task 10: open -> running
	2017-01-26 11:47:37 - Worker1    claimed task 10
	2017-01-26 11:47:37 - Worker1    executing task 10: sum 37 38 39
	2017-01-26 11:47:37 - Worker1    moving task 10: running -> executed
	2017-01-26 11:47:37 - Worker1    moving task 29: open -> running
	2017-01-26 11:47:37 - Worker1    claimed task 29
	2017-01-26 11:47:37 - Worker1    executing task 29: sum 94 95 96
	2017-01-26 11:47:37 - Worker1    moving task 29: running -> executed
	2017-01-26 11:47:37 - Worker1    moving task 27: open -> running
	2017-01-26 11:47:37 - Worker1    claimed task 27
	2017-01-26 11:47:37 - Worker1    executing task 27: sum 88 89 90
	2017-01-26 11:47:37 - Worker1    moving task 27: running -> executed
	2017-01-26 11:47:37 - Worker1    moving task 15: open -> running
	2017-01-26 11:47:37 - Worker1    claimed task 15
	2017-01-26 11:47:37 - Worker1    executing task 15: sum 52 53 54
	2017-01-26 11:47:37 - Worker1    moving task 15: running -> executed
	2017-01-26 11:47:37 - Worker1    moving task 35: open -> running
	2017-01-26 11:47:37 - Worker1    claimed task 35
	2017-01-26 11:47:37 - Worker1    executing task 35: sum 168 33
	2017-01-26 11:47:37 - Worker1    moving task 35: running -> executed
	2017-01-26 11:47:37 - Worker1    moving task 28: open -> running
	2017-01-26 11:47:37 - Worker1    claimed task 28
	2017-01-26 11:47:37 - Worker1    executing task 28: sum 91 92 93
	2017-01-26 11:47:37 - Worker1    moving task 28: running -> executed
	2017-01-26 11:47:37 - Worker1    moving task 4: open -> running
	2017-01-26 11:47:37 - Worker1    claimed task 4
	2017-01-26 11:47:37 - Worker1    executing task 4: sum 19 20 21
	2017-01-26 11:47:37 - Worker1    moving task 4: running -> executed
	2017-01-26 11:47:37 - Worker1    moving task 23: open -> running
	2017-01-26 11:47:37 - Worker1    claimed task 23
	2017-01-26 11:47:37 - Worker1    executing task 23: sum 76 77 78
	2017-01-26 11:47:38 - Worker1    moving task 23: running -> executed
	2017-01-26 11:47:38 - Worker1    moving task 7: open -> running
	2017-01-26 11:47:38 - Worker1    claimed task 7
	2017-01-26 11:47:38 - Worker1    executing task 7: sum 28 29 30
	2017-01-26 11:47:38 - Worker1    moving task 7: running -> executed
	2017-01-26 11:47:38 - Worker1    moving task 41: open -> running
	2017-01-26 11:47:38 - Worker1    claimed task 41
	2017-01-26 11:47:38 - Worker1    executing task 41: sum 114
	2017-01-26 11:47:38 - Worker1    moving task 41: running -> executed
	2017-01-26 11:47:38 - Worker1    moving task 39: open -> running
	2017-01-26 11:47:38 - Worker1    claimed task 39
	2017-01-26 11:47:38 - Worker1    executing task 39: sum 666 243 177
	2017-01-26 11:47:38 - Worker1    moving task 39: running -> executed
	2017-01-26 11:47:38 - Worker1    moving task 36: open -> running
	2017-01-26 11:47:38 - Worker1    claimed task 36
	2017-01-26 11:47:38 - Worker1    executing task 36: sum 222 51 195
	2017-01-26 11:47:38 - Worker1    moving task 36: running -> executed
	2017-01-26 11:47:38 - Worker1    moving task 40: open -> running
	2017-01-26 11:47:38 - Worker1    claimed task 40
	2017-01-26 11:47:38 - Worker1    executing task 40: sum 132 204 141
	2017-01-26 11:47:38 - Worker1    moving task 40: running -> executed
	2017-01-26 11:47:38 - Worker1    moving task 38: open -> running
	2017-01-26 11:47:38 - Worker1    claimed task 38
	2017-01-26 11:47:38 - Worker1    executing task 38: sum 240 355 78
	2017-01-26 11:47:38 - Worker1    moving task 38: running -> executed
	2017-01-26 11:47:38 - Worker1    moving task 37: open -> running
	2017-01-26 11:47:38 - Worker1    claimed task 37
	2017-01-26 11:47:38 - Worker1    executing task 37: sum 150 213 258
	2017-01-26 11:47:38 - Worker1    moving task 37: running -> executed
	2017-01-26 11:47:38 - Worker1    no open task to claim
	2017-01-26 11:47:40 - Worker1    moving task 42: open -> running
	2017-01-26 11:47:40 - Worker1    claimed task 42
	2017-01-26 11:47:40 - Worker1    executing task 42: sum 285 267 159
	2017-01-26 11:47:40 - Worker1    moving task 42: running -> executed
	2017-01-26 11:47:41 - Worker1    moving task 46: open -> running
	2017-01-26 11:47:41 - Worker1    claimed task 46
	2017-01-26 11:47:41 - Worker1    executing task 46: sum 673 621
	2017-01-26 11:47:41 - Worker1    moving task 46: running -> executed
	2017-01-26 11:47:41 - Worker1    moving task 44: open -> running
	2017-01-26 11:47:41 - Worker1    claimed task 44
	2017-01-26 11:47:41 - Worker1    executing task 44: sum 231 87 114
	2017-01-26 11:47:41 - Worker1    moving task 44: running -> executed
	2017-01-26 11:47:41 - Worker1    moving task 43: open -> running
	2017-01-26 11:47:41 - Worker1    claimed task 43
	2017-01-26 11:47:41 - Worker1    executing task 43: sum 201 276 60
	2017-01-26 11:47:41 - Worker1    moving task 43: running -> executed
	2017-01-26 11:47:41 - Worker1    moving task 45: open -> running
	2017-01-26 11:47:41 - Worker1    claimed task 45
	2017-01-26 11:47:41 - Worker1    executing task 45: sum 1086 468 477
	2017-01-26 11:47:41 - Worker1    moving task 45: running -> executed
	2017-01-26 11:47:41 - Worker1    no open task to claim
	2017-01-26 11:47:43 - Worker1    moving task 47: open -> running
	2017-01-26 11:47:43 - Worker1    claimed task 47
	2017-01-26 11:47:43 - Worker1    executing task 47: sum 711 1294 432
	2017-01-26 11:47:43 - Worker1    moving task 47: running -> executed
	2017-01-26 11:47:43 - Worker1    no open task to claim
	2017-01-26 11:47:45 - Worker1    moving task 48: open -> running
	2017-01-26 11:47:45 - Worker1    claimed task 48
	2017-01-26 11:47:45 - Worker1    executing task 48: sum 537 2031
	2017-01-26 11:47:45 - Worker1    moving task 48: running -> executed
	2017-01-26 11:47:45 - Worker1    no open task to claim
	2017-01-26 11:47:47 - Worker1    no open task to claim
	2017-01-26 11:47:49 - Worker1    moving task 49: open -> running
	2017-01-26 11:47:49 - Worker1    claimed task 49
	2017-01-26 11:47:49 - Worker1    executing task 49: sum 2437 2568
	2017-01-26 11:47:49 - Worker1    moving task 49: running -> executed
	2017-01-26 11:47:49 - Worker1    no open task to claim
	2017-01-26 11:47:51 - Worker1    no open task to claim
	2017-01-26 11:47:53 - Worker1    no open task to claim
	2017-01-26 11:47:55 - Worker1    no open task to claim
	2017-01-26 11:47:57 - Worker1    no open task to claim
	2017-01-26 11:47:59 - Worker1    no open task to claim





## Log output (server)

	2017-01-26 11:47:26 - Server     initializing 'Server' for namespace 'sum' (config: 'cfg/server.cfg')
	2017-01-26 11:47:27 - Server     0: processed 0 tasks
	2017-01-26 11:47:28 - Server     1: processed 0 tasks
	2017-01-26 11:47:29 - Server     2: processed 0 tasks
	2017-01-26 11:47:30 - Server     3: processed 0 tasks
	2017-01-26 11:47:31 - Server     4: processed 0 tasks
	2017-01-26 11:47:32 - Server     5: processed 0 tasks
	2017-01-26 11:47:32 - Server     processing 31 open tasks
	2017-01-26 11:47:33 - Server     6: processed 31 tasks
	2017-01-26 11:47:33 - Server     processing 31 open tasks
	2017-01-26 11:47:34 - Server     7: processed 31 tasks
	2017-01-26 11:47:34 - Server     processing 29 open tasks
	2017-01-26 11:47:34 - Server     processing 1 running tasks
	2017-01-26 11:47:34 - Server     processing 2 executed tasks
	2017-01-26 11:47:34 - Server     moving task 2: executed -> succeeded
	2017-01-26 11:47:34 - Server     moving task 8: executed -> succeeded
	2017-01-26 11:47:35 - Server     8: processed 32 tasks
	2017-01-26 11:47:35 - Server     processing 20 open tasks
	2017-01-26 11:47:35 - Server     processing 9 executed tasks
	2017-01-26 11:47:35 - Server     moving task 9: executed -> succeeded
	2017-01-26 11:47:35 - Server     moving task 25: executed -> succeeded
	2017-01-26 11:47:35 - Server     moving task 11: executed -> succeeded
	2017-01-26 11:47:35 - Server     moving task 30: executed -> succeeded
	2017-01-26 11:47:35 - Server     moving task 31: executed -> succeeded
	2017-01-26 11:47:35 - Server     moving task 18: executed -> succeeded
	2017-01-26 11:47:35 - Server     moving task 5: executed -> succeeded
	2017-01-26 11:47:35 - Server     moving task 16: executed -> succeeded
	2017-01-26 11:47:35 - Server     moving task 1: executed -> succeeded
	2017-01-26 11:47:36 - Server     9: processed 29 tasks
	2017-01-26 11:47:36 - Server     processing 16 open tasks
	2017-01-26 11:47:36 - Server     processing 8 executed tasks
	2017-01-26 11:47:36 - Server     moving task 22: executed -> succeeded
	2017-01-26 11:47:36 - Server     moving task 3: executed -> succeeded
	2017-01-26 11:47:36 - Server     moving task 19: executed -> succeeded
	2017-01-26 11:47:36 - Server     moving task 14: executed -> succeeded
	2017-01-26 11:47:36 - Server     moving task 21: executed -> succeeded
	2017-01-26 11:47:36 - Server     moving task 26: executed -> succeeded
	2017-01-26 11:47:36 - Server     moving task 24: executed -> succeeded
	2017-01-26 11:47:36 - Server     moving task 34: executed -> succeeded
	2017-01-26 11:47:37 - Server     10: processed 24 tasks
	2017-01-26 11:47:37 - Server     processing 8 open tasks
	2017-01-26 11:47:37 - Server     processing 8 executed tasks
	2017-01-26 11:47:37 - Server     moving task 6: executed -> succeeded
	2017-01-26 11:47:37 - Server     moving task 33: executed -> succeeded
	2017-01-26 11:47:37 - Server     moving task 32: executed -> succeeded
	2017-01-26 11:47:37 - Server     moving task 17: executed -> succeeded
	2017-01-26 11:47:37 - Server     moving task 12: executed -> succeeded
	2017-01-26 11:47:37 - Server     moving task 20: executed -> succeeded
	2017-01-26 11:47:37 - Server     moving task 13: executed -> succeeded
	2017-01-26 11:47:37 - Server     moving task 10: executed -> succeeded
	2017-01-26 11:47:38 - Server     11: processed 16 tasks
	2017-01-26 11:47:38 - Server     processing 5 open tasks
	2017-01-26 11:47:38 - Server     processing 9 executed tasks
	2017-01-26 11:47:38 - Server     moving task 29: executed -> succeeded
	2017-01-26 11:47:38 - Server     moving task 27: executed -> succeeded
	2017-01-26 11:47:38 - Server     moving task 15: executed -> succeeded
	2017-01-26 11:47:38 - Server     moving task 35: executed -> succeeded
	2017-01-26 11:47:38 - Server     moving task 28: executed -> succeeded
	2017-01-26 11:47:38 - Server     moving task 4: executed -> succeeded
	2017-01-26 11:47:38 - Server     moving task 23: executed -> succeeded
	2017-01-26 11:47:38 - Server     moving task 7: executed -> succeeded
	2017-01-26 11:47:38 - Server     moving task 41: executed -> succeeded
	2017-01-26 11:47:39 - Server     12: processed 14 tasks
	2017-01-26 11:47:39 - Server     processing 5 executed tasks
	2017-01-26 11:47:39 - Server     moving task 39: executed -> succeeded
	2017-01-26 11:47:39 - Server     moving task 36: executed -> succeeded
	2017-01-26 11:47:39 - Server     moving task 40: executed -> succeeded
	2017-01-26 11:47:39 - Server     moving task 38: executed -> succeeded
	2017-01-26 11:47:39 - Server     moving task 37: executed -> succeeded
	2017-01-26 11:47:40 - Server     13: processed 5 tasks
	2017-01-26 11:47:40 - Server     processing 5 open tasks
	2017-01-26 11:47:41 - Server     14: processed 5 tasks
	2017-01-26 11:47:41 - Server     processing 2 open tasks
	2017-01-26 11:47:41 - Server     processing 3 executed tasks
	2017-01-26 11:47:41 - Server     moving task 42: executed -> succeeded
	2017-01-26 11:47:41 - Server     moving task 46: executed -> succeeded
	2017-01-26 11:47:41 - Server     moving task 44: executed -> succeeded
	2017-01-26 11:47:42 - Server     15: processed 5 tasks
	2017-01-26 11:47:42 - Server     processing 1 open tasks
	2017-01-26 11:47:42 - Server     processing 2 executed tasks
	2017-01-26 11:47:42 - Server     moving task 43: executed -> succeeded
	2017-01-26 11:47:42 - Server     moving task 45: executed -> succeeded
	2017-01-26 11:47:43 - Server     16: processed 3 tasks
	2017-01-26 11:47:43 - Server     processing 1 open tasks
	2017-01-26 11:47:44 - Server     17: processed 1 tasks
	2017-01-26 11:47:44 - Server     processing 1 open tasks
	2017-01-26 11:47:44 - Server     processing 1 executed tasks
	2017-01-26 11:47:44 - Server     moving task 47: executed -> succeeded
	2017-01-26 11:47:45 - Server     18: processed 2 tasks
	2017-01-26 11:47:45 - Server     processing 1 open tasks
	2017-01-26 11:47:46 - Server     19: processed 1 tasks
	2017-01-26 11:47:46 - Server     processing 1 executed tasks
	2017-01-26 11:47:46 - Server     moving task 48: executed -> succeeded
	2017-01-26 11:47:47 - Server     20: processed 1 tasks
	2017-01-26 11:47:48 - Server     21: processed 0 tasks
	2017-01-26 11:47:48 - Server     processing 1 open tasks
	2017-01-26 11:47:49 - Server     22: processed 1 tasks
	2017-01-26 11:47:49 - Server     processing 1 open tasks
	2017-01-26 11:47:50 - Server     23: processed 1 tasks
	2017-01-26 11:47:50 - Server     processing 1 executed tasks
	2017-01-26 11:47:50 - Server     moving task 49: executed -> succeeded
	2017-01-26 11:47:51 - Server     24: processed 1 tasks
	2017-01-26 11:47:52 - Server     25: processed 0 tasks
	2017-01-26 11:47:53 - Server     26: processed 0 tasks
	2017-01-26 11:47:54 - Server     27: processed 0 tasks
	2017-01-26 11:47:55 - Server     28: processed 0 tasks
	2017-01-26 11:47:56 - Server     29: processed 0 tasks
	2017-01-26 11:47:57 - Server     30: processed 0 tasks


## Log output (manager)

	computing sum of [10,100] with bucket size p=3
	2017-01-26 11:47:32 - SumManager initializing 'SumManager' for namespace 'sum' (config: 'cfg/manager.cfg')
	2017-01-26 11:47:32 - SumManager FLUSHALL !!!!
	creating task for numbers: ['10', '11', '12']
	2017-01-26 11:47:32 - SumManager opened task 1: sum 10 11 12
	creating task for numbers: ['13', '14', '15']
	2017-01-26 11:47:32 - SumManager opened task 2: sum 13 14 15
	creating task for numbers: ['16', '17', '18']
	2017-01-26 11:47:32 - SumManager opened task 3: sum 16 17 18
	creating task for numbers: ['19', '20', '21']
	2017-01-26 11:47:32 - SumManager opened task 4: sum 19 20 21
	creating task for numbers: ['22', '23', '24']
	2017-01-26 11:47:32 - SumManager opened task 5: sum 22 23 24
	creating task for numbers: ['25', '26', '27']
	2017-01-26 11:47:32 - SumManager opened task 6: sum 25 26 27
	creating task for numbers: ['28', '29', '30']
	2017-01-26 11:47:32 - SumManager opened task 7: sum 28 29 30
	creating task for numbers: ['31', '32', '33']
	2017-01-26 11:47:32 - SumManager opened task 8: sum 31 32 33
	creating task for numbers: ['34', '35', '36']
	2017-01-26 11:47:32 - SumManager opened task 9: sum 34 35 36
	creating task for numbers: ['37', '38', '39']
	2017-01-26 11:47:32 - SumManager opened task 10: sum 37 38 39
	creating task for numbers: ['40', '41', '42']
	2017-01-26 11:47:32 - SumManager opened task 11: sum 40 41 42
	creating task for numbers: ['43', '44', '45']
	2017-01-26 11:47:32 - SumManager opened task 12: sum 43 44 45
	creating task for numbers: ['46', '47', '48']
	2017-01-26 11:47:32 - SumManager opened task 13: sum 46 47 48
	creating task for numbers: ['49', '50', '51']
	2017-01-26 11:47:32 - SumManager opened task 14: sum 49 50 51
	creating task for numbers: ['52', '53', '54']
	2017-01-26 11:47:32 - SumManager opened task 15: sum 52 53 54
	creating task for numbers: ['55', '56', '57']
	2017-01-26 11:47:32 - SumManager opened task 16: sum 55 56 57
	creating task for numbers: ['58', '59', '60']
	2017-01-26 11:47:32 - SumManager opened task 17: sum 58 59 60
	creating task for numbers: ['61', '62', '63']
	2017-01-26 11:47:32 - SumManager opened task 18: sum 61 62 63
	creating task for numbers: ['64', '65', '66']
	2017-01-26 11:47:32 - SumManager opened task 19: sum 64 65 66
	creating task for numbers: ['67', '68', '69']
	2017-01-26 11:47:32 - SumManager opened task 20: sum 67 68 69
	creating task for numbers: ['70', '71', '72']
	2017-01-26 11:47:32 - SumManager opened task 21: sum 70 71 72
	creating task for numbers: ['73', '74', '75']
	2017-01-26 11:47:32 - SumManager opened task 22: sum 73 74 75
	creating task for numbers: ['76', '77', '78']
	2017-01-26 11:47:32 - SumManager opened task 23: sum 76 77 78
	creating task for numbers: ['79', '80', '81']
	2017-01-26 11:47:32 - SumManager opened task 24: sum 79 80 81
	creating task for numbers: ['82', '83', '84']
	2017-01-26 11:47:32 - SumManager opened task 25: sum 82 83 84
	creating task for numbers: ['85', '86', '87']
	2017-01-26 11:47:32 - SumManager opened task 26: sum 85 86 87
	creating task for numbers: ['88', '89', '90']
	2017-01-26 11:47:32 - SumManager opened task 27: sum 88 89 90
	creating task for numbers: ['91', '92', '93']
	2017-01-26 11:47:32 - SumManager opened task 28: sum 91 92 93
	creating task for numbers: ['94', '95', '96']
	2017-01-26 11:47:32 - SumManager opened task 29: sum 94 95 96
	creating task for numbers: ['97', '98', '99']
	2017-01-26 11:47:32 - SumManager opened task 30: sum 97 98 99
	creating task for numbers: ['100']
	2017-01-26 11:47:32 - SumManager opened task 31: sum 100
	ending round 0 ([]) (31 tasks left)
	ending round 1 ([]) (31 tasks left)
	2017-01-26 11:47:36 - SumManager processing 11 succeeded tasks
	2017-01-26 11:47:36 - SumManager moving task 2: succeeded -> archived
	2017-01-26 11:47:36 - SumManager moving task 8: succeeded -> archived
	2017-01-26 11:47:36 - SumManager moving task 9: succeeded -> archived
	2017-01-26 11:47:36 - SumManager moving task 25: succeeded -> archived
	2017-01-26 11:47:36 - SumManager moving task 11: succeeded -> archived
	2017-01-26 11:47:36 - SumManager moving task 30: succeeded -> archived
	2017-01-26 11:47:36 - SumManager moving task 31: succeeded -> archived
	2017-01-26 11:47:36 - SumManager moving task 18: succeeded -> archived
	2017-01-26 11:47:36 - SumManager moving task 5: succeeded -> archived
	2017-01-26 11:47:36 - SumManager moving task 16: succeeded -> archived
	2017-01-26 11:47:36 - SumManager moving task 1: succeeded -> archived
	ending round 2 (['42', '96', '105', '249', '123', '294', '100', '186', '69', '168', '33']) (20 tasks left)
	creating task for numbers: ['42', '96', '105']
	2017-01-26 11:47:36 - SumManager opened task 32: sum 42 96 105
	creating task for numbers: ['249', '123', '294']
	2017-01-26 11:47:36 - SumManager opened task 33: sum 249 123 294
	creating task for numbers: ['100', '186', '69']
	2017-01-26 11:47:36 - SumManager opened task 34: sum 100 186 69
	creating task for numbers: ['168', '33']
	2017-01-26 11:47:36 - SumManager opened task 35: sum 168 33
	2017-01-26 11:47:38 - SumManager processing 16 succeeded tasks
	2017-01-26 11:47:38 - SumManager moving task 22: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 3: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 19: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 14: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 21: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 26: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 24: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 34: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 6: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 33: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 32: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 17: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 12: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 20: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 13: succeeded -> archived
	2017-01-26 11:47:38 - SumManager moving task 10: succeeded -> archived
	ending round 3 (['222', '51', '195', '150', '213', '258', '240', '355', '78', '666', '243', '177', '132', '204', '141', '114']) (8 tasks left)
	creating task for numbers: ['222', '51', '195']
	2017-01-26 11:47:38 - SumManager opened task 36: sum 222 51 195
	creating task for numbers: ['150', '213', '258']
	2017-01-26 11:47:38 - SumManager opened task 37: sum 150 213 258
	creating task for numbers: ['240', '355', '78']
	2017-01-26 11:47:38 - SumManager opened task 38: sum 240 355 78
	creating task for numbers: ['666', '243', '177']
	2017-01-26 11:47:38 - SumManager opened task 39: sum 666 243 177
	creating task for numbers: ['132', '204', '141']
	2017-01-26 11:47:38 - SumManager opened task 40: sum 132 204 141
	creating task for numbers: ['114']
	2017-01-26 11:47:38 - SumManager opened task 41: sum 114
	2017-01-26 11:47:40 - SumManager processing 14 succeeded tasks
	2017-01-26 11:47:40 - SumManager moving task 29: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 27: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 15: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 35: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 28: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 4: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 23: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 7: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 41: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 39: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 36: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 40: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 38: succeeded -> archived
	2017-01-26 11:47:40 - SumManager moving task 37: succeeded -> archived
	ending round 4 (['285', '267', '159', '201', '276', '60', '231', '87', '114', '1086', '468', '477', '673', '621']) (0 tasks left)
	creating task for numbers: ['285', '267', '159']
	2017-01-26 11:47:40 - SumManager opened task 42: sum 285 267 159
	creating task for numbers: ['201', '276', '60']
	2017-01-26 11:47:40 - SumManager opened task 43: sum 201 276 60
	creating task for numbers: ['231', '87', '114']
	2017-01-26 11:47:40 - SumManager opened task 44: sum 231 87 114
	creating task for numbers: ['1086', '468', '477']
	2017-01-26 11:47:40 - SumManager opened task 45: sum 1086 468 477
	creating task for numbers: ['673', '621']
	2017-01-26 11:47:40 - SumManager opened task 46: sum 673 621
	2017-01-26 11:47:42 - SumManager processing 3 succeeded tasks
	2017-01-26 11:47:42 - SumManager moving task 42: succeeded -> archived
	2017-01-26 11:47:42 - SumManager moving task 46: succeeded -> archived
	2017-01-26 11:47:42 - SumManager moving task 44: succeeded -> archived
	ending round 5 (['711', '1294', '432']) (2 tasks left)
	creating task for numbers: ['711', '1294', '432']
	2017-01-26 11:47:42 - SumManager opened task 47: sum 711 1294 432
	2017-01-26 11:47:44 - SumManager processing 2 succeeded tasks
	2017-01-26 11:47:44 - SumManager moving task 43: succeeded -> archived
	2017-01-26 11:47:44 - SumManager moving task 45: succeeded -> archived
	ending round 6 (['537', '2031']) (1 tasks left)
	creating task for numbers: ['537', '2031']
	2017-01-26 11:47:44 - SumManager opened task 48: sum 537 2031
	2017-01-26 11:47:46 - SumManager processing 1 succeeded tasks
	2017-01-26 11:47:46 - SumManager moving task 47: succeeded -> archived
	ending round 7 (['2437']) (1 tasks left)
	2017-01-26 11:47:48 - SumManager processing 1 succeeded tasks
	2017-01-26 11:47:48 - SumManager moving task 48: succeeded -> archived
	ending round 8 (['2437', '2568']) (0 tasks left)
	creating task for numbers: ['2437', '2568']
	2017-01-26 11:47:48 - SumManager opened task 49: sum 2437 2568
	ending round 9 ([]) (1 tasks left)
	2017-01-26 11:47:52 - SumManager processing 1 succeeded tasks
	2017-01-26 11:47:52 - SumManager moving task 49: succeeded -> archived
	ending round 10 (['5005']) (0 tasks left)
	FINAL RESULT: 5005
	result should be: 5005 = (100+10) / 2 * (100-10+1)