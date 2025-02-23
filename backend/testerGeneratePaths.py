
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
    backend = GeneratePaths(key)

    test_dict = backend.generateNearByDict("Union South", "Memorial Union", "library", 500)

    print(test_dict)

if __name__ == "__main__":
    main()