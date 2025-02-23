import googlemaps  # pip install googlemaps
import requests
import polyline
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def get_route(api_key, origin, destination):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK":
        return data["routes"][0]["overview_polyline"]["points"]
    else:
        return None
    
def get_place_location(api_key, place_name):
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={place_name}&inputtype=textquery&fields=geometry&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK":
        location = data["candidates"][0]["geometry"]["location"]
        return (location["lat"], location["lng"])
    else:
        return None

def addClassToCSV(df, fileName, count, name, location, coords):
    df.loc[count] = [name, location, coords]
    df.to_csv(fileName, index=False) 

def addNearbyLocationsToCSV(df, fileName, start_loc, end_loc, nearby_dict, count):
    df.loc[count] = [start_loc, end_loc, nearby_dict]
    df.to_csv(fileName, index=False) 

def main():
    API_KEY = os.environ.get("FLASK_APP_API_KEY")
    map_client = googlemaps.Client(API_KEY)
    fileName = ".\\locations.csv"
    fileName2 = ".\\nearbyLocations.csv"
    locsCount = 0
    nearByCount = 0
    headers = ["Class", "Location", "Coordinates"]
    headers2 = ["Start Location", "End Location", "Places Nearby"]
    restaurant_dict = {}
    df = pd.DataFrame(columns=headers) 
    dfNearby = pd.DataFrame(columns=headers2)
    

    quit = False
    while not quit:
        name = input("Enter a class name (or 'quit' to finish): ") 
        if name.lower() == "quit":
            break
        loc = input(f"Enter the location for {name}: ")
        coords = get_place_location(API_KEY, loc)
        if coords is None:
            print("Error: location not found")
            continue
        
        addClassToCSV(df, fileName, locsCount, name, loc, coords)
        locsCount += 1
    
    classes = df["Class"].tolist()
    print(classes)

    print(get_place_location(API_KEY, df["Location"].iloc[1]))
    

    for i in range (len(classes) - 1):
        startLoc = df["Location"].iloc[i]
        endLoc = df["Location"].iloc[i + 1]

        route_points = polyline.decode(get_route(API_KEY, df["Location"].iloc[i], df["Location"].iloc[i + 1]))

        for point in route_points[::2]:
            point_coord = (point[0], point[1])
            restaurants_nearby = map_client.places_nearby(location=point_coord, radius=500, type="restaurants")
            for restaurant in restaurants_nearby['results']:
                restaurant_dict[restaurant["name"]] = restaurant.get("vicinity", "No address provided")
        print("HEY")
        addNearbyLocationsToCSV(dfNearby, fileName2, startLoc, endLoc, restaurant_dict, nearByCount)


if __name__ == "__main__":
    main()
