from .app import db


class Event(db.Model):
    """Model for events

                            Table "public.events"
         Column      |            Type             |   Modifiers
    -----------------+-----------------------------+---------------
     lat             | numeric                     |
     lon             | numeric                     |
     energy          | numeric                     |
     duration        | numeric                     |
     depth           | numeric                     |
     num_stas        | integer                     |
     created_at      | timestamp without time zone | default now()
     time            | timestamp without time zone |
     catalog_version | integer                     |
     magnitude       | numeric
    Indexes:
        "events_catalog_version_idx" btree (catalog_version)
        "events_created_at_idx" btree (created_at)
        "events_lat_idx" btree (lat)
        "events_lon_idx" btree (lon)
        "events_time_idx" btree ("time")
    """

    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    depth = db.Column(db.Float)
    num_stas = db.Column(db.Float)
    energy = db.Column(db.Float)
    duration = db.Column(db.Float)
    magnitude = db.Column(db.Float)
    time = db.Column(db.DateTime)
    catalog_version = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, lat, lon, depth, num_stas, time, catalog_version=None,
                 energy=None, duration=None, magnitude=None):
        """initialize with name."""
        self.lat = lat
        self.lon = lon
        self.depth = depth
        self.num_stas = num_stas
        self.time = time
        self.catalog_version = catalog_version
        self.energy = energy
        self.duration = duration
        self.magnitude = magnitude

    RETURN_LIMIT = 20000

    @classmethod
    def get_id(self, id):
        '''get event by id'''
        return self.query.get(id)

    @classmethod
    def get_latest(self):
        '''return latest event'''
        return self.query.filter(
            (self.catalog_version == 1) | (self.catalog_version == 3)).order_by(
            self.time.desc()).limit(1).one()

    @classmethod
    def day_count(self, lat_min=None, lat_max=None,
                  lon_min=None, lon_max=None):
        '''request number of events per day

        with_entities() returns tuple and not query object of Events
        '''

        events = self.query.filter(
            (self.catalog_version == 1) | (self.catalog_version == 3)).with_entities(
                db.func.date_trunc('day', self.time)
                .label('day'), db.func.count(self.time))
        if lat_min is not None and lat_max is not None \
           and lon_min is not None and lon_max is not None:
            events = events.filter(
                self.catalog_version == 1 | self.catalog_version == 3).filter(
                self.lat.between(lat_min, lat_max)).filter(
                self.lon.between(lon_min, lon_max))
        return events.group_by('day').all()

    def delete(self):
        '''delete an event'''
        db.session.delete(self)
        db.session.commit()

    def save(self):
        '''save event'''
        db.session.add(self)
        db.session.commit()

    def to_dictionary(self):
        """For serialization remove _sa_instance_state key"""
        d = self.__dict__
        d.pop('_sa_instance_state', None)
        return d

    def __repr__(self):
        '''string repr of object'''
        return "<Event: {}>".format(self.id)
