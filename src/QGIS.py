import os
import pickle
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
import folium

import ee

def main():
    ## Trigger the authentication flow. You only need to do this once
    ee.Authenticate()

    # Initialize the library.
    ee.Initialize()

    # Print the elevation of Mount Everest.
    dem = ee.Image('USGS/SRTMGL1_003')
    xy = ee.Geometry.Point([86.9250, 27.9881])
    elev = dem.sample(xy, 30).first().get('elevation').getInfo()
    print('Mount Everest elevation (m):', elev)


if __name__ == "__main__":
    main()
