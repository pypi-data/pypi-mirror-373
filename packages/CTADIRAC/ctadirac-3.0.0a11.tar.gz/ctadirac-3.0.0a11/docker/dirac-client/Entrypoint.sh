#! /bin/bash

/usr/sbin/fetch-crl
source /home/dirac/diracos/diracosrc
exec "$@"
