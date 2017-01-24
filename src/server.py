#!/usr/bin/python

import sys
if len(sys.argv) == 3:
    name = sys.argv[1]
    cfg_filename = sys.argv[2]
else:
    sys.stderr.write("expecting 2 arguments (%s given)\n" % (len(sys.argv)-1))
    sys.stderr.write("    1: name of this server instance\n")
    sys.stderr.write("    2: path to the server config file\n")
    sys.exit(1)

import tdf
with tdf.TdfServer(name, cfg_filename) as server:
    server.run()