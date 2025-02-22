import googlemaps  # pip install googlemaps
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
    
    def __init__():
        global API_KEY
        global nameCount
        global df

        API_KEY = os.environ.get("FLASK_APP_API_KEY")
        nameCount = 0
        headers = ["Class", "Location", "Coordinates"]
        df = pd.DataFrame(columns=headers) 

    # Generate the route between 2 locations (addresses)
    # parameters:
    # - origin: start location
    # - destination: end location
    # return: 
    # - a list of coordinates (another list) of generated points between origin and destination
    # - None if something went wrong
    def get_route(api_key, origin, destination):
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={api_key}"
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
    # - None if something went wrong     
    def get_coords(api_key, location_name):
        url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location_name}&inputtype=textquery&fields=geometry&key={api_key}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "OK":
            location = data["candidates"][0]["geometry"]["location"]
            return (location["lat"], location["lng"])
        else:
            return None

    # Adds given class to specified CSV filename using a data frame
    # parameters:
    # - df: the datafram (pandas)
    # - fileName: the name of the file (.csv) you're printing to
    # - name: name of the class
    def addClassToCSV(df, fileName, class_name, location, coords):

        if (fileName.endswith(".csv")):
            df.loc[nameCount] = [class_name, location, coords]
            nameCount += 1
            df.to_csv(fileName, index=False)
            return True
        else:
            return False
        