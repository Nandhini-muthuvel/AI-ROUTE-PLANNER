import streamlit as st
import pandas as pd
import math
from geopy.geocoders import Nominatim
import time
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="AI Sales Route Planner", layout="wide")
st.title("AI-Optimized Sales Route Planner 🚀")

# -----------------------------
# Step 1: Upload CSV
# -----------------------------
uploaded_file = st.file_uploader("Upload your CSV (Client, Address, MeetingTime, Duration)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()  # clean headers

    st.subheader("Uploaded Data")
    st.dataframe(df)

    # -----------------------------
    # Step 2: Geocode missing coordinates
    # -----------------------------
    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        df['Latitude'] = None
        df['Longitude'] = None

    geolocator = Nominatim(user_agent="sales_route_planner")
    missing = df['Latitude'].isna() | df['Longitude'].isna()

    if missing.any():
        st.info("Geocoding missing addresses...")
        for idx in df[missing].index:
            addr = df.at[idx, 'Address']
            try:
                location = geolocator.geocode(addr)
                time.sleep(1)  # prevent rate limiting
                if location:
                    df.at[idx, 'Latitude'] = location.latitude
                    df.at[idx, 'Longitude'] = location.longitude
                else:
                    st.warning(f"Could not geocode: {addr}")
            except:
                st.warning(f"Error geocoding: {addr}")

    # Drop rows with missing coordinates
    df = df.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)
    coords = list(zip(df['Latitude'], df['Longitude']))
    N = len(coords)

    # -----------------------------
    # Step 3: Build distance matrix
    # -----------------------------
    def haversine(coord1, coord2):
        R = 6371  # km
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Optional: simulate traffic delays
    traffic_factor = st.slider("Traffic multiplier (simulate delays)", 1.0, 3.0, 1.0)
    dist_matrix = [[int(haversine(coords[i], coords[j])*1000*traffic_factor) for j in range(N)] for i in range(N)]

    # -----------------------------
    # Step 4: OR-Tools Routing
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

    if solution:
        # Extract route
        route = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))

        st.subheader("Optimized Visit Order")
        st.write([df['Client'][i] for i in route])

        # -----------------------------
        # Step 5: Display map
        # -----------------------------
        m = folium.Map(
    location=[df['Latitude'].mean(), df['Longitude'].mean()],
    zoom_start=12,
    tiles="CartoDB Positron"
)

        # Add markers
        for idx in route:
            client = df.iloc[idx]
            folium.Marker(
                [client['Latitude'], client['Longitude']],
                popup=f"{client['Client']} ({client['MeetingTime']})"
            ).add_to(m)

        # Draw route line
        route_coords = [coords[i] for i in route]
        folium.PolyLine(
    route_coords,
    color='blue',      # line color
    weight=5,          # line thickness
    opacity=0.9,
    dash_array='5,10'  # optional: dashed line
).add_to(m)
     

    else:
        st.error("No solution found!")

