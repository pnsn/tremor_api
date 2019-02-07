'''
    All this for a simple, single request api for tremor events queried by data
    What have I done with my life?
'''
from flask import request, abort, Flask, make_response
from sqlalchemy import create_engine
from flask import jsonify
from .config import app_config
def create_app(env_name):
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])
    db_connect = create_engine(app.config['DATABASE_URI'])
    conn = db_connect.connect() # connect to database

    #json exit with proper message and status code
    def json_abort(message, code):
        abort(make_response(jsonify(message = message), code))

    '''
        WARNING: to avoid SQL injection, DO NOT evalute string with user input
        before adding to conn.execute
        use form
        conn.execute(string with %s,(tuple_arg1, tuple_arg2,..., tuple_argn))
        where each %s has a coresponding tuple_arg
    '''

       ###################ROUTES##########################################



    ''' Description: Get all tremor events in time period
        Route: /events
        Method: GET
        Required Params:
            start: string time stamp,
            stop: string time stamp,
        Returns: list of events [{event1},{event2},...,{eventn}] or 404
        Example:/events?&start=2018-01-01&end=2018-01-02
    '''
    @app.route('/events')
    def events():
        starttime = request.args.get('starttime')
        endtime = request.args.get('endtime')
        if starttime and starttime is not None and endtime and endtime is not None:
            str = "SELECT * from events WHERE time between %s::timestamp and %s::timestamp"
            query = conn.execute(str,(starttime, endtime))
            if query.rowcount > 0:
                return jsonify([dict(zip(query.keys() ,i)) for i in query.cursor.fetchall()])
            json_abort("Resource not found", 404)
        json_abort("starttime and endtime params required",422)
    return app
