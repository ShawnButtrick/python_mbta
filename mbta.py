import logging
import requests
import json
import pprint
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    route_data = get_routes()
    
    # Make route "long name" lookup    
    routeId_to_routeLongName = {}
    routeIds_to_stopIds = {}
    logger.info('Subway routes: ')
    for temp_route in route_data['data']:
        routeId_to_routeLongName[temp_route['id']] = temp_route['attributes']['long_name']
        logger.info( '    ' + (temp_route['attributes']['long_name']) )
    
    # get STOPS and associate them with ROUTES
    routeIds_to_stopIds = get_routes_to_stops(route_data)

    # Build set-of-stops
    set_of_stops = show_min_and_max_stops(routeIds_to_stopIds)

    # Associate Routes to Stops (aka route-intersections)
    stopIds_to_routeIds = build_route_intersections(set_of_stops, routeIds_to_stopIds)

    # Show intersections
    show_intersections(stopIds_to_routeIds, routeId_to_routeLongName)

    # Do directions
    directions(routeIds_to_stopIds, stopIds_to_routeIds)


def get_routes():
    '''
    Return a list of routes 
    Routes filtered on the API side to save client-side effort and bandwidth.
    '''
    r = requests.get("https://api-v3.mbta.com/routes", {'filter[type]': '0,1'})
    if r.status_code != 200:
        raise Exception("got non-200 status code. bombing out.")
    else:
        route_data = r.json()
    
    return route_data


def get_routes_to_stops(route_data):
    '''
    Return a dictionary where the keys are routeIds and values are an lists-of-stopIds
    '''
    routeIds_to_stopIds = {}
    for temp_route in route_data['data']:
        logger.debug( 'getting stops for route: ' + temp_route['id'])

        r = requests.get("https://api-v3.mbta.com/stops", {'filter[route]': temp_route['id']})
        if r.status_code == 200:
            temp_stops_data = r.json()
            routeIds_to_stopIds[temp_route['id']] = [] #stops_data
            for stop in temp_stops_data['data']:
                routeIds_to_stopIds[temp_route['id']].append(stop['id'])
                logger.debug('Appended to Route: *' + temp_route['id'] + '* ' + stop['id'])
    return routeIds_to_stopIds


def show_min_and_max_stops(routeIds_to_stopIds):
    '''
    Display the route with the Most stops and the route with the Least stops.
    Return a set stops.
    '''
    # Find min & max stops
    logger.info("Showing Min and Max stops ------------------------------------------")
    set_of_stops = set()
    min_stops = 500
    min_stops_route = None
    max_stops = 0
    max_stops_route = None

    for route,stops in routeIds_to_stopIds.items():
        logger.debug('Route: ' + route + ', Stops: ' + str(len(stops)))
        if len(stops) > max_stops:
            max_stops = len(stops)
            max_stops_route = route

        if len(stops) < min_stops:
            min_stops = len(stops)
            min_stops_route = route

        for stop in stops:
            set_of_stops.add(stop)

    logger.info('Min stops: ' + str(min_stops) + ' on ' + min_stops_route)
    logger.info('Max stops: ' + str(max_stops) + ' on ' + max_stops_route)
    logger.info('Total Unique Stops:  ' + str(len(set_of_stops)))    
    return set_of_stops


def build_route_intersections(set_of_stops, routeIds_to_stopIds):
    '''
    This is a crude inverted dictionary.
    Also I should probably remove all the key+value where the value is list of length One.
    Returns a dictionary where a keys are stopIds and the values are lists-of-routeIds
    '''
    stopIds_to_routeIds = {}
    for temp_stop in set_of_stops:
        stopIds_to_routeIds[temp_stop] = []
        for route,stops in routeIds_to_stopIds.items():
            if temp_stop in stops:
                stopIds_to_routeIds[temp_stop].append(route)
    return stopIds_to_routeIds


def show_intersections(stopIds_to_routeIds, routeId_to_routeLongName):
    '''
    Method for outputting the STOPS where ROUTES intersect
    '''
    logger.info("Showing intersections -----------------------------------------------")
    for stop,routes in stopIds_to_routeIds.items():
        if len(routes) > 1:
            logger.info("Stop: " +stop  + " shared by " + str(len(routes)) + ' routes: ') # todo:  make stop names prettier
            for temp_route in routes:
                logger.info("    " + routeId_to_routeLongName[temp_route])


def directions(r_to_s, s_to_r):
    '''
    Method for gathering STOPS as user input and then giving feedback on how to get between the STOPS.
    This method cannot handle multiple-intersections yet.
    '''
    i1 = input('first STOP id: ')
    i2 = input('last STOP id: ')

    # first case:  same stop
    if i1 == i2:
        logger.info ("same stop")
        return


    # second case:  same route
    for route,stops in r_to_s.items():
        if i1 in stops and i2 in stops:
            logger.info("both stops are on the same route: " + route)
            return

    # third case:  intersecting routes

    # get route names (a stop could be at the intersection of multiple routes)
    start_routes = []
    end_routes = []
    # find the routes containing the user-inputted-stops
    for route,stops in r_to_s.items():
        if i1 in stops:
            start_routes.append(route)
            logger.debug('possible start route: ' + route)
        if i2 in stops:
            end_routes.append(route)
            logger.debug('possible end route: ' + route)

    if len(start_routes) == 0:
        raise Exception('input1, ' + i1 + ' not found on any route')
    if len(end_routes) == 0:
        raise Exception('input2, ' + i2 + ' not found on any route')
    
    # check if routes intersect
    # loop through each the possible start routes and possible end routes and see if they have an intersection
    for sr in start_routes:
        for er in end_routes:
            for stop,routes in s_to_r.items():
                if sr in routes and er in routes:
                    logger.info(i1 +' to ' + i2 + ' via ' + stop)
                    return

    # fourth case:  routes with multiple hops
    # todo (sorry!)
    raise Exception('Congratulations!  Youve won an Exception!')


if __name__ == "__main__":
    # execute only if run as a script
    main()
