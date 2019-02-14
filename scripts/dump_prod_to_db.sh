#!/usr/bin/env bash

stage=$1
if [ -z $stage ] || [ $stage == "production" ]; then
  echo "Usage enter stage environement as arg [testing|staging]"
  echo "production is not allowed as arg"
  exit 1
fi

db=tremor_$stage
NOWDATE=`date +%m%d%y%H%M%S`
path=$HOME/tremor_sql
mkdir -p $path
DUMP=$path/tremor_prod_dump$NOWDATE.sql

PGPASSWORD=$TREMOR_DB_PASSWD pg_dump -h $TREMOR_DB_HOST -U $TREMOR_DB_USER  tremor_production > $DUMP
PGPASSWORD=$TREMOR_DB_PASSWD psql -d $db -h $TREMOR_DB_HOST -U $TREMOR_DB_USER -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '$db' AND pid <> pg_backend_pid();"

PGPASSWORD=$TREMOR_DB_PASSWD dropdb -h $TREMOR_DB_HOST -U $TREMOR_DB_USER $db
PGPASSWORD=$TREMOR_DB_PASSWD createdb -h $TREMOR_DB_HOST -U $TREMOR_DB_USER $db
PGPASSWORD=$TREMOR_DB_PASSWD psql -h $TREMOR_DB_HOST -U $TREMOR_DB_USER $db < $DUMP
gzip  $DUMP
