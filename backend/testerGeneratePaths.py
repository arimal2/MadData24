
import googlemaps
import requests
import polyline
import pandas as pd
from dotenv import load_dotenv
import os
from generatePaths import GeneratePaths


def main():
    test_dict = {}
    load_dotenv()
    key = os.environ.get("FLASK_APP_API_KEY")
    backend = GeneratePaths()

    test_list = ["Union South, Madison", "Memorial Union, Madison", "8601 Stonebrook Circle, Middleton"]

    # test_dict = backend.generateNearByDict("Union South", "Memorial Union", "library", 500)
    # print(test_dict)
    
    # print(backend.getCoords("Memorial Union"))
    print(type(test_list))

    path_coordinates = backend.getShortestPath(test_list)
    print(path_coordinates[0])
    print(path_coordinates[1])

if __name__ == "__main__":
    main()