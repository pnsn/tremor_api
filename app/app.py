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
from flask import request, abort, Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from .config import app_config
from functools import wraps
from flask_caching import Cache

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
    print(cache_config)
    cache = Cache(app, cache_config)
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

    # ##################ROUTES##########################################

    @app.route('/v1.0/events', methods=['GET'])
    # this is how we can cache. memoize considers params as part of key
    # otherwise use @cache.cached(...)
    # @cache.memoize(86400)
    def get_events():
        '''Description: Get all tremor events in time period

            Route: /v1.0/events
            Method: GET
            Required Params:
                start: string time stamp,
                stop: string time stamp,
            Returns: list of events [{event1},{event2},...,{eventn}] or 404
            Example:/v1.0/events?&start=2018-01-01&end=2018-01-02
        '''
        starttime = request.args.get('starttime')
        endtime = request.args.get('endtime')
        if starttime and starttime is not None and \
                endtime and endtime is not None:
            events = Event.filter_by_date(starttime, endtime)
            if len(events.all()) > 0:
                return jsonify([e.to_dictionary() for e in events])
            json_abort("Resource not found", 404)
        json_abort("starttime and endtime params required", 422)

    @app.route('/v1.0/event/<int:event_id>', methods=['GET'])
    def get_event(event_id):
        '''Description: Get event by id, or find the latest with event_id =0

            Route: /event
            Method: GET
            Required Params:
                id
            Returns:single event
            Example:/v1.0/event/123
                    /v1.0/event/0 (latest
        '''

        if(event_id == 0):
            event = Event.get_latest()
        else:
            event = Event.get_id(event_id)
        if event is not None:
            return jsonify(event.to_dictionary())
        json_abort("Resource not found", 404)

    @app.route('/v1.0/day_counts', methods=['GET'])
    def day_counts():
        '''Description: Get counts for each day of tremor

            Route: /v1.0/day_count
            Method: GET
            Required Params:
                None
            Returns:collection of tuples
            Example:/v1.0/day_count
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
    @app.route('/v1.0/event/new', methods=['POST'])
    def event_new():
        pass

    return app
