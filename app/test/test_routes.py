import pytest
from app.app import create_app, db
from app.models import Event

'''
    To run all testse
     pytest --verbose -s
     -s prevents stderr out capturing allowing
     use of print statements
    to run all module tests
     pytest test/test_routes.py
    to run single test
     pytest test/test_routes.py::test_nearest_location

'''

'''
    decorator for all tests
    yield is where the magic happens

'''
@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('testing')
    testing_client = flask_app.test_client()
    # create_fixtures()
    with flask_app.app_context():
        # where all the test magic happens
        yield testing_client


# def event_data(test_client):
@pytest.fixture(scope='module')
def init_database(request):
    db.session.commit()
    db.drop_all()
    db.create_all()
    date1 = "2018-01-01"
    date2 = "2018-03-02"
    date3 = "2021-03-08"
    lat1 = 45.0
    lat2 = 48.0
    lon1 = -122.0
    lon2 = -116.0
    depth = 2.0
    num_stas = 3
    amplitude = 2.0
    magnitude = 1.0

    ''' stub out some test data
    # for each catalog version 1-3
       * create 5 events with date 1
       * create 5 events with date 2
       * add on single event with date3

    Since catalog 2 is deprecated, model is scoped to return
    on only 1 & 3
    so official:
    date1: 10 events
    date2: 10 events
    date3: 2 events

    '''
    for version in [1, 2, 3]:
        for _ in range(5):
            event = Event(lat1, lon1, depth, num_stas, date1, version,
                          amplitude, magnitude)
            event.save()
        for _ in range(5):
            event = Event(lat2, lon2, depth, num_stas, date2, version,
                          amplitude, magnitude)
            event.save()
        # now a late one:
        event = Event(lat1, lon1, depth, num_stas, date3, version,
                      amplitude, magnitude)
        event.save()
    yield db  # all magic goes here


def test_get_event(test_client, init_database):
    '''Test GET /events 422, 404, and 200

        Only test for 401 and 422 here since they all use the same
        decorator
    '''
    # no startime and endtime
    events_uri = "/api/v3.0/events"
    event_uri = "/api/v3.0/event/"
    uri = events_uri
    response = test_client.get(uri)
    assert response.status_code == 422

    # not found
    uri = events_uri + "?starttime=2000-01-01&endtime=2000-01-02"
    response = test_client.get(uri)
    # print(response.get_json())
    assert response.status_code == 404

    # success
    uri = events_uri + "?starttime=2018-01-01&endtime=2018-01-01"
    response = test_client.get(uri)
    print(response)
    json = response.get_json()
    print(json)
    assert len(json['features']) == 10
    assert response.status_code == 200
    # find some id to test

    id = json['features'][0]['properties']['id']

    uri = event_uri + str(id)
    response = test_client.get(uri)
    json = response.get_json()
    assert json['properties']['id'] == id


def test_day_count(test_client, init_database):
    uri = "/api/v3.0/day_counts"
    response = test_client.get(uri)
    assert response.status_code == 200
    js = response.get_json()
    assert len(js) == 3
    uri = "/api/v3.0/day_counts?lat_min=44.9&lat_max=45.1" + \
          "&lon_min=-122.1&lon_max=-121.9"
    response = test_client.get(uri)
    assert response.status_code == 200
    js = response.get_json()
    assert len(js) == 2


def test_lat_lon_select(test_client):
    '''test selecting by lat/lon
        cord 1 (count = 12)
          lat = 45.0
          lon = -122.0
        cord2 (count = 10)
          lat = 48.0
          lon = -116.0
    '''
    # all dates so we can test lat/lons
    uri_base = "/api/v3.0/events?starttime=2000-01-01&endtime=2040-01-01"
    # all lat/lons
    uri = uri_base + "&lat_min=30.0&lat_max=50.0&lon_min=-140.0&lon_max=-100.0"
    response = test_client.get(uri)
    json = response.get_json()
    assert len(json['features']) == 22
    assert response.status_code == 200
    # only between 40&41, -122, -120
    uri = uri_base + "&lat_min=44.0&lat_max=46.0&lon_min=-122.0&lon_max=-120.0"
    response = test_client.get(uri)
    json = response.get_json()
    assert len(json['features']) == 12
    assert response.status_code == 200
    # now should be 404
    uri = uri_base + "&lat_min=40.0&lat_max=41.0&lon_min=-122.0&lon_max=-120.0"
    response = test_client.get(uri)
    json = response.get_json()
    assert response.status_code == 404
    # should only return 1
    uri = "api/v3.0/events?starttime=2021-03-08&endtime=2021-03-09&" + \
          "&lat_min=30.0&lat_max=50.0&lon_min=-140.0&lon_max=-100.0"
    response = test_client.get(uri)
    json = response.get_json()
    assert len(json['features']) == 2
    assert response.status_code == 200
