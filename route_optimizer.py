import pandas as pd
import math
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import folium

# -----------------------------
# Step 1: Load geocoded CSV
# -----------------------------
df = pd.read_csv("clients_geocoded.csv")

# Strip extra spaces from column names
df.columns = df.columns.str.strip()

# Check for missing coordinates
missing_coords = df[df['Latitude'].isna() | df['Longitude'].isna()]
if not missing_coords.empty:
    print("Warning: These clients were removed due to missing coordinates:")
    print(missing_coords[['Client', 'Address']])
    # Remove rows with missing coordinates
    df = df.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)

# Extract coordinates as tuples
coords = list(zip(df['Latitude'], df['Longitude']))
N = len(coords)

# -----------------------------
# Step 2: Build distance matrix
# -----------------------------
def haversine(coord1, coord2):
    R = 6371  # Earth radius in km
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Distance matrix in meters
dist_matrix = [[int(haversine(coords[i], coords[j])*1000) for j in range(N)] for i in range(N)]

# -----------------------------
# Step 3: OR-Tools Routing
# -----------------------------
manager = pywrapcp.RoutingIndexManager(len(dist_matrix), 1, 0)
routing = pywrapcp.RoutingModel(manager)

def distance_callback(from_index, to_index):
    return dist_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

search_params = pywrapcp.DefaultRoutingSearchParameters()
search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

solution = routing.SolveWithParameters(search_params)

if not solution:
    print("No solution found!")
    exit()

# Extract route order
route = []
index = routing.Start(0)
while not routing.IsEnd(index):
    route.append(manager.IndexToNode(index))
    index = solution.Value(routing.NextVar(index))
route.append(manager.IndexToNode(index))

print("\nOptimized Visit Order:")
for i in route:
    print(df['Client'][i])

# -----------------------------
# Step 4: Visualize on Map
# -----------------------------
# Center map at average coordinates
m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=12)

# Add markers
for idx in route:
    client = df.iloc[idx]
    folium.Marker(
        [client['Latitude'], client['Longitude']],
        popup=f"{client['Client']} ({client['MeetingTime']})"
    ).add_to(m)

# Draw route line
route_coords = [coords[i] for i in route]
folium.PolyLine(route_coords, color='blue', weight=3, opacity=0.7).add_to(m)

# Save map
m.save("optimized_route.html")
print("\nMap saved as optimized_route.html. Open this file in your browser to see the route.")
