#!/bin/bash
# set -eE

/opt/omero/server/venv3/bin/omero group -u root -p 4064 -w omero --server omero-server \
                     add --perms rwra-- JCB2009
/opt/omero/server/venv3/bin/omero user  -u root -p 4064 -w omero --server omero-server \
                     add -P omero facility0 Facility0 Facility user
/opt/omero/server/venv3/bin/omero user -u root -p 4064 -w omero --server omero-server \
                     add -P omero user0 User0 Users  user
/opt/omero/server/venv3/bin/omero user -u root -p 4064 -w omero --server omero-server \
                     add -P omero user1 User1 Users  user
/opt/omero/server/venv3/bin/omero user -u root -p 4064 -w omero --server omero-server \
                     add -P omero user2 User2 Users  user
/opt/omero/server/venv3/bin/omero group -u root -p 4064 -w omero --server omero-server \
                     adduser --name JCB2009 --as-owner facility0
/opt/omero/server/venv3/bin/omero group -u root -p 4064 -w omero --server omero-server \
                     adduser  --name JCB2009 --as-owner user0
/opt/omero/server/venv3/bin/omero group -u root -p 4064 -w omero --server omero-server \
                     adduser  --name JCB2009 --as-owner user1
/opt/omero/server/venv3/bin/omero group -u root -p 4064 -w omero --server omero-server \
                     adduser  --name JCB2009 --as-owner user2
