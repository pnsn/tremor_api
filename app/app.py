'''
Where all the magic happens again, and again and again
'''
from flask import request, abort, Flask, make_response, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# from flask_csv import send_csv

from .config import app_config
from functools import wraps
import io

db = SQLAlchemy()


def create_app(env_name):
    from .models import Event
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    CORS(app, resources=r'/api/v3.0/*')
    db.init_app(app)

    def require_apikey(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            print("decorator")
            '''decorator to check for api key '''
            if request.args.get('key') and \
                    request.args.get('key') == app.config['API_KEY']:
                return view_function(*args, **kwargs)
            else:
                json_abort('API key required', 401)
        return decorated_function

    # json exit with proper message and status code
    def json_abort(message, code):
        return abort(make_response(jsonify(message=message), code))

    def export_to_geojson(collection, count):
        '''take collection of events and create geojson python dict and jsonify

            count attribute is the total that would be returned before limit is
            is applied.

        {
            "type": "FeatureCollection",
            "count": count (int)
            "features": [
                {
                  "type": "Feature",
                  "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                  },
                  "properties": {
                    "depth": float,
                    "amplitude": float,
                    "num_stas": integer
                    "time": string
                  }
                },
                ...
            }
            '''

        geo_dict = {}
        geo_dict['type'] = "FeatureCollection"
        geo_dict['count'] = count
        geo_dict['features'] = []
        for event in collection:
            feature = create_geojson_feature(event)
            geo_dict['features'].append(feature)
        # sort features by time for Kyla
        geo_dict['features'] \
            .sort(key=lambda feature: feature['properties']['time'])
        return jsonify(geo_dict)

    def create_geojson_feature(obj):
        feature = {}
        feature['type'] = 'Feature'
        feature['geometry'] = {}
        feature['geometry']['type'] = 'Point'
        feature['geometry']['coordinates'] = [round(obj.lon, 3),
                                              round(obj.lat, 3)]
        feature['properties'] = {}
        feature['properties']['depth'] = obj.depth
        # test for NaN. A NaN does not equal itself.
        amp = obj.amplitude if obj.amplitude == obj.amplitude else 0
        feature['properties']['amplitude'] = amp
        feature['properties']['magnitude'] = round(obj.magnitude, 1)
        feature['properties']['num_stas'] = obj.num_stas
        feature['properties']['time'] = obj.time
        feature['properties']['id'] = obj.id
        return feature

    # ##################ROUTES##########################################

    @app.route('/api/v3.0/events', methods=['GET'])
    def get_events():
        '''Description: Get all tremor events in time period

            Route: /api/v3.0/events
            Method: GET
            Required Params:
                start: string time stamp,
                stop: string time stamp,
            Optional Params:
                lat_min: float
                lat_max: float
                lon_min: float
                lon_max: float
            Returns: list of events [{event1},{event2},...,{eventn}] or 404
            Examples:
            /api/v3.0/events?&start=2018-01-01&end=2018-01-02
            /api/v3.0/events?&start=2018-01-01&end=2018-01-02&lat_min=40& \
            lat_max=48&lon_min=-120&lon_max=-116
        '''
        starttime = request.args.get('starttime')
        endtime = request.args.get('endtime')
        format = request.args.get('format')
        lat_min = request.args.get('lat_min')
        lat_max = request.args.get('lat_max')
        lon_min = request.args.get('lon_min')
        lon_max = request.args.get('lon_max')
        if starttime and starttime is not None and \
                endtime and endtime is not None:

            # start by calling with class
            events = Event.query.filter(
                     Event.time.between(starttime, endtime)).filter(
                    Event.catalog_version != 2)

            if lat_min and lat_min is not None and lat_max and \
                    lat_max is not None and lon_min and lon_min is not None \
                    and lon_max and lon_max is not None:
                # to chain, use returned collection to continue filtering
                events = events.filter(
                    Event.lat.between(lat_min, lat_max)).filter(
                    Event.lon.between(lon_min, lon_max))
            # count before trucating
            count = events.count()
            if format is None or format != 'csv':
                events = events.order_by(
                    db.func.random()).limit(Event.RETURN_LIMIT)
            if len(events.all()) > 0:
                if format == 'csv':
                    filename = "tremor_events-{}-{}.csv".format(starttime,
                                                                endtime)
                    fieldnames = ['lat', 'lon', 'depth', 'time']
                    csv_io = io.StringIO()
                    csv_io.write(str(','.join(fieldnames) + " \n "))
                    for e in events:
                        csv_io.write(
                            str("{}, {}, {}, {} \n ")
                            .format(e.lat, e.lon, e.depth, e.time)
                        )
                    response = Response(csv_io.getvalue(), mimetype='text/csv')
                    response.headers.set('Content-Disposition', 'attachment',
                                         filename=filename)
                    return response
                else:
                    geo_json = export_to_geojson(events, count)
                    return geo_json
            json_abort("Resource not found", 404)
        json_abort("starttime and endtime params required", 422)

    @app.route('/api/v3.0/event/<int:event_id>', methods=['GET'])
    def get_event(event_id):
        '''Description: Get event by id, or find the latest with event_id =0

            Route: /event
            Method: GET
            Required Params:
                id
            Returns:single event
            Example:/api/v3.0/event/123
                    /api/v3.0/event/0 (latest)
        '''

        if(event_id == 0):
            event = Event.get_latest()
        else:
            event = Event.get_id(event_id)
        if event is not None:
            feature = create_geojson_feature(event)
            return jsonify(feature)
        json_abort("Resource not found", 404)

    @app.route('/api/v3.0/day_counts', methods=['GET'])
    def day_counts():
        '''Description: Get counts for each day of tremor

            Route: /api/v3.0/day_count
            Method: GET
            Required Params:
                None
            Optional Params:
                lat_min: float
                lat_max: float
                lon_min: float
                lon_max: float
            Returns:collection of tuples
            Example:/api/v3.0/day_count
        '''

        lat_min = request.args.get('lat_min')
        lat_max = request.args.get('lat_max')
        lon_min = request.args.get('lon_min')
        lon_max = request.args.get('lon_max')

        events = Event.day_count(lat_min, lat_max, lon_min, lon_max)
        collection = {}
        for e in events:
            key = e[0].strftime("%Y-%m-%d")
            val = e[1]
            collection[key] = val
            # collection.append({key: val})
        return jsonify(collection)

    @require_apikey
    @app.route('/api/v3.0/event/new', methods=['POST'])
    def event_new():
        pass

    return app
