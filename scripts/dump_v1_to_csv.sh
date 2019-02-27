#!/usr/bin/env bash

#from legacy db, dump all events to csv

 mysql -p$TREMOR_DB_PASSWD  -u $TREMOR_DB_USER  tremor  -e 'select latitude, longitude, time from catalog'  | sed 's/\t/,/g' > /tmp/catalog.csv
