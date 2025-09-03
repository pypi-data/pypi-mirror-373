#!/bin/bash

iadmin mkuser user0 rodsuser
iadmin mkuser user1 rodsuser
iadmin mkuser user2 rodsuser
iadmin mkuser facility0 rodsuser
iadmin mkgroup JCB2009
iadmin atg JCB2009 omero-server
clientUserName=omero-server ichmod -r inherit /tempZone/home/JCB2009
iadmin atg JCB2009 user0
iadmin atg JCB2009 user1
iadmin atg JCB2009 user2
iadmin atg JCB2009 facility0
iadmin moduser facility0 password omero
ichmod -r own omero-server /tempZone/
