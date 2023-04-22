import math
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static

def haversine(source_coords, dest_coords):
    lon1, lat1, lon2, lat2 = map(math.radians, [source_coords[1], source_coords[0], dest_coords[1], dest_coords[0]])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371
    return c * r

st.set_page_config(layout="wide")
st.title("GIS311 Assignment 2")
merged_df = pd.read_csv('data/merged_data.csv', low_memory=False)
airports_df = merged_df[['Source airport', 'Destination airport', 'Latitude_x', 'Longitude_x', 'Latitude_y', 'Longitude_y', 'Name_x', 'Name_y']]

st.sidebar.title('Select Airports')
source_airport = st.sidebar.selectbox('Source Airport', [( airport_code,airport_name) for airport_code, airport_name in airports_df[['Source airport','Name_x']].drop_duplicates().values], format_func=lambda x: x[1])

#destination_airports = st.sidebar.multiselect('Destination Airport', [], format_func=lambda x: x[0], key='destination_airport', max_selections=1)

fg = folium.FeatureGroup()

folium_map = folium.Map(location=[0,0], zoom_start=3, tiles='CartoDB positron', crs='EPSG3857',)
folium_map.add_child(fg)

if source_airport:
    valid_destinations = airports_df[airports_df['Source airport'] == source_airport[0]]['Name_y'].unique().tolist()
    destination_airports = st.sidebar.multiselect('Destination Airport', [(airport_name, airport_code) for airport_code, airport_name in airports_df[['Destination airport', 'Name_y']].drop_duplicates().values if airport_name in valid_destinations], format_func=lambda x: x[0], key='destination_airport', max_selections=1)

if destination_airports:
    filtered_airports_df = airports_df[(airports_df['Source airport'] == source_airport[0]) & (airports_df['Destination airport'].isin(destination_airports[0]))]
    if not filtered_airports_df.empty:
        map_center = [filtered_airports_df['Latitude_x'].iloc[0], filtered_airports_df['Longitude_x'].iloc[0]]
        folium_map.fit_bounds([[filtered_airports_df['Latitude_x'].min(), filtered_airports_df['Longitude_x'].min()],
                               [filtered_airports_df['Latitude_y'].max(), filtered_airports_df['Longitude_y'].max()]])

        source_coords = [filtered_airports_df['Latitude_x'].iloc[0], filtered_airports_df['Longitude_x'].iloc[0]]
        folium.Marker(location=source_coords, tooltip=source_airport[0]).add_to(fg)

        for idx, row in filtered_airports_df.iterrows():
            dest_coords = [row['Latitude_y'], row['Longitude_y']]
            folium.Marker(location=dest_coords, tooltip=row['Destination airport']).add_to(fg)
            folium.PolyLine(locations=[source_coords, dest_coords], color='red', tooltip=str(round(haversine(source_coords, dest_coords),2))+"km", smooth_factor=0.5).add_to(fg)

        st.info("Distance between: " + source_airport[0] + " and "+destination_airports[0][0] +" is: " + str(round(haversine(source_coords, dest_coords),2)) + " km")
    else:
        st.sidebar.warning("No routes found for the selected source and destination airports.")

folium_static(folium_map, width=1400, height=600)
