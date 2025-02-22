import googlemaps  # pip install googlemaps
import requests
import polyline
import pandas as pd

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


def main():
    API_KEY = "AIzaSyBLM_O7mDQ3QxDWRK8rO6L4o-wlgii27k0"
    fileName = "C:\\Users\\yanna\\OneDrive\\Desktop\\MadData2025\\locations.csv"
    locsCount = 0
    headers = ["Class", "Location", "Coordinates"]
    df = pd.DataFrame(columns=headers) 

    quit = False
    while not quit:
        name = input("Enter a class name (or 'quit' to finish): ") 
        if name.lower() == "quit":
            break
        loc = input(f"Enter the location forH {name}: ")
        coords = get_place_location(API_KEY, loc)
        if coords is None:
            print("Error: location not found")
            continue
        
        addClassToCSV(df, fileName, locsCount, name, loc, coords)
        locsCount += 1
    
    classes = df["Class"].tolist()
    print(classes)

    for i in range (len(classes) - 1):
        first = a

if __name__ == "__main__":
    main()