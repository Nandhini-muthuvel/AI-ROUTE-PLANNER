import pandas as pd
from geopy.geocoders import Nominatim
import time

# Load CSV
df = pd.read_csv("clients.csv")

# Strip extra spaces from column names
df.columns = df.columns.str.strip()

# Check that 'Address' column exists
if 'Address' not in df.columns:
    print("Error: 'Address' column not found in CSV. Columns found:", df.columns.tolist())
    exit()

# Initialize geolocator
geolocator = Nominatim(user_agent="sales_route_planner")

# Geocode function
def geocode(address):
    if pd.isna(address) or address.strip() == "":
        return (None, None)
    try:
        location = geolocator.geocode(address)
        time.sleep(1)  # prevent rate limiting
        if location:
            return (location.latitude, location.longitude)
        else:
            return (None, None)
    except:
        return (None, None)

# Apply geocoding
df['Latitude'], df['Longitude'] = zip(*df['Address'].apply(geocode))

# Save new CSV
df.to_csv("clients_geocoded.csv", index=False)
print("Geocoding done! Saved as clients_geocoded.csv")
