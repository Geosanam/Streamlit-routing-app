import streamlit as st
import folium
from streamlit_folium import folium_static, st_folium

import requests
from geopy.geocoders import Nominatim

APP_TITLE = "Routing App"
APP_SUB_TITLE = "Using OpenRouteService Direction API"


#Geocoding of origin and destination
# @st.cache_data
def geocode(origin, destination):
    geolocator = Nominatim(user_agent = 'my_geocoder')

    current_location = geolocator.geocode(origin)
    dest_location = geolocator.geocode(destination)
    return current_location,dest_location


#Calling Openrouteservice Direction API
# @st.cache_data
def route(start, end):
    parameters = {
        'api_key':'5b3ce3597851110001cf6248ec533d4fedf241cd904da8356dd052b9',
        'start':'{},{}'.format(start.longitude,start.latitude),
        'end':'{},{}'.format(end.longitude,end.latitude)
    }

    response = requests.get('https://api.openrouteservice.org/v2/directions/driving-car',params = parameters)

    data = response.json()
    if 'error' in data:
        st.error('Error in data, please try again')
        return None
    # print(data)

    else:
        route_coords = data['features'][0]['geometry']['coordinates']

        final_coords = [[lat, long] for long, lat in route_coords]

        return final_coords



# def display_features_filter():
#     features = ["school","park","hospital"]
#     st.sidebar.selectbox("Choose Features: ",features)
    
# @st.cache_resource  # @st.cache_data
# def load_map(submit,input_start,input_end):
#     # Load the map
#     m = initial_map()  # init
#     # df = load_df()  # load data
#     m = process_map(submit,input_start,input_end, m)  # plot points
#     return m




def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)


    with st.sidebar:
        input_origin= st.text_input("Enter your current location: ")
        input_destination= st.text_input("Enter your destination: ")
        submit = st.button("Perform routing")
    

    #DISPLAY MAP
    m = folium.Map(tiles='OpenStreetMap')
    folium.TileLayer("CartoDB Positron").add_to(m)
    folium.TileLayer("Cartodb dark_matter").add_to(m)
    folium.TileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',name='OpenTopoMap').add_to(m)
    # folium.TileLayer("CartoBD Voyager").add_to(m)
    # folium.TileLayer("NASAGIBS Blue Marble").add_to(m)

    folium.LayerControl().add_to(m)
    m.fit_bounds([[26.347, 80.058],[30.447, 88.201]])





    # # m = initial_map()
    # final_map = load_map(submit,input_start,input_end)
    
    ### The workflow structure below is very important to optimise the input taken from the user and proper working of the app without any client-side erro ######
    if submit:
        if (input_origin and input_destination):

            # Geocoded output
            origin, destination = geocode(input_origin, input_destination)

            # Calling route function
            if origin and destination:
                output_route = route(origin, destination)

                if output_route: 

                    bbox = [
                    [min(lat for lat, lon in output_route),min(lon for lat, lon in output_route),],
                    [max(lat for lat, lon in output_route),max(lon for lat, lon in output_route)]]
                    m.fit_bounds(bbox)
                    folium.Marker(location=[origin.latitude,origin.longitude],popup=f'U r in {input_origin}').add_to(m)
                    folium.Marker(location=[destination.latitude,destination.longitude],popup=f'Ur destination is {input_destination}').add_to(m)
                    folium.PolyLine(
                        locations=output_route,
                        color="purple",
                        tooltip=f"{input_origin} to {input_destination}",
                        weight=5,
                    ).add_to(m)
                    # st_folium(m,width=800,height=450)
                else:
                    st.error(
                        'Request failed. Try again !!!'
                    )

            else:
                st.error("Request failed. Please try again!!!")
    
    folium_static(m,width=800,  height=450)



if __name__ == "__main__":
    main()
