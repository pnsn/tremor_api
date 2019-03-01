from .app import db


class Event(db.Model):
    """Model for events

                            Table "public.events"
         Column      |            Type             |   Modifiers
    -----------------+-----------------------------+---------------
     lat             | numeric                     |
     lon             | numeric                     |
     amplitude       | numeric                     |
     depth           | numeric                     |
     num_stas        | integer                     |
     created_at      | timestamp without time zone | default now()
     time            | timestamp without time zone |
     catalog_version | integer                     |
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
    amplitude = db.Column(db.Float)
    time = db.Column(db.DateTime)
    catalog_version = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, lat, lon, depth, num_stas, time, amplitude=None,
                 catalog_version=None):
        """initialize with name."""
        self.lat = lat
        self.lon = lon
        self.depth = depth
        self.num_stas = num_stas
        self.time = time
        self.amplitude = amplitude
        self.catalog_version = catalog_version

    @classmethod
    def get_all(self):
        return self.query.all()

    @classmethod
    def get_id(self, id):
        return self.query.get(id)

    @classmethod
    def get_latest(self):
        return self.query.order_by('created_at desc').limit(1).one()

    @classmethod
    def filter_by_date(self, starttime, endtime):
        return self.query.filter(self.time.between(starttime, endtime))\
            .order_by(self.time)

    @classmethod
    def day_count(self):
        '''request number of events per day

        with_entities() returns tuple and not query object of Events
        '''

        return self.query.with_entities(db.func.date_trunc('day', self.time)
                                        .label('day'),
                                        db.func.count(self.time))\
                         .group_by('day').all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dictionary(self):
        """For serialization remove _sa_instance_state key"""
        d = self.__dict__
        d.pop('_sa_instance_state', None)
        return d

    def __repr__(self):
        return "<Event: {}>".format(self.id)
