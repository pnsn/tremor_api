'''
parse csv file of legacy tremor data and populate db
file should be in /tmp/catalog.csv
call this script with
python scripts/dump_v1_to_staging.py /tmp/catalog.csv
'''
import sys
from app.app import create_app
from app.models import Event
import random
import csv

environment = 'staging'
infile = open(sys.argv[1])
flask_app = create_app(environment)
with flask_app.app_context():
    if environment != 'production':
        # delete everything
        Event.query.delete()
        with infile as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # skip the headers
            for row in reader:
                time = row[0]
                lat = float(row[1])
                lon = float(row[2])
                depth = random.randint(12, 24)
                num_stas = random.randint(3, 8)
                amplitude = None
                catalog_version = 9999
                e = Event(lat, lon, depth, num_stas, time, amplitude,
                          catalog_version)
                e.save()
