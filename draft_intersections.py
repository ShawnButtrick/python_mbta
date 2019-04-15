import logging
import requests
import json
import pprint
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache_file = './mbta_cache'

def main():
    r_to_s = {"r":["a","b"], "o":["b","c"], "q":["c","d"]}
    s_to_r = {"b":["r","o"], "c":["o","q"]}
    directions(r_to_s, s_to_r)

def directions(r_to_s, s_to_r):
    i1 = input('first STOP id: ')
    i2 = input('last STOP id: ')

    # first case:  same stop
    if i1 == i2:
        print ("same stop")
        return


    # second case:  same route
    for route,stops in r_to_s.items():
        if i1 in stops and i2 in stops:
            print ("both stops are on the same route: " + route)
            return

    # third case:  intersecting routes

    # get route names (a stop could be at the intersection of multiple routes)
    start_routes = []
    end_routes = []
    # find the routes containing the user-inputted-stops
    for route,stops in r_to_s.items():
        if i1 in stops:
            start_routes.append(route)
            print ('possible start route: ' + route)
        if i2 in stops:
            end_routes.append(route)
            print ('possible end route: ' + route)

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
                    print (i1 +' to ' + i2 + ' via ' + stop)
                    return

    # fourth case:  routes with multiple hops
    # todo (sorry!)


if __name__ == "__main__":
    # execute only if run as a script
    main()
