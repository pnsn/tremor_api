# tremor_api
A simple api to request tremor data

# Config
All configuration is managed by 
python-dotenv and The config class in app/config.py
## Environmental Variables
keep local variables in .env This file is gitignored

Once repo is cloned 
`cp .env-example .env`
Edit .env as needed. 

The .env file is source in app/ __init__.py
the value of APP_SETTINGS="production|staging|testing|development"  variable in .env determines which Config.Class to envoke

# Environments
## Development
APP_SETTINGS=development|testing 
To start app:
`run flask`
Calls the run.py script

## Testing
Uses pytest. From app root:
`pytest -s --verbose`

## Production and Staging
* Uses Gunicorn and WSGI/Apache
* Uses virtualenv python 3.6
* Does not call run.py 
* See tremor_api.wsgi file

# Routes
All routes in app/app.py
<pre>
        Route: /v1.0/events
        Description: Get all tremor events in time period
        Method: GET
        Required Params:
            start:time stamp (string),
            stop: time stamp (string),
        Returns: list of events [{event1},{event2},...,{eventn}] or 404
        Example:/v1.0/events?&start=2018-01-01&end=2018-01-02
</pre>
<pre>
        Route: /event
        Description: Get event by id, or find the latest with event_id =0
        Method: GET
        Required Params:
            id (int)
        Returns:single event
        Example:/v1.0/event/123
                /v1.0/event/0 (latest)

</pre>
