'''
Create a bunch of random data for client development
'''
from app.app import create_app
from app.models import Event
import random
import sys
sys.path.insert(0, '.')

flask_app = create_app('staging')
with flask_app.app_context():
    for month in range(1, 10):
        for day in range(1, 28):
            num = random.randint(0, 500)
            for _ in range(num):
                lat = random.randint(4000, 5000) / 100
                lon = random.randint(12000, 12500) / -100
                depth = random.randint(12, 24)
                num_stas = random.randint(3, 8)
                time = "2018-{}-{}".format(month, day)
                amplitude = None
                catalog_version = 9999
                e = Event(lat, lon, depth, num_stas, time, amplitude,
                          catalog_version)
                e.save()
