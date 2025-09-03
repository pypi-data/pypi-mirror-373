import requests
from lxml import etree
import time
import urllib3

def history_json(object_type, object_id, user_agent=None):
    url = 'https://api.openstreetmap.org/api/0.6/' + object_type + '/' + str(object_id) + '/history.json'
    params = {}
    if user_agent != None:
        params = {
            'user_agent': user_agent
        }
    json_data = {}
    r = make_get_request(url, params, json_data)
    if r.status_code != 200:
        print(r.status_code)
    if r.status_code == 503:
        print("will retry after waiting")
        time.sleep(60)
        return history_json(object_type, object_id, user_agent)
    try:
        return r.json()['elements']
    except simplejson.errors.JSONDecodeError:
        print(r)
        raise Exception("wat?")

def element_list_touched_by_changeset(changeset_id, user_agent=None):
    # https://wiki.openstreetmap.org/wiki/API_v0.6#Download:_GET_/api/0.6/changeset/#id/download
    # parse XML
    url = 'https://api.openstreetmap.org/api/0.6/changeset/' + str(changeset_id) + '/download'
    params = {}
    if user_agent != None:
        params = {
            'user_agent': user_agent
        }
    r = make_get_request(url, params)
    if r.status_code != 200:
        print(r.status_code)
        raise
    print(r)
    print(r.content)
    print()
    print()
    print(changeset_id)
    root = etree.fromstring(r.content)
    for lxml_element in root.getiterator():
        if(lxml_element.tag in ["relation", "way", "node"]):
            print(lxml_element.tag, lxml_element.attrib["id"])
    print()
    #print(str(r.content))
    #print(dir(r))

def changeset_list_json(bbox=None, user_id=None, closed_after=None, created_before=None, user_agent=None):
    # https://wiki.openstreetmap.org/wiki/API_v0.6#Query:_GET_/api/0.6/changesets
    # "by display name" deliberately not supported as unstable and asking for subtle bugs
    # TODO: turn it into generator?
    parameters = []
    if bbox != None:
        # create min_lon,min_lat,max_lon,max_lat formatted query parameter
        min_lon = bbox['min_lon']
        min_lat = bbox['min_lat']
        max_lon = bbox['max_lon']
        max_lat = bbox['max_lat']
        parameters.append("bbox=" + str(min_lon) + "," + str(min_lat) + "," + str(max_lon) + "," + str(max_lat))
    if user_id != None:
        raise NotImplementedError
    url = 'https://api.openstreetmap.org/api/0.6/changesets.json'
    if closed_after == None and created_before != None:
        raise NotImplementedError
    if closed_after != None and created_before == None:
        parameters.append("time=" + closed_after)
    if closed_after != None and created_before != None:
        parameters.append("time=" + closed_after + "," + created_before)
    params = {}
    if user_agent != None:
        params = {
            'user_agent': user_agent
        }
    json_data = {}
    if parameters != []:
        url += "?" + "&".join(parameters)
    r = make_get_request(url, params, json_data)
    if r.status_code != 200:
        print(r.status_code)
        raise
    return r.json()

def make_get_request(url, params, json_data={}):
    # unify it with overpass downloader code?
    while True:
        try:
            print(url)
            return requests.get(url, params=params, json=json_data)
        except requests.exceptions.ConnectionError as e:
            print(e)
            sleep_before_retry("requests.exceptions.ConnectionError", url, params, json_data)
            continue
        except requests.exceptions.HTTPError as e:
            print(e.response.status_code)
            if e.response.status_code == 503:
                sleep_before_retry("requests.exceptions.HTTPError", url, params, json_data)
                continue
            raise e
        except requests.exceptions.ReadTimeout as e:
            sleep_before_retry("requests.exceptions.ReadTimeout", url, params, json_data)
            continue
        except requests.exceptions.ChunkedEncodingError as e:
            print(e)
            sleep_before_retry("requests.exceptions.ChunkedEncodingError", url, params, json_data)
            continue
        # for example
        # ConnectionResetError(104, 'Connection reset by peer')
        # not sure is it happening on poor connection or explicit request by server
        # to slow down, in either case waiting a bit is a good idea
        except urllib3.exceptions.ProtocolError as e:
            print(e)
            sleep_before_retry("urllib3.exceptions.ProtocolError", url, params, json_data)
            continue

def sleep_before_retry(message, url, params, json_data):
    time.sleep(10)
    print(message, url, params, json_data)