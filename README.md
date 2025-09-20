# AI-ROUTE-PLANNER
This project is an AI-powered route optimization tool designed for B2B sales teams. It calculates the most efficient travel route for sales representatives based on client locations, meeting schedules, and simulated dynamic factors like traffic delays. The goal is to help sales teams maximize client visits while minimizing travel time. In this route optimizer you just need to select the csv file of your meeting schedule . The csv file should contain the client name , address, meeting time and duration . After uploading it will give you the ordered list to reduce the time for travelling.it contains the traffic delays also you can set the delay and it will show you the optimized route according to it. you can also visualize your route in your map!!

FEATURES 

Optimized Visit Order: Automatically calculates the shortest and most efficient route for visiting all clients.

Interactive Map: Displays client locations on a dark-themed, visually appealing map with numbered markers, colored route lines, and directional arrows.

Real-Time Updates: Supports traffic simulation and route adjustments using a traffic multiplier slider.

Detailed Popups: Each marker shows client name, meeting time, and address.

Exportable HTML Map: Generates a standalone HTML file of the route for easy sharing.

CSV Upload: Accepts client data via CSV with columns: Client, Address, MeetingTime, Duration.

TECHNOLOGIES USED 

Python 3

Streamlit – for web interface (optional, for demo)

Folium – for interactive mapping

OR-Tools – for route optimization

Geopy – for geocoding addresses
