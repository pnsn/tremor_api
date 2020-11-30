import pytest
from app.app import create_app, db
from app.models import Event
from unittest.mock import patch

'''
    To run all tests
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
# set high catalog_version to identify test data
catalog_version = 100000


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
    lat1 = 45.0
    lat2 = 48.0
    lon1 = -122.0
    lon2 = -116.0
    depth = 2.0
    num_stas = 3
    amplitude = 2.0

    # lat, lon, depth, num_stas, time, amplitude, catalog_version=None
    for _ in range(5):
        event = Event(lat1, lon1, depth, num_stas, date1, amplitude,
                      catalog_version)
        event.save()
    for _ in range(5):
        event = Event(lat2, lon2, depth, num_stas, date2, amplitude,
                      catalog_version)
        event.save()
    # now a late one:
    event = Event(lat1, lon1, depth, num_stas, "2019-01-01", amplitude,
                  catalog_version)
    event.save()
    yield db  # all magic goes here


def test_get_event(test_client, init_database):
    '''Test GET /events 422, 404, and 200

        Only test for 401 and 422 here since they all use the same
        decorator
    '''
    # no startime and endtime
    events_uri = "/api/v1.0/events"
    event_uri = "/api/v1.0/event/"
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
    json = response.get_json()
    assert len(json['features']) == 5
    assert response.status_code == 200
    # find some id to test

    id = json['features'][0]['properties']['id']

    uri = event_uri + str(id)
    response = test_client.get(uri)
    json = response.get_json()
    assert json['properties']['id'] == id


def test_day_count(test_client, init_database):
    uri = "/api/v1.0/day_counts"
    response = test_client.get(uri)
    assert response.status_code == 200
    js = response.get_json()
    assert len(js) == 3
    uri = "/api/v1.0/day_counts?lat_min=44.9&lat_max=45.1" + \
          "&lon_min=-122.1&lon_max=-121.9"
    response = test_client.get(uri)
    assert response.status_code == 200
    js = response.get_json()
    assert len(js) == 2


def test_lat_lon_select(test_client):
    '''test selecting by lat/lon'''
    # all dates so we can test lat/lons
    uri_base = "/api/v1.0/events?starttime=2000-01-01&endtime=2040-01-01"
    # all lat/lons
    uri = uri_base + "&lat_min=30.0&lat_max=50.0&lon_min=-140.0&lon_max=-100.0"
    response = test_client.get(uri)
    json = response.get_json()
    assert len(json['features']) == 11
    assert response.status_code == 200
    # only between 40&41, -122, -120
    uri = uri_base + "&lat_min=44.0&lat_max=46.0&lon_min=-122.0&lon_max=-120.0"
    response = test_client.get(uri)
    json = response.get_json()
    assert len(json['features']) == 6
    assert response.status_code == 200
    # now should be 404
    uri = uri_base + "&lat_min=40.0&lat_max=41.0&lon_min=-122.0&lon_max=-120.0"
    response = test_client.get(uri)
    json = response.get_json()
    assert response.status_code == 404
    # should only return 1
    uri = "api/v1.0/events?starttime=2019-01-01&endtime=2019-01-02&" + \
          "&lat_min=30.0&lat_max=50.0&lon_min=-140.0&lon_max=-100.0"
    response = test_client.get(uri)
    json = response.get_json()
    assert len(json['features']) == 1
    assert response.status_code == 200


def test_random_select(test_client):
    '''test that random selects limit'''
    # mock the return limit to number lower than query
    with patch.object(Event, "RETURN_LIMIT", 2):
        assert Event.RETURN_LIMIT == 2
        # all events
        uri = "/api/v1.0/events?starttime=2000-01-01&endtime=2040-01-01"
        response = test_client.get(uri)
        json = response.get_json()
        assert json['count'] == 11
        assert len(json['features']) == 2
        assert response.status_code == 200
        # test with format = csv should return all 11
        uri = "/api/v1.0/events?starttime=2000-01-01&endtime=2040-01-01&" + \
              "format=csv"
        response = test_client.get(uri)
        assert response.status_code == 200
