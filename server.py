import json
import flask
import requests
from haversine import haversine
import time
oba_key = '24e21799-f170-4620-b647-20d0ef7d5c81'
app = flask.Flask('682023 Hackathon Host Server')
reports = {} # stop id: type, time
def apibackend_opposite_dir_stop(direction):
    if direction == 'N':return 'S'
    if direction == 'S': return 'N'
    if direction == 'E': return 'W'
    if direction == 'W': return 'E'
    if direction == 'NW': return 'SE'
    if direction == 'NE': return 'SW'
    if direction == 'SE': return 'NW'
    if direction == 'SW': return 'NE'
    
@app.route('/api/stopForLL')
def api_stopforll():
    lat = flask.request.args['lat']
    lon = flask.request.args['lon']
    limit = flask.request.args.get('limit')
    data = requests.get('http://api.pugetsound.onebusaway.org/api/where/stops-for-location.json?key={}&lat={}&lon={}'.format(oba_key,lat,lon))
    data = data.json()
    first_dir0 = data['data']['list'][0]
    first_dir1 = None
    for stop in data['data']['list'][1:]:
        if stop['direction'] == apibackend_opposite_dir_stop(first_dir0['direction']):
            first_dir1 = stop
            break
    if limit == None:
        return json.dumps([first_dir0,first_dir1,data])
    else:
        return json.dumps(data['data']['list'][0:int(limit)])
    
@app.route('/api/routeForLL')
def api_routeforll():
    lat = flask.request.args['lat']
    lon = flask.request.args['lon']
    limit = flask.request.args.get('limit')
    data = requests.get('http://api.pugetsound.onebusaway.org/api/where/routes-for-location.json?key={}&lat={}&lon={}'.format(oba_key,lat,lon)).json()
    if limit == None:
        return json.dumps(data['data']['list'])
    return json.dumps(data['data']['list'][0:int(limit)])

@app.route('/api/vehiclesForLL')
def api_vehiclesforll():
    lat = float(flask.request.args['lat'])
    lon = float(flask.request.args['lon'])
    limit = int(flask.request.args.get('limit'))
    data = requests.get('http://api.pugetsound.onebusaway.org/api/where/vehicles-for-agency/1.json?key={}'.format(oba_key)).json()
    buses = {} # {busId: {'route_no': route shortname,headsign:headsign,trip_id:trip id, location: tuple (lat,lon,hdg) }}
    trip = None
    route = None
    trips = data['data']['references']['trips']
    routes = data['data']['references']['routes']
    for bus in data['data']['list']:
        if bus['phase'] == 'in_progress':
            if 'location' in list(bus.keys()):
                #bus has location tracking
                location = bus['location']
                location_time = bus['lastLocationUpdateTime']
                trip_id = bus['tripId']
                if len(trip_id) > 6:
                    for t in trips:
                        if t['id'] == trip_id:
                            trip = t
                    for r in routes:
                        if r['id'] == trip['routeId']:
                            route = r
                    try:
                        buses[bus['vehicleId']] = {'route_no':route['shortName'],'headsign':trip['tripHeadsign'],'trip_id':trip['id'],'location': (bus['location']['lat'],bus['location']['lon'])}
                    except Exception as error:
                        print(error)
                else:
                    pass
                
    #return buses
    listToReturn = []
    for bus in buses:
        bus = buses[bus]
        if haversine(bus['location'],(lat,lon)) > 0.25:
            pass
        else:
            listToReturn.append(bus)
        if len(listToReturn) == limit:
            return listToReturn
    return listToReturn


@app.route('/')
def frontend_index():
    return flask.render_template('index.html')

@app.route('/api/stopsForLL')
def api_stopsforll():
    lat = float(flask.request.args['lat'])
    lon = float(flask.request.args['lon'])
    data = requests.get('http://api.pugetsound.onebusaway.org/api/where/stops-for-location.json?key={}&lat={}&lon={}'.format(oba_key,lat,lon)).json()
    closestStop = data['data']['list'][0]
    print(closestStop)
    toReturn = {'name':closestStop['name'],'id':closestStop['id'],'location':(closestStop['lat'],closestStop['lon'])}
    #stopSchedule = requests.get('https://api.pugetsound.onebusaway.org/api/where/schedule-for-stop/{}.json?key={}'.format(toReturn['id'],oba_key)).json()
    return json.dumps(toReturn)

@app.route('/api/submitIssue')
def api_reportissue():
    issueType = flask.request.args['issueType']
    stopId = flask.request.args['stopId']
    lat = float(flask.request.args['lat'])
    lon = float(flask.request.args['lon'])
    reports[stopId] = {'issue':issueType,'time':time.time(),'location':(lat,lon)}
    print(reports)
    return 'True'

@app.route('/api/getIssues')
def api_getissues():
    lat = float(flask.request.args['lat'])
    lon = float(flask.request.args['lon'])
    toReturn = []
    for issue in reports:
        issue = reports[issue]
        if haversine(issue['location'],(lat,lon)) < 0.25:
            toReturn.append(issue)
            print('a')
        else:
            print('b')
    return toReturn
app.run(port=80,host='0.0.0.0')
