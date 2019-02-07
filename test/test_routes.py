import os
import sys
import pytest
sys.path.insert(0, '.')
from app.app import create_app
from app.config import TestingConfig as conf

'''
    To run all tests
     pytest
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
    flask_app= create_app('testing')
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client #where all the test magic happens

    ctx.pop()

def test_get_event(test_client):
    '''
        Test GET /events 422, 404, and 200
        Only test for 401 and 422 here since they all use the same
        decorator
    '''

    #no startime and endtime
    events_uri = "/events"
    uri = events_uri
    response = test_client.get(uri)
    assert response.status_code == 422

    #not found
    uri = events_uri + "?starttime=2000-01-01&endtime=2000-01-02"
    response=test_client.get(uri)
    assert response.status_code == 404

    #success
    uri = events_uri + "?starttime=2018-01-01&endtime=2018-01-02,"
    response=test_client.get(uri)
    assert response.status_code == 200
