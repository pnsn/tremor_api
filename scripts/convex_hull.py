'''
Create a convex hull from data given a min/max date
'''
from app.app import create_app
from app.models import Event
from scipy.spatial import ConvexHull
import numpy as np
import sys
import csv

starttime = sys.argv[1]
endtime = sys.argv[2]

flask_app = create_app('production')
with flask_app.app_context():
    events = Event.query.filter(Event.time.between(starttime, endtime))
    size = len(events.all())
    # create a 2 dim array of zeros then fill
    points = np.zeros(shape=(size, 2))
    for i in range(size):
        points[i][0] = events[i].lat
        points[i][1] = events[i].lon
    hull = ConvexHull(points)

    filename = "./csv/convex-hull-{}-{}.csv".format(starttime, endtime)

    with open(filename, mode='w') as file:
        writer = csv.writer(file, delimiter=',', fieldnames=['lat', 'lon'])
        writer.writeheader()
        for e in events:
            writer.writerow([e.lat, e.lon])
