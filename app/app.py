'''
    All this for a simple, single request api for tremor events queried by data
    What have I done with my life?
    # app/__init__.py

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    return app
'''
from flask import request, abort, Flask, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_cors import CORS

from .config import app_config
from functools import wraps


db = SQLAlchemy()


def create_app(env_name):
    from .models import Event
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    cache_config = {
        'CACHE_TYPE': app.config["CACHE_TYPE"],
        'CACHE_DEFAULT_TIMEOUT': app.config["CACHE_DEFAULT_TIMEOUT"],
        'CACHE_DIR': app.config["CACHE_DIR"],
        'CACHE_THRESHOLD': app.config["CACHE_THRESHOLD"]}
    Cache(app, cache_config)
    CORS(app, resources=r'/api/v1.0/*')
    db.init_app(app)
    # cache.init_app(app)

    def require_apikey(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
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

    def export_to_geojson(collection):
        '''take collection of events and create geojson python dict and jsonify


        {
            "type": "FeatureCollection",
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
        geo_dict['features'] = []
        for event in collection:
            feature = create_geojson_feature(event)
            geo_dict['features'].append(feature)
        return jsonify(geo_dict)

    def create_geojson_feature(obj):
        feature = {}
        feature['type'] = 'Feature'
        feature['geometry'] = {}
        feature['geometry']['type'] = 'Point'
        feature['geometry']['coordinates'] = [obj.lon, obj.lat]
        feature['properties'] = {}
        feature['properties']['depth'] = obj.depth
        feature['properties']['amplitude'] = obj.amplitude
        feature['properties']['num_stas'] = obj.num_stas
        feature['properties']['time'] = obj.time
        feature['properties']['id'] = obj.id
        return feature

    # ##################ROUTES##########################################

    @app.route('/api/v1.0/events', methods=['GET'])
    # this is how we can cache. memoize considers params as part of key
    # otherwise use @cache.cached(...)
    # @cache.memoize(86400)
    def get_events():
        '''Description: Get all tremor events in time period

            Route: /api/v1.0/events
            Method: GET
            Required Params:
                start: string time stamp,
                stop: string time stamp,
            Returns: list of events [{event1},{event2},...,{eventn}] or 404
            Example:/api/v1.0/events?&start=2018-01-01&end=2018-01-02
        '''
        starttime = request.args.get('starttime')
        endtime = request.args.get('endtime')
        if starttime and starttime is not None and \
                endtime and endtime is not None:
            events = Event.filter_by_date(starttime, endtime)
            if len(events.all()) > 0:
                geo_json = export_to_geojson(events)
                return geo_json
            json_abort("Resource not found", 404)
        json_abort("starttime and endtime params required", 422)

    @app.route('/api/v1.0/event/<int:event_id>', methods=['GET'])
    def get_event(event_id):
        '''Description: Get event by id, or find the latest with event_id =0

            Route: /event
            Method: GET
            Required Params:
                id
            Returns:single event
            Example:/api/v1.0/event/123
                    /api/v1.0/event/0 (latest
        '''

        if(event_id == 0):
            event = Event.get_latest()
        else:
            event = Event.get_id(event_id)
        if event is not None:
            feature = create_geojson_feature(event)
            return jsonify(feature)
        json_abort("Resource not found", 404)

    @app.route('/api/v1.0/day_counts', methods=['GET'])
    def day_counts():
        '''Description: Get counts for each day of tremor

            Route: /api/v1.0/day_count
            Method: GET
            Required Params:
                None
            Returns:collection of tuples
            Example:/api/v1.0/day_count
        '''
        events = Event.day_count()
        collection = {}
        for e in events:
            key = e[0].strftime("%Y-%m-%d")
            val = e[1]
            collection[key] = val
            # collection.append({key: val})
        return jsonify(collection)

    @require_apikey
    @app.route('/api/v1.0/event/new', methods=['POST'])
    def event_new():
        pass

    return app
