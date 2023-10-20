import pandas as pd
from geopy.geocoders import Nominatim
import pyexcel_ods
import os

ECHO_LOC = 'epa-echo-project/lib/raw/'
WRITE_PATH = os.path.join(os.path.dirname(os.path.abspath("")[:-3]), ECHO_LOC)



# Load the ODS file into a DataFrame
ods_data = pyexcel_ods.get_data('./lib/fire/SiteList.ods')
# Assuming the data is in the first sheet (you may need to adjust the index)
raw_data = ods_data[list(ods_data.keys())[0]]
# Skip the first three rows (header)
data = raw_data[3:]

# Create the DataFrame
df = pd.DataFrame(data, columns=raw_data[2])

# Initialize the Nominatim geocoder
geolocator = Nominatim(user_agent="geocoder")

# Define a function to geocode an address and handle exceptions
def geocode_address(address, city, state):
    full_address = f'{address}, {city}, {state}'
    try:
        location = geolocator.geocode(full_address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Error geocoding {full_address}: {str(e)}")
        return None, None

# Create new columns for latitude and longitude, handling exceptions
df['Latitude'], df['Longitude'] = zip(*df.apply(lambda row: geocode_address(row['Host Site'], row['City'], row['State']), axis=1))

# Print the DataFrame with latitude and longitude
print(df.head())


# Save the geocoded data to a CSV file
df.to_csv(f'{WRITE_PATH}geocoded_data.csv', index=False)