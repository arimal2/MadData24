import googlemaps
import requests
import polyline
import pandas as pd
from dotenv import load_dotenv
import os

#
# Author: Yanna Keohane
# Date: 02/22/2025
# The GeneratesPaths class can generate routes between locations integrating googlemaps API
#

class GeneratePaths:

    # Constructor for GeneratePaths
    # Initializes globals: API_KEY, name_count, df, and fileName
    def __init__(self):
        global API_KEY
        global name_count
        global df
        global fileName

        API_KEY = os.environ.get("FLASK_APP_API_KEY")
        # this will count for the .csv file where to put the next line
        name_count = 0
        # creating the data frame with it's three headers
        headers = ["Class", "Location", "Coordinates"]
        df = pd.DataFrame(columns=headers) 
        # the file we're printing to
        fileName = ".\\locations.csv"

    # Generate the route between 2 locations (addresses)
    # parameters:
    # - origin: start location
    # - destination: end location
    # return: 
    # - a list of coordinates (list of list) of generated points between origin and destination
    # - None if couldn't generate route between origin and destination
    def getRoute(self, origin, destination):
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "OK":
            return polyline.decode(data["routes"][0]["overview_polyline"]["points"])
        else:
            return None
        
    # Generates the coordinates of a specific location
    # parameters:
    # - location_name: the name of the location
    # return: 
    # - the coordinates of a given location
    # - None if could not find coordinates of given location
    def getCoords(self, location_name):
        url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location_name}&inputtype=textquery&fields=geometry&key={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "OK":
            location = data["candidates"][0]["geometry"]["location"]
            return (location["lat"], location["lng"])
        else:
            return None

    # Adds given class to specified CSV filename using a data frame (pandas)
    # parameters:
    # - name: name of the class
    # - location: the location of the class to add
    # - coords: the coordinates of the class
    # return:
    # - True if added to file
    # - False if something went wrong and not added to file
    def addClassToCSV(self, class_name, location, coords):
        try:
            if (fileName.endswith(".csv")):
                df.loc[name_count] = [class_name, location, coords]
                nameCount += 1
                df.to_csv(fileName, index=False)
                return True
            else:
                return False
        except:
            return False
        
    # Generates a dictionary of resturants from one location to another
    # parameters:
    # - start_loc: starting location
    # - end_loc: end location
    # - meters: the vicinity (meters) of places you can find
    # return:
    # - a dictionary of resturant names and their location
    # - None if any issues or if there are no resturants between locations
def generateNearByDict(self, start_loc, end_loc, type, meters):
    restaurant_dict = {}
    map_client = googlemaps.Client(API_KEY)

    # generating a route from start location to end location
    route_points = self.getRoute(API_KEY, start_loc, end_loc)

    # if problem occured generating route None is returned
    if not route_points:
        return None

    # traversing through every other point generated in route
    for point in route_points[::2]:
        point_coord = (point[0], point[1])
        try:
            # finding places nearby given point
            restaurants_nearby = map_client.places_nearby(location=point_coord, radius=meters, type=type)
            # adding all nearby areas of point to dictionary (repeats get overriden)
            for restaurant in restaurants_nearby.get('results', []):
                restaurant_dict[restaurant["name"]] = restaurant.get("vicinity", "No address provided")
        except:
            return None

    # if there are nearby places to go None is returned
    if (restaurant_dict):
        return restaurant_dict
    else:
        return None