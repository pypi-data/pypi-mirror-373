#!/bin/bash
source /opt/dirac/bashrc
RUNSVCTRL=`which runsvctrl`
chpst -u dirac $RUNSVCTRL d /opt/dirac/startup/*
killall runsv svlogd
killall runsvdir
