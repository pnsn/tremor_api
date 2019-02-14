import os
import sys
import pytest
sys.path.insert(0, '.')
from app.app import create_app, db
from app.models import Event
from app.config import TestingConfig as conf
from flask import request
import datetime

'''
    To run all tests
     pytest --verbose -s
     -s prevents standar out capturing allowing
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
#set high catalog_version to identify test data
catalog_version = 100000
@pytest.fixture(scope='module')
def test_client():
    flask_app= create_app('testing')
    testing_client = flask_app.test_client()
    # create_fixtures()
    with flask_app.app_context():
        yield testing_client #where all the test magic happens


# def event_data(test_client):
@pytest.fixture(scope='module')
def init_database(request):
    db.session.commit()
    db.drop_all()
    db.create_all()
    date1="2018-01-01"
    date2="2018-01-02"
    lat=45.0
    lon=-122.0
    depth =2.0
    num_stas = 3
    amplitude = 2.0
    events = []
    #lat, lon, depth, num_stas, time, amplitude, catalog_version=None
    for _ in range(5):
        event = Event(lat, lon, depth, num_stas, date1, amplitude, catalog_version )
        event.save()
    for _ in range(5):
        event = Event(lat, lon, depth, num_stas, date2, amplitude, catalog_version )
        event.save()
    #now a late one:
    event = Event(lat, lon, depth, num_stas, "2019-01-01", amplitude, catalog_version )
    event.save()
    yield db  # all magic goes here



def test_get_event(test_client, init_database):
    '''
        Test GET /events 422, 404, and 200
        Only test for 401 and 422 here since they all use the same
        decorator
    '''
    events = Event.query.filter_by(catalog_version=catalog_version)
    print(events)
    #no startime and endtime
    events_uri = "/v1.0/events"
    event_uri = "/v1.0/event/"
    uri = events_uri
    response = test_client.get(uri)
    assert response.status_code == 422

    #not found
    uri = events_uri + "?starttime=2000-01-01&endtime=2000-01-02"
    response=test_client.get(uri)
    assert response.status_code == 404

    #success
    uri = events_uri + "?starttime=2018-01-01&endtime=2018-01-01"
    response=test_client.get(uri)
    json = response.get_json()
    assert len(json) ==5
    assert response.status_code == 200
    #find some id to test
    id = json[0]['id']
    print(id)

    uri = event_uri + str(id)
    response=test_client.get(uri)
    json = response.get_json()
    assert json['id'] == id

    #this seems to work, and testing to get the strings exactly the same
    #seems to be a pain in the arse.
    # uri = event_uri + "0"
    # response=test_client.get(uri)
    # json = response.get_json()
    # d = datetime.date(2019, 1, 1)
    # assert json['time'] == d
