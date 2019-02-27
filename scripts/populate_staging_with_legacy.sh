#!/usr/bin/env bash
 psql -d tremor_staging -c "delete from events;"
 psql -d tremor_staging -c "\copy events(lat,lon,time) FROM '/tmp/catalog.csv' WITH (FORMAT csv);"
